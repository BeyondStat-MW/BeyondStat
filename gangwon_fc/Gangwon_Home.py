
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
import base64
from utils import gangwon_data_loader as data_loader

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Gangwon FC Dashboard", page_icon="⚽")

# --- Helper: Image to Base64 ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# --- Custom CSS (Gangwon Styling) ---
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        /* Main Theme */
        :root {
            --gw-orange: #F58220;
            --gw-green: #006442;
            --gw-dark: #1e1e1e;
            --gw-light: #f4f4f4;
        }
        
        html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
        
        .stApp { background-color: #f8f9fa; }
        
        /* Header */
        .header-container {
            display: flex; align-items: center; padding: 20px 0;
            border-bottom: 2px solid var(--gw-orange); margin-bottom: 20px;
        }
        .header-title {
            font-size: 32px; font-weight: 800; color: var(--gw-green);
            margin-left: 20px; text-transform: uppercase;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: var(--gw-green);
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        
        /* Metric Cards */
        .metric-card {
            background: white; border-radius: 12px; padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            text-align: center; border-left: 5px solid var(--gw-orange);
            transition: transform 0.2s;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-value { font-size: 28px; font-weight: 800; color: var(--gw-dark); }
        .metric-label { font-size: 14px; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 1px; }
        
        /* Content Containers */
        .content-box {
            background: white; border-radius: 16px; padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 20px;
        }
        
    </style>
    """, unsafe_allow_html=True)

load_css()

# --- Load Assets ---
logo_b64 = get_base64_of_bin_file("gangwon_fc/gangwon_logo.png")
logo_img = f'<img src="data:image/png;base64,{logo_b64}" width="80">' if logo_b64 else "⚽"

# --- Sidebar Navigation ---
st.sidebar.markdown(f"<div style='text-align:center; margin-bottom:30px;'>{logo_img}</div>", unsafe_allow_html=True)
st.sidebar.markdown("### MENU")
view_mode = st.sidebar.radio("View", ["Dashboard (Player & Team)", "Insight Analysis"], label_visibility="collapsed")

# --- Main Logic ---

# 1. Dashboard View
if view_mode == "Dashboard (Player & Team)":
    
    # 1. Header
    st.markdown(f"""
    <div class="header-container">
        {logo_img}
        <div class="header-title">Gangwon FC Performance Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Team Overview (Top Section)
    team_stats = data_loader.get_team_aggregates()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Team Avg CMJ</div>
            <div class="metric-value">{team_stats['Avg_CMJ_Height']} cm</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Team Avg Strength</div>
            <div class="metric-value">{team_stats['Avg_Nordbord_Force']} N</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Readiness</div>
            <div class="metric-value">{team_stats['Team_Readiness']}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: var(--gw-green);">
            <div class="metric-label">Squad Size</div>
            <div class="metric-value">{len(data_loader.get_player_list())}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")

    # 3. Player Dashboard (Split View)
    # Left: Player Selection List
    # Right: Dashboard
    
    layout_col1, layout_col2 = st.columns([1, 4])
    
    with layout_col1:
        st.markdown("### Player List")
        players = data_loader.get_player_list()
        
        # Search Box
        search = st.text_input("🔍 Search", "")
        if search:
            players = [p for p in players if search.lower() in p.lower()]
            
        selected_player = st.radio("Select Player", players, label_visibility="collapsed")
        
    with layout_col2:
        if selected_player:
            # Load Data
            p_data = data_loader.load_player_data(selected_player)
            
            st.markdown(f"## 🏃 {selected_player}")
            
            # --- TABBED VIEW ---
            tab1, tab2, tab3 = st.tabs(["📊 Performance Profile", "📈 Detailed Trends", "📋 Raw Data"])
            
            # Tab 1: Profile (Radar + Key Stats)
            with tab1:
                if 'CMJ' in p_data and not p_data['CMJ'].empty:
                    latest_cmj = p_data['CMJ'].iloc[-1]
                    
                    # Radar Chart Logic (Mocked Categories for visual)
                    categories = ['Power', 'Strength', 'Speed', 'Agility', 'Endurance']
                    # Normally we'd calculate these percentile ranks
                    r_values = [80, 70, 60, 85, 90] 
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=r_values,
                        theta=categories,
                        fill='toself',
                        name=selected_player,
                        line_color='#F58220'
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False,
                        title="Athlete Profile (Percentile Rank)"
                    )
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.markdown("### Latest Metrics")
                        st.dataframe(latest_cmj.to_frame().T, use_container_width=True)
                else:
                    st.info("No CMJ Data available for profile.")
            
            # Tab 2: Trends
            with tab2:
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    if 'CMJ' in p_data:
                        fig = px.line(p_data['CMJ'], x='Test_Date', y='Jump_Height', title="CMJ Trend", markers=True)
                        fig.update_traces(line_color='#F58220')
                        st.plotly_chart(fig, use_container_width=True)
                with col_t2:
                    if 'Nordbord' in p_data:
                        fig = px.line(p_data['Nordbord'], x='Test_Date', y=['Max_Force_Left', 'Max_Force_Right'], title="Nordbord Trend", markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                        
            with tab3:
                for k, v in p_data.items():
                    with st.expander(f"{k} Data"):
                        st.dataframe(v)
        else:
            st.info("Select a player to view details.")

# 2. Insight View
elif view_mode == "Insight Analysis":
    st.markdown(f"""
    <div class="header-container">
        {logo_img}
        <div class="header-title">Team Insights</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    insight_sub = st.sidebar.radio("Analysis Type", ["Injury Risk", "Position Comparison", "Training Load"])
    
    if insight_sub == "Injury Risk":
        st.markdown("### 🚑 Injury Risk Analysis (Asymmetry)")
        st.info("Visualizing athletes with high ForceFrame/Nordbord asymmetry.")
        
        # Mock Scatter Plot
        # In real app, we would aggregate all player recent data
        df_risk = pd.DataFrame({
            'Player': ['P1', 'P2', 'P3', 'P4', 'P5'],
            'Asymmetry_Perc': [5, 12, 2, 18, 7],
            'Strength_Score': [400, 350, 420, 310, 380]
        })
        
        fig = px.scatter(df_risk, x='Strength_Score', y='Asymmetry_Perc', text='Player', 
                         color='Asymmetry_Perc', size='Asymmetry_Perc',
                         color_continuous_scale='RdYlGn_r',
                         title="Strength vs Asymmetry (Risk Matrix)")
        
        # Add 'Safe Zone' Lines
        fig.add_hrect(y0=0, y1=10, line_width=0, fillcolor="green", opacity=0.1)
        fig.add_hrect(y0=10, y1=20, line_width=0, fillcolor="orange", opacity=0.1)
        
        st.plotly_chart(fig, use_container_width=True)
        
    elif insight_sub == "Position Comparison":
        st.markdown("### 📊 Position Group Analysis")
        st.info("Comparing physical metrics across different playing positions.")
        
        # Mock Data for Positions
        # Generate some random data for GK, DF, MF, FW
        data_pos = []
        for pos in ['GK', 'DF', 'MF', 'FW']:
            for _ in range(10): # 10 players per position
                data_pos.append({
                    'Position': pos,
                    'CMJ_Height': np.random.normal(loc=40 if pos=='GK' else 45 if pos=='MF' else 48, scale=5),
                    'Max_Force': np.random.normal(loc=350 if pos=='GK' else 400, scale=30)
                })
        df_pos = pd.DataFrame(data_pos)
        
        c1, c2 = st.columns(2)
        with c1:
            fig_cmj = px.box(df_pos, x='Position', y='CMJ_Height', color='Position', 
                             title="Jump Height by Position",
                             color_discrete_sequence=['#F58220', '#006442', '#1B263B', '#888888'])
            st.plotly_chart(fig_cmj, use_container_width=True)
            
        with c2:
            fig_str = px.box(df_pos, x='Position', y='Max_Force', color='Position', 
                             title="Strength (Nordbord) by Position",
                             color_discrete_sequence=['#F58220', '#006442', '#1B263B', '#888888'])
            st.plotly_chart(fig_str, use_container_width=True)
        
    elif insight_sub == "Training Load":
        st.markdown("### 🔋 Training Readiness & Load")
        st.info("Monitoring Weekly Load (Arbitrary Units) and Acute:Chronic Workload Ratio.")
        
        # Mock Load Data
        dates = pd.date_range(end=datetime.date.today(), periods=28, freq='D')
        load_data = []
        for d in dates:
            daily_load = np.random.randint(200, 800)
            load_data.append({'Date': d, 'Daily_Load': daily_load})
            
        df_load = pd.DataFrame(load_data)
        # Calculate Rolling Averages
        df_load['Acute_Load'] = df_load['Daily_Load'].rolling(window=7).mean()
        df_load['Chronic_Load'] = df_load['Daily_Load'].rolling(window=28).mean()
        df_load['ACWR'] = df_load['Acute_Load'] / (df_load['Chronic_Load'] + 1e-6) # Avoid div by 0
        
        # Filter to last 14 days for display
        df_display = df_load.tail(14)
        
        # Combo Chart: Bars for Daily Load, Line for ACWR
        fig = go.Figure()
        
        # Bar: Daily Load
        fig.add_trace(go.Bar(
            x=df_display['Date'], y=df_display['Daily_Load'],
            name='Daily Load', marker_color='#E0E0E0'
        ))
        
        # Line: ACWR (Secondary Y-axis)
        fig.add_trace(go.Scatter(
            x=df_display['Date'], y=df_display['ACWR'],
            name='ACWR', line=dict(color='#F58220', width=3),
            yaxis='y2'
        ))
        
        # Sweet Spot Zone (0.8 - 1.3)
        fig.add_hrect(y0=0.8, y1=1.3, line_width=0, fillcolor="green", opacity=0.1, yref='y2', annotation_text="Sweet Spot", annotation_position="top left")
        
        fig.update_layout(
            title="Training Load & ACWR",
            yaxis=dict(title="Daily Load (AU)"),
            yaxis2=dict(title="ACWR", overlaying='y', side='right', range=[0, 2.0]),
            legend=dict(x=0.01, y=0.99)
        )
        
        st.plotly_chart(fig, use_container_width=True)


