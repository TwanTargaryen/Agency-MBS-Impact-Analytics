# PenFed 2024 Strategic Securitization & Audit Framework

This repository provides an automated pipeline for auditing and securitizing mortgage assets, specifically calibrated to the **Pentagon Federal Credit Union 2024 Annual Report**.

## 🏗️ Architecture
* **`engine.py`**: Deterministic cash-flow engine (Amortization, SMM, and MSR fee stripping).
* **`cpr_ensemble.py`**: A 9-model ML ensemble for prepayment (CPR) forecasting.
* **`pipeline_securitization.py`**: Business logic for Fannie Mae delivery, including "Eligibility Guardrails" (Note 3 & 5 compliance).
* **`stress_test.py`**: Scenario analysis for Interest Rate (IR) shocks and Credit Stress.

## 🚀 Quick Start
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Run the Dashboard**: `python scripts/main_dashboard.py`
3. **Run Validation Tests**: `pytest tests/`

## 🛡️ Audit Governance Features
* **Auto-Purge**: Automatically identifies and removes ineligible assets (e.g., Taxi Medallions) from securitization pools.
* **Credit Enhancement Validation**: Verifies that the Allowance for Credit Losses (ACL) meets secondary market thresholds.
* **MSR Mark-to-Market**: Validates the reported $8.5M in Mortgage Banking Activities against ML-projected cash flows.

---
*Developed for Strategic Audit Analysis - 2026*
