# app.py
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
            # Read the Excel file (keep as original for output)
            with st.spinner("Loading Excel file..."):
                df = pd.read_excel(uploaded_file, header=None)
                st.session_state.uploaded_data = df.copy()  # keep original for outputs
            
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
            
            # Keep your preview behaviour (show 10 rows starting from the 4th row)
            preview_df = df.iloc[3:13].copy()  # Show 10 rows of actual data starting from row 4
            st.dataframe(preview_df, use_container_width=True)
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

# --- Helper: US states set (two-letter codes)
US_STATES = set([
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA',
    'ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK',
    'OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'
])

def run_validation(df, check_banner, check_trade, check_address_cols, check_z_code, check_non_us):
    """Run the data validation process with your updated rules.
       - df: the original dataframe read header=None (so we keep first 3 rows)
       - We skip first 3 rows for validation but keep them in output
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🔧 Initializing validation engine...")
    progress_bar.progress(10)
    time.sleep(0.3)
    
    status_text.text("📊 Preparing data for validation...")
    progress_bar.progress(30)
    time.sleep(0.3)
    
    # Work on a copy to avoid mutating original state directly
    full_df = df.copy().reset_index(drop=True)  # original raw (header rows included)
    
    # ensure enough columns - if file is narrower, we won't crash
    ncols = full_df.shape[1]
    
    # Create error columns (default empty)
    for col in ["Banner_Error", "Address_Error", "Trade_Error", "State_Error", "Zcode_Error", "AO_AP_Error", "Remarks"]:
        full_df[col] = ""
    
    # We'll validate rows starting from the 4th row (index 3)
    if len(full_df) <= 3:
        st.error("No data rows to validate after skipping first 3 rows.")
        return
    
    data_df = full_df.iloc[3:].reset_index(drop=True)  # data rows for validation
    progress_bar.progress(50)
    status_text.text("🔍 Running validation checks...")
    time.sleep(0.3)
    
    # Column index mapping (0-based) by Excel letter positions:
    # A=0, B=1, ... so:
    idx_map = {
        'C': 2,   # Trade
        'F': 5, 'G': 6,   # Banner (F=client banner, G=matched)
        'I': 8, 'J': 9, 'K': 10,  # Address: I (client came info?), J/K as asked (we'll use J & K)
        'O': 14, 'P': 15,  # States
        'AL': 37,  # Z Code
        'AO': 40, 'AP': 41  # AO/AP job id & client store (mandatory on mismatch)
    }
    # Ensure we don't index out-of-range if uploaded sheet has fewer columns
    def safe_get(row, col_idx):
        if col_idx is None:
            return ""
        if col_idx < len(row):
            val = row[col_idx]
            return "" if pd.isna(val) else str(val).strip()
        return ""
    
    # Results dict for display_validation_results (same keys used earlier)
    results = {
        'banner_mismatches': [],
        'trade_errors': [],
        'address_column_mismatches': [],
        'z_code_errors': [],
        'non_us_states': []
    }
    
    for i, row in data_df.iterrows():
        excel_row_index = i + 3  # index in full_df (0-based)
        remarks = []
        row_has_issue = False
        
        # --- Banner check (F vs G) - use LEFT(...,4), skip if G blank ---
        if check_banner:
            f_val = safe_get(row, idx_map.get('F'))
            g_val = safe_get(row, idx_map.get('G'))
            if g_val != "":
                if f_val[:4] != g_val[:4]:
                    row_has_issue = True
                    full_df.at[excel_row_index, "Banner_Error"] = "Banner mismatch"
                    remarks.append("Banner mismatch")
                    # record into results (1-based excel row)
                    results['banner_mismatches'].append({
                        'row': excel_row_index + 1,
                        'F': f_val,
                        'G': g_val,
                        'AO': safe_get(row, idx_map.get('AO')),
                        'AP': safe_get(row, idx_map.get('AP'))
                    })
        
        # --- State check (O & P) ---
        if check_non_us:
            o_val = safe_get(row, idx_map.get('O'))
            p_val = safe_get(row, idx_map.get('P'))
            if o_val != "" and o_val.upper() not in US_STATES:
                row_has_issue = True
                full_df.at[excel_row_index, "State_Error"] += "O-not-US"
                remarks.append("State outside US (O)")
                results['non_us_states'].append({
                    'row': excel_row_index + 1,
                    'col': 'O',
                    'value': o_val,
                    'AO': safe_get(row, idx_map.get('AO')),
                    'AP': safe_get(row, idx_map.get('AP'))
                })
            if p_val != "" and p_val.upper() not in US_STATES:
                row_has_issue = True
                if full_df.at[excel_row_index, "State_Error"]:
                    full_df.at[excel_row_index, "State_Error"] += "; P-not-US"
                else:
                    full_df.at[excel_row_index, "State_Error"] = "P-not-US"
                remarks.append("State outside US (P)")
                results['non_us_states'].append({
                    'row': excel_row_index + 1,
                    'col': 'P',
                    'value': p_val,
                    'AO': safe_get(row, idx_map.get('AO')),
                    'AP': safe_get(row, idx_map.get('AP'))
                })
        
        # --- Trade Error check (C column) ---
        if check_trade:
            c_val = safe_get(row, idx_map.get('C'))
            # Normalize numeric like 5.0 -> "05" if possible
            c_str = c_val
            if c_str and c_str.isdigit() and len(c_str) == 1:
                c_str = c_str.zfill(2)
            if c_str not in ["05", "03", "07"]:
                # treat empty as error (change if you want to ignore blanks)
                row_has_issue = True
                full_df.at[excel_row_index, "Trade_Error"] = "Trade error"
                remarks.append("Trade error")
                results['trade_errors'].append({
                    'row': excel_row_index + 1,
                    'C': c_val,
                    'AO': safe_get(row, idx_map.get('AO')),
                    'AP': safe_get(row, idx_map.get('AP'))
                })
        
        # --- Address Check (J vs K) - use LEFT(...,4), skip if K blank ---
        if check_address_cols:
            j_val = safe_get(row, idx_map.get('J'))
            k_val = safe_get(row, idx_map.get('K'))
            if k_val != "":
                if j_val[:4] != k_val[:4]:
                    row_has_issue = True
                    full_df.at[excel_row_index, "Address_Error"] = "Address mismatch"
                    remarks.append("Address mismatch")
                    results['address_column_mismatches'].append({
                        'row': excel_row_index + 1,
                        'J': j_val,
                        'K': k_val,
                        'AO': safe_get(row, idx_map.get('AO')),
                        'AP': safe_get(row, idx_map.get('AP'))
                    })
        
        # --- Z code error (AL) ---
        if check_z_code:
            al_val = safe_get(row, idx_map.get('AL'))
            if al_val != "" and al_val not in ["777750Z", "777796Z"]:
                row_has_issue = True
                full_df.at[excel_row_index, "Zcode_Error"] = "Z Code error"
                remarks.append("Z Code error")
                results['z_code_errors'].append({
                    'row': excel_row_index + 1,
                    'AL': al_val,
                    'AO': safe_get(row, idx_map.get('AO')),
                    'AP': safe_get(row, idx_map.get('AP'))
                })
        
        # --- AO & AP mandatory if any mismatch ---
        if row_has_issue:
            ao_val = safe_get(row, idx_map.get('AO'))
            ap_val = safe_get(row, idx_map.get('AP'))
            if not ao_val or not ap_val:
                full_df.at[excel_row_index, "AO_AP_Error"] = "AO/AP missing"
                remarks.append("AO/AP missing")
        
        # Set combined remarks column
        if remarks:
            full_df.at[excel_row_index, "Remarks"] = "; ".join(remarks)
    
    # Save results to session state for display
    st.session_state.validation_results = results
    st.session_state.uploaded_data = full_df  # full_df contains original rows + error cols
    
    # Finish progress
    progress_bar.progress(100)
    status_text.text("✅ Validation completed successfully!")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    
    # Celebration (brief) — properly closed triple-quoted string
    st.markdown("""
    <div style="position: f

            
