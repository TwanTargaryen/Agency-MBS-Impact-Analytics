# Agency MBS Impact Analytics
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![ESG](https://img.shields.io/badge/ESG-Metrics-green)

Quantitative engine for benchmarking Agency MBS portfolios against Fannie Mae ESG (Green/Social) metrics and modeling cash flow sensitivity.

## 🚀 The Mission
To reconcile internal portfolio performance against GSE (Fannie Mae) benchmarks for Social and Green impact, while quantifying the economic value of MSR (Mortgage Servicing Rights) under varying prepayment speeds.

## 📊 Core Functionality
* **Cash Flow Waterfall:** 360-month projection of Principal, Interest, and Prepayments using CPR/SMM models.
* **Prepayment Modeling:** Implements the PSA Standard Prepayment Model to account for seasoning ramps.
* **Green Bond Attribution:** Maps CUSIPs to Energy Savings (kBTU) and Emissions (MTCO2e) based on 2024 Fannie Mae disclosures.
* **Sensitivity Analysis:** Stress tests MSR value against interest rate shocks (Contraction vs. Extension Risk).

## 📂 Project Structure
* `scripts/mbs_engine.py`: The core mathematical class for cash flow generation.
* `scripts/stress_test.py`: Scenario runner for interest rate and prepayment sensitivity.
* `data_samples/`: Synthetic portfolio data (based on CUSIP MB0291) to demonstrate model logic.
* `visuals/`: Output directory for CPR curves and MSR valuation charts.

## 🛠️ Tech Stack
* **Python:** Pandas, NumPy (Vectorized cash flow math)
* **Visuals:** Matplotlib (Prepayment S-curves)
