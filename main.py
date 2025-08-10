import streamlit as st
import pandas as pd
import io
import time

# Utility functions (previously in utils.py)
def format_validation_results(results):
    summary = []
    for check, issues in results.items():
        summary.append({'Check': check, 'Issues Found': len(issues)})
    return pd.DataFrame(summary)

def export_report(df, results):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        # Write each validation result in separate sheets
        for check, issues in results.items():
            if issues:
                pd.DataFrame(issues).to_excel(writer, index=False, sheet_name=check[:31])
            else:
                pd.DataFrame(columns=['No issues found']).to_excel(writer, sheet_name=check[:31])
    output.seek(0)
    return output.getvalue()

# Set page configuration
st.set_page_config(
    page_title="Matching QC Tool",
    page_icon="🔍",
    layout="wide"
)

# Add custom CSS for animations and styling
st.markdown("""
<style>
    /* (Your existing CSS from above here; omitted for brevity in this snippet) */
    /* Copy-paste all your CSS styles here from your original code */
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
            
            preview_df = df.iloc[3:13].copy()  # Show 10 rows of actual data starting from row 4
            
            def highlight_4th_column(df):
                styles = pd.DataFrame('', index=df.index, columns=df.columns)
                if len(df.columns) > 3:
                    styles.iloc[:, 3] = 'font-weight: bold; background-color: #f0f2f6;'
                return styles
            
            styled_df = preview_df.style.apply(highlight_4th_column, axis=None)
            st.dataframe(styled_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Validation settings with animation
            st.markdown('<div class="validation-section">', unsafe_allow_html=True)
            st.header("⚙ Validation Settings")
            
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

def validate_data(df, checks):
    results = {}

    # 1. Banner mismatches (6th vs 7th columns, first 4 letters must match, skip blank G)
    if checks.get('banner_mismatches', False):
        mismatches = []
        if df.shape[1] > 6:
            for idx, (f_val, g_val) in enumerate(zip(df.iloc[:, 5], df.iloc[:, 6])):
                if pd.notna(g_val) and str(f_val)[:4] != str(g_val)[:4]:
                    mismatches.append({'row': idx + 4, 'F': f_val, 'G': g_val})
        results['banner_mismatches'] = mismatches

    # 2. Trade errors (3rd column must be 05, 03, or 07)
    if checks.get('trade_errors', False):
        errors = []
        if df.shape[1] > 2:
            for idx, val in enumerate(df.iloc[:, 2]):
                if str(val) not in ['05', '03', '07']:
                    errors.append({'row': idx + 4, 'C': val})
        results['trade_errors'] = errors

    # 3. Address column mismatches (10th vs 11th columns, first 4 letters must match, skip blank K)
    if checks.get('address_column_mismatches', False):
        mismatches = []
        if df.shape[1] > 10:
            for idx, (j_val, k_val) in enumerate(zip(df.iloc[:, 9], df.iloc[:, 10])):
                if pd.notna(k_val) and str(j_val)[:4] != str(k_val)[:4]:
                    mismatches.append({'row': idx + 4, 'J': j_val, 'K': k_val})
        results['address_column_mismatches'] = mismatches

    # 4. Z code errors (38th column must be 777750Z or 777796Z)
    if checks.get('z_code_errors', False):
        errors = []
        if df.shape[1] > 37:
            for idx, val in enumerate(df.iloc[:, 37]):
                if str(val) not in ['777750Z', '777796Z']:
                    errors.append({'row': idx + 4, 'AL': val})
        results['z_code_errors'] = errors

    # 5. Non-US states (15th & 16th columns, must be 2-letter US state codes)
    if checks.get('non_us_states', False):
        us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
            'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
            'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }
        errors = []
        for col_idx in [14, 15]:
            if df.shape[1] > col_idx:
                for idx, val in enumerate(df.iloc[:, col_idx]):
                    if pd.notna(val) and str(val).upper() not in us_states:
                        errors.append({'row': idx + 4, 'column': df.columns[col_idx], 'value': val})
        results['non_us_states'] = errors

    return results

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
        data_df = df.iloc[3:]  # Skip first 3 rows as headers
        results = validate_data(
            data_df,
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

    # Fireworks effect
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
    st.experimental_rerun()

def display_validation_results():
    results = st.session_state.validation_results
    
    st.header("📋 Validation Results")
    
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
    
    st.subheader("🔍 Detailed Issues")
    
    for check_type, issues in results.items():
        if issues:
            with st.expander(f"{check_type.replace('_', ' ').title()} ({len(issues)} issues)", expanded=False):
                st.markdown('<div class="validation-report-box">', unsafe_allow_html=True)
                if isinstance(issues, list) and len(issues) > 0:
                    if isinstance(issues[0], dict):
                        issues_df = pd.DataFrame(issues)
                        st.dataframe(issues_df, use_container_width=True)
                    else:
                        for i, issue in enumerate(issues, 1):
                            st.write(f"{i}. {issue}")
                else:
                    st.write("No specific details available for these issues.")
                st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📤 Export Report")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Detailed Report", use_container_
