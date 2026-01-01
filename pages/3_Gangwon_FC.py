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
    
    st.markdown("### 📊 DASHBOARD")
    if st.button("Team Dashboard", use_container_width=True, type="primary" if st.session_state['gw_view_mode'] == 'Team Dashboard' else "secondary"):
        st.session_state['gw_view_mode'] = 'Team Dashboard'
        st.rerun()
        
    if st.button("Player Dashboard", use_container_width=True, type="primary" if st.session_state['gw_view_mode'] == 'Player Dashboard' else "secondary"):
        st.session_state['gw_view_mode'] = 'Player Dashboard'
        st.rerun()
        
    st.markdown("### 🧠 ANALYSIS")
    if st.button("Insight Analysis", use_container_width=True, type="primary" if st.session_state['gw_view_mode'] == 'Insight Analysis' else "secondary"):
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

# --- Global Date Filter (Main Area) ---
# Date Range Slider
start_date, end_date = st.slider(
    "📅 Date Filter",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)
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
    st.subheader("⚡ Power Metrics")
    metric_opt = st.selectbox("Select Metric", ["CMJ", "SquatJ", "SLJ"], key="team_pow")
    
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
    st.subheader("💪 Strength Metrics")
    metric_opt_s = st.selectbox("Select Metric", ["Hamstring Ecc", "Hamstring ISO", "HipAdd", "HipAbd"], key="team_str")
    
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

            # --- Trends Charts ---
            st.subheader(f"📈 Performance Trends: {selected_player}")
            
            def create_trend_chart(df, metrics_dict, title, chart_type='line'):
                """
                df: Dataframe
                metrics_dict: { 'Label': 'Column_Name' }
                title: Chart Title
                chart_type: 'line' or 'bar'
                """
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
                            x=df['Test_Date'], 
                            y=df[col], 
                            name=label,
                            marker_color=colors[i % len(colors)]
                        ))
                    else:
                        fig.add_trace(go.Scatter(
                            x=df['Test_Date'], 
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
                fig.update_xaxes(type='category', tickformat="%Y-%m-%d") # Use category to remove gaps
                
                if has_data:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No data for {title}")

            # 1. Power Trends (Line Charts)
            st.markdown("### ⚡ Power Trends")
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

            # 2. Strength Metrics (Bar Charts)
            st.markdown("### 💪 Strength Trends")
            s_c1, s_c2 = st.columns(2)
            
            with s_c1:
                create_trend_chart(df_p, {'Left': 'Hamstring_Ecc_L', 'Right': 'Hamstring_Ecc_R'}, "Hamstring Eccentric", 'bar')
                create_trend_chart(df_p, {'Left': 'HipAdd_L', 'Right': 'HipAdd_R'}, "Hip Adduction", 'bar')
                
            with s_c2:
                create_trend_chart(df_p, {'Left': 'Hamstring_ISO_L', 'Right': 'Hamstring_ISO_R'}, "Hamstring Isometric", 'bar')
                create_trend_chart(df_p, {'Left': 'HipAbd_L', 'Right': 'HipAbd_R'}, "Hip Abduction", 'bar')
                
            st.divider()
                
            # --- Data Table ---
            st.markdown("### 📋 Data Log")
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
        
    if col_cmj in df_insight.columns and col_sj in df_insight.columns:
        # Aggregated EUR per player
        eur_df = df_insight.groupby('Name')[[col_cmj, col_sj]].mean().reset_index()
        eur_df['EUR'] = eur_df[col_cmj] / eur_df[col_sj]
        
        fig_eur = px.scatter(eur_df, x=col_sj, y=col_cmj, text='Name', 
                             color='EUR', color_continuous_scale='RdYlGn', 
                             size_max=10, 
                             labels={col_sj: "Squat Jump (cm)", col_cmj: "CMJ (cm)"},
                             title="Elasticity Profiling (CMJ vs SquatJump)")
        
        # Reference Lines
        max_val = max(eur_df[col_cmj].max(), eur_df[col_sj].max())
        fig_eur.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="Gray", dash="dash"), name="EUR=1.0")
        fig_eur.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val*1.1, line=dict(color="Green", dash="dot"), name="EUR=1.1")
        fig_eur.update_traces(textposition='top center')
        st.plotly_chart(fig_eur, use_container_width=True)
    else:
        st.info("Insufficient data for EUR calculation (Missing CMJ or SquatJ).")

    st.divider()

    st.markdown("### 2. Limb Asymmetry Watchlist")
    with st.expander("ℹ️ 비대칭(Asymmetry)이 위험한 이유"):
        st.markdown("""
        **15% 이상의 비대칭**은 높은 부상 위험 요인으로 간주됩니다.
        이 차트는 **외발 점프(SLJ)**의 좌우 불균형을 보여줍니다.
        - **양수 (+)**: 오른쪽이 더 강함
        - **음수 (-)**: 왼쪽이 더 강함
        - **붉은 막대**: 10% 이상의 불균형 (주의 필요)
        """)
        
    slj_l = 'SLJ_Height_L_Imp_mom_'
    slj_r = 'SLJ_Height_R_Imp_mom_'
    
    if slj_l in df_insight.columns and slj_r in df_insight.columns:
        # Check non-nulls
        valid_slj = df_insight.dropna(subset=[slj_l, slj_r])
        if not valid_slj.empty:
            asy_df = valid_slj.groupby('Name')[[slj_l, slj_r]].mean().reset_index()
            # Asymmetry Formula: (R - L) / Max(R,L) * 100
            asy_df['Max_SLJ'] = asy_df[[slj_l, slj_r]].max(axis=1)
            asy_df['Asymmetry'] = ((asy_df[slj_r] - asy_df[slj_l]) / asy_df['Max_SLJ']) * 100
            
            # Color logic
            asy_df['Color'] = asy_df['Asymmetry'].apply(lambda x: 'red' if abs(x) > 10 else 'green')
            
            fig_asy = px.bar(asy_df.sort_values('Asymmetry'), x='Asymmetry', y='Name', orientation='h',
                             color='Color', color_discrete_map={'red': '#FF4B4B', 'green': '#006442'},
                             text_auto='.1f', title="SLJ Asymmetry (%) : Right(+) vs Left(-)")
            
            fig_asy.add_vline(x=10, line_dash="dash", line_color="red")
            fig_asy.add_vline(x=-10, line_dash="dash", line_color="red")
            fig_asy.update_layout(showlegend=False)
            st.plotly_chart(fig_asy, use_container_width=True)
    else:
        st.info("Insufficient data for SLJ Asymmetry.")

    st.divider()

    c3, c4 = st.columns(2)
    
    with c3:
        st.markdown("### 3. Groin Risk (Add/Abd Ratio)")
        with st.expander("ℹ️ 서혜부(Groin) 건강"):
            st.markdown("""
            **내전근 / 외전근 비율 (Add / Abd Ratio)**:
            - 내전근(안쪽)과 외전근(바깥쪽/둔근) 사이의 힘의 균형을 측정합니다.
            - **위험 구간 (< 0.80)**: 내전근 좌상(Strain) 위험이 높음.
            - **목표 범위**: > 0.90 - 1.0
            """)
        
        # Using HipAdd_L/R and HipAbd_L/R
        # Calculate Avg Add and Avg Abd first
        if 'HipAdd_L' in df_insight.columns and 'HipAbd_L' in df_insight.columns:
             groin_df = df_insight.groupby('Name')[['HipAdd_L', 'HipAdd_R', 'HipAbd_L', 'HipAbd_R']].mean().reset_index()
             groin_df['Add_Avg'] = (groin_df['HipAdd_L'] + groin_df['HipAdd_R']) / 2
             groin_df['Abd_Avg'] = (groin_df['HipAbd_L'] + groin_df['HipAbd_R']) / 2
             groin_df['Ratio'] = groin_df['Add_Avg'] / groin_df['Abd_Avg']
             
             fig_groin = px.scatter(groin_df, x='Abd_Avg', y='Add_Avg', color='Ratio',
                                    text='Name', color_continuous_scale='RdYlGn', range_color=[0.5, 1.2],
                                    title="Adductor vs Abductor Strength")
             # Risk Line ratio=0.8 implies y = 0.8x
             max_abd = groin_df['Abd_Avg'].max()
             fig_groin.add_shape(type="line", x0=0, y0=0, x1=max_abd, y1=max_abd*0.8, line=dict(color="Red", dash="dash"), name="Risk (0.8)")
             st.plotly_chart(fig_groin, use_container_width=True)

    with c4:
        st.markdown("### 4. Hamstring Robustness")
        with st.expander("ℹ️ 햄스트링 강건성"):
            st.markdown("""
            **NordBord 신장성 근력 (Eccentric Strength)**:
            - **X축**: 절대적인 신장성 근력 (좌우 평균, N).
            - **Y축**: 좌우 불균형 (Asymmetry, %).
            - **위험 영역**: 좌측 하단 (힘도 약하고 불균형도 심함).
            """)
            
        if 'Hamstring_Ecc_L' in df_insight.columns:
             ham_df = df_insight.groupby('Name')[['Hamstring_Ecc_L', 'Hamstring_Ecc_R']].mean().reset_index()
             ham_df['Ecc_Avg'] = (ham_df['Hamstring_Ecc_L'] + ham_df['Hamstring_Ecc_R']) / 2
             # Absolute Asymmetry
             ham_df['Max_Ecc'] = ham_df[['Hamstring_Ecc_L', 'Hamstring_Ecc_R']].max(axis=1)
             ham_df['Asy_Abs'] = (abs(ham_df['Hamstring_Ecc_L'] - ham_df['Hamstring_Ecc_R']) / ham_df['Max_Ecc']) * 100
             
             # Drop NaNs to prevent size=[nan] error
             ham_df = ham_df.dropna(subset=['Ecc_Avg', 'Asy_Abs'])
             
             fig_ham = px.scatter(ham_df, x='Ecc_Avg', y='Asy_Abs', text='Name', size='Ecc_Avg',
                                  color='Asy_Abs', color_continuous_scale='RdYlGn_r', # Red is high asy
                                  labels={'Ecc_Avg': "Avg Strengh (N)", 'Asy_Abs': "Asymmetry (%)"},
                                  title="Hamstring: Strength vs Imbalance")
             
             # Quadrant Lines (Arbitrary benchmarks: 300N Strength, 15% Asymmetry)
             fig_ham.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="High Risk (>15%)")
             fig_ham.add_vline(x=300, line_dash="dash", line_color="orange", annotation_text="Target Str")
             st.plotly_chart(fig_ham, use_container_width=True)

    st.divider()
    
    st.markdown("### 5. Fatigue Monitoring (Z-Score)")
    with st.expander("ℹ️ Z-Score 분석이란?"):
        st.markdown("""
        **최근 측정된 CMJ** vs **선수 본인의 과거 평균** 비교.
        - **Z < -1.5**: 피로도가 상당히 높음 (주의/경고).
        - **Z ~ 0**: 평소와 비슷한 정상 컨디션.
        - **Z > 1.0**: 컨디션이 매우 좋음 (Peaking).
        """)
        
    # Need Full History for this calculation, not just filtered range
    # But for simplicity, we use df_global but calculate stats per player
    if col_cmj in df_global.columns:
        # 1. Calc Player Stats (Mean/Std) from ALL data
        stats = df_global.groupby('Name')[col_cmj].agg(['mean', 'std']).reset_index()
        
        # 2. Get LATEST record for each player within the selected date range
        latest_recs = df_insight.sort_values('Test_Date').groupby('Name').tail(1)[['Name', 'Test_Date', col_cmj]]
        
        merged = pd.merge(latest_recs, stats, on='Name')
        merged['Z_Score'] = (merged[col_cmj] - merged['mean']) / merged['std']
        
        # Filter NaNs
        merged = merged.dropna(subset=['Z_Score'])
        
        fig_z = px.bar(merged, x='Name', y='Z_Score', color='Z_Score', 
                       color_continuous_scale='RdYlGn', range_color=[-2, 2],
                       title=f"Neuromuscular Fatigue Status")
        
        fig_z.add_hline(y=-1.5, line_width=2, line_dash="dash", line_color="red")
        fig_z.add_hline(y=0, line_width=1, line_color="gray")
        st.plotly_chart(fig_z, use_container_width=True)
