import logging
import pandas as pd
from clean_pool import CleanPoolBuilder
from cpr_ensemble import CPREnsemble
from mbs_engine import MBSEngine
from portfolio_strategy import PortfolioStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SecuritizationPipeline")

class SecuritizationPipeline:
    def __init__(self, raw_data, snapshot_json=None):
        self.portfolio_data = pd.DataFrame(raw_data) if isinstance(raw_data, pd.DataFrame) else pd.DataFrame(raw_data)
        self.strategy = PortfolioStrategy(raw_data)
        self.engine = MBSEngine()
        self.snapshot_json = snapshot_json

    def build_clean_pool(self):
        if self.snapshot_json is None:
            raise ValueError("Snapshot JSON required for clean pool")
        builder = CleanPoolBuilder(self.snapshot_json)
        return builder.build_pool()

    def run_fannie_delivery(self, treasury_rate=4.25):
        clean_pool = self.build_clean_pool()
        eligible_upb = clean_pool["Clean_Pool_UPB"]
        real_estate_acl = clean_pool["Credit_Enhancement_ACL"]
        allowance_ratio = real_estate_acl / eligible_upb
        credit_ok = allowance_ratio >= 0.0040

        ensemble = CPREnsemble(treasury_rate=treasury_rate, portfolio_wac=6.5)
        cpr_prediction, risk_score = ensemble.get_consensus_cpr()

        df, summary = self.engine.generate_cash_flows(eligible_upb, note_rate=6.5, servicing_fee_bps=25, cpr_scenario=cpr_prediction)

        wal = summary["WAL_Years"]
        msr_value = summary["MSR_PV"]

        deliverable = (
            wal > 4 and wal < 12 and
            5 <= cpr_prediction <= 25 and
            credit_ok
        )
        status = "Deliverable" if deliverable else "Review Required"

        # Confidence band
        if risk_score < 1.0:
            confidence_band = "Stable"
        elif risk_score < 2.0:
            confidence_band = "Moderate"
        else:
            confidence_band = "Elevated"

        return {
            "Status": status,
            "Pool_Size": eligible_upb,
            "ML_CPR_Forecast": cpr_prediction,
            "Model_Risk_Score": risk_score,
            "Model_Confidence": confidence_band,
            "WAL_Years": wal,
            "Retained_MSR_Value": msr_value,
            "Allowance_Ratio": round(allowance_ratio, 4)
        }
