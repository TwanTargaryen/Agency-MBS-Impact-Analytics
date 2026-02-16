from mbs_engine import MBSEngine
import pandas as pd

def run_interview_demo():
    engine = MBSEngine()
    
    # Using your Fannie Mae Data Point: MB0291
    upb = 106496121 
    note_rate = 6.5
    
    print("--- 2024 Agency MBS Sensitivity Analysis ---")
    
    # Run three scenarios to show 'Symmetry'
    scenarios = {"Slow (6% CPR)": 6, "Base (12% CPR)": 12, "Fast (25% CPR)": 25}
    
    for name, cpr in scenarios.items():
        df = engine.generate_cash_flows(upb, note_rate, 25, cpr)
        total_msr = df['MSR_Fee'].sum()
        print(f"{name}: Lifetime MSR Fee Value = ${total_msr:,.2f}")

if __name__ == "__main__":
    run_interview_demo()
