from pipeline_securitization import SecuritizationPipeline
import json

def run_demo():
    # Load the "Audit Reality" from our data samples
    with open('data_samples/penfed_2024_snapshot.json') as f:
        data = json.load(f)

    print("🚀 INITIALIZING PENFED AUDIT TERMINAL...")
    
    # Run the Securitization Pipeline
    pipeline = SecuritizationPipeline(data)
    results = pipeline.run_fannie_delivery()

    print(f"\n--- 2024 FANNIE MAE DELIVERY SUMMARY ---")
    print(f"Eligible Pool UPB:  ${results['Pool_Size']:,.2f}")
    print(f"ML Prepay Forecast: {results['ML_CPR_Forecast']}")
    print(f"Retained MSR Value: ${results['Retained_MSR_Value']:,.2f}")
    print(f"Compliance Status:  {results['Status']}")
    print(f"Confidence Level:   {results['Model_Confidence']}")

if __name__ == "__main__":
    run_demo()
