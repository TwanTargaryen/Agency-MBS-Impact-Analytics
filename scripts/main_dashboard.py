from engine import MBSEngine
from portfolio_strategy import PortfolioStrategy

# 1. Input the PenFed Balance Sheet Data
penfed_data = {
    'Category': ['Loans', 'Loans', 'Investments', 'Investments'],
    'Fiscal Year': [2023, 2024, 2023, 2024],
    'Balance': [28701635, 24752940, 3116861, 3145073]
}

# 2. Run Strategy
strategy = PortfolioStrategy(penfed_data)
current_loan_book = strategy.get_analysis()

# 3. Run Quantitative Scenarios
engine = MBSEngine()
scenarios = {'Slow': 6, 'Base': 12, 'Fast': 25}

print("\nSCENARIO SENSITIVITY (Macro Portfolio Level):")
for name, cpr in scenarios.items():
    df = engine.generate_waterfall(current_loan_book, 6.5, cpr)
    total_msr = df['MSR_Fee'].sum()
    print(f"{name} ({cpr}% CPR): MSR Asset Value = ${total_msr:,.2f}")
