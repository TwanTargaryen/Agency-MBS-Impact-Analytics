import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PortfolioStrategy")

class PortfolioStrategy:
    """
    Translates PenFed Financial Statement Trends
    into Securitization Modeling Inputs.
    """

    def __init__(self, data_dict):
        self.df = pd.DataFrame(data_dict)

    def get_analysis(self):
        pivot = self.df.pivot(
            index='Category',
            columns='Fiscal Year',
            values='Balance'
        )

        if 'Loans' not in pivot.index:
            raise ValueError("Missing 'Loans' category")
        if 2023 not in pivot.columns or 2024 not in pivot.columns:
            raise ValueError("Missing fiscal year data")

        loans_2023 = pivot.loc['Loans', 2023]
        loans_2024 = pivot.loc['Loans', 2024]
        loan_change = (loans_2024 - loans_2023) / loans_2023

        insight = {
            "Loan_2023": loans_2023 * 1000,
            "Loan_2024": loans_2024 * 1000,
            "YoY_Change": round(loan_change, 4),
            "Strategic_Message": f"Loan portfolio contracted by {loan_change:.1%}"
        }

        logger.info(f"Portfolio Analysis: {insight}")
        return insight
