import pandas as pd
import numpy as np

class MBSEngine:
    """Core MBS Cash Flow Engine with WAL & Discounted MSR"""

    @staticmethod
    def cpr_to_smm(cpr):
        return 1 - (1 - (cpr / 100))**(1/12)

    @staticmethod
    def _monthly_payment(balance, rate, term):
        return balance * (rate * (1 + rate)**term) / ((1 + rate)**term - 1)

    def generate_cash_flows(self, upb, note_rate, servicing_fee_bps, cpr_scenario, msr_discount=0.08):
        monthly_rate = (note_rate / 100) / 12
        monthly_servicing = (servicing_fee_bps / 10000) / 12
        smm = self.cpr_to_smm(cpr_scenario)

        results = []
        beg_bal = upb
        msr_pv = 0

        for month in range(1, 361):
            if beg_bal <= 0: break
            remaining_term = 361 - month
            total_pmt = self._monthly_payment(beg_bal, monthly_rate, remaining_term)
            interest_pmt = beg_bal * monthly_rate
            sched_prin = total_pmt - interest_pmt
            prepay = (beg_bal - sched_prin) * smm
            servicing_income = beg_bal * monthly_servicing
            total_prin = min(beg_bal, sched_prin + prepay)
            end_bal = beg_bal - total_prin
            msr_pv += servicing_income / ((1 + msr_discount/12)**month)
            results.append([month, beg_bal, sched_prin, prepay, servicing_income, end_bal])
            beg_bal = end_bal

        df = pd.DataFrame(results, columns=['Month','Beg_Bal','Sched_Prin','Prepay','MSR_Fee','End_Bal'])
        total_principal = df['Sched_Prin'] + df['Prepay']
        wal = (df['Month'] * total_principal).sum() / upb / 12

        summary = {
            "WAL_Years": round(wal, 2),
            "Total_Principal": round(total_principal.sum(), 2),
            "Total_Prepay": round(df['Prepay'].sum(), 2),
            "MSR_PV": round(msr_pv, 2),
            "Final_Balance": round(beg_bal, 2)
        }

        return df, summary

    def calculate_green_impact(self, total_upb, kbtu_factor):
        return (total_upb / 1_000_000) * kbtu_factor
