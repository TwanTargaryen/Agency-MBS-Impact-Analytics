import pandas as pd
from engine import MBSEngine
from cpr_ensemble import CPREnsemble
from portfolio_strategy import PortfolioStrategy

class SecuritizationPipeline:
    def __init__(self, raw_data):
        # 1. CLEANING: Use your existing Strategy class
        self.strat = PortfolioStrategy(raw_data)
        self.engine = MBSEngine()
        
    def run_fannie_delivery(self):
        # 2. FILTERING: Use the Delinquency data from the 2024 Report
        # We only take 'Current' Real Estate loans
        eligible_upb = 14307394 * 1000 # Amortized Cost of 'Current' Real Estate
        
        # 3. PREDICTION: Get ML-driven speeds for the sale
        ensemble = CPREnsemble(treasury_rate=4.25, portfolio_wac=6.5)
        cpr_prediction, risk_score = ensemble.get_consensus_cpr()
        
        # 4. VALUATION: Calculate what PenFed keeps (The MSR)
        # Fannie gets the Principal/Interest; PenFed keeps the 25bps Servicing Fee
        mbs_waterfall = self.engine.generate_waterfall(eligible_upb, 6.5, cpr_prediction)
        retained_value = mbs_waterfall['MSR_Fee'].sum()
        
        return {
            "Pool_Size": eligible_upb,
            "CPR_Forecast": cpr_prediction,
            "MSR_Asset_Created": retained_value,
            "Model_Risk_Buffer": risk_score
        }

# Logic for the "Executive Dashboard"
pipeline = SecuritizationPipeline(penfed_raw_dict)
results = pipeline.run_fannie_delivery()
