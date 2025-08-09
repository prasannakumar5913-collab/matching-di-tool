class DataValidator:
    def validate_data(self, df, column_mapping, checks):
        results = {}

        # 1. Banner mismatches (F vs G columns, first 4 letters must match, skip blank G)
        if checks.get('banner_mismatches', False):
            mismatches = []
            if 'F' in df.columns and 'G' in df.columns:
                for idx, (f_val, g_val) in enumerate(zip(df['F'], df['G'])):
                    if pd.notna(g_val) and str(f_val)[:4] != str(g_val)[:4]:
                        mismatches.append({'row': idx + 2, 'F': f_val, 'G': g_val})  # +2 for Excel row
            results['banner_mismatches'] = mismatches

        # 2. Trade errors (C column must be 05, 03, or 07)
        if checks.get('trade_errors', False):
            errors = []
            if 'C' in df.columns:
                for idx, val in enumerate(df['C']):
                    if str(val) not in ['05', '03', '07']:
                        errors.append({'row': idx + 2, 'C': val})
            results['trade_errors'] = errors

        # 3. Address column mismatches (J vs K columns, first 4 letters must match, skip blank K)
        if checks.get('address_column_mismatches', False):
            mismatches = []
            if 'J' in df.columns and 'K' in df.columns:
                for idx, (j_val, k_val) in enumerate(zip(df['J'], df['K'])):
                    if pd.notna(k_val) and str(j_val)[:4] != str(k_val)[:4]:
                        mismatches.append({'row': idx + 2, 'J': j_val, 'K': k_val})
            results['address_column_mismatches'] = mismatches

        # 4. Z code errors (AL column must be 777750Z or 777796Z)
        if checks.get('z_code_errors', False):
            errors = []
            if 'AL' in df.columns:
                for idx, val in enumerate(df['AL']):
                    if str(val) not in ['777750Z', '777796Z']:
                        errors.append({'row': idx + 2, 'AL': val})
            results['z_code_errors'] = errors

        # 5. Non-US states (O & P columns, must be 2-letter US state codes)
        if checks.get('non_us_states', False):
            us_states = {
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
                'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
                'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
            }
            errors = []
            for col in ['O', 'P']:
                if col in df.columns:
                    for idx, val in enumerate(df[col]):
                        if pd.notna(val) and str(val).upper() not in us_states:
                            errors.append({'row': idx + 2, 'column': col, 'value': val})
            results['non_us_states'] = errors

        return results
