import pandas as pd
import numpy as np

def generate_mbs_cashflow(upb, note_rate, servicing_fee_bps, cpr_assumed):
    """
    Generates a 360-month cash flow for an MBS Bond.
    """
    monthly_rate = note_rate / 12 / 100
    monthly_servicing = servicing_fee_bps / 12 / 10000
    smm = 1 - (1 - cpr_assumed/100)**(1/12) # Convert Annual CPR to Monthly SMM
    
    data = []
    beg_balance = upb
    
    for month in range(1, 361):
        # 1. Calculate Scheduled Interest & Principal
        interest_pmt = beg_balance * monthly_rate
        total_pmt = beg_balance * (monthly_rate * (1 + monthly_rate)**360) / ((1 + monthly_rate)**360 - 1)
        sched_principal = total_pmt - interest_pmt
        
        # 2. Calculate Prepayment (SMM)
        prepayment = (beg_balance - sched_principal) * smm
        
        # 3. Servicing Fee Income (What Guidehouse cares about)
        servicing_income = beg_balance * monthly_servicing
        
        total_principal = sched_principal + prepayment
        end_balance = beg_balance - total_principal
        
        data.append([month, beg_balance, sched_principal, prepayment, interest_pmt, servicing_income])
        
        beg_balance = end_balance
        if beg_balance <= 0: break

    return pd.DataFrame(data, columns=['Month', 'Beg_Balance', 'Principal', 'Prepay', 'Interest', 'Servicing_Fee'])

# Example Run for the Interview
df = generate_mbs_cashflow(upb=1000000, note_rate=6.5, servicing_fee_bps=25, cpr_assumed=10)
print(df.head())
