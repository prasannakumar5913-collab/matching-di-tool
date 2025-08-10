import streamlit as st
import pandas as pd
import io
from validators import DataValidator
from utils import format_validation_results, export_report
import os
import time

# Set page configuration
st.set_page_config(
    page_title="Matching DI Tool",
    page_icon="🔍",
    layout="wide"
)

# Add custom CSS for animations and styling
st.markdown("""
<style>
.bold-highlight {
    font-weight: bold;
    background-color: #f0f2f6;
}
.title {
    font-size: 32px;
    font-weight: bold;
    animation: fadeIn 2s ease-in-out;
}
.subtitle {
    font-size: 18px;
    margin-bottom: 20px;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

def main():
    # Title and subtitle
    st.markdown("""
    <div class="title">MATCHING DI TOOL</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="subtitle">📊 Upload an Excel file to perform comprehensive data validation including address checks and data quality analysis</div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None

    # File upload section
    st.header("📁 File Upload")
    uploaded_file = st.file_uploader(
        "Choose an Excel file", type=['xlsx', 'xls'],
        help="Upload Excel files (.xlsx or .xls format) for data inspection"
    )

    if uploaded_file is not None:
        try:
            with st.spinner("Loading Excel file..."):
                df = pd.read_excel(uploaded_file)
                st.session_state.uploaded_data = df

            st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")

            st.subheader("📊 Data Preview")
            preview_df = df.head(10).copy()

            def highlight_4th_column(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                if len(df.columns) > 3:
                    styles.iloc[:, 3] = 'font-weight: bold; background-color: #f0f2f6;'
                return styles

            styled_df = preview_df.style.apply(highlight_4th_column, axis=None)
            st.dataframe(styled_df, use_container_width=True)

            if len(df.columns) > 3:
                st.info(f"**📌 Column D (4th column):** {df.columns[3]} - Headers are highlighted (contains structural information, not validated as data)")

            # Validation settings
            st.header("⚙️ Validation Settings")
            st.subheader("🎯 Primary Validations")

            col1, col2 = st.columns(2)
            with col1:
                check_banner_mismatches = st.checkbox("Check Banner Mismatches (F vs G columns)", value=True)
                check_trade_errors = st.checkbox("Check Trade Errors (C column)", value=True)
                check_address_column_mismatches = st.checkbox("Check Address Mismatches (J vs K columns)", value=True)
            with col2:
                check_z_code_errors = st.checkbox("Check Z Code Errors (AL column)", value=True)
                check_non_us_states = st.checkbox("Check Non-US States (O & P columns)", value=True)

            if st.button("🚀 Run Validation", type="primary", use_container_width=True):
                run_validation(
                    df,
                    check_banner_mismatches,
                    check_trade_errors,
                    check_address_column_mismatches,
                    check_z_code_errors,
                    check_non_us_states
                )

        except Exception as e:
            st.error(f"❌ Error reading Excel file: {str(e)}")
            st.markdown("Please ensure the file is a valid Excel format (.xlsx or .xls).")

    if st.session_state.validation_results is not None:
        display_validation_results()

def run_validation(df, check_banner, check_trade, check_address_cols, check_z_code, check_non_us):
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("🔧 Initializing validation engine...")
    progress_bar.progress(20)
    time.sleep(0.5)

    status_text.text("📊 Loading and analyzing data...")
    progress_bar.progress(40)
    time.sleep(0.5)

    status_text.text("🔍 Running validation checks...")
    progress_bar.progress(60)
    time.sleep(0.5)

    with st.spinner("Processing validation results..."):
        validator = DataValidator()
        results = validator.validate_data(
            df,
            {},
            {
                'banner_mismatches': check_banner,
                'trade_errors': check_trade,
                'address_column_mismatches': check_address_cols,
                'z_code_errors': check_z_code,
                'non_us_states': check_non_us
            }
        )

    status_text.text("✅ Validation completed successfully!")
    progress_bar.progress(100)
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

    st.session_state.validation_results = results
    st.success("✅ Validation completed! Results are ready for review.")
    time.sleep(2)
    st.rerun()

def display_validation_results():
    results = st.session_state.validation_results
    st.header("📋 Validation Results")

    total_issues = sum(len(issues) for issues in results.values())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Issues Found", total_issues)
    with col2:
        st.metric("Total Records Checked", len(st.session_state.uploaded_data))
    with col3:
        issue_rate = (total_issues / len(st.session_state.uploaded_data)) * 100 if len(st.session_state.uploaded_data) > 0 else 0
        st.metric("Issue Rate", f"{issue_rate:.1f}%")
    with col4:
        rows_with_issues = set()
        for issues in results.values():
            if issues:
                for issue in issues:
                    if isinstance(issue, dict) and 'row' in issue:
                        rows_with_issues.add(issue['row'])
                    elif isinstance(issue, dict) and 'rows' in issue:
                        rows_with_issues.update(issue['rows'])
        clean_records = len(st.session_state.uploaded_data) - len(rows_with_issues)
        st.metric("Clean Records", clean_records)

    st.subheader("🔍 Detailed Issues")
    for check_type, issues in results.items():
        if issues:
            with st.expander(f"{check_type.replace('_', ' ').title()} ({len(issues)} issues)", expanded=False):
                if isinstance(issues, list) and len(issues) > 0:
                    if isinstance(issues[0], dict):
                        issues_df = pd.DataFrame(issues)
                        st.dataframe(issues_df, use_container_width=True)
                    else:
                        for i, issue in enumerate(issues, 1):
                            st.write(f"{i}. {issue}")
                else:
                    st.write("No specific details available for these issues.")

    st.subheader("📤 Export Report")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Download Detailed Report", use_container_width=True):
            report_data = export_report(st.session_state.uploaded_data, results)
            st.download_button(
                label="💾 Download Excel Report",
                data=report_data,
                file_name="validation_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    with col2:
        if st.button("📋 Download Summary Report", use_container_width=True):
            summary_report = format_validation_results(results)
            st.download_button(
                label="💾 Download Summary (CSV)",
                data=summary_report.to_csv(index=False),
                file_name="validation_summary.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
