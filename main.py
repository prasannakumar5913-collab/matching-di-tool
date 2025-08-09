import streamlit as st
import pandas as pd
import os
import time

# ========== RULE IMPLEMENTATIONS ==========
def check_banner_mismatches(df):
    issues = []
    if 'F' in df.columns and 'G' in df.columns:
        for i, row in df.iterrows():
            f_val = str(row['F']) if pd.notna(row['F']) else ''
            g_val = str(row['G']) if pd.notna(row['G']) else ''
            if g_val.strip() != '':  # skip blank G
                if f_val[:4] != g_val[:4]:
                    issues.append({"row": i+2, "F": f_val, "G": g_val})  # +2 for Excel-like row numbers
    return issues

def check_trade_errors(df):
    issues = []
    valid_values = {"05", "03", "07"}
    if 'C' in df.columns:
        for i, val in enumerate(df['C']):
            val_str = str(val).strip()
            if val_str not in valid_values:
                issues.append({"row": i+2, "C": val_str})
    return issues

def check_address_column_mismatches(df):
    issues = []
    if 'J' in df.columns and 'K' in df.columns:
        for i, row in df.iterrows():
            j_val = str(row['J']) if pd.notna(row['J']) else ''
            k_val = str(row['K']) if pd.notna(row['K']) else ''
            if k_val.strip() != '':  # skip blank K
                if j_val[:4] != k_val[:4]:
                    issues.append({"row": i+2, "J": j_val, "K": k_val})
    return issues

def check_z_code_errors(df):
    issues = []
    valid_codes = {"777750Z", "777796Z"}
    if 'AL' in df.columns:
        for i, val in enumerate(df['AL']):
            val_str = str(val).strip()
            if val_str not in valid_codes:
                issues.append({"row": i+2, "AL": val_str})
    return issues

def check_non_us_states(df):
    issues = []
    valid_states = {
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
        "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
        "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
        "VA","WA","WV","WI","WY"
    }
    for col in ['O', 'P']:
        if col in df.columns:
            for i, val in enumerate(df[col]):
                val_str = str(val).strip()
                if val_str and val_str not in valid_states:
                    issues.append({"row": i+2, col: val_str})
    return issues

# ========== STREAMLIT APP ==========
st.set_page_config(page_title="Matching DI Tool", page_icon="🔍", layout="wide")

def main():
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None

    st.header("📁 File Upload")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload Excel files (.xlsx or .xls format)"
    )

    if uploaded_file is not None:
        try:
            with st.spinner("Loading Excel file..."):
                df = pd.read_excel(uploaded_file)
                st.session_state.uploaded_data = df

            st.success(f"✅ File uploaded successfully! {len(df)} rows × {len(df.columns)} cols")

            st.subheader("📊 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)

            st.header("⚙️ Validation Settings")
            check_banner = st.checkbox("Check Banner Mismatches (F vs G)", True)
            check_trade = st.checkbox("Check Trade Errors (C)", True)
            check_addr = st.checkbox("Check Address Mismatches (J vs K)", True)
            check_z = st.checkbox("Check Z Code Errors (AL)", True)
            check_states = st.checkbox("Check Non-US States (O & P)", True)

            if st.button("🚀 Run Validation"):
                run_validation(df, check_banner, check_trade, check_addr, check_z, check_states)

        except Exception as e:
            st.error(f"❌ Error reading Excel file: {str(e)}")

    if st.session_state.validation_results is not None:
        display_results()

def run_validation(df, check_banner, check_trade, check_addr, check_z, check_states):
    results = {}
    if check_banner:
        results['banner_mismatches'] = check_banner_mismatches(df)
    if check_trade:
        results['trade_errors'] = check_trade_errors(df)
    if check_addr:
        results['address_column_mismatches'] = check_address_column_mismatches(df)
    if check_z:
        results['z_code_errors'] = check_z_code_errors(df)
    if check_states:
        results['non_us_states'] = check_non_us_states(df)

    st.session_state.validation_results = results
    st.success("✅ Validation completed!")

def display_results():
    results = st.session_state.validation_results
    st.header("📋 Validation Results")

    total_issues = sum(len(v) for v in results.values())
    st.metric("Total Issues Found", total_issues)

    for name, issues in results.items():
        if issues:
            st.subheader(f"{name} ({len(issues)} issues)")
            st.dataframe(pd.DataFrame(issues), use_container_width=True)
        else:
            st.subheader(f"{name} - No issues")

if __name__ == "__main__":
    main()
