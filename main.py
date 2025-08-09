import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# ==============================
# Page Config
# ==============================
st.set_page_config(
    page_title="Matching DI Tool",
    page_icon="🔍",
    layout="wide"
)

# ==============================
# Custom Styling (Light Mode + Hide Branding)
# ==============================
st.markdown("""
    <style>
    /* Force light background */
    .stApp {
        background-color: white !important;
        color: black !important;
    }

    /* Ensure all text is dark */
    html, body, [class*="css"] {
        color: black !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #222 !important;
    }

    /* Metric styling */
    .stMetric {
        background-color: #f8f9fa !important;
        color: black !important;
        border-radius: 10px;
        padding: 10px;
    }

    /* Hide Streamlit default menu/footer/header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==============================
# Your Existing Code Starts Here
# ==============================
st.title("Matching DI Tool")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.write("Preview of Uploaded Data:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
from validators import DataValidator

df = pd.DataFrame({
    'F': ['ABCD123', 'ABCD456', 'WXYZ789'],
    'G': ['ABCD999', 'WXYZ000', 'WXYZ111'],
    'C': ['05', '99', '03'],
    'J': ['ADDR1', 'ADDR2', 'ADDR3'],
    'K': ['ADDR1', 'ADDRX', 'ADDR3'],
    'AL': ['777750Z', 'BADCODE', '777796Z'],
    'O': ['CA', 'XX', 'NY'],
    'P': ['TX', 'ZZ', 'FL']
})
checks = {
    'banner_mismatches': True,
    'trade_errors': True,
    'address_column_mismatches': True,
    'z_code_errors': True,
    'non_us_states': True
}
validator = DataValidator()
results = validator.validate_data(df, {}, checks)
print(results)
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

def main():
    # Professional animated title with enhanced styling
        
    # Animated subtitle with floating icon
        
    # Initialize session state
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    
    # File upload section without box
    st.header("📁 File Upload")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload Excel files (.xlsx or .xls format) for data inspection"
    )
    
    if uploaded_file is not None:
        try:
            # Read the Excel file
            with st.spinner("Loading Excel file..."):
                df = pd.read_excel(uploaded_file)
                st.session_state.uploaded_data = df
            
            # Animated success message
            st.markdown('<div class="success-animation">', unsafe_allow_html=True)
            st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display basic file information with animation
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df), delta=None)
            with col2:
                st.metric("Total Columns", len(df.columns), delta=None)
            with col3:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB", delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show data preview with animation
            st.markdown('<div class="data-preview">', unsafe_allow_html=True)
            st.subheader("📊 Data Preview")
            
            # Create a styled dataframe with 4th column headers in bold
            preview_df = df.head(10).copy()
            
            # Style the dataframe to highlight 4th column (D column) headers
            def highlight_4th_column(df):
                # Create an empty style dataframe
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                
                # If there's a 4th column (index 3), style it
                if len(df.columns) > 3:
                    # Bold the 4th column header and first row
                    styles.iloc[:, 3] = 'font-weight: bold; background-color: #f0f2f6;'
                
                return styles
            
            # Display styled dataframe
            styled_df = preview_df.style.apply(highlight_4th_column, axis=None)
            st.dataframe(styled_df, use_container_width=True)
            
            # Show column headers info for 4th column
            if len(df.columns) > 3:
                st.info(f"**📌 Column D (4th column):** {df.columns[3]} - Headers are highlighted (contains structural information, not validated as data)")
            st.markdown('</div>', unsafe_allow_html=True)
            


            # Validation settings with animation
            st.markdown('<div class="validation-section">', unsafe_allow_html=True)
            st.header("⚙️ Validation Settings")
            
            # Primary validations
            st.subheader("🎯 Primary Validations")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="checkbox-container">', unsafe_allow_html=True)
                check_banner_mismatches = st.checkbox("Check Banner Mismatches (F vs G columns)", value=True, help="Uses LEFT(F,4)=LEFT(G,4) logic, skips blank G rows")
                check_trade_errors = st.checkbox("Check Trade Errors (C column)", value=True, help="Validates C column contains only 05, 03, or 07")
                check_address_column_mismatches = st.checkbox("Check Address Mismatches (J vs K columns)", value=True, help="Uses LEFT(J,4)=LEFT(K,4) logic, skips blank K rows")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="checkbox-container">', unsafe_allow_html=True)
                check_z_code_errors = st.checkbox("Check Z Code Errors (AL column)", value=True, help="Validates AL column contains only 777750Z or 777796Z")
                check_non_us_states = st.checkbox("Check Non-US States (O & P columns)", value=True, help="Checks columns O and P for non-US states")
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            

            

            # Run validation button
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
    
    # Display validation results if available
    if st.session_state.validation_results is not None:
        display_validation_results()

def run_validation(df, check_banner, check_trade, check_address_cols, check_z_code, check_non_us):
    """Run the data validation process"""
    
    # Animated progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Initialize
    status_text.text("🔧 Initializing validation engine...")
    progress_bar.progress(20)
    time.sleep(0.5)
    
    # Step 2: Load data
    status_text.text("📊 Loading and analyzing data...")
    progress_bar.progress(40)
    time.sleep(0.5)
    
    # Step 3: Run validations
    status_text.text("🔍 Running validation checks...")
    progress_bar.progress(60)
    time.sleep(0.5)
    
    with st.spinner("Processing validation results..."):
        # Initialize validator
        validator = DataValidator()
        
        # Run validations
        results = validator.validate_data(
            df, 
            {},  # No column mapping needed for primary validations
            {
                'banner_mismatches': check_banner,
                'trade_errors': check_trade,
                'address_column_mismatches': check_address_cols,
                'z_code_errors': check_z_code,
                'non_us_states': check_non_us
            }
        )
        
        # Complete progress
        status_text.text("✅ Validation completed successfully!")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.session_state.validation_results = results
    
    # Fireworks celebration effect
        
    st.success("✅ Validation completed! Results are ready for review.")
    time.sleep(2)  # Show fireworks for 2 seconds
    st.rerun()

def display_validation_results():
    """Display the validation results"""
    results = st.session_state.validation_results
    
    st.header("📋 Validation Results")
    
    # Summary metrics with light styling
    total_issues = sum(len(issues) for issues in results.values())
    
    st.markdown('<div class="validation-summary">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Issues Found", total_issues)
    with col2:
        st.metric("Total Records Checked", len(st.session_state.uploaded_data))
    with col3:
        issue_rate = (total_issues / len(st.session_state.uploaded_data)) * 100 if len(st.session_state.uploaded_data) > 0 else 0
        st.metric("Issue Rate", f"{issue_rate:.1f}%")
    with col4:
        # Calculate clean records by getting unique row numbers with issues
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
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed results
    st.subheader("🔍 Detailed Issues")
    
    for check_type, issues in results.items():
        if issues:
            with st.expander(f"{check_type.replace('_', ' ').title()} ({len(issues)} issues)", expanded=False):
                st.markdown('<div class="validation-report-box">', unsafe_allow_html=True)
                if isinstance(issues, list) and len(issues) > 0:
                    if isinstance(issues[0], dict):
                        # Display as DataFrame for structured data
                        issues_df = pd.DataFrame(issues)
                        st.dataframe(issues_df, use_container_width=True)
                    else:
                        # Display as simple list
                        for i, issue in enumerate(issues, 1):
                            st.write(f"{i}. {issue}")
                else:
                    st.write("No specific details available for these issues.")
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Export functionality
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
