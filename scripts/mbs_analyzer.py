import pandas as pd

def calculate_impact(upb, kbtu):
    """Calculates Energy Savings Efficiency per $1M UPB."""
    return kbtu / (upb / 1_000_000)

# Market Benchmarks from Fannie Mae 2024 Disclosures
benchmarks = {
    'low_income_share': 0.268,
    'first_time_homebuyer': 0.195,
    'minority_tract': 0.127
}

print("MBS Impact Engine: Benchmarks Loaded.")
