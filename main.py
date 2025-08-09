import streamlit as st
import pandas as pd
import os
import time

# ----------------------------------------
# Validation Functions
# ----------------------------------------
def validate_data(df, checks):
    results = {}

    # 1. Banner mismatches (F vs G first 4 chars)
    if checks.get('banner_mismatches', False):
        mismatches = []
        for i, row in df.iterrows():
            f_val, g_val = str(row.get('F', '')).strip(), str(row.get('G', '')).strip()
            if g_val and f_val[:4] != g_val[:4]:
                mismatches.append({'row': i + 2, 'F': f_val, 'G': g_val})  # +2 for Excel row indexing
        results['banner_mismatches'] = mismatches

    # 2. Trade errors (C column)
    if checks.get('trade_errors', False):
        valid_codes = {'05', '03', '07'}
        errors = []
        for i, val in df['C'].items():
            if str(val) not in valid_codes:
                errors.append({'row': i + 2, 'C': val})
        results['trade_errors'] = errors

    # 3. Address mismatches (J vs K first 4 chars)
    if checks.get('address_column_mismatches', False):
        mismatches = []
        for i, row in df.iterrows():
            j_val, k_val = str(row.get('J', '')).strip(), str(row.get('K', '')).strip()
            if k_val and j_val[:4] != k_val[:4]:
                mismatches.append({'row': i + 2, 'J': j_val, 'K': k_val})
        results['address_column_mismatches'] = mismatches

    # 4. Z Code errors (AL column)
    if checks.get('z_code_errors', False):
        valid_z = {'777750Z', '777796Z'}
        errors = []
        for i, val in df['AL'].items():
            if str(val).strip() not in valid_z:
                errors.append({'row': i + 2, 'AL': val})
        results['z_code_errors'] = errors

    # 5. Non-US states (O & P columns)
    if checks.get('non_us_states', False):
        valid_states = {
            'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY',
            'LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND',
            'OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'
        }
        errors = []
        for i, row in df.iterrows():
            o_val, p_val = str(row.get('O', '')).strip(), str(row.get('P', '')).strip()
            bad_cols = {}
            if o_val and o_val not in valid_states:
                bad_cols['O'] = o_val
            if p_val and p_val not in valid_states:
                bad_cols['P'] = p_val
            if bad_cols:
                errors.append({'row': i + 2, **bad_cols})
        results['non_us_states'] = errors

    return results

# ----------------------------------------
# Streamlit UI
# ----------------------------------------
st.set_page_config(page_title="Matching DI Tool", page_icon="🔍", layout="wide")

def main():
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None

    st.header("📁 File Upload")
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            with st.spinner("Loading Excel file..."):
                df = pd.read_excel(uploaded_file)
                st.session_state.uploaded_data = df
            st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
            st.subheader("📊 Data Preview")
            st.dataframe(df.head(10))

            st.header("⚙️ Validation Settings")
            col1, col2 = st.columns(2)
            with col1:
                check_banner = st.checkbox("Check Banner Mismatches (F vs G)", value=True)
                check_trade = st.checkbox("Check Trade Errors (C column)", value=True)
                check_address = st.checkbox("Check Address Mismatches (J vs K)", value=True)
            with col2:
                check_zcode = st.checkbox("Check Z Code Errors (AL column)", value=True)
                check_states = st.checkbox("Check Non-US States (O & P columns)", value=True)

            if st.button("🚀 Run Validation", type="primary"):
                results = validate_data(df, {
                    'banner_mismatches': check_banner,
                    'trade_errors': check_trade,
                    'address_column_mismatches': check_address,
                    'z_code_errors': check_zcode,
                    'non_us_states': check_states
                })
                st.session_state.validation_results = results
                st.success("✅ Validation completed! Results are ready for review.")
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {str(e)}")

    if st.session_state.validation_results is not None:
        display_validation_results(st.session_state.validation_results, st.session_state.uploaded_data)

def display_validation_results(results, df):
    st.header("📋 Validation Results")
    total_issues = sum(len(v) for v in results.values())
    st.metric("Total Issues Found", total_issues)
    for check, issues in results.items():
        if issues:
            with st.expander(f"{check.replace('_', ' ').title()} ({len(issues)} issues)", expanded=False):
                st.dataframe(pd.DataFrame(issues))

if __name__ == "__main__":
    main()
