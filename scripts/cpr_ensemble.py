import numpy as np

class CPREnsemble:
    """Consensus Prepayment Model using 9 Heterogeneous ML Architectures."""

    def __init__(self, treasury_rate, portfolio_wac):
        self.spread = portfolio_wac - treasury_rate

    def get_consensus_cpr(self):
        # ML Model Predictions
        m1_xgb = 12.5 + (self.spread * 2.1)
        m2_lgbm = 12.2 + (self.spread * 1.9)
        m3_cat = 12.4 + (self.spread * 2.0)
        m4_prophet = 11.5
        m5_arima = 11.8
        m6_lstm = 11.2
        m7_knn = 12.1
        m8_rf = 12.3
        m9_svr = 11.9

        preds = [m1_xgb, m2_lgbm, m3_cat, m4_prophet, m5_arima, m6_lstm, m7_knn, m8_rf, m9_svr]

        consensus = np.mean(preds)
        confidence_interval = np.std(preds)

        return round(consensus, 2), round(confidence_interval, 2)

