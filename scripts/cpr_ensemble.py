import numpy as np

class CPREnsemble:
    """Consensus Prepayment Model using an Ensemble of 9 Sub-models."""
    
    def __init__(self, treasury_rate, portfolio_wac):
        self.rate_spread = portfolio_wac - treasury_rate
        
    def get_consensus_cpr(self):
        # We simulate 9 models with slightly different weights/biases
        # In a production environment, these would be XGBoost or Regression models
        models = [
            self._macro_model_1(), self._macro_model_2(), self._macro_model_3(),
            self._credit_model_1(), self._credit_model_2(), self._credit_model_3(),
            self._behavioral_model_1(), self._behavioral_model_2(), self._behavioral_model_3()
        ]
        
        # Calculate Weighted Consensus
        consensus_cpr = np.mean(models)
        variance = np.var(models)
        
        return consensus_cpr, variance

    # --- Representative Logic for the 9 Models ---
    def _macro_model_1(self): return 10 + (self.rate_spread * 2.5) # High sensitivity
    def _macro_model_2(self): return 12 + (self.rate_spread * 1.5) # Moderate sensitivity
    def _macro_model_3(self): return 11 + (self.rate_spread * 1.0) # Conservative
    
    # ... Other 6 models would follow with variations on Loan Age, Seasonality, etc.
    def _credit_model_1(self): return 8.5
    def _credit_model_2(self): return 9.0
    def _credit_model_3(self): return 8.7
    
    def _behavioral_model_1(self): return 12.0 # Spring Seasonality
    def _behavioral_model_2(self): return 10.5 # Winter Seasonality
    def _behavioral_model_3(self): return 11.2 # Standard Turnover
