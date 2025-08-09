import streamlit as st
import pandas as pd
import io
from validators import DataValidator
from utils import format_validation_results, export_report
import os
import time

# Set page configuration
st.set_page_config(
    page_title="Matching QC Tool",
    page_icon="🔍",
    layout="wide"
)

# Add custom CSS for animations and styling
st.markdown("""
<style>
    /* Main title animation */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(51, 51, 255, 0.3); }
        50% { box-shadow: 0 0 20px rgba(51, 51, 255, 0.6); }
        100% { box-shadow: 0 0 5px rgba(51, 51, 255, 0.3); }
    }
    
    /* Apply animations to specific elements */
    .main-title {
        animation: fadeInDown 1s ease-out;
    }
    
    .metric-container {
        animation: slideInLeft 0.8s ease-out;
        transition: transform 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
    }
    
    .validation-section {
        animation: slideInRight 1s ease-out;
    }
    
    .stButton > button {
        animation: pulse 2s infinite;
        transition: all 0.3s ease;
        border-radius: 10px;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        animation: none;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    .upload-area {
        border: 3px dashed #4ECDC4;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        background: linear-gradient(135deg, rgba(78, 205, 196, 0.1), rgba(255, 107, 107, 0.1));
        animation: glow 3s infinite;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        transform: scale(1.02);
        border-color: #FF6B6B;
    }
    
    .success-animation {
        animation: slideInLeft 0.5s ease-out;
    }
    
    .checkbox-container {
        transition: all 0.3s ease;
        padding: 10px;
        border-radius: 8px;
    }
    
    .checkbox-container:hover {
        background-color: rgba(78, 205, 196, 0.1);
        transform: translateX(10px);
    }
    
    .data-preview {
        animation: fadeInDown 1.2s ease-out;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress bar animation */
    .stProgress > div > div {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1);
        background-size: 300% 300%;
        animation: gradientMove 2s ease infinite;
    }
    
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Custom header styling */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: 2px;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .tool-name {
        display: block;
        position: relative;
        text-align: center;
        width: 100%;
        margin: 0 auto 2rem auto;
        padding: 20px 40px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 20px;
        border: 2px solid transparent;
        background-clip: padding-box;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .tool-name::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 20px;
        z-index: -1;
        opacity: 0.1;
        animation: borderGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes borderGlow {
        0% { opacity: 0.1; transform: scale(1); }
        100% { opacity: 0.3; transform: scale(1.02); }
    }
    
    /* Floating elements */
    .floating-icon {
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Hide copy buttons throughout the app */
    button[title="Copy to clipboard"] {
        display: none !important;
    }
    
    .copy-to-clipboard {
        display: none !important;
    }
    
    /* Light colored validation report styling */
    .validation-summary {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f4f8 100%);
        border: 2px solid #d1e7f0;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .validation-report-box {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
        border: 1px solid #b3d9ff;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Professional animated title with enhanced styling
    st.markdown('''
    <div class="tool-name main-title">
        <h1 class="custom-header">
            <span style="color: #667eea;">MATCHING</span>
            <span style="color: #764ba2; margin-left: 15px;">DI</span>
            <span style="color: #667eea; margin-left: 15px;">TOOL</span>
        </h1>
    </div>
    ''', unsafe_allow_html=True)
    
    # Animated subtitle with floating icon
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="floating-icon" style="font-size: 2rem;">📊</span>
        <p style="font-size: 1.2rem; color: #666; margin-top: 1rem;">
            Upload an Excel file to perform comprehensive data validation including address checks and data quality analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", len(df), delta=None)
            with col2:
                st.metric("Data Rows", len(df) - 3 if len(df) > 3 else 0, delta=None)
            with col3:
                st.metric("Total Columns", len(df.columns), delta=None)
            with col4:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB", delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show data preview with animation
            st.markdown('<div class="data-preview">', unsafe_allow_html=True)
            st.subheader("📊 Data Preview")
            
            # Create a styled dataframe starting from row 4 (actual data rows)
            # Skip first 3 rows as they contain headers/structural info
            preview_df = df.iloc[3:13].copy()  # Show 10 rows of actual data starting from row 4
            
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
            
      
            


            # Validation settings with animation
            st.markdown('<div class="validation-section">', unsafe_allow_html=True)
            st.header("⚙ Validation Settings")
            
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
    st.markdown("""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999;">
        <div class="fireworks">
            <div class="firework"></div>
            <div class="firework"></div>
            <div class="firework"></div>
        </div>
    </div>
    
    <style>
    .fireworks {
        position: relative;
        width: 100%;
        height: 100%;
    }
    
    .firework {
        position: absolute;
        width: 4px;
        height: 4px;
        background: #ff6b6b;
        border-radius: 50%;
        animation: firework 2s ease-out;
    }
    
    .firework:nth-child(1) {
        left: 20%;
        top: 30%;
        animation-delay: 0s;
        background: #4ecdc4;
    }
    
    .firework:nth-child(2) {
        left: 60%;
        top: 20%;
        animation-delay: 0.5s;
        background: #45b7d1;
    }
    
    .firework:nth-child(3) {
        left: 80%;
        top: 40%;
        animation-delay: 1s;
        background: #ff6b6b;
    }
    
    @keyframes firework {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(20); opacity: 0.7; }
        100% { transform: scale(40); opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True)
    
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

if _name_ == "_main_":
    main()
