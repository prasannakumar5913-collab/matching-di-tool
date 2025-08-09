import streamlit as st
import pandas as pd
import io
import time
from validators import DataValidator
from utils import format_validation_results, export_report

st.set_page_config(
    page_title="Matching QC Tool",
    page_icon="🔍",
    layout="wide"
)

# Your full CSS from above (omitted here for brevity, insert your entire CSS string here)
st.markdown("""
<style>
    /* Insert all your CSS here exactly as you provided */
</style>
""", unsafe_allow_html=True)

def run_validation(df, check_banner, check_trade, check_address_cols, check_z_code, check_non_us):
    # PLACEHOLDER: Your existing validation logic goes here.
    # Make sure to set:
    #   st.session_state.validation_results = {...}
    #   st.session_state.uploaded_data = df_with_error_columns_or_original_df
    # For demo, let's just create empty results:
    results = {
        'banner_mismatches': [],
        'trade_errors': [],
        'address_column_mismatches': [],
        'z_code_errors': [],
        'non_us_states': []
    }
    st.session_state.validation_results = results
    st.session_state.uploaded_data = df
    time.sleep(1)  # simulate processing

def main():
    st.markdown('''
    <div class="tool-name main-title">
        <h1 class="custom-header">
            <span style="color: #667eea;">MATCHING</span>
            <span style="color: #764ba2; margin-left: 15px;">DI</span>
            <span style="color: #667eea; margin-left: 15px;">TOOL</span>
        </h1>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="floating-icon" style="font-size: 2rem;">📊</span>
        <p style="font-size: 1.2rem; color: #666; margin-top: 1rem;">
            Upload an Excel file to perform comprehensive data validation including address checks and data quality analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None

    st.header("📁 File Upload")
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            with st.spinner("Loading Excel file..."):
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
            
            # Validation options UI
            col1, col2 = st.columns(2)
            with col1:
                check_banner_mismatches = st.checkbox("Check Banner Mismatches (F vs G columns)", value=True)
                check_trade_errors = st.checkbox("Check Trade Errors (C column)", value=True)
                check_address_column_mismatches = st.checkbox("Check Address Mismatches (J vs K columns)", value=True)
            with col2:
                check_z_code_errors = st.checkbox("Check Z Code Errors (AL column)", value=True)
                check_non_us_states = st.checkbox("Check Non-US States (O & P columns)", value=True)

            if st.button("🚀 Run Validation"):
                run_validation(
                    df,
                    check_banner_mismatches,
                    check_trade_errors,
                    check_address_column_mismatches,
                    check_z_code_errors,
                    check_non_us_states
                )
                st.success("✅ Validation completed! Results are ready for review.")
                st.experimental_rerun()

        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")

    if st.session_state.validation_results:
        display_validation_results()

def display_validation_results():
    results = st.session_state.validation_results
    full_df = st.session_state.uploaded_data

    st.header("📋 Validation Results")

    total_issues = sum(len(v) for v in results.values())
    total_records = len(full_df) if full_df is not None else 0
    issue_rate = (total_issues / total_records * 100) if total_records > 0 else 0

    st.markdown('<div class="validation-summary">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Issues Found", total_issues)
    with col2:
        st.metric("Total Records Checked", total_records)
    with col3:
        st.metric("Issue Rate", f"{issue_rate:.1f}%")
    with col4:
        rows_with_issues = set()
        for issues in results.values():
            for issue in issues:
                if isinstance(issue, dict) and 'row' in issue:
                    rows_with_issues.add(issue['row'])
        clean_records = total_records - len(rows_with_issues)
        st.metric("Clean Records", clean_records)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("🔍 Detailed Issues")
    for check_type, issues in results.items():
        if issues:
            with st.expander(f"{check_type.replace('_', ' ').title()} ({len(issues)} issues)"):
                if isinstance(issues[0], dict):
                    st.dataframe(pd.DataFrame(issues), use_container_width=True)
                else:
                    for i, issue in enumerate(issues, 1):
                        st.write(f"{i}. {issue}")

    st.subheader("📤 Export Report")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Download Detailed Report"):
            data = export_report(full_df, results)
            st.download_button(
                label="💾 Download Excel Report",
                data=data,
                file_name="validation_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    with col2:
        if st.button("📋 Download Summary Report"):
            summary_report = format_validation_results(results)
            csv_bytes = summary_report.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download Summary (CSV)",
                data=csv_bytes,
                file_name="validation_summary.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
