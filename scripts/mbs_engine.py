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
    
    # 1. Establish Lagged UPB (Beginning of Period Balance)
    # Sort ensure chronological order per loan for the 'shift' to work
    df = df.sort(["loan_id", "period"])
    
    df = df.with_columns([
        pl.col("upb").shift(1).over("loan_id").alias("beg_upb")
    ])

    # 2. Calculate Interest and Total Principal Waterfall
    df = df.with_columns([
        (pl.col("beg_upb") * (pl.col("note_rate") / BASIS_POINTS_DIVISOR)).alias("int_cf"),
        (pl.col("beg_upb") - pl.col("upb")).alias("total_prin_cf")
    ])

    # 3. Calculate Scheduled Monthly Payment (P&I)
    # Standard Amortization Formula: P = L * [i(1+i)^n] / [(1+i)^n - 1]
    df = df.with_columns([
        (pl.col("note_rate") / BASIS_POINTS_DIVISOR).alias("monthly_rate"),
        (STANDARD_TERM_MONTHS - pl.col("loan_age")).alias("remaining_months")
    ])

    # We use a small epsilon to avoid division by zero on matured loans
    df = df.with_columns([
        (
            pl.col("beg_upb") * (pl.col("monthly_rate") * (1 + pl.col("monthly_rate"))**pl.col("remaining_months")) / 
            ((1 + pl.col("monthly_rate"))**pl.col("remaining_months") - 1 + 1e-10)
        ).alias("scheduled_pi")
    ])

    # 4. Isolate Prepayments (Voluntary Paydowns)
    df = df.with_columns([
        (pl.col("scheduled_pi") - pl.col("int_cf")).alias("sched_prin_cf")
    ]).with_columns([
        (pl.col("total_prin_cf") - pl.col("sched_prin_cf")).alias("prepay_cf")
    ])

    # 5. Calculate Prepayment Speeds (SMM & CPR)
    # SMM = Prepay / (Beginning UPB - Scheduled Principal)
    df = df.with_columns([
        (pl.col("prepay_cf") / (pl.col("beg_upb") - pl.col("sched_prin_cf") + 1e-10))
        .fill_nan(0)
        .clip(0, 1) 
        .alias("smm")
    ]).with_columns([
        (1 - (1 - pl.col("smm"))**MONTHS_IN_YEAR).alias("cpr")
    ])

    # 6. CRITICAL: Return the processed dataframe
    return df.drop_nulls(subset=["beg_upb"])

def get_pool_kpis(df: pl.DataFrame):
    """Summarizes the loan-level data into Portfolio-level metrics."""
    if df.is_empty():
        return {"Error": "Dataframe is empty"}
        
    metrics = {
        "WAC": df["note_rate"].mean(),
        "Avg_CPR": df["cpr"].mean(),
        "Total_Cash_Flow": df["int_cf"].sum() + df["total_prin_cf"].sum(),
        "Prepay_Ratio": df["prepay_cf"].sum() / (df["total_prin_cf"].sum() + 1e-10)
    }
    return metrics
