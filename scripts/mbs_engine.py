import polars as pl

# Industry Constants
MONTHS_IN_YEAR = 12
BASIS_POINTS_DIVISOR = 1200  # Converts Annual % to Monthly Decimal
STANDARD_TERM_MONTHS = 360   # Standard 30-year fixed

def calculate_mbs_cashflows(df: pl.DataFrame) -> pl.DataFrame:
    """
    Performs vectorized mortgage amortization to isolate Scheduled vs. 
    Unscheduled (Prepayment) principal from Fannie Mae performance data.
    """
    
    # 1. Sort to ensure chronological order per loan
    df = df.sort(["loan_id", "period"])
    
    # 2. Establish Beginning UPB
    # coalesce ensures that for the first month (or single-row files), 
    # beg_upb is not null by using the current UPB as the starting point.
    df = df.with_columns([
        pl.col("upb").shift(1).over("loan_id").alias("prev_upb")
    ]).with_columns([
        pl.coalesce(pl.col("prev_upb"), pl.col("upb")).alias("beg_upb")
    ])

    # 3. Calculate Interest and Total Principal Waterfall
    df = df.with_columns([
        (pl.col("beg_upb") * (pl.col("note_rate") / BASIS_POINTS_DIVISOR)).alias("int_cf"),
        (pl.col("beg_upb") - pl.col("upb")).alias("total_prin_cf")
    ])

    # 4. Calculate Scheduled Monthly Payment (P&I)
    # Formula: P = L * [i(1+i)^n] / [(1+i)^n - 1]
    df = df.with_columns([
        (pl.col("note_rate") / BASIS_POINTS_DIVISOR).alias("i"),
        (STANDARD_TERM_MONTHS - pl.col("loan_age")).alias("n")
    ]).with_columns([
        (
            pl.col("beg_upb") * (pl.col("i") * (1 + pl.col("i"))**pl.col("n")) / 
            ((1 + pl.col("i"))**pl.col("n") - 1 + 1e-10)
        ).alias("scheduled_pi")
    ])

    # 5. Isolate Prepayments (Voluntary Paydowns)
    # Scheduled Principal = Total P&I Payment - Interest portion
    df = df.with_columns([
        (pl.col("scheduled_pi") - pl.col("int_cf")).alias("sched_prin_cf")
    ]).with_columns([
        (pl.col("total_prin_cf") - pl.col("sched_prin_cf")).alias("prepay_cf")
    ])

    # 6. Calculate Prepayment Speeds (SMM & CPR)
    # SMM = Prepay / (Beginning UPB - Scheduled Principal)
    df = df.with_columns([
        (pl.col("prepay_cf") / (pl.col("beg_upb") - pl.col("sched_prin_cf") + 1e-10))
        .fill_nan(0)
        .clip(0, 1) 
        .alias("smm")
    ]).with_columns([
        (1 - (1 - pl.col("smm"))**MONTHS_IN_YEAR).alias("cpr")
    ])

    return df.filter(pl.col("beg_upb") > 0)

def get_pool_kpis(df: pl.DataFrame):
    """
    Summarizes the loan-level data into Portfolio-level metrics.
    Returns zeroed metrics if the dataframe is empty to prevent dashboard crashes.
    """
    if df.is_empty():
        return {
            "WAC": 0.0, "Avg_CPR": 0.0, "WAL": 0.0, 
            "Total_Int_Income": 0.0, "Total_Prin_Recovered": 0.0, "Prepay_Ratio": 0.0
        }
        
    metrics = {
        "WAC": df["note_rate"].mean(),
        "Avg_CPR": df["cpr"].mean(),
        "Total_Int_Income": df["int_cf"].sum(),
        "Total_Prin_Recovered": df["total_prin_cf"].sum(),
    }
    
    # Calculate Weighted Average Life (WAL)
    total_prin = metrics["Total_Prin_Recovered"]
    metrics["WAL"] = (df["total_prin_cf"] * (df["loan_age"] / 12)).sum() / (total_prin + 1e-10)
    metrics["Prepay_Ratio"] = df["prepay_cf"].sum() / (total_prin +
