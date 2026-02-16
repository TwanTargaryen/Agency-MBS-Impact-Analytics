import pandas as pd
import numpy as np

class MBSEngine:
    """Core Mathematical Engine for MBS Cash Flow Projections."""
    
    @staticmethod
    def calculate_pass_through(gross_rate, servicing_bps=25, g_fee_bps=15):
        return gross_rate - ((servicing_bps + g_fee_bps) / 100)

    def generate_waterfall(self, upb, note_rate, cpr, months=360):
        monthly_rate = (note_rate / 100) / 12
        smm = 1 - (1 - (cpr / 100))**(1/12)
        
        results = []
        balance = upb
        
        for m in range(1, months + 1):
            interest = balance * monthly_rate
            # Standard Amortization Formula
            pmt = upb * (monthly_rate * (1+monthly_rate)**months) / ((1+monthly_rate)**months - 1)
            sched_prin = pmt - interest
            prepay = (balance - sched_prin) * smm
            
            total_prin = min(balance, sched_prin + prepay)
            msr_fee = balance * (0.0025 / 12) # The 25bps servicing strip
            
            balance -= total_prin
            results.append([m, total_prin, interest, msr_fee, balance])
            if balance <= 0: break
            
        return pd.DataFrame(results, columns=['Month', 'Prin', 'Int', 'MSR_Fee', 'Balance'])
