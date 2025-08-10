def validate_data(df, checks):
    results = {}

    # Prepare US states set for validation
    us_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
        'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
        'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    }

    # Banner mismatches (F vs G columns)
    if checks.get('banner_mismatches', False):
        mismatches = []
        if df.shape[1] > max(6, 39, 40):  # Make sure columns exist (F=5,G=6,AO=39,AP=40)
            for idx, row in df.iterrows():
                f_val = str(row.iloc[5]) if pd.notna(row.iloc[5]) else ''
                g_val = str(row.iloc[6]) if pd.notna(row.iloc[6]) else ''
                ao_val = row.iloc[39] if df.shape[1] > 39 else None
                ap_val = row.iloc[40] if df.shape[1] > 40 else None
                # Skip blank G
                if g_val.strip() == '':
                    continue
                # Case-insensitive left 4 chars compare
                if f_val[:4].lower() != g_val[:4].lower():
                    mismatches.append({
                        'row': idx + 4,
                        'F (Client Banner)': f_val,
                        'G (Matched Banner)': g_val,
                        'AO (Job ID)': ao_val,
                        'AP (Client Store)': ap_val
                    })
        results['banner_mismatches'] = mismatches

    # Trade errors (C column must be 05, 03, or 07)
    if checks.get('trade_errors', False):
        errors = []
        if df.shape[1] > 2:
            for idx, row in df.iterrows():
                c_val = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ''
                ao_val = row.iloc[39] if df.shape[1] > 39 else None
                ap_val = row.iloc[40] if df.shape[1] > 40 else None
                if c_val not in ['05', '03', '07']:
                    errors.append({
                        'row': idx + 4,
                        'C (Trade Code)': c_val,
                        'AO (Job ID)': ao_val,
                        'AP (Client Store)': ap_val
                    })
        results['trade_errors'] = errors

    # Address column mismatches (I vs K columns)
    if checks.get('address_column_mismatches', False):
        mismatches = []
        if df.shape[1] > max(8, 10, 39, 40):  # I=8, K=10
            for idx, row in df.iterrows():
                i_val = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''
                k_val = str(row.iloc[10]) if pd.notna(row.iloc[10]) else ''
                ao_val = row.iloc[39] if df.shape[1] > 39 else None
                ap_val = row.iloc[40] if df.shape[1] > 40 else None
                if k_val.strip() == '':
                    continue
                if i_val[:4].lower() != k_val[:4].lower():
                    mismatches.append({
                        'row': idx + 4,
                        'I (Client Address)': i_val,
                        'K (Matched Address)': k_val,
                        'AO (Job ID)': ao_val,
                        'AP (Client Store)': ap_val
                    })
        results['address_column_mismatches'] = mismatches

    # Z code errors (AL column must be 777750Z or 777796Z)
    if checks.get('z_code_errors', False):
        errors = []
        if df.shape[1] > 37:
            for idx, row in df.iterrows():
                al_val = str(row.iloc[37]) if pd.notna(row.iloc[37]) else ''
                ao_val = row.iloc[39] if df.shape[1] > 39 else None
                ap_val = row.iloc[40] if df.shape[1] > 40 else None
                if al_val.strip() == '':
                    continue
                if al_val not in ['777750Z', '777796Z']:
                    errors.append({
                        'row': idx + 4,
                        'AL (Z Code)': al_val,
                        'AO (Job ID)': ao_val,
                        'AP (Client Store)': ap_val
                    })
        results['z_code_errors'] = errors

    # Non-US states (O & P columns)
    if checks.get('non_us_states', False):
        errors = []
        for col_idx in [14, 15]:  # O=14, P=15
            if df.shape[1] > col_idx:
                for idx, row in df.iterrows():
                    val = str(row.iloc[col_idx]) if pd.notna(row.iloc[col_idx]) else ''
                    ao_val = row.iloc[39] if df.shape[1] > 39 else None
                    ap_val = row.iloc[40] if df.shape[1] > 40 else None
                    if val.strip() != '' and val.upper() not in us_states:
                        errors.append({
                            'row': idx + 4,
                            'Column': df.columns[col_idx],
                            'Value': val,
                            'AO (Job ID)': ao_val,
                            'AP (Client Store)': ap_val
                        })
        results['non_us_states'] = errors

    return results
