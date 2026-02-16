import pandas as pd

class PortfolioStrategy:
    """Translates PenFed Balance Sheet trends into Modeling Inputs."""
    
    def __init__(self, data_dict):
        self.df = pd.DataFrame(data_dict)

    def get_analysis(self):
        # Pivot the PenFed data to find the 2023-2024 delta
        pivot = self.df.pivot(index='Category', columns='Fiscal Year', values='Balance')
        loan_change = (pivot.loc['Loans', 2024] - pivot.loc['Loans', 2023]) / pivot.loc['Loans', 2023]
        
        # Guidehouse-style insight
        print(f"STRATEGIC INSIGHT: Loan Portfolio contracted by {loan_change:.1%}")
        print(f"Targeting remaining ${pivot.loc['Loans', 2024]:,.0f} (in 000s) for MBS modeling.")
        
        return pivot.loc['Loans', 2024] * 1000 # Convert 000s to actual dollars
