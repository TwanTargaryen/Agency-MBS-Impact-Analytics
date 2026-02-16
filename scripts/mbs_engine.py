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
    # We sort by loan_id and period to ensure the shift aligns correctly
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
    # Formula: P = L * [c(1+c)^n] / [(1+c)^n - 1]
    # where n is remaining terms (Original Term - Current Age)
    df = df.with_columns([
        (pl.col("note_rate") / BASIS_POINTS_DIVISOR).alias("monthly_rate"),
        (STANDARD_TERM_MONTHS - pl.col("loan_age")).alias("remaining_months")
    ])

    df = df.with_columns([
        (
            pl.col("beg_upb") * (pl.col("monthly_rate") * (1 + pl.col("monthly_rate"))**pl.col("remaining_months")) / 
            ((1 + pl.col("monthly_rate"))**pl.col("remaining_months") - 1)
        ).alias("scheduled_pi")
    ])

    # 4. Isolate Prepayments (Voluntary Paydowns)
    # Sched Prin = Total Scheduled Payment - Interest Part
    # Prepay = Actual Principal Received - Scheduled Principal
    df = df.with_columns([
        (pl.col("scheduled_pi") - pl.col("int_cf")).alias("sched_prin_cf")
    ]).with_columns([
        (pl.col("total_prin_cf") - pl.col("sched_prin_cf")).alias("prepay_cf")
    ])

    #
