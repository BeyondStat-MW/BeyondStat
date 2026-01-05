# --- Page Config ---
import streamlit as st
st.set_page_config(layout="wide", page_title="Yongin FC Dashboard", page_icon="🐉")

# --- Authentication Logic (Gatekeeper) ---
from utils import auth

# Strict Isolation: Always hide sidebar/header on this client page
auth.inject_custom_css(hide_sidebar=True, hide_header=False)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def handle_login():
    username = st.session_state.get('yongin_user', '')
    password = st.session_state.get('yongin_pass', '')
    # Check for 'yongin' role or 'admin'
    role = auth.authenticate_user(username, password, required_roles=['yongin', 'admin'])
    
    if role:
        st.session_state['logged_in'] = True
        st.session_state['role'] = role
        st.session_state['current_user'] = username
    else:
        st.session_state['login_error'] = "인증 실패 (Yongin/Admin Only)"

# Case 1: Not Logged In (Direct Access)
if not st.session_state['logged_in']:
    auth.inject_custom_css()
    
    st.markdown("""
    <style>
        .login-super { display: flex; justify-content: center; margin-top: 100px; }
    </style>
    <div class='login-super'><h2 style='text-align: center; color: #E6002D;'>🐉 Yongin FC Login</h2></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if 'login_error' in st.session_state:
            st.error(st.session_state['login_error'])
            del st.session_state['login_error']
            
        st.text_input("ID", key="yongin_user")
        st.text_input("PW", type="password", key="yongin_pass", on_change=handle_login)
        st.button("Login", on_click=handle_login, type="primary", use_container_width=True)
    st.stop()

# Case 2: Logged In but Wrong Role (e.g. K-League user trying to access Yongin)
if st.session_state.get('role') not in ['yongin', 'admin']:
    auth.inject_custom_css()
    st.error("Access Denied")
    st.stop()

# --- Main App Logic ---
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from yongin_fc.utils import yongin_data_loader as data_loader
from utils import analysis_utils
import importlib
try:
    importlib.reload(data_loader)
except:
    pass

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp { background-color: #FAFAFA; }
    div[data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #eee; }
    
    /* KPI Box Style */
    .kpi-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        height: 100%;
    }
    .kpi-label {
        font-size: 13px;
        color: #666;
        font-weight: 600;
        margin-bottom: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-value {
        font-size: 20px;
        color: #E6002D; /* Yongin Red */
        font-weight: 800;
    }
    
    /* Navigation Buttons */
    .nav-btn-active { border: 2px solid #F37021 !important; color: #F37021 !important; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
# Use Session State to track current view
if 'yf_view_mode' not in st.session_state:
    st.session_state['yf_view_mode'] = 'Team Dashboard'

# Load Global Data for Sidebar Filters (Date Range)
try:
    with st.spinner("Initializing..."):
        df_global = data_loader.get_full_team_data()
        if not df_global.empty:
            min_date = df_global['Test_Date'].min()
            max_date = df_global['Test_Date'].max()
        else:
            import datetime
            min_date = datetime.date(2024, 1, 1)
            max_date = datetime.date.today()
except:
    import datetime
    min_date = datetime.date(2024, 1, 1)
    max_date = datetime.date.today()

with st.sidebar:
    h_col1, h_col2 = st.columns([1, 2.5])
    with h_col1:
        try:
            st.image("yongin_fc/yongin_logo.png", use_container_width=True)
        except:
            pass
    with h_col2:
        st.markdown("<h3 style='margin-top: 10px; margin-bottom: 0;'>Yongin FC</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Global Date Filter (Sidebar) ---
    st.markdown("### 📅 DATE FILTER")
    
    # Initialize Session State for Dates if not exists
    if 'yf_start_date' not in st.session_state:
        st.session_state['yf_start_date'] = min_date
    if 'yf_end_date' not in st.session_state:
        st.session_state['yf_end_date'] = max_date

    # Date Inputs with Bidirectional Sync
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        start_date = st.date_input("시작일", value=st.session_state['yf_start_date'], min_value=min_date, max_value=max_date, key='yf_start_date_picker', label_visibility="collapsed")
    with d_col2:
        end_date = st.date_input("종료일", value=st.session_state['yf_end_date'], min_value=min_date, max_value=max_date, key='yf_end_date_picker', label_visibility="collapsed")
    
    # Update state from picker
    if start_date != st.session_state['yf_start_date']:
        st.session_state['yf_start_date'] = start_date
        st.rerun()
    if end_date != st.session_state['yf_end_date']:
        st.session_state['yf_end_date'] = end_date
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📊 MENU")
    
    # Map friendly names to internal logic
    menu_map = {
        "팀 대시보드 (Team)": "Team Dashboard",
        "선수 상세 분석 (Player)": "Player Dashboard",
        "인사이트 분석 (Insight)": "Insight Analysis"
    }
    
    # Reverse map for default index
    reverse_map = {v: k for k, v in menu_map.items()}
    default_index = list(menu_map.values()).index(st.session_state['yf_view_mode'])
    
    selected_menu = st.radio(
        "이동할 메뉴를 선택하세요", 
        list(menu_map.keys()), 
        index=default_index,
        label_visibility="collapsed"
    )
    
    # Update Session State
    if st.session_state['yf_view_mode'] != menu_map[selected_menu]:
        st.session_state['yf_view_mode'] = menu_map[selected_menu]
        st.rerun()
    
    st.markdown("---")
    if st.button("Logout"):
        auth.logout()

# --- Header Section ---
col_h1, col_h2 = st.columns([0.8, 6])
with col_h1:
    # Try loading logo, fallback to emoji if missing
    try:
        st.image("yongin_fc/yongin_logo.png", width=80)
    except:
        st.markdown("## 🐉")

with col_h2:
    # Dynamic Subtitle based on View Mode
    subtitle = st.session_state['yf_view_mode']
    st.markdown(f"""
    <div style="display: flex; align-items: baseline; gap: 15px;">
        <h1 style='margin: 0; padding: 0; color: #1a1a1a; font-size: 36px;'>YONGIN FC <span style='color: #E6002D;'>Performance Center</span></h1>
        <h3 style='margin: 0; padding: 0; color: #666; font-weight: 400;'>| &nbsp; {subtitle}</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("Monitor player physical condition and training load.")

st.divider()

# --- Global Date Filter (Main Area) --- (Removed)
st.markdown("<br>", unsafe_allow_html=True) # Spacer

# --- Helper functions ---
def safe_mean(df, col):
    if col in df.columns:
        return df[col].mean()
    return 0

def calculate_derived_cols(df):

    if 'Hamstring_Ecc_L' in df.columns and 'Hamstring_Ecc_Avg' not in df.columns:
        df['Hamstring_Ecc_Avg'] = df[['Hamstring_Ecc_L', 'Hamstring_Ecc_R']].mean(axis=1)
    if 'Hamstring_ISO_L' in df.columns and 'Hamstring_ISO_Avg' not in df.columns:
        df['Hamstring_ISO_Avg'] = df[['Hamstring_ISO_L', 'Hamstring_ISO_R']].mean(axis=1)
    if 'HipAdd_L' in df.columns and 'HipAdd_Avg' not in df.columns:
        df['HipAdd_Avg'] = df[['HipAdd_L', 'HipAdd_R']].mean(axis=1)
    if 'HipAbd_L' in df.columns and 'HipAbd_Avg' not in df.columns:
        df['HipAbd_Avg'] = df[['HipAbd_L', 'HipAbd_R']].mean(axis=1)

    # Added Hip Flexion Kicker Average
    if 'HipFlexion_Kicker_L' in df.columns and 'HipFlexion_Kicker_R' in df.columns and 'HipFlex_Avg' not in df.columns:
        df['HipFlex_Avg'] = df[['HipFlexion_Kicker_L', 'HipFlexion_Kicker_R']].mean(axis=1)

    return df

# --- VIEW: Team Dashboard ---
if st.session_state['yf_view_mode'] == 'Team Dashboard':
    # title removed
    
    # Filter df_global (which is df_team) by date
    if df_global.empty:
        st.warning("No data available.")
        st.stop()
        
    mask = (df_global['Test_Date'] >= start_date) & (df_global['Test_Date'] <= end_date)
    df_team = df_global.loc[mask]
    
    if df_team.empty:
        st.warning(f"No data found between {start_date} and {end_date}.")
        st.stop()
        
    df_team = calculate_derived_cols(df_team)
    
    # Identify correct columns (Prioritize trailing underscore versions if present)
    col_cmj = 'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_team.columns else 'CMJ_Height_Imp_mom'
    col_sj  = 'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_team.columns else 'SquatJ_Height_Imp_mom'
    
    # 1. 8 KPI Boxes
    kpis = [
        ("CMJ Height<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, col_cmj)),
        ("Squat Jump<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, col_sj)),
        ("HopTest RSI<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, 'HopTest_MeanRSI')),
        ("Hamstring Ecc<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, 'Hamstring_Ecc_Avg')),
        ("Hamstring ISO<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, 'Hamstring_ISO_Avg')),
        ("Hip Add<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, 'HipAdd_Avg')),
        ("Hip Abd<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, 'HipAbd_Avg')),
        ("Hip Flexion<br><span style='font-size:12px; color:#888'>(Avg)</span>", safe_mean(df_team, 'HipFlex_Avg'))
    ]
    
    cols = st.columns(8)
    for i, (label, val) in enumerate(kpis):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label" title="{label}">{label}</div>
                <div class="kpi-value">{val:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.divider()
    
    # 2. Charts Section (Power / Strength) - Vertical Layout
    
    # --- Power Metrics ---
    st.subheader("⚡ 파워 분석 (Power Metrics)")
    metric_opt = st.selectbox("지표 선택 (Select Metric)", ["CMJ", "SquatJ", "HopTest RSI"], key="team_pow")
    
    col_map = {
        "CMJ": col_cmj, 
        "SquatJ": col_sj, 
        "HopTest RSI": "HopTest_MeanRSI"
    }
    y_col = col_map[metric_opt]
    
    # Aggregation by Player (Mean of all their records)
    if y_col in df_team.columns:
        df_agg = df_team.groupby("Name")[y_col].mean().reset_index().sort_values(y_col, ascending=False)
        fig = px.bar(df_agg, x="Name", y=y_col, color=y_col, color_continuous_scale="Greens", text_auto='.1f', title=f"Team Ranking: {metric_opt}")
        
        # UI Updates: 90deg rotate, no color bar
        fig.update_layout(
            xaxis_tickangle=-90,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"Data for selected metric ({metric_opt}) not found in columns: {y_col}")

    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    # --- Strength Metrics ---
    st.subheader("💪 근력 분석 (Strength Metrics)")
    metric_opt_s = st.selectbox("지표 선택 (Select Metric)", ["Hamstring Ecc", "Hamstring ISO", "HipAdd", "HipAbd", "Hip Flexion"], key="team_str")
    
    col_map_s = {"Hamstring Ecc": "Hamstring_Ecc_Avg", "Hamstring ISO": "Hamstring_ISO_Avg", "HipAdd": "HipAdd_Avg", "HipAbd": "HipAbd_Avg", "Hip Flexion": "HipFlex_Avg"}
    y_col_s = col_map_s[metric_opt_s]
    
    if y_col_s in df_team.columns:
        df_agg_s = df_team.groupby("Name")[y_col_s].mean().reset_index().sort_values(y_col_s, ascending=False)
        fig_s = px.bar(df_agg_s, x="Name", y=y_col_s, color=y_col_s, color_continuous_scale="Oranges", text_auto='.0f', title=f"Team Ranking: {metric_opt_s}")
        
        # UI Updates: 90deg rotate, no color bar
        fig_s.update_layout(
            xaxis_tickangle=-90,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("Data for selected metric not found.")

# --- VIEW: Player Dashboard ---
elif st.session_state['yf_view_mode'] == 'Player Dashboard':
    
    player_list = data_loader.get_player_list()
    player_list = [p for p in player_list if isinstance(p, str)] # Simple clean
    
    # Callback for player change
    def on_player_change():
        selected = st.session_state['yf_selected_player']
        # Fetch player's data to determine date range
        df = data_loader.load_player_data(selected)
        if not df.empty:
            p_start = df['Test_Date'].min().date()
            p_end = df['Test_Date'].max().date()
            st.session_state['yf_start_date'] = p_start
            st.session_state['yf_end_date'] = p_end
            # Force update pickers via state keys (Streamlit handles this if keys match)
    
    c_header, c_sel = st.columns([3, 1])
    with c_sel:
        # Use session state for selection
        if 'yf_selected_player' not in st.session_state:
             st.session_state['yf_selected_player'] = player_list[0] if player_list else None

        selected_player = st.selectbox(
            "Select Player", 
            player_list, 
            key='yf_selected_player', 
            label_visibility='collapsed',
            on_change=on_player_change
        )
    
    with c_header:
        if selected_player:
            st.markdown(f"### 👤 선수별 분석 : {selected_player}")
        else:
            st.markdown("### 👤 선수별 분석")
        
    if selected_player:
        # Load Player Data
        df_p = data_loader.load_player_data(selected_player)
        
        if df_p.empty:
            st.warning("No data found for this player.")
        else:
            mask_p = (df_p['Test_Date'] >= start_date) & (df_p['Test_Date'] <= end_date)
            df_p = df_p.loc[mask_p]
            
            if df_p.empty:
                st.warning(f"No data for {selected_player} in the selected range.")
            else:
                df_p = calculate_derived_cols(df_p)
            
            # --- Helper Function for Premium UI Cards ---
            def create_detail_card(title, metrics, status_label, status_color):
                """
                Generates a premium-styled HTML card for player metrics.
                metrics: List of (Label, ValueHTML) tuples. ValueHTML can contain spans with colors.
                """
                rows_html = ""
                for label, val_html in metrics:
                    rows_html += f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 13px;'><span style='color: #666; font-weight: 500; flex: 0 1 auto;'>{label}</span><span style='font-weight: 700; color: #333; flex: 1 0 auto; text-align: right; white-space: nowrap;'>{val_html}</span></div>"
                
                # Single line strings to avoid markdown code block indentation issues
                card_style = "background-color: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; height: 100%; min-height: 305px; display: flex; flex-direction: column; justify-content: space-between;"
                title_style = "font-size: 15px; font-weight: 800; color: #111; border-bottom: 2px solid #E6002D; padding-bottom: 8px; margin-bottom: 15px; letter-spacing: -0.3px;"
                badge_style = f"display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; color: white; background-color: {status_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.08);"
                
                html = f"<div style='{card_style}'>"
                html += f"<div><div style='{title_style}'>{title}</div>{rows_html}</div>"
                html += f"<div style='text-align: right; margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px;'><span style='{badge_style}'>{status_label}</span></div>"
                html += "</div>"
                return html
            
            # Identify correct columns (Prioritize trailing underscore versions if present)
            col_cmj = 'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_p.columns else 'CMJ_Height_Imp_mom'
            col_sj  = 'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_p.columns else 'SquatJ_Height_Imp_mom'

            # --- 🔎 Player Deep Dive Check (Latest Status) ---
            # Helper for Badge Style Delta
            def format_delta_html(current_val, prev_val, unit="", inverse=False, decimal=1, suffix_lr=False):
                if pd.isna(current_val): return "N/A"
                
                # Suffix Logic (Left/Right)
                display_val = current_val
                lr_str = ""
                if suffix_lr:
                    lr_str = "L " if current_val < 0 else "R "
                    display_val = abs(current_val)
                
                # Formatted current value
                val_str = f"{lr_str}{display_val:.{decimal}f}% <small style='color:#888'>{unit}</small>" if suffix_lr else f"{current_val:.{decimal}f} <small style='color:#888'>{unit}</small>"
                
                # Check for missing previous data
                if pd.isna(prev_val) or prev_val == 0:
                     badge_html = f"""
                    <div style='display:inline-flex; align-items:center; justify-content:flex-end;'>
                        <span>{val_str}</span>
                        <span style='background-color:#f0f0f0; color:#999; border-radius:12px; padding:2px 6px; font-size:10px; font-weight:700; margin-left:6px; white-space:nowrap;'>-%</span>
                    </div>
                    """
                     return badge_html
                
                delta = ((current_val - prev_val) / prev_val) * 100
                
                # Colors
                if inverse: # Lower is better
                    is_good = delta <= 0
                else: # Higher is better
                    is_good = delta >= 0
                    
                color = "#006442" if is_good else "#d62728"
                bg_color = "rgba(0, 100, 66, 0.1)" if is_good else "rgba(214, 39, 40, 0.1)"
                     
                sign = "+" if delta > 0 else ""
                
                badge_html = f"""
                <div style='display:inline-flex; align-items:center; justify-content:flex-end;'>
                    <span>{val_str}</span>
                    <span style='background-color:{bg_color}; color:{color}; border-radius:12px; padding:2px 6px; font-size:10px; font-weight:700; margin-left:6px; white-space:nowrap;'>{sign}{delta:.1f}%</span>
                </div>
                """
                return badge_html

            # Sort by date desc to get latest 2 records
            df_hist = df_p.sort_values('Test_Date', ascending=False).head(2)
            
            if df_hist.empty:
                st.info("선택한 선수의 데이터가 없습니다.")
            else:
                df_latest = df_hist.iloc[[0]]
                if len(df_hist) > 1:
                    df_prev = df_hist.iloc[[1]]
                else:
                    df_prev = pd.DataFrame() # No previous data
                latest_date = df_latest['Test_Date'].iloc[0]
                st.markdown(f"<div style='margin-bottom:10px; font-size:14px; color:grey;'>Latest Test: {latest_date}</div>", unsafe_allow_html=True)
                
                # 1. EUR
                eur_val = 0
                eur_prev = 0
                eur_status = "N/A"
                eur_color = "grey"
                
                if col_cmj in df_latest.columns and col_sj in df_latest.columns:
                    c_val = pd.to_numeric(df_latest[col_cmj], errors='coerce').fillna(0).iloc[0]
                    s_val = pd.to_numeric(df_latest[col_sj], errors='coerce').fillna(0).iloc[0]
                    
                    # Prev Data
                    c_prev = 0
                    s_prev = 0
                    if not df_prev.empty:
                        c_prev = pd.to_numeric(df_prev[col_cmj], errors='coerce').fillna(0).iloc[0]
                        s_prev = pd.to_numeric(df_prev[col_sj], errors='coerce').fillna(0).iloc[0]

                    if s_val > 0:
                        eur_val = c_val / s_val
                        if eur_val > 1.15: eur_status, eur_color = "Strength (근력 우세)", "#EF553B" # Red
                        elif eur_val >= 1.1: eur_status, eur_color = "Optimal (이상적)", "#00CC96" # Green
                        else: eur_status, eur_color = "Elastic (탄력적)", "#636EFA" # Blue
                    
                    if s_prev > 0:
                        eur_prev = c_prev / s_prev

                # 2. SLJ Asymmetry
                slj_asym = 0
                slj_status = "Balanced"
                slj_color = "#E6002D"
                col_slj_l = 'SLJ_Height_L_Imp_mom_'
                col_slj_r = 'SLJ_Height_R_Imp_mom_'
                
                if col_slj_l in df_latest.columns and col_slj_r in df_latest.columns:
                    l_val = df_latest[col_slj_l].fillna(0).iloc[0]
                    r_val = df_latest[col_slj_r].fillna(0).iloc[0]
                    max_slj = max(l_val, r_val)
                    if max_slj > 0:
                        slj_asym = ((r_val - l_val) / max_slj) * 100
                        if abs(slj_asym) > 10: 
                            slj_status, slj_color = f"Imbalance ({slj_asym:.1f}%)", "#d62728"
                        else:
                            slj_status, slj_color = f"Normal ({slj_asym:.1f}%)", "#E6002D"
                            
                    l_prev = df_prev[col_slj_l].fillna(0).iloc[0] if not df_prev.empty and col_slj_l in df_prev.columns else 0
                    r_prev = df_prev[col_slj_r].fillna(0).iloc[0] if not df_prev.empty and col_slj_r in df_prev.columns else 0
                    
                    max_slj_prev = max(l_prev, r_prev)
                    slj_asym_prev = 0
                    if max_slj_prev > 0:
                        slj_asym_prev = ((r_prev - l_prev) / max_slj_prev) * 100

                # 3. Strength Asymmetry (Hamstring Eccentric)
                ham_asym = 0
                ham_status = "Balanced"
                ham_color = "#E6002D"
                h_l = df_latest['Hamstring_Ecc_L'].fillna(0).iloc[0] if 'Hamstring_Ecc_L' in df_latest.columns else 0
                h_r = df_latest['Hamstring_Ecc_R'].fillna(0).iloc[0] if 'Hamstring_Ecc_R' in df_latest.columns else 0
                max_ham = max(h_l, h_r)
                if max_ham > 0:
                    ham_asym = ((h_r - h_l) / max_ham) * 100
                    if abs(ham_asym) > 15:
                        ham_status, ham_color = f"Risk ({ham_asym:.1f}%)", "#d62728"
                    else:
                        ham_status, ham_color = f"Stable ({ham_asym:.1f}%)", "#E6002D"

                # 4. Groin Risk (Hip Add/Abd Ratio)
                groin_status = "Good"
                groin_color = "#E6002D"
                add_l = df_latest['HipAdd_L'].fillna(0).iloc[0] if 'HipAdd_L' in df_latest.columns else 0
                abd_l = df_latest['HipAbd_L'].fillna(0).iloc[0] if 'HipAbd_L' in df_latest.columns else 0
                
                ratio_l = add_l / abd_l if abd_l > 0 else 0
                add_r = df_latest['HipAdd_R'].fillna(0).iloc[0] if 'HipAdd_R' in df_latest.columns else 0
                abd_r = df_latest['HipAbd_R'].fillna(0).iloc[0] if 'HipAbd_R' in df_latest.columns else 0
                ratio_r = add_r / abd_r if abd_r > 0 else 0
                
                if (ratio_l > 0 and ratio_l < 0.8) or (ratio_r > 0 and ratio_r < 0.8):
                    groin_status, groin_color = "High Risk (<0.8)", "#d62728"
                else:
                    groin_status, groin_color = "Stable (>0.8)", "#E6002D"

                # Layout: Row 1 (3 Columns)
                r1_c1, r1_c2, r1_c3 = st.columns(3)
                
                # --- Row 1, Box 1: Jump & Elasticity (Simplified) ---
                with r1_c1:
                    # RSI removed from here
                    metrics_1 = [
                        ("CMJ Height", format_delta_html(c_val, c_prev, "cm")),
                        ("Squat Jump", format_delta_html(s_val, s_prev, "cm")),
                        ("EUR", format_delta_html(eur_val, eur_prev, "ratio", decimal=2))
                    ]
                    st.markdown(create_detail_card("⚡ Jump & Elasticity", metrics_1, eur_status, eur_color), unsafe_allow_html=True)

                # --- Row 1, Box 2: Hamstring (Strength) ---
                with r1_c2:
                    # Get ISO Data
                    iso_l = df_latest['Hamstring_ISO_L'].fillna(0).iloc[0] if 'Hamstring_ISO_L' in df_latest.columns else 0
                    iso_r = df_latest['Hamstring_ISO_R'].fillna(0).iloc[0] if 'Hamstring_ISO_R' in df_latest.columns else 0
                    max_iso = max(iso_l, iso_r)
                    iso_asym = ((iso_r - iso_l) / max_iso * 100) if max_iso > 0 else 0
                    
                    # Ratio
                    ecc_avg = (h_l + h_r) / 2
                    iso_avg = (iso_l + iso_r) / 2
                    ham_ratio = ecc_avg / iso_avg if iso_avg > 0 else 0
                    
                    # PREVIOUS DATA
                    h_l_prev = df_prev['Hamstring_Ecc_L'].fillna(0).iloc[0] if not df_prev.empty and 'Hamstring_Ecc_L' in df_prev.columns else 0
                    h_r_prev = df_prev['Hamstring_Ecc_R'].fillna(0).iloc[0] if not df_prev.empty and 'Hamstring_Ecc_R' in df_prev.columns else 0
                    iso_l_prev = df_prev['Hamstring_ISO_L'].fillna(0).iloc[0] if not df_prev.empty and 'Hamstring_ISO_L' in df_prev.columns else 0
                    iso_r_prev = df_prev['Hamstring_ISO_R'].fillna(0).iloc[0] if not df_prev.empty and 'Hamstring_ISO_R' in df_prev.columns else 0
                    
                    ecc_avg_prev = (h_l_prev + h_r_prev) / 2
                    iso_avg_prev = (iso_l_prev + iso_r_prev) / 2
                    ham_ratio_prev = ecc_avg_prev / iso_avg_prev if iso_avg_prev > 0 else 0

                    max_iso_prev = max(iso_l_prev, iso_r_prev)
                    iso_asym_prev = ((iso_r_prev - iso_l_prev) / max_iso_prev * 100) if max_iso_prev > 0 else 0

                    max_ham_prev = max(h_l_prev, h_r_prev)
                    ham_asym_prev = ((h_r_prev - h_l_prev) / max_ham_prev * 100) if max_ham_prev > 0 else 0

                    # Ratio Status
                    if ham_ratio < 1.1: h_r_stat, h_r_col = "Ecc Deficit", "#d62728"
                    elif ham_ratio > 1.15: h_r_stat, h_r_col = "Iso Deficit", "#F37021"
                    else: h_r_stat, h_r_col = "Optimal", "#00CCA3"
                    
                    metrics_3 = [
                        ("Eccentric (L/R)", f"<div style='display:flex; justify-content:flex-end; white-space:nowrap;'>{format_delta_html(h_l, h_l_prev, 'N')} <span style='margin:0 5px; color:#ccc'>/</span> {format_delta_html(h_r, h_r_prev, 'N')}</div>"),
                        ("Ecc. Imbalance", format_delta_html(ham_asym, ham_asym_prev, "%", inverse=True, suffix_lr=True)),
                        ("Isometric (L/R)", f"<div style='display:flex; justify-content:flex-end; white-space:nowrap;'>{format_delta_html(iso_l, iso_l_prev, 'N')} <span style='margin:0 5px; color:#ccc'>/</span> {format_delta_html(iso_r, iso_r_prev, 'N')}</div>"),
                        ("Iso. Imbalance", format_delta_html(iso_asym, iso_asym_prev, "%", inverse=True, suffix_lr=True)),
                        ("Ecc/Iso Ratio", format_delta_html(ham_ratio, ham_ratio_prev, "ratio", decimal=2)) 
                    ]
                    st.markdown(create_detail_card("🦵 Hamstring Profile", metrics_3, h_r_stat, h_r_col), unsafe_allow_html=True)
                    
                # --- Row 1, Box 3: Groin (Strength) ---
                with r1_c3:
                    add_asym = ((add_r - add_l) / max(add_l, add_r) * 100) if max(add_l, add_r) > 0 else 0
                    abd_asym = ((abd_r - abd_l) / max(abd_l, abd_r) * 100) if max(abd_l, abd_r) > 0 else 0
                    
                    # Prev Groin
                    add_l_prev = df_prev['HipAdd_L'].fillna(0).iloc[0] if not df_prev.empty and 'HipAdd_L' in df_prev.columns else 0
                    add_r_prev = df_prev['HipAdd_R'].fillna(0).iloc[0] if not df_prev.empty and 'HipAdd_R' in df_prev.columns else 0
                    abd_l_prev = df_prev['HipAbd_L'].fillna(0).iloc[0] if not df_prev.empty and 'HipAbd_L' in df_prev.columns else 0
                    abd_r_prev = df_prev['HipAbd_R'].fillna(0).iloc[0] if not df_prev.empty and 'HipAbd_R' in df_prev.columns else 0
                    
                    ratio_l_prev = add_l_prev / abd_l_prev if abd_l_prev > 0 else 0
                    ratio_r_prev = add_r_prev / abd_r_prev if abd_r_prev > 0 else 0
                    
                    max_add_prev = max(add_l_prev, add_r_prev)
                    add_asym_prev = ((add_r_prev - add_l_prev) / max_add_prev * 100) if max_add_prev > 0 else 0

                    abd_asym_prev = ((abd_r_prev - abd_l_prev) / max(abd_l_prev, abd_r_prev) * 100) if max(abd_l_prev, abd_r_prev) > 0 else 0

                    metrics_4 = [
                        ("Adduction (L/R)", f"<div style='display:flex; justify-content:flex-end; white-space:nowrap;'>{format_delta_html(add_l, add_l_prev, 'N')} <span style='margin:0 5px; color:#ccc'>/</span> {format_delta_html(add_r, add_r_prev, 'N')}</div>"),
                        ("Add. Imbalance", format_delta_html(add_asym, add_asym_prev, "", inverse=True, suffix_lr=True)),
                        ("Abduction (L/R)", f"<div style='display:flex; justify-content:flex-end; white-space:nowrap;'>{format_delta_html(abd_l, abd_l_prev, 'N')} <span style='margin:0 5px; color:#ccc'>/</span> {format_delta_html(abd_r, abd_r_prev, 'N')}</div>"),
                        ("Abd. Imbalance", format_delta_html(abd_asym, abd_asym_prev, "", inverse=True, suffix_lr=True)),
                        ("Add/Abd Ratio", f"<div style='display:flex; justify-content:flex-end; white-space:nowrap;'>{format_delta_html(ratio_l, ratio_l_prev, 'ratio', decimal=2)} <span style='margin:0 5px; color:#ccc'>/</span> {format_delta_html(ratio_r, ratio_r_prev, 'ratio', decimal=2)}</div>")
                    ]
                    st.markdown(create_detail_card("🛡️ Groin Profile", metrics_4, groin_status, groin_color), unsafe_allow_html=True)
            
                st.markdown("<br>", unsafe_allow_html=True) # Spacer

                # Layout: Row 2 (3 Columns)
                r2_c1, r2_c2, r2_c3 = st.columns(3)

                # --- Row 2, Box 1: Other Jump Data ---
                with r2_c1:
                    # New Metrics: CMJ P1, P2, Landing, HopTest
                    rsi_val = df_latest['CMJ_RSI_mod_Imp_mom_'].fillna(0).iloc[0] if 'CMJ_RSI_mod_Imp_mom_' in df_latest.columns else 0
                    rsi_prev = df_prev['CMJ_RSI_mod_Imp_mom_'].fillna(0).iloc[0] if not df_prev.empty and 'CMJ_RSI_mod_Imp_mom_' in df_prev.columns else 0

                    p1_val = df_latest['CMJ_ConcentricImpulseP1'].fillna(0).iloc[0] if 'CMJ_ConcentricImpulseP1' in df_latest.columns else 0
                    p2_val = df_latest['CMJ_ConcentricImpulseP2'].fillna(0).iloc[0] if 'CMJ_ConcentricImpulseP2' in df_latest.columns else 0
                    land_val = df_latest['CMJ_PeakLandingForce'].fillna(0).iloc[0] if 'CMJ_PeakLandingForce' in df_latest.columns else 0
                    hop_rsi = df_latest['HopTest_MeanRSI'].fillna(0).iloc[0] if 'HopTest_MeanRSI' in df_latest.columns else 0
                    
                    # Prev
                    p1_prev = df_prev['CMJ_ConcentricImpulseP1'].fillna(0).iloc[0] if not df_prev.empty and 'CMJ_ConcentricImpulseP1' in df_prev.columns else 0
                    p2_prev = df_prev['CMJ_ConcentricImpulseP2'].fillna(0).iloc[0] if not df_prev.empty and 'CMJ_ConcentricImpulseP2' in df_prev.columns else 0
                    land_prev = df_prev['CMJ_PeakLandingForce'].fillna(0).iloc[0] if not df_prev.empty and 'CMJ_PeakLandingForce' in df_prev.columns else 0
                    hop_prev = df_prev['HopTest_MeanRSI'].fillna(0).iloc[0] if not df_prev.empty and 'HopTest_MeanRSI' in df_prev.columns else 0

                    metrics_jump_detail = [
                        ("CMJ RSI-mod", format_delta_html(rsi_val, rsi_prev, "index")),
                        ("CMJ P1 %", format_delta_html(p1_val, p1_prev, "%")),
                        ("CMJ P2 %", format_delta_html(p2_val, p2_prev, "%")),
                        ("CMJ Landing Force", format_delta_html(land_val, land_prev, "N")),
                        ("Hop Test Mean RSI", format_delta_html(hop_rsi, hop_prev, ""))
                    ]
                    st.markdown(create_detail_card("📊 Other Jump Data", metrics_jump_detail, "Info", "#999"), unsafe_allow_html=True)

                # --- Row 2, Box 2: Hip Flexion Kicker ---
                with r2_c2:
                    hf_l = df_latest['HipFlexion_Kicker_L'].fillna(0).iloc[0] if 'HipFlexion_Kicker_L' in df_latest.columns else 0
                    hf_r = df_latest['HipFlexion_Kicker_R'].fillna(0).iloc[0] if 'HipFlexion_Kicker_R' in df_latest.columns else 0
                    hf_imb = df_latest['HipFlexion_Kicker_Imbalance'].fillna(0).iloc[0] if 'HipFlexion_Kicker_Imbalance' in df_latest.columns else 0

                    hf_l_prev = df_prev['HipFlexion_Kicker_L'].fillna(0).iloc[0] if not df_prev.empty and 'HipFlexion_Kicker_L' in df_prev.columns else 0
                    hf_r_prev = df_prev['HipFlexion_Kicker_R'].fillna(0).iloc[0] if not df_prev.empty and 'HipFlexion_Kicker_R' in df_prev.columns else 0
                    hf_imb_prev = df_prev['HipFlexion_Kicker_Imbalance'].fillna(0).iloc[0] if not df_prev.empty and 'HipFlexion_Kicker_Imbalance' in df_prev.columns else 0
                    
                    hf_status = "Risk" if abs(hf_imb) > 15 else "Balanced"
                    hf_color = "#d62728" if abs(hf_imb) > 15 else "#E6002D"

                    metrics_hf = [
                        ("Left Force", format_delta_html(hf_l, hf_l_prev, "N")),
                        ("Right Force", format_delta_html(hf_r, hf_r_prev, "N")),
                        ("Imbalance", format_delta_html(hf_imb, hf_imb_prev, "%", inverse=True, suffix_lr=True))
                    ]
                    st.markdown(create_detail_card("🦵 Hip Flexion Kicker", metrics_hf, hf_status, hf_color), unsafe_allow_html=True)

                # --- Row 2, Box 3: Shoulder Profile ---
                with r2_c3:
                    ir_l = df_latest['ShoulderIR_L'].fillna(0).iloc[0] if 'ShoulderIR_L' in df_latest.columns else 0
                    ir_r = df_latest['ShoulderIR_R'].fillna(0).iloc[0] if 'ShoulderIR_R' in df_latest.columns else 0
                    ir_imb = df_latest['ShoulderIR_Imbalance'].fillna(0).iloc[0] if 'ShoulderIR_Imbalance' in df_latest.columns else 0

                    er_l = df_latest['ShoulderER_L'].fillna(0).iloc[0] if 'ShoulderER_L' in df_latest.columns else 0
                    er_r = df_latest['ShoulderER_R'].fillna(0).iloc[0] if 'ShoulderER_R' in df_latest.columns else 0
                    try:
                        er_imb = df_latest['ShoulderER_Imbalance'].fillna(0).iloc[0] if 'ShoulderER_Imbalance' in df_latest.columns else 0
                    except: er_imb = 0

                    # Prev
                    ir_l_prev = df_prev['ShoulderIR_L'].fillna(0).iloc[0] if not df_prev.empty and 'ShoulderIR_L' in df_prev.columns else 0
                    ir_r_prev = df_prev['ShoulderIR_R'].fillna(0).iloc[0] if not df_prev.empty and 'ShoulderIR_R' in df_prev.columns else 0
                    er_l_prev = df_prev['ShoulderER_L'].fillna(0).iloc[0] if not df_prev.empty and 'ShoulderER_L' in df_prev.columns else 0
                    er_r_prev = df_prev['ShoulderER_R'].fillna(0).iloc[0] if not df_prev.empty and 'ShoulderER_R' in df_prev.columns else 0

                    sh_status = "Balanced"
                    sh_color = "#E6002D"

                    metrics_sh = [
                        ("IR (L/R)", f"<div style='display:flex; justify-content:flex-end; white-space:nowrap;'>{format_delta_html(ir_l, ir_l_prev, 'N')} <span style='margin:0 5px; color:#ccc'>/</span> {format_delta_html(ir_r, ir_r_prev, 'N')}</div>"),
                        ("ER (L/R)", f"<div style='display:flex; justify-content:flex-end; white-space:nowrap;'>{format_delta_html(er_l, er_l_prev, 'N')} <span style='margin:0 5px; color:#ccc'>/</span> {format_delta_html(er_r, er_r_prev, 'N')}</div>"),
                        ("IR Imbalance", format_delta_html(ir_imb, 0, "%", inverse=True, suffix_lr=True)), # Prev not tracked easily for now
                        ("ER Imbalance", format_delta_html(er_imb, 0, "%", inverse=True, suffix_lr=True))
                    ]
                    st.markdown(create_detail_card("💪 Shoulder Profile", metrics_sh, sh_status, sh_color), unsafe_allow_html=True)
            
            st.divider()

            # --- Trends Charts ---
            st.markdown("<h3 style='font-size: 24px; font-weight: 700; color: #111; margin-top: 30px; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;'>📈 트렌드 분석 (Trend Analysis)</h3>", unsafe_allow_html=True)
            st.markdown("---")
            
            def create_trend_chart(df, metrics_dict, title, chart_type='line'):
                df_chart = df.copy()
                try:
                    df_chart['Date_Str'] = df_chart['Test_Date'].dt.strftime('%Y-%m-%d')
                except:
                    df_chart['Date_Str'] = df_chart['Test_Date'].astype(str).str[:10]
                
                df_chart = df_chart.sort_values('Test_Date')
                fig = go.Figure()
                has_data = False
                colors = ['#E6002D', '#F37021', '#1f77b4', '#d62728'] # Yongin Main Color
                
                valid_cols = []
                for label, col in metrics_dict.items():
                    if col in df.columns and not df[col].isnull().all():
                        valid_cols.append((label, col))

                for i, (label, col) in enumerate(valid_cols):
                    if chart_type == 'bar':
                        fig.add_trace(go.Bar(
                            x=df_chart['Date_Str'],  
                            y=df[col], 
                            name=label,
                            marker_color=colors[i % len(colors)]
                        ))
                    else:
                        fig.add_trace(go.Scatter(
                            x=df_chart['Date_Str'], 
                            y=df[col], 
                            name=label, 
                            mode='lines+markers',
                            line=dict(color=colors[i % len(colors)])
                        ))
                    has_data = True
                
                layout_args = dict(
                    title=dict(text=title, font=dict(size=14)),
                    hovermode="x unified", 
                    legend=dict(orientation="h", y=1.15, x=1, xanchor='right', bgcolor='rgba(255,255,255,0.5)'),
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis=dict(
                        tickformat="%Y-%m-%d", 
                        type='category'
                    )
                )
                
                if chart_type == 'bar':
                    layout_args['barmode'] = 'group'
                    
                fig.update_layout(**layout_args)
                fig.update_layout(margin=dict(t=50))

                if has_data:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No data for {title}")

            def create_strength_diverging_chart(df, col_l, col_r, title):
                df_chart = df.sort_values('Test_Date', ascending=True).copy()
                try:
                    df_chart['Date_Str'] = df_chart['Test_Date'].dt.strftime('%Y-%m-%d')
                except:
                    df_chart['Date_Str'] = df_chart['Test_Date'].astype(str)

                l_vals = df_chart[col_l].fillna(0)
                r_vals = df_chart[col_r].fillna(0)
                l_plot = l_vals * -1 # Negative for Left
                
                max_val = df_chart[[col_l, col_r]].max(axis=1).replace(0, 1)
                imbalance = ((r_vals - l_vals) / max_val) * 100
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=df_chart['Date_Str'], x=l_plot, orientation='h', name='Left',
                    marker_color='#56B4E9', hovertext=l_vals, hovertemplate='Left: %{hovertext:.1f} N<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    y=df_chart['Date_Str'], x=r_vals, orientation='h', name='Right',
                    marker_color='#F37021', hovertemplate='Right: %{x:.1f} N<extra></extra>'
                ))
                fig.add_trace(go.Scatter(
                    y=df_chart['Date_Str'], x=imbalance, xaxis='x2', mode='markers', name='Imbalance %',
                    marker=dict(color='black', size=8, symbol='circle'), hovertemplate='Imbalance: %{x:.1f}%<extra></extra>'
                ))
                
                fig.update_layout(
                    title=dict(text=title, font=dict(size=14)), barmode='relative',
                    xaxis=dict(range=[-1000, 1000], title='Force (N)', zeroline=True, zerolinecolor='grey'),
                    xaxis2=dict(range=[-50, 50], title='Imbalance (%)', overlaying='x', side='top', zeroline=True),
                    yaxis=dict(type='category'), legend=dict(orientation="h", y=-0.15, x=0.5, xanchor='center'),
                    margin=dict(t=80, b=50, l=50, r=50), height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("### ⚡ 파워 분석 (Power Trends)")
            p_c1, p_c2, p_c3 = st.columns(3)
            
            with p_c1:
                create_trend_chart(df_p, {'CMJ': col_cmj}, "CMJ Height", 'line')
            with p_c2:
                create_trend_chart(df_p, {'SquatJ': col_sj}, "Squat Jump Height", 'line')
            with p_c3:
                # Replaced SLJ with HopTest
                create_trend_chart(df_p, {'HopTest RSI': 'HopTest_MeanRSI'}, "HopTest Mean RSI", 'line')

            # 2. Strength Metrics (3x2 Grid)
            st.markdown("### 💪 근력 분석 (Strength Metrics)")
            
            # Create Ratio Columns for Trend
            if 'Hamstring_Ecc_L' in df_p.columns and 'Hamstring_ISO_L' in df_p.columns:
                 ecc_sum = df_p['Hamstring_Ecc_L'].fillna(0) + df_p['Hamstring_Ecc_R'].fillna(0)
                 iso_sum = df_p['Hamstring_ISO_L'].fillna(0) + df_p['Hamstring_ISO_R'].fillna(0)
                 df_p['Hamstring_Ratio_Trend'] = np.where(iso_sum > 0, ecc_sum / iso_sum, 0)
            
            if 'HipAdd_L' in df_p.columns and 'HipAbd_L' in df_p.columns:
                 add_sum = df_p['HipAdd_L'].fillna(0) + df_p['HipAdd_R'].fillna(0)
                 abd_sum = df_p['HipAbd_L'].fillna(0) + df_p['HipAbd_R'].fillna(0)
                 df_p['Hip_Ratio_Trend'] = np.where(abd_sum > 0, add_sum / abd_sum, 0)

            def create_ratio_dot_chart(df, col_ratio, title, safe_min, safe_max, x_range=[0, 1.5]):
                if df.empty: return
                df_chart = df.sort_values('Test_Date', ascending=True).copy()
                try: df_chart['Date_Str'] = df_chart['Test_Date'].dt.strftime('%Y-%m-%d')
                except: df_chart['Date_Str'] = df_chart['Test_Date'].astype(str)
                
                def get_color(val):
                    if val >= safe_min and val <= safe_max: return '#006442' 
                    if val < safe_min * 0.9 or val > safe_max * 1.1: return '#d62728' 
                    return '#F37021'
                
                df_chart['Color'] = df_chart[col_ratio].apply(get_color)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=df_chart['Date_Str'], x=df_chart[col_ratio], mode='markers+lines',
                    marker=dict(color=df_chart['Color'], size=10, symbol='circle', line=dict(width=1, color='white')),
                    line=dict(color='#cccccc', width=1, dash='dot'), hovertemplate='Ratio: %{x:.2f}<br>Date: %{y}<extra></extra>'
                ))
                fig.add_vrect(x0=x_range[0], x1=safe_min, fillcolor="red", opacity=0.05, layer="below", line_width=0)
                fig.add_vrect(x0=safe_min, x1=safe_max, fillcolor="green", opacity=0.1, layer="below", line_width=0)
                fig.add_vrect(x0=safe_max, x1=x_range[1], fillcolor="red", opacity=0.05, layer="below", line_width=0)
                
                fig.update_layout(
                    title=dict(text=title, font=dict(size=14)), yaxis=dict(type='category', title=None),
                    xaxis=dict(title='Ratio', tickformat='.2f', range=x_range, dtick=0.1),
                    margin=dict(t=50, b=50, l=50, r=20), height=400, showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

            # --- Row 1: Hamstring ---
            r1_c1, r1_c2, r1_c3 = st.columns(3)
            with r1_c1:
                create_strength_diverging_chart(df_p, 'Hamstring_Ecc_L', 'Hamstring_Ecc_R', "Hamstring Eccentric (L/R)")
            with r1_c2:
                create_strength_diverging_chart(df_p, 'Hamstring_ISO_L', 'Hamstring_ISO_R', "Hamstring Isometric (L/R)")
            with r1_c3:
                create_ratio_dot_chart(df_p, 'Hamstring_Ratio_Trend', 'Hamstring Ratio Trend (Ecc/Iso)', 1.1, 1.15, [0.8, 1.2])

            # --- Row 2: Hip ---
            r2_c1, r2_c2, r2_c3 = st.columns(3)
            with r2_c1:
                 create_strength_diverging_chart(df_p, 'HipAdd_L', 'HipAdd_R', "Hip Adduction (L/R)")
            with r2_c2:
                 create_strength_diverging_chart(df_p, 'HipAbd_L', 'HipAbd_R', "Hip Abduction (L/R)")
            with r2_c3:
                 create_ratio_dot_chart(df_p, 'Hip_Ratio_Trend', 'Hip Ratio Trend (Add/Abd)', 0.9, 1.0, [0.5, 1.5])
                 
            # --- Row 3: Hip Flexion & Shoulder ---
            r3_c1, r3_c2, r3_c3 = st.columns(3)
            with r3_c1:
                 create_strength_diverging_chart(df_p, 'HipFlexion_Kicker_L', 'HipFlexion_Kicker_R', "Hip Flexion Kicker (L/R)")
            with r3_c2:
                 create_strength_diverging_chart(df_p, 'ShoulderIR_L', 'ShoulderIR_R', "Shoulder IR (L/R)")
            with r3_c3:
                 create_strength_diverging_chart(df_p, 'ShoulderER_L', 'ShoulderER_R', "Shoulder ER (L/R)")

            st.divider()

# --- VIEW: Insight Analysis ---
elif st.session_state['yf_view_mode'] == 'Insight Analysis':
    from utils import analysis_utils

    if df_global.empty:
        st.warning("No data available.")
        st.stop()
        
    mask = (df_global['Test_Date'] >= start_date) & (df_global['Test_Date'] <= end_date)
    df_insight = df_global.loc[mask]
    
    if df_insight.empty:
        st.warning(f"No data found between {start_date} and {end_date}.")
        st.stop()
        
    df_insight = calculate_derived_cols(df_insight)

    with st.container():
        st.markdown("""
        <style>
        .mode-select-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; margin-bottom: 20px; }
        </style>
        <div class='mode-select-box'>
            <h4 style='margin:0; padding-bottom:10px; color:#E6002D;'>🔍 분석 모드 선택 (Analysis Mode)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        an_mode = st.radio(
            "분석 모드를 선택하세요:", 
            ["피지컬 종합 리포트 (Physical Report)", "심층 분석 (Deep Analysis)", "전후 비교 (Development Tracker)"], 
            horizontal=True,
            label_visibility="collapsed"
        )
    
    st.markdown("---")

    # 1. Periodic Diagnosis Mode
    if an_mode == "피지컬 종합 리포트 (Physical Report)":
        st.markdown("<h3 style='font-size: 24px; font-weight: 700; color: #111; margin-top: 20px; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;'>📊 팀 피지컬 리포트 (Team Status)</h3>", unsafe_allow_html=True)
        
        tier_metrics = {
            'Power': [
                'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_insight.columns else 'CMJ_Height_Imp_mom',
                'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_insight.columns else 'SquatJ_Height_Imp_mom',
                'CMJ_RSI_mod_Imp_mom_' if 'CMJ_RSI_mod_Imp_mom_' in df_insight.columns else 'CMJ_RSI_mod_Imp_mom',
                'CMJ_ConcentricImpulseP1', 'CMJ_ConcentricImpulseP2', 'CMJ_PeakLandingForce', 'HopTest_MeanRSI'
            ],
            'Strength': [
                'Hamstring_Ecc_L', 'Hamstring_Ecc_R', 'Hamstring_ISO_L', 'Hamstring_ISO_R',
                'HipAdd_L', 'HipAdd_R', 'HipAbd_L', 'HipAbd_R',
                'HipFlexion_Kicker_L', 'HipFlexion_Kicker_R',
                'ShoulderIR_L', 'ShoulderIR_R', 'ShoulderER_L', 'ShoulderER_R'
            ]
        }
        
        tier_df = analysis_utils.calculate_physical_tier(df_insight, tier_metrics)
        
        if not tier_df.empty:
            c_top1, c_top2 = st.columns([1, 1])
            with c_top1:
                fig_tier = analysis_utils.plot_tier_distribution(tier_df)
                if fig_tier: st.plotly_chart(fig_tier, use_container_width=True)
                
            with c_top2:
                st.markdown("##### 🥇 종합 Top 5 (Overall)")
                top5_overall = tier_df.sort_values('Physical_Score', ascending=False).head(5)
                st.dataframe(top5_overall[['Name', 'Physical_Score', 'Tier']].style.format({'Physical_Score': '{:.1f}'}), hide_index=True, use_container_width=True)
                
                st.markdown("""
                <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 12px; color: #555;'>
                    <i><b>Physical Tier Score</b> = (Power Rank + Strength Rank) / 2</i>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            
            # 2. Category Leaders
            st.markdown("##### 🥈 부문별 리더 (Category Leaders)")
            cat1, cat2, cat3 = st.columns(3)
            
            with cat1:
                 st.markdown("**⚡ Power Rank**")
                 if 'Power_Score' in tier_df.columns:
                     top5_pow = tier_df.sort_values('Power_Score', ascending=False).head(5)
                     st.dataframe(top5_pow[['Name', 'Power_Score']].style.format({'Power_Score': '{:.1f}'}), hide_index=True, use_container_width=True)
            
            with cat2:
                 st.markdown("**💪 Strength Rank**")
                 if 'Strength_Score' in tier_df.columns:
                     top5_str = tier_df.sort_values('Strength_Score', ascending=False).head(5)
                     st.dataframe(top5_str[['Name', 'Strength_Score']].style.format({'Strength_Score': '{:.1f}'}), hide_index=True, use_container_width=True)

            with cat3:
                 st.markdown("**⚖️ Balance Rank (Disabled)**")
                 st.info("SLJ data removed.")

            st.markdown("---")
            with st.expander("📋 View Full Tier List"):
                 st.dataframe(tier_df[['Name', 'Tier', 'Physical_Score']].sort_values('Physical_Score', ascending=False), use_container_width=True)
        else:
            st.info("티어 산출을 위한 데이터가 부족합니다.")

    # 2. Development Tracker
    elif an_mode == "전후 비교 (Development Tracker)":
        st.markdown("<h3 style='font-size: 24px; font-weight: 700; color: #111; margin-top: 20px; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;'>📈 Pre-Post Development Analysis</h3>", unsafe_allow_html=True)
        
        valid_dates = df_global['Test_Date'].dropna().unique()
        col_dates = sorted(valid_dates)
        
        if len(col_dates) < 2:
            st.warning("비교를 위해서는 최소 2개 이상의 측정 날짜가 필요합니다.")
        else:
            c_d1, c_d2 = st.columns(2)
            with c_d1: date_pre = st.selectbox("기준 시점 (Pre)", col_dates, index=0)
            with c_d2: date_post = st.selectbox("비교 시점 (Post)", col_dates, index=len(col_dates)-1)
            
            if date_pre == date_post:
                st.warning("서로 다른 날짜를 선택해주세요.")
            else:
                df_pre = df_global[df_global['Test_Date'] == date_pre]
                df_post = df_global[df_global['Test_Date'] == date_post]
                
                st.markdown("##### 🔧 분석 지표 선택")
                delta_metrics_all = {
                    "Power: CMJ Height": "CMJ_Height_Imp_mom_",
                    "Power: Squat Jump Height": "SquatJ_Height_Imp_mom_",
                    "Power: CMJ RSI-mod": "CMJ_RSI_mod_Imp_mom_"
                }
                delta_mode = st.selectbox("분석 지표를 선택하세요", list(delta_metrics_all.keys()))
                target_metric = delta_metrics_all.get(delta_mode)
                delta_metrics = {delta_mode: target_metric} if target_metric else {}
                
                delta_df = analysis_utils.calculate_pre_post_delta(df_pre, df_post, delta_metrics)
                
                if not delta_df.empty:
                    st.markdown(f"#### 🔍 변화량 분석 (Delta %): {date_pre} -> {date_post}")
                    fig_d = analysis_utils.plot_delta_chart(delta_df, delta_mode)
                    if fig_d: st.plotly_chart(fig_d, use_container_width=True)
                else:
                    st.info("두 시점 간 공통 측정 선수가 없습니다.")

    # 3. Deep Dive
    elif an_mode == "심층 분석 (Deep Analysis)":
        col_cmj = 'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_insight.columns else 'CMJ_Height_Imp_mom'
        col_sj  = 'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_insight.columns else 'SquatJ_Height_Imp_mom'
        
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #111; margin-top: 30px; margin-bottom: 10px;'>1. Eccentric Utilization Ratio (EUR)</h3>", unsafe_allow_html=True)
        
        with st.expander("ℹ️ EUR 지표란?"):
            st.markdown("""
            **신장 단축 주기 효율성 (EUR)** = CMJ / Squat Jump
            - **< 1.1**: **Elastic (탄력적)**
            - **1.1 ~ 1.15**: **Optimal (이상적)**
            - **> 1.15**: **Strength (근력 우세)**
            """)

        eur_df = analysis_utils.calculate_eur(df_insight, col_cmj, col_sj)
        if not eur_df.empty:
            c_chart, c_list = st.columns([2.5, 1])
            with c_chart:
                fig_eur = analysis_utils.plot_eur(eur_df, col_cmj, col_sj)
                if fig_eur: st.plotly_chart(fig_eur, use_container_width=True)
            with c_list:
                st.markdown("##### 📋 Status Summary")
                if 'Status' in eur_df.columns:
                    for status_label in ['Elastic (< 1.1)', 'Optimal (1.1 - 1.15)', 'Strength (> 1.15)']:
                        subset = eur_df[eur_df['Status'] == status_label]
                        count = len(subset)
                        if count > 0:
                            color = "blue" if "Elastic" in status_label else "green" if "Optimal" in status_label else "red"
                            st.markdown(f":{color}[**{status_label}**] ({count}명)")
                            st.caption(", ".join(subset['Name'].tolist()))
        
        st.divider()
        st.divider()
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #111; margin-top: 30px; margin-bottom: 10px;'>2. 불균형 요주의 리스트 (Limb Asymmetry Watchlist)</h3>", unsafe_allow_html=True)
        asy_metric = st.selectbox("비대칭 분석 지표 선택", 
                                  ["Hamstring Eccentric", "Hamstring Isometric", "Hip Adduction", "Hip Abduction", 
                                   "Hip Flexion Kicker", "Shoulder IR", "Shoulder ER"])
        
        if asy_metric == "Hamstring Eccentric":
            col_l, col_r, ref_threshold = 'Hamstring_Ecc_L', 'Hamstring_Ecc_R', 15
        elif asy_metric == "Hamstring Isometric":
            col_l, col_r, ref_threshold = 'Hamstring_ISO_L', 'Hamstring_ISO_R', 15
        elif asy_metric == "Hip Adduction":
            col_l, col_r, ref_threshold = 'HipAdd_L', 'HipAdd_R', 15
        elif asy_metric == "Hip Abduction":
            col_l, col_r, ref_threshold = 'HipAbd_L', 'HipAbd_R', 15
        elif asy_metric == "Hip Flexion Kicker":
            col_l, col_r, ref_threshold = 'HipFlexion_Kicker_L', 'HipFlexion_Kicker_R', 15
        elif asy_metric == "Shoulder IR":
            col_l, col_r, ref_threshold = 'ShoulderIR_L', 'ShoulderIR_R', 15
        elif asy_metric == "Shoulder ER":
            col_l, col_r, ref_threshold = 'ShoulderER_L', 'ShoulderER_R', 15

        asy_df = analysis_utils.calculate_asymmetry(df_insight, col_l, col_r)
        if not asy_df.empty:
            c_chart, c_list = st.columns([2.5, 1])
            with c_chart:
                fig_lolly = analysis_utils.plot_asymmetry_lollipop(asy_df, threshold=ref_threshold)
                if fig_lolly: st.plotly_chart(fig_lolly, use_container_width=True)
            with c_list:
                st.markdown("##### 📋 Imbalance Watchlist")
                risk_df = asy_df[asy_df['Asymmetry'].abs() > ref_threshold].sort_values('Asymmetry', key=abs, ascending=False)
                if not risk_df.empty:
                    st.markdown(f":red[**High Risk ({len(risk_df)}명)**]")
                    for _, row in risk_df.iterrows(): st.caption(f"**{row['Name']}**: {row['Asymmetry']:.1f}%")

        st.divider()
        st.divider()
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #111; margin-top: 30px; margin-bottom: 10px;'>3. Groin Risk (Add/Abd Ratio)</h3>", unsafe_allow_html=True)
        groin_df = analysis_utils.calculate_groin_risk(df_insight, 'HipAdd_L', 'HipAdd_R', 'HipAbd_L', 'HipAbd_R')
        if not groin_df.empty:
            c_chart, c_list = st.columns([2.5, 1])
            with c_chart:
                fig_groin = analysis_utils.plot_groin_risk(groin_df)
                if fig_groin: st.plotly_chart(fig_groin, use_container_width=True)
            with c_list:
                st.markdown("##### 📋 Risk Summary")
                for status_label in ['High Risk (< 0.80)', 'Watch (0.80 - 0.90)']:
                     subset = groin_df[groin_df['Ratio'].apply(lambda x: 'High' if x < 0.8 else 'Watch' if x < 0.9 else 'Good') == status_label.split()[0]]
                     if not subset.empty:
                         st.markdown(f":red[**{status_label}**] ({len(subset)}명)")
                         for _, row in subset.iterrows(): st.caption(f"**{row['Name']}**: {row['Ratio']:.2f}")

        st.divider()
        st.divider()
        st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #111; margin-top: 30px; margin-bottom: 10px;'>4. Hamstring Profiling (Functional Ratio)</h3>", unsafe_allow_html=True)
        if 'Hamstring_ISO_L' in df_insight.columns:
            df_insight['H_ISO_Mean'] = df_insight[['Hamstring_ISO_L','Hamstring_ISO_R']].mean(axis=1)
            df_insight['H_Ecc_Mean'] = df_insight[['Hamstring_Ecc_L','Hamstring_Ecc_R']].mean(axis=1)
            
            # Calculate Functional Ratio for Risk Summary
            df_insight['Ham_Ratio'] = df_insight['H_Ecc_Mean'] / df_insight['H_ISO_Mean']
            
            c_chart, c_list = st.columns([2.5, 1])
            with c_chart:
                fig_ham = analysis_utils.plot_hamstring_functional_ratio(df_insight, 'H_ISO_Mean', 'H_Ecc_Mean', title="Hamstring Profile")
                st.plotly_chart(fig_ham, use_container_width=True)
            with c_list:
                st.markdown("##### 📋 Risk Summary")
                # Criteria from Player Card: < 1.1 (Ecc Deficit), > 1.15 (Iso Deficit)
                for status_label in ['Ecc Deficit (< 1.1)', 'Iso Deficit (> 1.15)']:
                    if 'Ecc' in status_label:
                        subset = df_insight[df_insight['Ham_Ratio'] < 1.1]
                        color = 'red'
                    else:
                        subset = df_insight[df_insight['Ham_Ratio'] > 1.15]
                        color = 'orange'
                        
                    if not subset.empty:
                        st.markdown(f":{color}[**{status_label}**] ({len(subset)}명)")
                        for _, row in subset.iterrows(): st.caption(f"**{row['Name']}**: {row['Ham_Ratio']:.2f}")
