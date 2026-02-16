import polars as pl
import numpy as np

class LoanDataFactory:
    """Generates or loads millions of rows for Loan-Level analysis."""
    @staticmethod
    def generate_mock_portfolio(n=1_000_000):
        return pl.DataFrame({
            "loan_id": np.arange(n),
            "upb": np.random.uniform(50000, 500000, n),
            "note_rate": np.random.uniform(3.5, 7.5, n),
            "fico_score": np.random.normal(720, 50, n).clip(300, 850),
            "ltv": np.random.uniform(60, 95, n)
        })
