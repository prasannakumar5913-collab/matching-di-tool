class DataValidator:
    def validate_data(self, df, column_mapping, checks):
        # Dummy implementation: returns empty results for each check
        return {k: [] for k, v in checks.items() if v}
