# --- Page Config ---
import streamlit as st
st.set_page_config(layout="wide", page_title="Gangwon FC Dashboard", page_icon="⚽")

# --- Authentication Logic (Gatekeeper) ---
from utils import auth

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def handle_login():
    username = st.session_state.get('gangwon_user', '')
    password = st.session_state.get('gangwon_pass', '')
    # Check for 'gangwon' role or 'admin'
    role = auth.authenticate_user(username, password, required_roles=['gangwon', 'admin'])
    
    if role:
        st.session_state['logged_in'] = True
        st.session_state['role'] = role
        st.session_state['current_user'] = username
    else:
        st.session_state['login_error'] = "인증 실패 (Gangwon/Admin Only)"

# Case 1: Not Logged In (Direct Access)
if not st.session_state['logged_in']:
    auth.inject_custom_css()
    
    st.markdown("""
    <style>
        .login-super { display: flex; justify-content: center; margin-top: 100px; }
    </style>
    <div class='login-super'><h2 style='text-align: center; color: #006442;'>🐻 Gangwon FC Login</h2></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if 'login_error' in st.session_state:
            st.error(st.session_state['login_error'])
            del st.session_state['login_error']
            
        st.text_input("ID", key="gangwon_user")
        st.text_input("PW", type="password", key="gangwon_pass", on_change=handle_login)
        st.button("Login", on_click=handle_login, type="primary", use_container_width=True)
    st.stop()

# Case 2: Logged In but Wrong Role (e.g. K-League user trying to access Gangwon)
if st.session_state.get('role') not in ['gangwon', 'admin']:
    auth.inject_custom_css()
    st.error("Access Denied")
    st.stop()

# --- Main App Logic ---
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from gangwon_fc.utils import gangwon_data_loader as data_loader
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
        color: #006442; /* Gangwon Green */
        font-weight: 800;
    }
    
    /* Navigation Buttons */
    .nav-btn-active { border: 2px solid #F37021 !important; color: #F37021 !important; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
# Use Session State to track current view
if 'gw_view_mode' not in st.session_state:
    st.session_state['gw_view_mode'] = 'Team Dashboard'

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
            st.image("gangwon_fc/gangwon_logo.png", use_container_width=True)
        except:
            pass
    with h_col2:
        st.markdown("<h3 style='margin-top: 10px; margin-bottom: 0;'>Gangwon FC</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # --- Global Date Filter (Sidebar) ---
    st.markdown("### 📅 DATE FILTER")
    start_date, end_date = st.slider(
        "기간 선택",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📊 DASHBOARD")
    if st.button("팀 대시보드 (Team)", use_container_width=True, type="primary" if st.session_state['gw_view_mode'] == 'Team Dashboard' else "secondary"):
        st.session_state['gw_view_mode'] = 'Team Dashboard'
        st.rerun()
        
    if st.button("선수 상세 분석 (Player)", use_container_width=True, type="primary" if st.session_state['gw_view_mode'] == 'Player Dashboard' else "secondary"):
        st.session_state['gw_view_mode'] = 'Player Dashboard'
        st.rerun()
        
    st.markdown("### 🧠 ANALYSIS")
    if st.button("인사이트 분석 (Insight)", use_container_width=True, type="primary" if st.session_state['gw_view_mode'] == 'Insight Analysis' else "secondary"):
        st.session_state['gw_view_mode'] = 'Insight Analysis'
        st.rerun()
    
    st.markdown("---")
    if st.button("Logout"):
        auth.logout()

# --- Header Section ---
col_h1, col_h2 = st.columns([0.8, 6])
with col_h1:
    # Try loading logo, fallback to emoji if missing
    try:
        st.image("gangwon_fc/gangwon_logo.png", width=80)
    except:
        st.markdown("## 🐻")

with col_h2:
    # Dynamic Subtitle based on View Mode
    subtitle = st.session_state['gw_view_mode']
    st.markdown(f"""
    <div style="display: flex; align-items: baseline; gap: 15px;">
        <h1 style='margin: 0; padding: 0; color: #1a1a1a; font-size: 36px;'>GANGWON FC <span style='color: #006442;'>Performance Center</span></h1>
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
    # SLJ: Prioritize L/R average, fallback to single column
    if 'SLJ_Height_L' in df.columns and 'SLJ_Avg' not in df.columns:
        df['SLJ_Avg'] = df[['SLJ_Height_L', 'SLJ_Height_R']].mean(axis=1)
    elif 'SLJ_Height_Imp_mom_' in df.columns and 'SLJ_Avg' not in df.columns:
         df['SLJ_Avg'] = df['SLJ_Height_Imp_mom_']

    if 'Hamstring_Ecc_L' in df.columns and 'Hamstring_Ecc_Avg' not in df.columns:
        df['Hamstring_Ecc_Avg'] = df[['Hamstring_Ecc_L', 'Hamstring_Ecc_R']].mean(axis=1)
    if 'Hamstring_ISO_L' in df.columns and 'Hamstring_ISO_Avg' not in df.columns:
        df['Hamstring_ISO_Avg'] = df[['Hamstring_ISO_L', 'Hamstring_ISO_R']].mean(axis=1)
    if 'HipAdd_L' in df.columns and 'HipAdd_Avg' not in df.columns:
        df['HipAdd_Avg'] = df[['HipAdd_L', 'HipAdd_R']].mean(axis=1)
    if 'HipAbd_L' in df.columns and 'HipAbd_Avg' not in df.columns:
        df['HipAbd_Avg'] = df[['HipAbd_L', 'HipAbd_R']].mean(axis=1)
    return df

# --- VIEW: Team Dashboard ---
if st.session_state['gw_view_mode'] == 'Team Dashboard':
    # title removed
    
    # Filter df_global (which is df_team) by date
    if df_global.empty:
        st.warning("No data available.")
        st.stop()
        
    # Fix TypeError: Convert date objects to Timestamp for datetime64 comparison -> REVERTED
    # Since df has date objects, we compare with date objects directly
    
    mask = (df_global['Test_Date'] >= start_date) & (df_global['Test_Date'] <= end_date)
    df_team = df_global.loc[mask]
    
    if df_team.empty:
        st.warning(f"No data found between {start_date} and {end_date}.")
        st.stop()
        
    if df_team.empty:
        st.warning("No data available.")
        st.stop()
        
    df_team = calculate_derived_cols(df_team)
    
    # Identify correct columns (Prioritize trailing underscore versions if present)
    col_cmj = 'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_team.columns else 'CMJ_Height_Imp_mom'
    col_sj  = 'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_team.columns else 'SquatJ_Height_Imp_mom'
    
    # 1. 7 KPI Boxes
    kpis = [
        ("CMJ (Avg)", safe_mean(df_team, col_cmj)),
        ("Squat Jump (Avg)", safe_mean(df_team, col_sj)),
        ("Single Jump (Avg)", safe_mean(df_team, 'SLJ_Avg')),
        ("Hamstring Ecc (Avg)", safe_mean(df_team, 'Hamstring_Ecc_Avg')),
        ("Hamstring ISO (Avg)", safe_mean(df_team, 'Hamstring_ISO_Avg')),
        ("Hip Add (Avg)", safe_mean(df_team, 'HipAdd_Avg')),
        ("Hip Abd (Avg)", safe_mean(df_team, 'HipAbd_Avg')),
    ]
    
    cols = st.columns(7)
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
    metric_opt = st.selectbox("지표 선택 (Select Metric)", ["CMJ", "SquatJ", "SLJ"], key="team_pow")
    
    col_map = {
        "CMJ": col_cmj, 
        "SquatJ": col_sj, 
        "SLJ": "SLJ_Avg"
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
    metric_opt_s = st.selectbox("지표 선택 (Select Metric)", ["Hamstring Ecc", "Hamstring ISO", "HipAdd", "HipAbd"], key="team_str")
    
    col_map_s = {"Hamstring Ecc": "Hamstring_Ecc_Avg", "Hamstring ISO": "Hamstring_ISO_Avg", "HipAdd": "HipAdd_Avg", "HipAbd": "HipAbd_Avg"}
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
elif st.session_state['gw_view_mode'] == 'Player Dashboard':
    # st.title("Player Dashboard") # Removed
    
    player_list = data_loader.get_player_list()
    player_list = [p for p in player_list if isinstance(p, str)] # Simple clean
    
    c_sel, _ = st.columns([1, 3])
    with c_sel:
        selected_player = st.selectbox("Select Player", player_list)
        
    if selected_player:
        # Load Player Data
        df_p = data_loader.load_player_data(selected_player)
        
        if df_p.empty:
            st.warning("No data found for this player.")
        else:
            # Apply Date Filter (Fix TypeError)
            # ts_start = pd.Timestamp(start_date) -> REVERTED
            # ts_end = pd.Timestamp(end_date)
            
            mask_p = (df_p['Test_Date'] >= start_date) & (df_p['Test_Date'] <= end_date)
            df_p = df_p.loc[mask_p]
            
            if df_p.empty:
                st.warning(f"No data for {selected_player} in the selected range.")
            else:
                df_p = calculate_derived_cols(df_p)
            
            # Identify correct columns (Prioritize trailing underscore versions if present)
            col_cmj = 'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_p.columns else 'CMJ_Height_Imp_mom'
            col_sj  = 'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_p.columns else 'SquatJ_Height_Imp_mom'

            # --- 🔎 Player Deep Dive Check (Latest Status) ---
            # Sort by date desc to get latest
            df_latest = df_p.sort_values('Test_Date', ascending=False).head(1)
            
            if not df_latest.empty:
                latest_date = df_latest['Test_Date'].iloc[0]
                st.markdown(f"#### 🔎 선수 심층 진단 (Deep Dive Check) <span style='font-size:14px; color:grey'>(Latest: {latest_date})</span>", unsafe_allow_html=True)
                
                # 1. EUR
                eur_val = 0
                eur_status = "N/A"
                eur_color = "grey"
                if col_cmj in df_latest.columns and col_sj in df_latest.columns:
                    c_val = df_latest[col_cmj].fillna(0).iloc[0]
                    s_val = df_latest[col_sj].fillna(0).iloc[0]
                    if s_val > 0:
                        eur_val = c_val / s_val
                        if eur_val > 1.1: eur_status, eur_color = "Excellent (탄력 우수)", "#006442" # Green
                        elif eur_val >= 1.0: eur_status, eur_color = "Normal (정상)", "#1f77b4" # Blue
                        else: eur_status, eur_color = "Low (탄력 저하)", "#d62728" # Red

                # 2. SLJ Asymmetry
                slj_asym = 0
                slj_status = "Balanced"
                slj_color = "#006442"
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
                            slj_status, slj_color = f"Normal ({slj_asym:.1f}%)", "#006442"

                # 3. Strength Asymmetry (Hamstring Eccentric)
                ham_asym = 0
                ham_status = "Balanced"
                ham_color = "#006442"
                h_l = df_latest['Hamstring_Ecc_L'].fillna(0).iloc[0] if 'Hamstring_Ecc_L' in df_latest.columns else 0
                h_r = df_latest['Hamstring_Ecc_R'].fillna(0).iloc[0] if 'Hamstring_Ecc_R' in df_latest.columns else 0
                max_ham = max(h_l, h_r)
                if max_ham > 0:
                    ham_asym = ((h_r - h_l) / max_ham) * 100
                    if abs(ham_asym) > 15:
                        ham_status, ham_color = f"Risk ({ham_asym:.1f}%)", "#d62728"
                    else:
                        ham_status, ham_color = f"Stable ({ham_asym:.1f}%)", "#006442"

                # 4. Groin Risk (Hip Add/Abd Ratio) - Average of L/R
                groin_status = "Good"
                groin_color = "#006442"
                add_l = df_latest['HipAdd_L'].fillna(0).iloc[0] if 'HipAdd_L' in df_latest.columns else 0
                abd_l = df_latest['HipAbd_L'].fillna(0).iloc[0] if 'HipAbd_L' in df_latest.columns else 0
                
                ratio_l = add_l / abd_l if abd_l > 0 else 0
                # Check simple average ratio or singular risk? Let's check Left (common dominant) or worst case?
                # Let's check if ANY side is < 0.8
                add_r = df_latest['HipAdd_R'].fillna(0).iloc[0] if 'HipAdd_R' in df_latest.columns else 0
                abd_r = df_latest['HipAbd_R'].fillna(0).iloc[0] if 'HipAbd_R' in df_latest.columns else 0
                ratio_r = add_r / abd_r if abd_r > 0 else 0
                
                if (ratio_l > 0 and ratio_l < 0.8) or (ratio_r > 0 and ratio_r < 0.8):
                    groin_status, groin_color = "High Risk (<0.8)", "#d62728"
                else:
                    groin_status, groin_color = "Stable (>0.8)", "#006442"

                # Visualization (Cards)
                chk_c1, chk_c2, chk_c3, chk_c4 = st.columns(4)
                
                def card(col, label, value, color):
                    col.markdown(f"""
                    <div style="border:1px solid #ddd; padding:10px; border-radius:5px; border-left: 5px solid {color}; background-color: white;">
                        <span style="font-size:12px; font-weight:bold; color:black;">{label}</span><br>
                        <span style="font-size:16px; color:{color}; font-weight:bold;">{value}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                card(chk_c1, "EUR (탄력성)", f"{eur_val:.2f}", eur_color)
                card(chk_c2, "SLJ 불균형", slj_status, slj_color)
                card(chk_c3, "햄스트링 불균형", ham_status, ham_color)
                card(chk_c4, "서혜부(Groin) 리스크", groin_status, groin_color)
            
            st.divider()

            # --- Trends Charts ---
            st.subheader(f"📈 선수별 트렌드 분석: {selected_player}")
            
            def create_trend_chart(df, metrics_dict, title, chart_type='line'):
                """
                df: Dataframe
                metrics_dict: { 'Label': 'Column_Name' }
                title: Chart Title
                chart_type: 'line' or 'bar'
                """
                # Prepare Data (Format Date)
                df_chart = df.copy()
                try:
                    df_chart['Date_Str'] = df_chart['Test_Date'].dt.strftime('%Y-%m-%d')
                except:
                    df_chart['Date_Str'] = df_chart['Test_Date'].astype(str).str[:10]
                
                df_chart = df_chart.sort_values('Test_Date')

                fig = go.Figure()
                has_data = False
                colors = ['#006442', '#F37021', '#1f77b4', '#d62728'] # Gangwon Colors + Defaults
                
                # Check for empty columns first
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
                
                # Layout updates
                layout_args = dict(
                    title=dict(text=title, font=dict(size=14)),
                    hovermode="x unified", 
                    # Legend: Top Right, strictly avoiding title overlap
                    legend=dict(orientation="h", y=1.15, x=1, xanchor='right', bgcolor='rgba(255,255,255,0.5)'),
                    margin=dict(l=20, r=20, t=50, b=20), # Increased top margin for legend
                    xaxis=dict(
                        tickformat="%Y-%m-%d", 
                        type='category' # Category usually looks better for discrete dates in Bar charts
                    )
                )
                
                if chart_type == 'bar':
                    layout_args['barmode'] = 'group'
                    
                fig.update_layout(**layout_args)
                # Adjust margin to ensure title visibility
                fig.update_layout(margin=dict(t=50))

                if has_data:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No data for {title}")

            def create_strength_diverging_chart(df, col_l, col_r, title):
                """
                Generates Diverging Bar Chart for L/R Strength + Imbalance Scatter.
                """
                # Prepare Data
                df_chart = df.sort_values('Test_Date', ascending=True).copy()
                
                # Format Date Y-Axis
                try:
                    df_chart['Date_Str'] = df_chart['Test_Date'].dt.strftime('%Y-%m-%d')
                except:
                    df_chart['Date_Str'] = df_chart['Test_Date'].astype(str)

                # Data Logic
                l_vals = df_chart[col_l].fillna(0)
                r_vals = df_chart[col_r].fillna(0)
                l_plot = l_vals * -1 # Negative for Left
                
                # Imbalance Calculation
                # (R - L) / Max * 100
                max_val = df_chart[[col_l, col_r]].max(axis=1).replace(0, 1)
                imbalance = ((r_vals - l_vals) / max_val) * 100
                
                fig = go.Figure()
                
                # 1. Left Bar (Sky Blue) #56B4E9
                fig.add_trace(go.Bar(
                    y=df_chart['Date_Str'],
                    x=l_plot,
                    orientation='h',
                    name='Left',
                    marker_color='#56B4E9',
                    hovertext=l_vals,
                    hovertemplate='Left: %{hovertext:.1f} N<extra></extra>'
                ))
                
                # 2. Right Bar (Orange) #F37021
                fig.add_trace(go.Bar(
                    y=df_chart['Date_Str'],
                    x=r_vals,
                    orientation='h',
                    name='Right',
                    marker_color='#F37021',
                    hovertemplate='Right: %{x:.1f} N<extra></extra>'
                ))
                
                # 3. Imbalance Dot (Black) on Secondary Axis
                fig.add_trace(go.Scatter(
                    y=df_chart['Date_Str'],
                    x=imbalance,
                    xaxis='x2',
                    mode='markers',
                    name='Imbalance %',
                    marker=dict(color='black', size=8, symbol='circle'),
                    hovertemplate='Imbalance: %{x:.1f}%<extra></extra>'
                ))
                
                fig.update_layout(
                    title=dict(text=title, font=dict(size=14)),
                    barmode='relative',
                    xaxis=dict(
                        range=[-1000, 1000],
                        title='Force (N)',
                        tickvals=[-1000, -500, 0, 500, 1000],
                        ticktext=['1000', '500', '0', '500', '1000'],
                        zeroline=True, zerolinewidth=1, zerolinecolor='grey'
                    ),
                    xaxis2=dict(
                        range=[-50, 50],
                        title='Imbalance (%)',
                        overlaying='x', 
                        side='top',
                        showgrid=False,
                        zeroline=True, zerolinewidth=1, zerolinecolor='black'
                    ),
                    yaxis=dict(type='category'),
                    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor='center'),
                    margin=dict(t=80, b=50, l=50, r=50),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)



            def create_strength_diverging_chart(df, col_l, col_r, title, threshold=15):
                """
                Generates Diverging Bar Chart for L/R Strength + Imbalance Scatter.
                threshold: Risk threshold % (default 15 for strength, 10 for SLJ)
                """
                if df.empty: return

                # Prepare Data
                df_chart = df.sort_values('Test_Date', ascending=True).copy()
                
                # Format Date Y-Axis
                try:
                    df_chart['Date_Str'] = df_chart['Test_Date'].dt.strftime('%Y-%m-%d')
                except:
                    df_chart['Date_Str'] = df_chart['Test_Date'].astype(str)

                # Data Logic
                l_vals = df_chart[col_l].fillna(0)
                r_vals = df_chart[col_r].fillna(0)
                l_plot = l_vals * -1 # Negative for Left
                
                # Imbalance Calculation (R - L) / Max * 100
                max_val = df_chart[[col_l, col_r]].max(axis=1).replace(0, 1)
                imbalance = ((r_vals - l_vals) / max_val) * 100
                
                # Color Points based on Threshold
                point_colors = ['#FF4B4B' if abs(x) > threshold else 'black' for x in imbalance]
                
                fig = go.Figure()
                
                # 1. Left Bar (Sky Blue)
                fig.add_trace(go.Bar(
                    y=df_chart['Date_Str'],
                    x=l_plot,
                    orientation='h',
                    name='Left',
                    marker_color='#56B4E9',
                    hovertext=l_vals,
                    hovertemplate='Left: %{hovertext:.1f} N<extra></extra>'
                ))
                
                # 2. Right Bar (Orange)
                fig.add_trace(go.Bar(
                    y=df_chart['Date_Str'],
                    x=r_vals,
                    orientation='h',
                    name='Right',
                    marker_color='#F37021',
                    hovertemplate='Right: %{x:.1f} N<extra></extra>'
                ))
                
                # 3. Imbalance Dot (Red/Black)
                fig.add_trace(go.Scatter(
                    y=df_chart['Date_Str'],
                    x=imbalance,
                    xaxis='x2',
                    mode='markers',
                    name='Imbalance %',
                    marker=dict(color=point_colors, size=8, symbol='circle', line=dict(width=1, color='white')),
                    hovertemplate='Imbalance: %{x:.1f}%<extra></extra>'
                ))
                
                fig.update_layout(
                    title=dict(text=title, font=dict(size=14)),
                    barmode='relative',
                    xaxis=dict(
                        range=[-1000, 1000],
                        title='Force (N)',
                        tickvals=[-1000, -500, 0, 500, 1000],
                        ticktext=['1000', '500', '0', '500', '1000'],
                        zeroline=True, zerolinewidth=1, zerolinecolor='grey'
                    ),
                    xaxis2=dict(
                        range=[-50, 50],
                        title='Imbalance (%)',
                        overlaying='x', 
                        side='top',
                        showgrid=False,
                        zeroline=True, zerolinewidth=1, zerolinecolor='black'
                    ),
                    yaxis=dict(type='category'),
                    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor='center'),
                    margin=dict(t=80, b=50, l=50, r=50),
                    height=400,
                    shapes=[
                        # Threshold Lines
                        dict(type="line", xref="x2", yref="paper", x0=threshold, y0=0, x1=threshold, y1=1, line=dict(color="red", width=1, dash="dash")),
                        dict(type="line", xref="x2", yref="paper", x0=-threshold, y0=0, x1=-threshold, y1=1, line=dict(color="red", width=1, dash="dash")),
                    ]
                )
                
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("### ⚡ 파워 분석 (Power Trends)")
            p_c1, p_c2, p_c3 = st.columns(3)
            
            with p_c1:
                create_trend_chart(df_p, {'CMJ': col_cmj}, "CMJ Height", 'line')
            with p_c2:
                create_trend_chart(df_p, {'SquatJ': col_sj}, "Squat Jump Height", 'line')
            with p_c3:
                # Corrected SLJ Columns
                create_trend_chart(df_p, {
                    'Left': 'SLJ_Height_L_Imp_mom_', 
                    'Right': 'SLJ_Height_R_Imp_mom_'
                }, "Single Leg Jump", 'line')

            # 2. Strength Metrics (Diverging Bar Charts)
            st.markdown("### 💪 근력 분석 (Strength Metrics)")
            s_c1, s_c2 = st.columns(2)
            
            with s_c1:
                create_strength_diverging_chart(df_p, 'Hamstring_Ecc_L', 'Hamstring_Ecc_R', "Hamstring Eccentric (L/R)")
                create_strength_diverging_chart(df_p, 'HipAdd_L', 'HipAdd_R', "Hip Adduction (L/R)")
                
            with s_c2:
                create_strength_diverging_chart(df_p, 'Hamstring_ISO_L', 'Hamstring_ISO_R', "Hamstring Isometric (L/R)")
                create_strength_diverging_chart(df_p, 'HipAbd_L', 'HipAbd_R', "Hip Abduction (L/R)")
                
            st.divider()
                
            # --- Data Table ---
            st.markdown("### 📋 데이터 로그 (Data Log)")
            # Show ALL columns (sorted by date)
            # Apply formatting ONLY to numeric columns to avoid "Unknown format code 'f' for object of type 'str'"
            
            # Identify numeric columns for formatting
            numeric_cols = df_p.select_dtypes(include=[np.number]).columns.tolist()
            
            st.dataframe(
                df_p.sort_values('Test_Date', ascending=False).style.format("{:.1f}", subset=numeric_cols, na_rep="-"),
                use_container_width=True,
                hide_index=True
            )

# --- VIEW: Insight Analysis ---
elif st.session_state['gw_view_mode'] == 'Insight Analysis':
    from utils import analysis_utils

    # Load Data
    if df_global.empty:
        st.warning("No data available.")
        st.stop()
        
    mask = (df_global['Test_Date'] >= start_date) & (df_global['Test_Date'] <= end_date)
    df_insight = df_global.loc[mask]
    
    if df_insight.empty:
        st.warning(f"No data found between {start_date} and {end_date}.")
        st.stop()
        
    # Ensure derived cols are calculated
    df_insight = calculate_derived_cols(df_insight)

    # --- Mode Selection ---
    with st.container():
        st.markdown("""
        <style>
        .mode-select-box {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #d1d5db;
            margin-bottom: 20px;
        }
        </style>
        <div class='mode-select-box'>
            <h4 style='margin:0; padding-bottom:10px; color:#006442;'>🔍 분석 모드 선택 (Analysis Mode)</h4>
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
        st.subheader("📊 팀 피지컬 리포트 (Team Status)")
        
        # Calculate Tiers
        # Metrics: Power (CMJ, SJ), Strength (Hamstring, Hip), Balance (SLJ)
        tier_metrics = {
            'Power': [
                'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_insight.columns else 'CMJ_Height_Imp_mom',
                'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_insight.columns else 'SquatJ_Height_Imp_mom'
            ],
            'Strength': [
                'Hamstring_Ecc_L', 'Hamstring_Ecc_R', 
                'Hamstring_ISO_L', 'Hamstring_ISO_R',
                'HipAdd_L', 'HipAdd_R',
                'HipAbd_L', 'HipAbd_R'
            ],
            'Balance': [
                'SLJ_Height_L_Imp_mom_', 
                'SLJ_Height_R_Imp_mom_'
            ]
        }
        
        tier_df = analysis_utils.calculate_physical_tier(df_insight, tier_metrics)
        
        if not tier_df.empty:
            # 1. Overall Top 5 & Distribution
            c_top1, c_top2 = st.columns([1, 1])
            with c_top1:
                fig_tier = analysis_utils.plot_tier_distribution(tier_df)
                if fig_tier: st.plotly_chart(fig_tier, use_container_width=True)
                
            with c_top2:
                st.markdown("##### 🥇 종합 Top 5 (Overall)")
                top5_overall = tier_df.sort_values('Physical_Score', ascending=False).head(5)
                st.dataframe(
                    top5_overall[['Name', 'Physical_Score', 'Tier']].style.format({'Physical_Score': '{:.1f}'}), 
                    hide_index=True, 
                    use_container_width=True
                )
                
                st.markdown("""
                <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 12px; color: #555;'>
                    <i><b>Physical Tier Score</b> = (Power Rank + Strength Rank + Balance Rank) / 3</i><br>
                    <i>S (Top 20%), A (20-50%), B (50-80%), C (Bottom 20%)</i>
                    <ul style='margin-top: 5px; padding-left: 20px;'>
                        <li><b>Power</b>: CMJ & Squat Jump (Height)</li>
                        <li><b>Strength</b>: Hamstring (Ecc/ISO) & Hip (Add/Abd) - Mean Rank</li>
                        <li><b>Balance</b>: Single Leg Jump (Left & Right)</li>
                    </ul>
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
                 st.markdown("**⚖️ Balance Rank**")
                 if 'Balance_Score' in tier_df.columns:
                     top5_bal = tier_df.sort_values('Balance_Score', ascending=False).head(5)
                     st.dataframe(top5_bal[['Name', 'Balance_Score']].style.format({'Balance_Score': '{:.1f}'}), hide_index=True, use_container_width=True)

            st.markdown("---")
            st.markdown("---")
            # Description moved to top right
                
            with st.expander("📋 View Full Tier List"):
                 st.dataframe(tier_df[['Name', 'Tier', 'Physical_Score']].sort_values('Physical_Score', ascending=False), use_container_width=True)
        else:
            st.info("티어 산출을 위한 데이터가 부족합니다.")

    # 2. Development Tracker
    elif an_mode == "전후 비교 (Development Tracker)":
        st.subheader("📈 Pre-Post Development Analysis")
        
        # Filter out NaT values before sorting
        valid_dates = df_global['Test_Date'].dropna().unique()
        col_dates = sorted(valid_dates)
        
        if len(col_dates) < 2:
            st.warning("비교를 위해서는 최소 2개 이상의 측정 날짜가 필요합니다.")
        else:
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                date_pre = st.selectbox("기준 시점 (Pre)", col_dates, index=0)
            with c_d2:
                date_post = st.selectbox("비교 시점 (Post)", col_dates, index=len(col_dates)-1)
            
            if date_pre == date_post:
                st.warning("서로 다른 날짜를 선택해주세요.")
            else:
                df_pre = df_global[df_global['Test_Date'] == date_pre]
                df_post = df_global[df_global['Test_Date'] == date_post]
                
                # Calculate Delta
                # Calculate Delta
                # Calculate Delta
                st.markdown("##### 🔧 분석 지표 선택")
                
                # Comprehensive Metric Map for Development Tracker
                delta_metrics_all = {
                    "Power: CMJ Height (Imp Momentum)": "CMJ_Height_Imp_mom_",
                    "Power: Squat Jump Height (Imp Momentum)": "SquatJ_Height_Imp_mom_",
                    "Strength: Hamstring Eccentric (Left)": "Hamstring_Ecc_L",
                    "Strength: Hamstring Eccentric (Right)": "Hamstring_Ecc_R",
                    "Strength: Hamstring Isometric (Left)": "Hamstring_ISO_L",
                    "Strength: Hamstring Isometric (Right)": "Hamstring_ISO_R",
                    "Strength: Hip Adduction (Left)": "HipAdd_L",
                    "Strength: Hip Adduction (Right)": "HipAdd_R",
                    "Strength: Hip Abduction (Left)": "HipAbd_L",
                    "Strength: Hip Abduction (Right)": "HipAbd_R",
                    "Balance: Single Leg Jump (Left)": "SLJ_Height_L_Imp_mom_",
                    "Balance: Single Leg Jump (Right)": "SLJ_Height_R_Imp_mom_"
                }
                
                delta_mode = st.selectbox("분석 지표를 선택하세요", list(delta_metrics_all.keys()))

                # Filter metrics based on selection
                target_metric = delta_metrics_all.get(delta_mode)
                delta_metrics = {delta_mode: target_metric} if target_metric else {}
                
                delta_df = analysis_utils.calculate_pre_post_delta(df_pre, df_post, delta_metrics)
                
                if not delta_df.empty:
                    st.markdown(f"#### 🔍 변화량 분석 (Delta %): {date_pre} -> {date_post}")
                    
                    fig_d = analysis_utils.plot_delta_chart(delta_df, delta_mode)
                    if fig_d: st.plotly_chart(fig_d, use_container_width=True)
                else:
                    st.info("두 시점 간 공통 측정 선수가 없습니다.")

    # 3. Deep Dive (Existing Logic)
    elif an_mode == "심층 분석 (Deep Analysis)":

    
        # Improve Column Selection
        col_cmj = 'CMJ_Height_Imp_mom_' if 'CMJ_Height_Imp_mom_' in df_insight.columns else 'CMJ_Height_Imp_mom'
        col_sj  = 'SquatJ_Height_Imp_mom_' if 'SquatJ_Height_Imp_mom_' in df_insight.columns else 'SquatJ_Height_Imp_mom'
        
        st.markdown("### 1. Eccentric Utilization Ratio (EUR)")
        with st.expander("ℹ️ EUR 지표란?"):
            st.markdown("""
            **신장 단축 주기 효율성 (EUR)** = CMJ / Squat Jump
            - **> 1.1**: 우수한 탄력성. 신장-단축 주기(SSC)를 효율적으로 사용함.
            - **1.0 - 1.1**: 정상 범위.
            - **< 1.0**: 낮은 탄력성. 순수 근력(Concentric) 의존도가 높음. **플라이오메트릭 훈련 권장.**
            """)
        
        eur_df = analysis_utils.calculate_eur(df_insight, col_cmj, col_sj)
        if not eur_df.empty:
            fig_eur = analysis_utils.plot_eur(eur_df, col_cmj, col_sj)
            if fig_eur: st.plotly_chart(fig_eur, use_container_width=True)
        else:
            st.info("Insufficient data for EUR calculation (Missing CMJ or SquatJ).")

        st.divider()

        st.markdown("### 2. 불균형 요주의 리스트 (Limb Asymmetry Watchlist)")
        
        # Asymmetry Metric Selector
        asy_metric = st.selectbox("비대칭 분석 지표 선택", 
                                  ["Single Leg Jump (SLJ)", "Hamstring Eccentric", "Hamstring Isometric", "Hip Adduction", "Hip Abduction"])
        
        # Dynamic Columns & Reference Text based on selection
        if asy_metric == "Single Leg Jump (SLJ)":
            col_l = 'SLJ_Height_L_Imp_mom_'
            col_r = 'SLJ_Height_R_Imp_mom_'
            ref_threshold = 10
            ref_text = """
            **외발 점프(SLJ) 비대칭**:
            - **10% 이상의 차이**는 기능적 불균형을 의미하며, 경기력 저하 및 부상 위험과 연관될 수 있습니다.
            - **양수 (+)**: 오른쪽 우세 / **음수 (-)**: 왼쪽 우세
            """
        elif asy_metric == "Hamstring Eccentric":
            col_l = 'Hamstring_Ecc_L'
            col_r = 'Hamstring_Ecc_R'
            ref_threshold = 15
            ref_text = """
            **햄스트링 신장성 근력(Eccentric) 비대칭**:
            - 신장성 근력 불균형(**>15%**)은 햄스트링 손상의 주요 위험 요소입니다.
            - **목표**: 좌우 차이 10% 미만 유지.
            """
        elif asy_metric == "Hamstring Isometric":
            col_l = 'Hamstring_ISO_L'
            col_r = 'Hamstring_ISO_R'
            ref_threshold = 15
            ref_text = """
            **햄스트링 등척성 근력(Isometric) 비대칭**:
            - VALD 및 관련 연구에 따르면, **15% 이상의 근력 불균형**은 햄스트링 부상 위험을 유의미하게 증가시킬 수 있습니다.
            - **목표**: 좌우 차이 10% 미만 유지.
            """
        elif asy_metric == "Hip Adduction":
            col_l = 'HipAdd_L'
            col_r = 'HipAdd_R'
            ref_threshold = 15
            ref_text = """
            **고관절 내전근(Adduction) 비대칭**:
            - 내전근의 좌우 불균형(**>15%**)은 서혜부 통증(Groin Pain) 및 스포츠 탈장의 잠재적 위험 요인입니다.
            - **양수 (+)**: 오른쪽 우세 / **음수 (-)**: 왼쪽 우세
            """
        elif asy_metric == "Hip Abduction":
            col_l = 'HipAbd_L'
            col_r = 'HipAbd_R'
            ref_threshold = 15
            ref_text = """
            **고관절 외전근(Abduction) 비대칭**:
            - 중둔근을 포함한 외전근의 불균형(**>15%**)은 골반 안정성 저하 및 무릎 부상(ACL 등)과 연관될 수 있습니다.
            """

        with st.expander(f"ℹ️ {asy_metric} 기준 및 설명"):
            st.markdown(ref_text)
            
        # Calculate Asymmetry
        asy_df = analysis_utils.calculate_asymmetry(df_insight, col_l, col_r)
        
        if not asy_df.empty:

            fig_lolly = analysis_utils.plot_asymmetry_lollipop(asy_df, threshold=ref_threshold)
            if fig_lolly: st.plotly_chart(fig_lolly, use_container_width=True)

        else:
            st.info(f"선택한 지표 ({asy_metric})에 대한 데이터가 부족합니다.")
            
        st.divider()

        # Removed columns to make Groin Risk full width
        
        # with c3:
        st.markdown("### 3. Groin Risk (Add/Abd Ratio)")
        with st.expander("ℹ️ 서혜부(Groin) 건강"):
            st.markdown("""
            **내전근 / 외전근 비율 (Add / Abd Ratio)**:
            - 내전근(안쪽)과 외전근(바깥쪽/둔근) 사이의 힘의 균형을 측정합니다.
            - **위험 구간 (< 0.80)**: 내전근 좌상(Strain) 위험이 높음.
            - **목표 범위**: > 0.90 - 1.0
            """)
        
        col_add_l = 'HipAdd_L' if 'HipAdd_L' in df_insight.columns else 'HipAdd_L_N_'
        col_add_r = 'HipAdd_R' if 'HipAdd_R' in df_insight.columns else 'HipAdd_R_N_'
        col_abd_l = 'HipAbd_L' if 'HipAbd_L' in df_insight.columns else 'HipAbd_L_N_'
        col_abd_r = 'HipAbd_R' if 'HipAbd_R' in df_insight.columns else 'HipAbd_R_N_'

        groin_df = analysis_utils.calculate_groin_risk(df_insight, 'HipAdd_L', 'HipAdd_R', 'HipAbd_L', 'HipAbd_R')
        if not groin_df.empty:
            fig_groin = analysis_utils.plot_groin_risk(groin_df)
            if fig_groin: st.plotly_chart(fig_groin, use_container_width=True)
        else:
             st.info("Insufficient data for Groin Risk.")




