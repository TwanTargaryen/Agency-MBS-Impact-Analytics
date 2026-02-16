import pandas as pd
import numpy as np

class MBSEngine:
    """
    Core engine for calculating Agency MBS Cash Flows and ESG Impact.
    Used for Guidehouse-style Quantitative Analysis.
    """
    
    @staticmethod
    def cpr_to_smm(cpr):
        """Converts Annual Prepayment Rate (CPR) to Monthly Mortality (SMM)."""
        return 1 - (1 - (cpr / 100))**(1/12)

    def generate_cash_flows(self, upb, note_rate, servicing_fee_bps, cpr_scenario):
        """
        Generates a 360-month waterfall.
        Includes Principal, Interest, Prepayments, and MSR Fees.
        """
        monthly_rate = (note_rate / 100) / 12
        monthly_servicing = (servicing_fee_bps / 10000) / 12
        
        results = []
        beg_bal = upb
        
        for month in range(1, 361):
            smm = self.cpr_to_smm(cpr_scenario)
            
            # Standard Amortization Math
            interest_pmt = beg_bal * monthly_rate
            # Standard Mortgage Payment Formula
            total_pmt = beg_bal * (monthly_rate * (1 + monthly_rate)**360) / ((1 + monthly_rate)**360 - 1)
            sched_prin = total_pmt - interest_pmt
            
            # Prepayment & Servicing Logic
            prepay = (beg_bal - sched_prin) * smm
            servicing_income = beg_bal * monthly_servicing
            
            total_prin = sched_prin + prepay
            end_bal = max(0, beg_bal - total_prin)
            
            results.append([month, beg_bal, sched_prin, prepay, servicing_income, end_bal])
            
            beg_bal = end_bal
            if beg_bal <= 0: break
            
        return pd.DataFrame(results, columns=['Month', 'Beg_Bal', 'Prin', 'Prepay', 'MSR_Fee', 'End_Bal'])

    def calculate_green_impact(self, total_upb, kbtu_factor):
        """Maps UPB to Fannie Mae Green Disclosure metrics (kBTU Savings)."""
        return (total_upb / 1_000_000) * kbtu_factor
