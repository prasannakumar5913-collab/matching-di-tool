import pandas as pd
import re
import numpy as np
from typing import Dict, List, Any, Optional

class DataValidator:
    """Data validation class for Excel file inspection"""
    
    def __init__(self):
        # Define banned address patterns (common examples)
        self.banned_address_patterns = [
            r'(?i)\b(p\.?o\.?\s*box|post\s*office\s*box)\b',  # PO Box variations
            r'(?i)\b(general\s*delivery)\b',
            r'(?i)\b(mail\s*drop)\b',
            r'(?i)\b(private\s*mail\s*box|pmb)\b',
            r'(?i)\b(do\s*not\s*mail|dnm)\b',
            r'(?i)\b(deceased|vacant|abandoned)\b',
            r'(?i)\b(return\s*to\s*sender|rts)\b'
        ]
        
        # US states and territories
        self.us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
            'DC', 'AS', 'GU', 'MP', 'PR', 'VI'  # Territories
        }
        
        # Full state names to abbreviations mapping
        self.state_name_to_abbr = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC'
        }
    
    def validate_data(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                     validation_options: Dict[str, bool]) -> Dict[str, List]:
        """Main validation method that runs all selected checks"""
        
        results = {}
        
        # Banner validation using F and G columns
        if validation_options.get('banner_mismatches', False):
            results['banner_mismatches'] = self.check_banner_mismatches(df)
        
        # Trade validation using C column
        if validation_options.get('trade_errors', False):
            results['trade_errors'] = self.check_trade_errors(df)
        
        # Address validation using J and K columns
        if validation_options.get('address_column_mismatches', False):
            results['address_column_mismatches'] = self.check_address_column_mismatches(df)
        
        # Z Code validation using AL column
        if validation_options.get('z_code_errors', False):
            results['z_code_errors'] = self.check_z_code_errors(df)
        
        if validation_options.get('banned_addresses', False) and column_mapping.get('address'):
            results['banned_addresses'] = self.check_banned_addresses(df, column_mapping['address'])
        
        if validation_options.get('address_mismatches', False):
            results['address_mismatches'] = self.check_address_mismatches(df, column_mapping)
        
        # Check states in O and P columns for non-US states
        if validation_options.get('non_us_states', False):
            results['non_us_states'] = self.check_non_us_states_op_columns(df)
        
        if validation_options.get('duplicate_addresses', False) and column_mapping.get('address'):
            results['duplicate_addresses'] = self.check_duplicate_addresses(df, column_mapping['address'])
        
        if validation_options.get('incomplete_addresses', False):
            results['incomplete_addresses'] = self.check_incomplete_addresses(df, column_mapping)
        
        if validation_options.get('invalid_zip_codes', False) and column_mapping.get('zip'):
            results['invalid_zip_codes'] = self.check_invalid_zip_codes(df, column_mapping['zip'])
        
        return results
    
    def check_banned_addresses(self, df: pd.DataFrame, address_column: str) -> List[Dict[str, Any]]:
        """Check for banned address patterns"""
        banned_addresses = []
        
        if address_column not in df.columns:
            return banned_addresses
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        for idx, address in df[address_column].fillna('').items():
            idx = int(idx)  # Ensure idx is int
            address_str = str(address)
            for pattern in self.banned_address_patterns:
                if re.search(pattern, address_str):
                    banned_record = {
                        'row': idx + 1,
                        'address': address_str,
                        'reason': 'Contains banned pattern',
                        'pattern_matched': pattern
                    }
                    
                    # Add Job ID and Client Store ID if available
                    if ao_column is not None:
                        job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                        banned_record['job_id'] = job_id
                    
                    if ap_column is not None:
                        client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                        banned_record['client_store_id'] = client_store_id
                    
                    banned_addresses.append(banned_record)
                    break
        
        return banned_addresses
    
    def check_address_mismatches(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check for potential address component mismatches"""
        mismatches = []
        
        address_col = column_mapping.get('address')
        city_col = column_mapping.get('city')
        state_col = column_mapping.get('state')
        zip_col = column_mapping.get('zip')
        
        if not any([address_col, city_col, state_col, zip_col]):
            return mismatches
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        for idx, row in df.iterrows():
            idx = int(idx)  # Ensure idx is int
            issues = []
            
            # Check if city appears in address but differs from city column
            if address_col and city_col and address_col in df.columns and city_col in df.columns:
                address = str(row.get(address_col, '')).lower()
                city = str(row.get(city_col, '')).lower()
                
                if city and len(city) > 2 and city in address:
                    # City found in address, this is generally good
                    pass
                elif city and len(city) > 2 and city not in address:
                    issues.append(f"City '{city}' not found in address")
            
            # Check state consistency
            if address_col and state_col and address_col in df.columns and state_col in df.columns:
                address = str(row.get(address_col, '')).lower()
                state = str(row.get(state_col, '')).upper()
                
                if state and len(state) >= 2:
                    state_abbr = state[:2] if len(state) > 2 else state
                    if state_abbr not in address.upper() and state.lower() not in address:
                        issues.append(f"State '{state}' not found in address")
            
            if issues:
                mismatch_record = {
                    'row': idx + 1,
                    'issues': issues,
                    'address': str(row.get(address_col, '')) if address_col else '',
                    'city': str(row.get(city_col, '')) if city_col else '',
                    'state': str(row.get(state_col, '')) if state_col else ''
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    mismatch_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    mismatch_record['client_store_id'] = client_store_id
                
                mismatches.append(mismatch_record)
        
        return mismatches
    
    def check_non_us_states(self, df: pd.DataFrame, state_column: str) -> List[Dict[str, Any]]:
        """Check for non-US states"""
        non_us_states = []
        
        if state_column not in df.columns:
            return non_us_states
        
        for idx, state in df[state_column].fillna('').items():
            state_str = str(state).strip().upper()
            
            if not state_str:
                continue
            
            # Check if it's a valid US state abbreviation
            if len(state_str) == 2 and state_str in self.us_states:
                continue
            
            # Check if it's a full state name
            state_lower = state_str.lower()
            if state_lower in self.state_name_to_abbr:
                continue
            
            # Check if it might be a typo of a US state
            is_likely_us_state = False
            for us_state in list(self.us_states) + list(self.state_name_to_abbr.keys()):
                if abs(len(state_str) - len(us_state)) <= 2:  # Similar length
                    # Simple similarity check
                    matches = sum(1 for a, b in zip(state_str.lower(), us_state.lower()) if a == b)
                    if matches / max(len(state_str), len(us_state)) > 0.7:
                        is_likely_us_state = True
                        break
            
            if not is_likely_us_state:
                non_us_states.append({
                    'row': idx + 1,
                    'state': state_str,
                    'reason': 'Not a recognized US state or territory'
                })
        
        return non_us_states
    
    def check_duplicate_addresses(self, df: pd.DataFrame, address_column: str) -> List[Dict[str, Any]]:
        """Check for duplicate addresses"""
        duplicates = []
        
        if address_column not in df.columns:
            return duplicates
        
        # Normalize addresses for comparison
        df_copy = df.copy()
        df_copy['normalized_address'] = df_copy[address_column].fillna('').astype(str).str.lower().str.strip()
        
        # Find duplicates
        duplicate_groups = df_copy.groupby('normalized_address').size()
        duplicate_addresses = duplicate_groups[duplicate_groups > 1].index
        
        for addr in duplicate_addresses:
            if addr:  # Skip empty addresses
                duplicate_rows = df_copy[df_copy['normalized_address'] == addr].index.tolist()
                duplicates.append({
                    'address': addr,
                    'rows': [row + 1 for row in duplicate_rows],
                    'count': len(duplicate_rows)
                })
        
        return duplicates
    
    def check_incomplete_addresses(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check for incomplete or missing address components"""
        incomplete = []
        
        address_col = column_mapping.get('address')
        city_col = column_mapping.get('city')
        state_col = column_mapping.get('state')
        zip_col = column_mapping.get('zip')
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        for idx, row in df.iterrows():
            idx = int(idx)  # Ensure idx is int
            missing_components = []
            
            if address_col and address_col in df.columns:
                if pd.isna(row.get(address_col)) or not str(row.get(address_col, '')).strip():
                    missing_components.append('address')
            
            if city_col and city_col in df.columns:
                if pd.isna(row.get(city_col)) or not str(row.get(city_col, '')).strip():
                    missing_components.append('city')
            
            if state_col and state_col in df.columns:
                if pd.isna(row.get(state_col)) or not str(row.get(state_col, '')).strip():
                    missing_components.append('state')
            
            if zip_col and zip_col in df.columns:
                if pd.isna(row.get(zip_col)) or not str(row.get(zip_col, '')).strip():
                    missing_components.append('zip')
            
            if missing_components:
                incomplete_record = {
                    'row': idx + 1,
                    'missing_components': missing_components,
                    'address': str(row.get(address_col, '')) if address_col else '',
                    'city': str(row.get(city_col, '')) if city_col else '',
                    'state': str(row.get(state_col, '')) if state_col else '',
                    'zip': str(row.get(zip_col, '')) if zip_col else ''
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    incomplete_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    incomplete_record['client_store_id'] = client_store_id
                
                incomplete.append(incomplete_record)
        
        return incomplete
    
    def check_invalid_zip_codes(self, df: pd.DataFrame, zip_column: str) -> List[Dict[str, Any]]:
        """Check for invalid ZIP codes"""
        invalid_zips = []
        
        if zip_column not in df.columns:
            return invalid_zips
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        # ZIP code patterns (5 digits or 5+4 format)
        zip_pattern = re.compile(r'^\d{5}(-\d{4})?$')
        
        for idx, zip_code in df[zip_column].fillna('').items():
            idx = int(idx)  # Ensure idx is int
            zip_str = str(zip_code).strip()
            
            if not zip_str:
                continue
            
            # Remove any non-digit characters except hyphens
            cleaned_zip = re.sub(r'[^\d-]', '', zip_str)
            
            if not zip_pattern.match(cleaned_zip):
                invalid_record = {
                    'row': idx + 1,
                    'zip_code': zip_str,
                    'reason': 'Invalid ZIP code format (expected 5 digits or 5+4 format)'
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    invalid_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    invalid_record['client_store_id'] = client_store_id
                
                invalid_zips.append(invalid_record)
        
        return invalid_zips
    
    def check_banner_mismatches(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check banner mismatches using F and G columns with LEFT(F,4)=LEFT(G,4) logic"""
        banner_mismatches = []
        
        # Check if F and G columns exist (0-based indexing: F=5, G=6)
        if len(df.columns) < 7:
            return banner_mismatches
        
        f_column = df.iloc[:, 5]  # F column (6th column, 0-based index 5)
        g_column = df.iloc[:, 6]  # G column (7th column, 0-based index 6)
        
        # Get AO and AP columns if they exist (AO=40, AP=41 in 0-based indexing)
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        for idx in range(3, len(df)):  # Start validation from 4th row (index 3)
            f_value = str(f_column.iloc[idx]) if pd.notna(f_column.iloc[idx]) else ""
            g_value = str(g_column.iloc[idx]) if pd.notna(g_column.iloc[idx]) else ""
            
            # Skip if G column is blank (don't treat as mismatch)
            if not g_value.strip():
                continue
            
            # Apply LEFT(F,4)=LEFT(G,4) logic (case-insensitive)
            f_left4 = f_value[:4].upper() if len(f_value) >= 4 else f_value.upper()
            g_left4 = g_value[:4].upper() if len(g_value) >= 4 else g_value.upper()
            
            if f_left4 != g_left4:
                mismatch_record = {
                    'row': idx + 1,
                    'client_banner': f_value,
                    'matched_info': g_value,
                    'f_left4': f_left4,
                    'g_left4': g_left4,
                    'reason': f'Banner mismatch: "{f_left4}" ≠ "{g_left4}"'
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    mismatch_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    mismatch_record['client_store_id'] = client_store_id
                
                banner_mismatches.append(mismatch_record)
        
        return banner_mismatches
    
    def check_non_us_states_op_columns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for non-US states in O and P columns"""
        non_us_states = []
        
        # Check if O and P columns exist (0-based indexing: O=14, P=15)
        if len(df.columns) < 16:
            return non_us_states
        
        o_column = df.iloc[:, 14]  # O column (15th column, 0-based index 14)
        p_column = df.iloc[:, 15]  # P column (16th column, 0-based index 15)
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        for idx in range(3, len(df)):  # Start validation from 4th row (index 3)
            # Check O column
            o_value = str(o_column.iloc[idx]) if pd.notna(o_column.iloc[idx]) else ""
            if o_value.strip() and not self._is_us_state(o_value.strip()):
                state_record = {
                    'row': idx + 1,
                    'column': 'O',
                    'state': o_value.strip(),
                    'reason': 'Not a recognized US state or territory'
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    state_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    state_record['client_store_id'] = client_store_id
                
                non_us_states.append(state_record)
            
            # Check P column
            p_value = str(p_column.iloc[idx]) if pd.notna(p_column.iloc[idx]) else ""
            if p_value.strip() and not self._is_us_state(p_value.strip()):
                state_record = {
                    'row': idx + 1,
                    'column': 'P',
                    'state': p_value.strip(),
                    'reason': 'Not a recognized US state or territory'
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    state_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    state_record['client_store_id'] = client_store_id
                
                non_us_states.append(state_record)
        
        return non_us_states
    
    def _is_us_state(self, state_value: str) -> bool:
        """Helper method to check if a state value is a valid US state"""
        state_str = state_value.upper().strip()
        
        # Skip header-like text (Column D header text)
        header_texts = ['CLIENT STATE', 'CLIENTSTATE', 'STATE', 'CLIENT', 'STATES', 
                       'CLIENT BANNED', 'CLIENTBANNED', 'BANNED', 'CLIENT ADDRESS', 
                       'CLIENTADDRESS', 'ADDRESS', 'Z CODE', 'ZCODE']
        if state_str in header_texts:
            return True  # Treat header text as valid to skip validation
        
        # Check if it's a valid US state abbreviation
        if len(state_str) == 2 and state_str in self.us_states:
            return True
        
        # Check if it's a full state name
        state_lower = state_str.lower()
        if state_lower in self.state_name_to_abbr:
            return True
        
        # Check if it might be a typo of a US state (similarity check)
        for us_state in list(self.us_states) + list(self.state_name_to_abbr.keys()):
            if abs(len(state_str) - len(us_state)) <= 2:  # Similar length
                # Simple similarity check
                matches = sum(1 for a, b in zip(state_str.lower(), us_state.lower()) if a == b)
                if matches / max(len(state_str), len(us_state)) > 0.7:
                    return True
        
        return False
    
    def check_trade_errors(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check C column for valid trade codes (05, 03, 07)"""
        trade_errors = []
        
        # Check if C column exists (0-based indexing: C=2)
        if len(df.columns) < 3:
            return trade_errors
        
        c_column = df.iloc[:, 2]  # C column (3rd column, 0-based index 2)
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        # Valid trade codes
        valid_trade_codes = ['05', '03', '07']
        
        # Header text to exclude (Column D and other header text)
        header_texts = ['trade class', 'tradeclass', 'trade', 'class', 'client banned', 
                       'clientbanned', 'banned', 'client address', 'clientaddress', 
                       'address', 'z code', 'zcode']
        
        for idx in range(3, len(df)):  # Start validation from 4th row (index 3)
            c_value = str(c_column.iloc[idx]).strip() if pd.notna(c_column.iloc[idx]) else ""
            
            # Skip empty values and header-like text
            if not c_value or c_value.lower() in header_texts:
                continue
            
            if c_value not in valid_trade_codes:
                trade_record = {
                    'row': idx + 1,
                    'trade_code': c_value,
                    'reason': f'Invalid trade code "{c_value}" (valid codes: 05, 03, 07)'
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    trade_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    trade_record['client_store_id'] = client_store_id
                
                trade_errors.append(trade_record)
        
        return trade_errors
    
    def check_address_column_mismatches(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check address mismatches using J and K columns with LEFT formula logic"""
        address_mismatches = []
        
        # Check if J and K columns exist (0-based indexing: J=9, K=10)
        if len(df.columns) < 11:
            return address_mismatches
        
        j_column = df.iloc[:, 9]   # J column (10th column, 0-based index 9)
        k_column = df.iloc[:, 10]  # K column (11th column, 0-based index 10)
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        # Header text to exclude
        header_texts = ['client address', 'clientaddress', 'address', 'client banned', 
                       'clientbanned', 'banned']
        
        for idx in range(3, len(df)):  # Start validation from 4th row (index 3)
            j_value = str(j_column.iloc[idx]) if pd.notna(j_column.iloc[idx]) else ""
            k_value = str(k_column.iloc[idx]) if pd.notna(k_column.iloc[idx]) else ""
            
            # Skip if K column is blank or contains header text (don't treat as mismatch)
            if not k_value.strip() or j_value.lower().strip() in header_texts or k_value.lower().strip() in header_texts:
                continue
            
            # Apply LEFT formula logic (case-insensitive)
            # Use first 4 characters for comparison, similar to banner validation
            j_left4 = j_value[:4].upper() if len(j_value) >= 4 else j_value.upper()
            k_left4 = k_value[:4].upper() if len(k_value) >= 4 else k_value.upper()
            
            if j_left4 != k_left4:
                mismatch_record = {
                    'row': idx + 1,
                    'client_address': j_value,
                    'reference_info': k_value,
                    'j_left4': j_left4,
                    'k_left4': k_left4,
                    'reason': f'Address mismatch: "{j_left4}" ≠ "{k_left4}"'
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    mismatch_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    mismatch_record['client_store_id'] = client_store_id
                
                address_mismatches.append(mismatch_record)
        
        return address_mismatches
    
    def check_z_code_errors(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check AL column for valid Z codes (777750Z and 777796Z)"""
        z_code_errors = []
        
        # Check if AL column exists (0-based indexing: AL=37)
        if len(df.columns) < 38:
            return z_code_errors
        
        al_column = df.iloc[:, 37]  # AL column (38th column, 0-based index 37)
        
        # Get AO and AP columns if they exist
        ao_column = df.iloc[:, 40] if len(df.columns) > 40 else None  # AO column (Job ID)
        ap_column = df.iloc[:, 41] if len(df.columns) > 41 else None  # AP column (Client Store ID)
        
        # Valid Z codes
        valid_z_codes = ['777750Z', '777796Z']
        
        # Header text to exclude
        header_texts = ['z code', 'zcode', 'z-code', 'code']
        
        for idx in range(3, len(df)):  # Start validation from 4th row (index 3)
            z_value = str(al_column.iloc[idx]).strip() if pd.notna(al_column.iloc[idx]) else ""
            
            # Skip empty/blank values and header-like text
            if not z_value or z_value.lower() in header_texts:
                continue
            
            if z_value not in valid_z_codes:
                z_code_record = {
                    'row': idx + 1,
                    'z_code': z_value,
                    'reason': f'Invalid Z code "{z_value}" (valid codes: 777750Z, 777796Z)'
                }
                
                # Add Job ID and Client Store ID if available
                if ao_column is not None:
                    job_id = str(ao_column.iloc[idx]) if pd.notna(ao_column.iloc[idx]) else ""
                    z_code_record['job_id'] = job_id
                
                if ap_column is not None:
                    client_store_id = str(ap_column.iloc[idx]) if pd.notna(ap_column.iloc[idx]) else ""
                    z_code_record['client_store_id'] = client_store_id
                
                z_code_errors.append(z_code_record)
        
        return z_code_errors
