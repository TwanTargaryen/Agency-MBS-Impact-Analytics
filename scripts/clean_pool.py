class CleanPoolBuilder:
    """
    Extracts and sanitizes securitization-eligible pool
    from 2024 Financial Condition snapshot.
    """

    def __init__(self, snapshot_json):
        self.data = snapshot_json

    def build_pool(self):
        assets = self.data["assets"]
        acl = self.data["allowance_for_credit_losses"]

        real_estate = assets["real_estate_current"] * 1000
        delinquent = assets["delinquent_total"] * 1000
        taxi = assets["taxi_medallions"] * 1000
        real_estate_acl = acl["real_estate"] * 1000

        clean_pool = real_estate - delinquent - taxi

        result = {
            "Real_Estate_UPB": real_estate,
            "Delinquencies_Removed": delinquent,
            "Taxi_Removed": taxi,
            "Clean_Pool_UPB": clean_pool,
            "Credit_Enhancement_ACL": real_estate_acl
        }

        return result
