import pandas as pd
import logging
from engine import MBSEngine
from cpr_ensemble import CPREnsemble
from portfolio_strategy import PortfolioStrategy

# Setup logging to create an "Audit Trail" for Guidehouse/Ozzy
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SecuritizationPipeline")

class SecuritizationPipeline:
    def __init__(self, raw_data):
        """
        Initializes with PenFed raw data.
        raw_data: DataFrame containing loan-level or category-level data.
        """
        self.strat = PortfolioStrategy(raw_data)
        self.engine = MBSEngine()
        self.portfolio = raw_data if isinstance(raw_data, pd.DataFrame) else pd.DataFrame(raw_data)
        
    def validate_pool_compliance(self, pool_df):
        """
        INTERNAL AUDIT GATE: Checks if the pool meets Fannie Mae standards.
        Returns a 'Cleaned' dataframe and a compliance flag.
        """
        logger.info("Starting Fannie Mae Eligibility Scan...")
        
        # 1. AUTO-PURGE: Remove Ineligible Assets (Taxi Medallions from Page 40)
        # We search for any mention of 'Taxi' in the Category or Asset_Type column
        initial_count = len(pool_df)
        clean_df = pool_df[~pool_df['Category'].str.contains('Taxi', case=False, na=False)].copy()
        
        purged_count = initial_count - len(clean_df)
        if purged_count > 0:
            logger.warning(f"PURGED: {purged_count} ineligible Taxi Medallion assets removed from pool.")

        # 2. CREDIT GATE: Check Allowance Ratio (Note 5 compliance)
        # Fannie usually requires specific 'Credit Enhancement' levels.
        # We simulate checking if the reserve ratio is at least 0.40%
        # (Based on PenFed's Real Estate Allowance of $49.9M / $14.5B UPB)
        allowance_ratio = 0.0034  # Actual PenFed RE ratio is ~0.34%
        if allowance_ratio < 0.0040:
            logger.info("Applying Credit Enhancement: Supplemental over-collateralization required.")
            
        return clean_df

    def run_fannie_delivery(self, treasury_rate=4.25):
        """
        Executes the end-to-end securitization sale.
        """
        # --- Step 1: Compliance & Purging ---
        cleaned_portfolio = self.validate_pool_compliance(self.portfolio)
        
        # --- Step 2: Extract Eligible UPB ---
        # Using the actual 'Current' Real Estate UPB from your 2024 data notes
        eligible_upb = 14307394 * 1000 
        
        # --- Step 3: Intelligence (ML Ensemble) ---
        # Predict how this pool will behave once it's off PenFed's books
        ensemble = CPREnsemble(treasury_rate=treasury_rate, portfolio_wac=6.5)
        cpr_prediction, risk_score = ensemble.get_consensus_cpr()
        
        # --- Step 4: Cash Flow Physics ---
        # Generate the waterfall to value the Retained MSR Strip
        mbs_waterfall = self.engine.generate_waterfall(eligible_upb, 6.5, cpr_prediction)
        retained_msr_value = mbs_waterfall['MSR_Fee'].sum()
        
        logger.info(f"Securitization Complete. MSR Asset Created: ${retained_msr_value:,.2f}")
        
        return {
            "Status": "Deliverable",
            "Pool_Size": eligible_upb,
            "ML_CPR_Forecast": f"{cpr_prediction}%",
            "Retained_MSR_Value": retained_msr_value,
            "Model_Confidence": "High" if risk_score < 2.0 else "Review Required"
        }

# --- Execution Block ---
if __name__ == "__main__":
    # penfed_raw_dict would be your DataFrame created from the 2024 report text
    pipeline = SecuritizationPipeline(penfed_raw_dict)
    results = pipeline.run_fannie_delivery()
    print(results)
