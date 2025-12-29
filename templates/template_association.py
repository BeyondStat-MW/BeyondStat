
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from utils.ui_utils import get_base64_of_bin_file

def show_dashboard(df):
    # --- CSS Styling for "World Class" Design ---
    st.markdown("""
    <style>
        /* 1. Global Background & Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* 전체 배경: 세련된 라이트 그레이 */
        .stApp {
            background-color: #f8f9fa;
        }
        
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 95% !important;
        }

        /* 2. Container Cards (The "Removal of Jail Bars") */
        /* st.container(border=True)를 "감옥 창살"에서 "고급 카드"로 변신시킴 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important; /* 테두리 제거 */
            border-radius: 16px !important; /* 더 둥글게 */
            background-color: #ffffff; /* 카드 배경은 흰색 */
            box-shadow: 0 4px 20px rgba(0,0,0,0.05); /* 부드러운 그림자 */
            margin-bottom: 24px;
            padding: 25px;
        }
        
        /* 3. Hero KPI Numbers (Impact!) */
        .metric-value {
            font-family: 'Inter', sans-serif;
            font-weight: 900;
            font-size: 42px; /* 18px -> 42px 폭발적 확대 */
            letter-spacing: -0.05em;
            color: #1B263B; /* Navy Brand Color */
            line-height: 1.1;
        }
        
        .metric-unit {
            font-weight: 600;
            font-size: 14px;
            color: #8D99AE;
            margin-left: 5px;
            vertical-align: middle;
        }

        /* 4. Headings & Titles */
        .section-title {
            font-family: 'Inter', sans-serif;
            font-weight: 900;
            font-size: 18px;
            color: #1B263B;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: -0.02em;
        }

        .chart-title {
            font-family: 'Inter', sans-serif;
            font-weight: 800;       
            font-size: 14px;        
            color: #415A77;         
            margin-bottom: 5px;
        }
        
        /* 5. Custom Components */
        hr {
            margin: 10px 0px 20px 0px; 
            border: 0;
            border-top: 1px solid #e0e0e0; /* 연하게 변경 */
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 15px;
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 30px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            font-size: 16px;
            font-weight: 600;
            color: #8D99AE;
        }
        .stTabs [aria-selected="true"] {
            color: #1B263B;
            border-bottom: 3px solid #1B263B;
        }
        
        /* Selectbox Customization (Cleaner) */
        div[data-baseweb="select"] > div {
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            background-color: #fff;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # --- Custom Navbar Styles ---
    custom_css = """
    <style>
        [data-testid="stRadio"] > div {
            display: flex;
            justify-content: center;
            gap: 30px; /* 더 넓게 */
            background-color: transparent;
            margin-top: -10px;
        }
        [data-testid="stRadio"] label > div:first-child { display: none !important; }
        [data-testid="stRadio"] label {
            background-color: transparent !important;
            border: none !important;
            cursor: pointer !important;
        }
        [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
            font-size: 15px !important;
            font-weight: 600 !important;
            color: #8D99AE !important;
        }
        /* Active State */
        .stApp [data-testid="stRadio"] label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
            font-size: 18px !important;
            color: #1B263B !important;
            font-weight: 900 !important;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # --- Header Layout ---
    logo_path = "assets/logo.png"
    logo_base64 = get_base64_of_bin_file(logo_path)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="50" style="vertical-align: middle;">' if logo_base64 else "⚽"

    header_col1, header_col2, header_col3 = st.columns([3, 4, 1], gap="medium")
    with header_col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; height: 50px;">
            <div style="margin-right: 15px;">{logo_html}</div>
            <div style="line-height: 1.2;">
                <div style="font-family: 'Inter'; font-size: 20px; font-weight: 900; color: #1B263B;">K League</div>
                <div style="font-family: 'Inter'; font-size: 14px; font-weight: 400; color: #415A77;">Youth Data Platform</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with header_col2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) 
        selected_tab = st.radio("Nav", ["홈 (Home)", "프로토콜 (Protocol)", "인사이트 (Insight)", "Player (선수 상세)"], horizontal=True, label_visibility="collapsed")

    with header_col3:
        c_user, c_logout = st.columns([1, 1])
        with c_user:
            st.markdown("<div style='text-align: right; padding-top: 12px; font-size: 20px;'>👤</div>", unsafe_allow_html=True)
        with c_logout:
            if st.button("⏻", key="logout_btn", help="로그아웃"):
                st.session_state['authenticated'] = False
                st.rerun()

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True) # Spacer

    # Common Logic
    df['Test_ID'] = df['Test_ID'].astype(str)

    # ==========================================
    # Tab: Home
    # ==========================================
    if "홈" in selected_tab:
        
        # Top KPI Section (New Design)
        all_test_ids_home = sorted([x for x in df['Test_ID'].unique() if x and x.lower() != 'nan' and x != 'None'], reverse=True)
        sel_home_test_id = st.sidebar.selectbox("측정 차수 (Test ID)", ["All"] + all_test_ids_home, index=0) # Move filter to sidebar for cleaner Hero
        
        home_df = df.copy()
        if sel_home_test_id != "All": home_df = home_df[home_df['Test_ID'] == sel_home_test_id]

        if 'Birth_Year' in home_df.columns: total_players = home_df.groupby(['Player', 'Birth_Year']).ngroups
        else: total_players = home_df['Player'].nunique()
        total_teams = home_df['Team'].nunique()
        
        # Hero KPI Cards
        kp1, kp2, kp3 = st.columns(3)
        with kp1:
            with st.container(border=True):
                st.markdown(f"""
                    <div style="color: #8D99AE; font-size: 14px; font-weight: 600; margin-bottom: 5px;">총 측정 선수</div>
                    <div class="metric-value">{total_players:,}<span class="metric-unit">명</span></div>
                """, unsafe_allow_html=True)
        with kp2:
            with st.container(border=True):
                 st.markdown(f"""
                    <div style="color: #8D99AE; font-size: 14px; font-weight: 600; margin-bottom: 5px;">측정 구단</div>
                    <div class="metric-value">{total_teams}<span class="metric-unit">개</span></div>
                """, unsafe_allow_html=True)
        with kp3:
            with st.container(border=True):
                if not home_df.empty and 'Date' in home_df.columns:
                    s_date = pd.to_datetime(home_df['Date']).min().strftime('%y.%m.%d')
                    e_date = pd.to_datetime(home_df['Date']).max().strftime('%y.%m.%d')
                    d_range = f"{s_date} - {e_date}"
                else: d_range = "-"
                st.markdown(f"""
                    <div style="color: #8D99AE; font-size: 14px; font-weight: 600; margin-bottom: 5px;">데이터 기간</div>
                    <div class="metric-value" style="font-size: 28px; line-height: 1.5;">{d_range}</div>
                """, unsafe_allow_html=True)

        st.write("")
        
        col_home_1, col_home_2 = st.columns(2)
        
        with col_home_1:
            with st.container(border=True):
                st.markdown('<div class="section-title">측정 현황 (Trends)</div>', unsafe_allow_html=True)
                trend_stats = df.groupby('Test_ID')['Test_ID'].count().reset_index(name='Count').sort_values('Test_ID')
                
                # Spacer to match the Selectbox height on the right (approx 45px)
                st.markdown("<div style='height: 45px;'></div>", unsafe_allow_html=True)
                
                # Bar Chart: Color Consistency (Navy)
                fig_trend = px.bar(
                    trend_stats, x='Count', y='Test_ID', 
                    text='Count', orientation='h'
                )
                fig_trend.update_layout(
                    height=280, margin=dict(t=10, b=10, l=20, r=20),
                    xaxis_title=None, yaxis_title=None,
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(type='category', tickfont=dict(size=14, color='#1B263B')),
                    xaxis=dict(showgrid=False)
                )
                fig_trend.update_traces(
                    marker_color='#1B263B', # Navy
                    textfont=dict(size=14, color='white'),
                    textposition='auto' 
                )
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

        with col_home_2:
            with st.container(border=True):
                st.markdown('<div class="section-title">선수 구성 (Distribution)</div>', unsafe_allow_html=True)
                
                all_teams = sorted([x for x in df['Team'].unique() if pd.notna(x) and x != 'nan'])
                sel_team = st.selectbox("구단 선택", all_teams, index=0 if all_teams else None, label_visibility="collapsed")
                
                if sel_team:
                    team_df_sub = df[df['Team'] == sel_team].copy()
                    team_comp = team_df_sub['Grade'].value_counts().reset_index()
                    team_comp.columns = ['Grade', 'Count']
                    
                    grade_order = ['중1', '중2', '중3', '고1', '고2', '고3']
                    team_comp['Grade'] = pd.Categorical(team_comp['Grade'], categories=grade_order, ordered=True)
                    team_comp = team_comp.sort_values('Grade')
                    
                    # Donut Chart: Color Consistency (Navy Palette)
                    navy_palette = ['#1B263B', '#415A77', '#778DA9', '#E0E1DD', '#A9D6E5', '#61A5C2']
                    
                    fig_donut = px.pie(
                        team_comp, values='Count', names='Grade', hole=0.6,
                        category_orders={"Grade": grade_order}, 
                        color_discrete_sequence=navy_palette
                    )
                    fig_donut.update_layout(
                        height=280, margin=dict(t=10, b=10, l=10, r=10),
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0)
                    )
                    fig_donut.update_traces(textinfo='label+percent', textfont_size=13)
                    
                    # Center Text
                    fig_donut.add_annotation(text=str(team_df_sub.shape[0]), x=0.5, y=0.5, font_size=30, showarrow=False, font_weight='bold', font_color='#1B263B')
                    fig_donut.add_annotation(text="명", x=0.5, y=0.4, font_size=14, showarrow=False, font_color='#8D99AE')
                    
                    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

    # ==========================================
    # Tab: Protocol
    # ==========================================
    elif "프로토콜" in selected_tab:
        
        # Sub-nav style
        protocol_tab = st.radio("Protocol_Nav", 
                               ["신체 프로필", "스피드", "민첩성", "근력", "파워"], 
                               horizontal=True, label_visibility="collapsed", key="prot_sub_nav")
        st.write("")
        
        # Filter is important, keep it but cleaner
        with st.container(border=True):
             # Use CSS grid inside markdown for "Invisible" layout or st.columns
             pf_c1, pf_c2, pf_c3, pf_c4, pf_c5 = st.columns(5)
             all_test_ids = sorted([x for x in df['Test_ID'].unique() if pd.notna(x)], reverse=True)
             f_test_id = pf_c1.selectbox("Test ID", ["All"] + all_test_ids)
             f_team = pf_c2.selectbox("Team", ["All"] + sorted([x for x in df['Team'].unique() if pd.notna(x)]))
             f_grade = pf_c3.selectbox("Grade", ["All"] + sorted([x for x in df['Grade'].unique() if pd.notna(x)]))
             
             pos_col = 'Position' if 'Position' in df.columns else 'Main_Position' 
             possible_cols = [c for c in df.columns if 'Pos' in c] if pos_col not in df.columns else []
             if not pos_col and possible_cols: pos_col = possible_cols[0]
             f_pos = pf_c4.selectbox("Position", ["All"] + sorted([x for x in df[pos_col].unique() if pd.notna(x)])) if pos_col else pf_c4.selectbox("Position", ["All"])
             f_name = pf_c5.text_input("Player Name", "", placeholder="이름 검색")

        p_df = df.copy()
        if f_test_id != "All": p_df = p_df[p_df['Test_ID'] == f_test_id]
        if f_team != "All": p_df = p_df[p_df['Team'] == f_team]
        if f_grade != "All": p_df = p_df[p_df['Grade'] == f_grade]
        if pos_col and f_pos != "All": p_df = p_df[p_df[pos_col] == f_pos]
        if f_name: p_df = p_df[p_df['Name'].str.contains(f_name, na=False)]

        st.write("")

        # Metrics Mapping (Same Logic, new Desc)
        METRIC_GROUPS = {
            "신체 프로필": {"metrics": ["Height", "Weight"], "names": ["신장 (Height)", "체중 (Weight)"], "units": ["cm", "kg"], "desc": ["선수의 키", "몸무게"]},
            "스피드": {"metrics": ["_5m_sec_", "_10m_sec_", "_30m_sec_"], "names": ["5m 스프린트", "10m 스프린트", "30m 스프린트"], "units": ["sec", "sec", "sec"], "inverse": [True]*3, "desc": ["초기 가속", "중거리 가속", "최대 속도"]},
            "민첩성": {"metrics": ["COD_sec_", "COD_ball_sec_"], "names": ["방향 전환 (COD)", "방향 전환 (Ball)"], "units": ["sec", "sec"], "inverse": [True, True], "desc": ["General Agility", "Agility with Ball"]},
            "근력": {"metrics": ["HamECC_L_N_", "HamECC_R_N_", "HipAdd_L_N_", "HipAdd_R_N_", "HipAbd_L_N_", "HipAbd_R_N_", "ShoulderIR_L_N_", "ShoulderIR_R_N_", "ShoulderER_L_N_", "ShoulderER_R_N_"], "names": ["햄스트링 L", "햄스트링 R", "고관절 모음 L", "고관절 모음 R", "고관절 벌림 L", "고관절 벌림 R", "어깨 내회전 L", "어깨 내회전 R", "어깨 외회전 L", "어깨 외회전 R"], "units": ["N"]*10, "desc": [""]*10},
            "파워": {"metrics": ["CMJ_Height_cm_", "CMJ_TakeoffConcentricPeakForce_N_", "CMRJ_RSI_Point_", "SquatJ_Height_cm_", "IMTP_N_", "Strength_Sum"], "names": ["CMJ 높이", "CMJ Peak Force", "CMRJ RSI", "Squat Jump", "IMTP", "근력 합계"], "units": ["cm", "N", "Idx", "cm", "N", "N"], "desc": ["반동 점프 높이", "점프 최대 힘", "탄력성 지수", "무반동 점프", "등척성 최대 근력", "전신 근력 합계"]}
        }
        
        # Metric Render Function (Updated styling)
        def render_metric_card(df, col_name, title, unit, desc, all_test_ids):
            clean_col = col_name.strip('_')
            target_col = None
            if clean_col in df.columns: target_col = clean_col
            elif col_name in df.columns: target_col = col_name
            else:
                 map_legacy = {'5m_sec': '5m_Sprint', '10m_sec': '10m_Sprint', '30m_sec': '30m_Sprint', 'COD_sec': 'COD_L', 'CMJ_Height_cm': 'Jump_CMJ', 'SquatJ_Height_cm': 'Jump_SQ'}
                 if clean_col in map_legacy and map_legacy[clean_col] in df.columns: target_col = map_legacy[clean_col]
            
            # Using HTML for Layout inside the Column
            if not target_col or df[target_col].dropna().empty:
                 st.markdown(f"""
                    <div style="text-align:center; padding: 20px; color: #ced4da;">
                        <div style="font-size: 20px; margin-bottom:5px;">📭</div>
                        <div style="font-size: 14px; font-weight:600;">{title}</div>
                        <div style="font-size: 11px;">데이터 없음</div>
                    </div>
                 """, unsafe_allow_html=True)
                 return
            
            df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
            val_df = df.dropna(subset=[target_col])
            mean_val = val_df[target_col].mean()
            
            # Trend Chart (Line with Zoomed Y-axis & Full X-axis)
            trend = val_df.groupby('Test_ID')[target_col].mean().reset_index().sort_values('Test_ID')
            
            y_min = trend[target_col].min()
            y_max = trend[target_col].max()
            # Handle flat line case
            if y_min == y_max:
                y_range = [y_min * 0.95, y_max * 1.05] if y_min != 0 else [0, 1]
            else:
                y_range = [y_min * 0.95, y_max * 1.05]

            fig = px.line(trend, x='Test_ID', y=target_col, markers=True, text=target_col)
            fig.update_layout(
                height=150, margin=dict(t=10, b=10, l=0, r=0),
                xaxis=dict(
                    visible=True, title=None, tickfont=dict(size=10),
                    type='category', categoryorder='array', categoryarray=all_test_ids # Enforce all IDs
                ), 
                yaxis=dict(visible=False, range=y_range),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x unified'
            )
            fig.update_traces(
                line_color='#1B263B', line_width=2, 
                marker_size=6, marker_color='#1B263B',
                texttemplate='%{y:.1f}', textposition='top center'
            )

            # Flex Layout
            c1, c2 = st.columns([0.4, 0.6])
            with c1:
                 st.markdown(f"""
                 <div style="margin-top: 5px;">
                    <div style="font-size: 12px; font-weight: 700; color: #415A77; margin-bottom: 2px;">
                        {title} <span title="{desc}" style="cursor:help; color:#adb5bd;">ⓘ</span>
                    </div>
                    <div style="font-size: 24px; font-weight: 900; color: #1B263B; line-height: 1;">
                        {mean_val:.1f}<span style="font-size: 12px; font-weight: 600; color: #8D99AE; margin-left: 2px;">{unit}</span>
                    </div>
                 </div>
                 """, unsafe_allow_html=True)
            with c2:
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            return target_col

        group = METRIC_GROUPS.get(protocol_tab)
        active_cols = []
        if group:
            metrics = group['metrics']
            n_cols = 2
            rows = [metrics[i:i + n_cols] for i in range(0, len(metrics), n_cols)]
            for row in rows:
                cols = st.columns(n_cols)
                for idx, m in enumerate(row):
                     m_idx = metrics.index(m)
                     with cols[idx]:
                         with st.container(border=True): # Card Style
                             ac = render_metric_card(
                                 p_df, m, group['names'][m_idx], group['units'][m_idx], 
                                 group.get('desc', [""]*len(metrics))[m_idx],
                                 sorted(df['Test_ID'].unique()) # Pass all Test IDs (global)
                            )
                             if ac: active_cols.append((group['names'][m_idx], ac))

        if active_cols:
             st.write("")
             with st.container(border=True):
                st.markdown('<div class="section-title">팀 비교 (Team Comparison)</div>', unsafe_allow_html=True)
                sel_n, sel_c = active_cols[0]
                if len(active_cols) > 1:
                    sel_n = st.selectbox("비교할 지표 선택", [ac[0] for ac in active_cols], label_visibility="collapsed")
                    sel_c = [ac[1] for ac in active_cols if ac[0] == sel_n][0]
                
                p_df[sel_c] = pd.to_numeric(p_df[sel_c], errors='coerce')
                comp_df = p_df.dropna(subset=[sel_c]).groupby('Team')[sel_c].mean().reset_index()
                
                if not comp_df.empty:
                    y_min = comp_df[sel_c].min()
                    y_max = comp_df[sel_c].max()
                    if y_min == y_max:
                        y_range = [y_min * 0.95, y_max * 1.05] if y_min != 0 else [0, 1]
                    else:
                        y_range = [y_min * 0.95, y_max * 1.05]

                    fig_comp = px.bar(comp_df, x='Team', y=sel_c, text_auto='.1f')
                    fig_comp.update_layout(
                        height=250, margin=dict(t=20, b=20, l=20, r=20),
                        xaxis_title=None, yaxis_title=None,
                        yaxis=dict(range=y_range), # Zoomed Y-axis
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    )
                    # Navy Single Color for clean look
                    fig_comp.update_traces(marker_color='#1B263B', width=0.4) 
                    avg_line = p_df[sel_c].mean()
                    fig_comp.add_hline(y=avg_line, line_width=1, line_dash="dash", line_color="#EF233C")
                    st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("비교할 데이터가 없습니다.")

    # ==========================================
    # Tab: Insight
    # ==========================================

    elif "인사이트" in selected_tab:
        # Insight Sidebar / Sub-nav
        insight_tab = st.radio("Insight_Nav", 
                               ["성숙도 (Maturation)", "상관관계 (Correlation Matrix)"], 
                               horizontal=True, label_visibility="collapsed", key="insight_sub_nav")
        st.write("")
        
        if "성숙도" in insight_tab:
             st.markdown('<div class="section-title">성숙도 분석 (Maturation Analysis)</div>', unsafe_allow_html=True)
             
             # Filter Section
             with st.container(border=True):
                 c_filter_1, c_filter_2 = st.columns([1, 2])
                 with c_filter_1:
                     all_test_ids = sorted([x for x in df['Test_ID'].unique() if pd.notna(x)], reverse=True)
                     sel_test_id = st.selectbox("측정 차수 선택 (Test ID)", ["All"] + all_test_ids, index=0)
                 with c_filter_2:
                     st.info("ℹ️ 현재 성숙도 분석은 **'중1 (Middle 1)'** 학년 데이터를 기준으로 수행됩니다.")

             sel_mat_grade = "중1"
             mat_df = df[df['Grade'] == sel_mat_grade].copy()
             if sel_test_id != 'All':
                 mat_df = mat_df[mat_df['Test_ID'] == sel_test_id]
             
             st.write("")

             if mat_df.empty:
                 st.warning(f"⚠️ {sel_test_id} 기간에 해당하는 '중1' 데이터가 없습니다.")
             else:
                 # Row 1: RAE | Scatter
                 r1_c1, r1_c2 = st.columns(2)
                 
                 # --- RAE (Relative Age Effect) ---
                 with r1_c1:
                     with st.container(border=True): # New Design Card
                         st.markdown('<div class="section-title">상대적 연령 효과 (RAE)</div>', unsafe_allow_html=True)
                         if 'Birth_Month' in mat_df.columns:
                             rae_month_counts = mat_df['Birth_Month'].value_counts().reindex(range(1, 13), fill_value=0).reset_index()
                             rae_month_counts.columns = ['Month', 'Count']
                             
                             def get_quarter_color(m):
                                 if m <= 3: return 'Q1'
                                 elif m <= 6: return 'Q2'
                                 elif m <= 9: return 'Q3'
                                 else: return 'Q4'
                             rae_month_counts['Quarter'] = rae_month_counts['Month'].apply(get_quarter_color)
                             
                             # Custom Navy Palette for Quarters
                             q_colors = {'Q1':'#1B263B', 'Q2':'#415A77', 'Q3':'#778DA9', 'Q4':'#E0E1DD'} 
                             
                             fig_rae = px.bar(
                                 rae_month_counts, x='Month', y='Count', 
                                 color='Quarter',
                                 color_discrete_map=q_colors,
                                 text='Count'
                             )
                             fig_rae.update_layout(
                                 height=350, margin=dict(t=10, b=10, l=10, r=10),
                                 xaxis=dict(tickmode='linear', tick0=1, dtick=1, title="월 (Month)", showgrid=False),
                                 yaxis=dict(showgrid=True, gridcolor='#f1f1f1'),
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                             )
                             
                             q1_sum = rae_month_counts[rae_month_counts['Quarter']=='Q1']['Count'].sum()
                             q4_sum = rae_month_counts[rae_month_counts['Quarter']=='Q4']['Count'].sum()
                             ratio = q1_sum / q4_sum if q4_sum > 0 else 0
                             
                             # Add Caption as Annotation for Perfect Alignment
                             fig_rae.add_annotation(
                                 text=f"📌 Q1(1~3월) vs Q4(10~12월) 비율: <b>{ratio:.1f}배</b>",
                                 xref="paper", yref="paper",
                                 x=0, y=-0.25, showarrow=False,
                                 font=dict(size=12, color="#8D99AE")
                             )
                             
                             st.plotly_chart(fig_rae, use_container_width=True, config={'displayModeBar': False})

                 # --- Scatter (APHV vs Month) ---
                 with r1_c2:
                      with st.container(border=True):
                         st.markdown('<div class="section-title">출생 월별 성숙도 (Month vs APHV)</div>', unsafe_allow_html=True)
                         if 'APHV' in mat_df.columns and 'Birth_Month' in mat_df.columns:
                             if 'Maturity_Cat' not in mat_df.columns:
                                  def get_mat_cat(aphv):
                                     if pd.isna(aphv): return "Unknown"
                                     if aphv < 13.1: return 'Early (조기)'
                                     elif aphv <= 15.1: return 'Average (평균)'
                                     else: return 'Late (만기)'
                                  mat_df['Maturity_Cat'] = mat_df['APHV'].apply(get_mat_cat)

                             mat_df['Date_Seasonality'] = mat_df['Birth_date'].apply(lambda x: x.replace(year=2000) if pd.notnull(x) else pd.NaT)
                             
                             # Navy/Red Highlight Colors
                             mat_colors = {'Early (조기)':'#EF233C', 'Average (평균)':'#415A77', 'Late (만기)':'#1B263B'}
                             
                             fig_scat = px.scatter(
                                 mat_df, x='Date_Seasonality', y='APHV',
                                 color='Maturity_Cat',
                                 color_discrete_map=mat_colors,
                                 hover_data=['Player']
                             )
                             fig_scat.update_layout(
                                 height=350, margin=dict(t=10, b=10, l=10, r=10),
                                 xaxis=dict(title="월 (Month)", tickformat="%m월", dtick="M1", showgrid=True, gridcolor='#f1f1f1'),
                                 yaxis=dict(title="APHV", showgrid=True, gridcolor='#f1f1f1'),
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                             )
                             st.plotly_chart(fig_scat, use_container_width=True, config={'displayModeBar': False})


                 st.write("")
                 
                 # Row 2: Distribution | Velocity
                 r2_c1, r2_c2 = st.columns(2)
                 
                 with r2_c1:
                     with st.container(border=True):
                         st.markdown('<div class="section-title">성숙도 분포 (APHV Distribution)</div>', unsafe_allow_html=True)
                         if 'APHV' in mat_df.columns:
                             import plotly.figure_factory as ff
                             hist_vals = mat_df['APHV'].dropna()
                             if len(hist_vals) > 1:
                                 # Distplot with Navy color
                                 fig_dist = ff.create_distplot([hist_vals], ['APHV'], show_hist=False, show_rug=False, colors=['#1B263B'])
                                 
                                 # Shaded Regions (Standard)
                                 fig_dist.add_vrect(x0=10, x1=13.1, fillcolor="#EF233C", opacity=0.1, annotation_text="Early")
                                 fig_dist.add_vrect(x0=13.1, x1=15.1, fillcolor="#8D99AE", opacity=0.1, annotation_text="Avg")
                                 fig_dist.add_vrect(x0=15.1, x1=18, fillcolor="#2B2D42", opacity=0.1, annotation_text="Late")
                                 
                                 fig_dist.update_layout(
                                     height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False,
                                     plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
                                 )
                                 st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
                             else:
                                 st.info("데이터 부족")

                 with r2_c2:
                     with st.container(border=True):
                         st.markdown('<div class="section-title">성장 속도 (Growth Velocity)</div>', unsafe_allow_html=True)
                         target_players = mat_df['Player'].unique()
                         history_df = df[df['Player'].isin(target_players)].copy()
                         velocities = []
                         if not history_df.empty:
                             history_df = history_df.sort_values(['Player', 'Age'])
                             for p in target_players:
                                  p_df = history_df[history_df['Player'] == p]
                                  if len(p_df) > 1:
                                     p_df['H_Diff'] = p_df['Height'].diff()
                                     p_df['Age_Diff'] = p_df['Age'].diff()
                                     p_df = p_df[p_df['Age_Diff'] > 0] # Avoid zero division
                                     p_df['Velocity'] = p_df['H_Diff'] / p_df['Age_Diff']
                                     # Filter unreasonable values
                                     p_df = p_df[(p_df['Velocity'] > 0) & (p_df['Velocity'] < 20) & (p_df['Age_Diff'] > 0.5)]
                                     if not p_df.empty:
                                         velocities.append(p_df[['Age', 'Velocity']])
                         
                         if velocities:
                             vel_df = pd.concat(velocities)
                             vel_df['Age_Rounded'] = vel_df['Age'].apply(lambda x: round(x * 2) / 2)
                             avg_vel = vel_df.groupby('Age_Rounded')['Velocity'].mean().reset_index()
                             
                             fig_vel = px.line(avg_vel, x='Age_Rounded', y='Velocity', markers=True)
                             fig_vel.update_layout(
                                 height=300, margin=dict(t=10, b=10, l=10, r=10),
                                 xaxis_title="나이 (Age)", yaxis_title="성장 속도 (cm/year)",
                                 plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
                             )
                             fig_vel.update_traces(line_color='#1B263B', line_width=3, marker_size=6)
                             
                             # Peak Height Velocity Zone
                             fig_vel.add_vrect(x0=13.5, x1=14.5, fillcolor="#EF233C", opacity=0.1, annotation_text="PHV Zone")
                             st.plotly_chart(fig_vel, use_container_width=True, config={'displayModeBar': False})
                         else:
                             st.info("연속 측정 데이터가 부족하여 성장 속도를 계산할 수 없습니다.")
        
        elif "상관관계" in insight_tab:
            st.info("🚧 준비 중입니다 (상관관계 분석)")


    # ==========================================
    # Tab: Player (선수 상세) - NEW!
    # ==========================================
    elif "Player" in selected_tab:
        st.markdown('<div class="section-title">선수 상세 분석 (Player Profile)</div>', unsafe_allow_html=True)
        st.info("🔎 원하는 선수를 검색하여 상세 리포트를 확인하세요.")
        
        # 1. Hierarchical Filters (Team -> Under -> Player)
        c_team, c_under, c_player, c_test = st.columns(4)
        
        # A. Team Filter
        teams = sorted([x for x in df['Team'].unique() if pd.notna(x)])
        sel_team = c_team.selectbox("소속팀 (Team)", ["All"] + teams)
        
        # Link DF
        df_team = df if sel_team == "All" else df[df['Team'] == sel_team]
        
        # B. Under Filter
        unders = sorted([str(x) for x in df_team['Under'].unique() if pd.notna(x)])
        sel_under = c_under.selectbox("연령 (Under)", ["All"] + unders)
        
        # Link DF
        df_under = df_team if sel_under == "All" else df_team[df_team['Under'].astype(str) == sel_under]
        
        # C. Player Filter
        players = sorted([x for x in df_under['Player'].unique() if pd.notna(x)])
        sel_player_name = c_player.selectbox("선수 (Player)", ["Select..."] + players)
        
        if sel_player_name and sel_player_name != "Select...":
            # Filter Data
            p_history = df[df['Player'] == sel_player_name].copy()
            if p_history.empty:
                st.error("선수 데이터를 찾을 수 없습니다.")
            else:
                # D. Test_ID Filter (Specific to Radar)
                all_test_ids = sorted(p_history['Test_ID'].unique(), reverse=True)
                sel_test_id = c_test.selectbox("측정 차수 (Test ID)", all_test_ids, index=0)
                
                # Target Data for Radar & Profile
                latest_data = p_history[p_history['Test_ID'] == sel_test_id].iloc[0]
                
                # --- A. Player Profile Card ---
                with st.container(border=True):
                    prof_c1, prof_c2, prof_c3, prof_c4, prof_c5 = st.columns(5)
                    prof_c1.metric("이름 (Name)", latest_data['Player'])
                    prof_c2.metric("소속팀 (Team)", latest_data['Team'])
                    prof_c3.metric("학년 (Grade)", latest_data['Grade'])
                    
                    pos_val = latest_data.get('Position', latest_data.get('Main_Position', '-'))
                    prof_c4.metric("포지션 (Position)", pos_val)
                    
                    # Age (if DOB exists)
                    age_val = "-"
                    if 'Birth_date' in latest_data and pd.notnull(latest_data['Birth_date']):
                        try:
                            b_year = pd.to_datetime(latest_data['Birth_date']).year
                            c_year = pd.Timestamp.now().year
                            age_val = c_year - b_year
                        except: pass
                    prof_c5.metric("나이 (Age)", f"{age_val}세")

                st.write("")
                
                # --- B. Radar Chart (10-Point Score) ---
                row2_c1, row2_c2 = st.columns([1, 1])
                
                with row2_c1:
                    with st.container(border=True):
                        st.markdown('<div class="section-title">능력치 오각형 (Performance Radar)</div>', unsafe_allow_html=True)
                        st.caption(f"📌 측정 지표별 **10점 만점 환산 점수**입니다.")
                        
                        # 1. Identify all "Point" columns
                        all_point_cols = [c for c in df.columns if 'Point_' in c or 'Point' in c and df[c].dtype in ['float64', 'int64']]
                        # Filter out some non-metric points if any, but usually they are fine.
                        # Refine filtering to ensure they are the ones we want (ending in Point_ or Point)
                        all_point_cols = sorted([c for c in df.columns if c.endswith('Point_') or c.endswith('Point')])
                        
                        # 2. Define Defaults (User Requested) with Fuzzy Matching
                        # User: Strength_Sum_Point_, _CMJ_Height_Point_, _5m_sec__Point_, _30m_sec__Point_, COD_ball_Point_
                        
                        target_defaults = [
                            'strength_sum_point', 'strength_sum_point_', 
                            'cmj_height_point', 'cmj_height_point_', 'cmj_height_cm_point_',
                            '_5m_sec__point_', '5m_sec__point_',
                            '_30m_sec__point_', '30m_sec__point_',
                            'cod_ball_point_', 'cod_ball_point'
                        ]
                        
                        default_cols = []
                        lower_map = {c.lower(): c for c in all_point_cols}
                        
                        # Custom search for specific functional groups
                        # 1. Strength Sum
                        for k in lower_map:
                            if 'strength' in k and 'sum' in k and 'point' in k:
                                default_cols.append(lower_map[k])
                                break
                        
                        # 2. CMJ Height
                        for k in lower_map:
                            if 'cmj' in k and 'height' in k and 'point' in k:
                                default_cols.append(lower_map[k])
                                break
                                
                        # 3. 5m Sprint
                        for k in lower_map:
                            if '5m' in k and 'point' in k and 'sec' in k:
                                default_cols.append(lower_map[k])
                                break
                                
                        # 4. 30m Sprint
                        for k in lower_map:
                            if '30m' in k and 'point' in k and 'sec' in k:
                                default_cols.append(lower_map[k])
                                break
                                
                        # 5. COD Ball (or just COD if Ball missing)
                        for k in lower_map:
                            if 'cod' in k and 'ball' in k and 'point' in k:
                                default_cols.append(lower_map[k])
                                break
                        
                        # Remove duplicates
                        default_cols = list(dict.fromkeys(default_cols))
                        
                        # Fallback if defaults missing
                        if len(default_cols) < 3:
                            default_cols = all_point_cols[:5]
                            
                        # 3. Multiselect
                        sel_radar_cols = st.multiselect("지표 선택 (Select Metrics)", all_point_cols, default=default_cols)
                        
                        if len(sel_radar_cols) < 3:
                            st.warning("최소 3개 이상의 지표를 선택해주세요.")
                        else:
                            # 4. Prepare Data
                            radar_values = []
                            valid_metrics = []
                            
                            for col in sel_radar_cols:
                                val = pd.to_numeric(latest_data.get(col), errors='coerce')
                                if pd.notna(val):
                                    radar_values.append(val)
                                    # Label Cleaning: remove underscores and 'Point' for cleaner chart
                                    label = col.replace('_Point_', '').replace('_Point', '').replace('_', ' ').strip()
                                    valid_metrics.append(label)
                                else:
                                    radar_values.append(0) # or skip? Better to show 0 for missing
                                    label = col.replace('_Point_', '').replace('_Point', '').replace('_', ' ').strip()
                                    valid_metrics.append(label)

                            # World Class Radar Design
                            fig_radar = go.Figure()
                            
                            fig_radar.add_trace(go.Scatterpolar(
                                r=radar_values,
                                theta=valid_metrics,
                                fill='toself',
                                name=latest_data['Player'],
                                line=dict(color='#1B263B', width=2),
                                fillcolor='rgba(27, 38, 59, 0.4)',
                                marker=dict(size=6, color='#FFD700', symbol='circle', line=dict(color='#1B263B', width=1)), # Gold Markers
                            ))
                            
                            fig_radar.update_layout(
                                polar=dict(
                                    radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10, color='#8D99AE'), gridcolor='#e0e0e0', linecolor='rgba(0,0,0,0)'),
                                    angularaxis=dict(tickfont=dict(size=12, weight='bold', color='#1B263B'), gridcolor='#e0e0e0', linecolor='rgba(0,0,0,0)'),
                                    bgcolor='rgba(255,255,255,0.8)'
                                ),
                                showlegend=False,
                                height=400, # Fixed Height for Alignment
                                margin=dict(t=40, b=40, l=40, r=40),
                                paper_bgcolor='rgba(0,0,0,0)',
                            )
                            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})


                # --- C. Longitudinal History (Growth) ---
                with row2_c2:
                    with st.container(border=True):
                        st.markdown('<div class="section-title">성장 리포트 (Growth History)</div>', unsafe_allow_html=True)
                        
                        # Height & Weight Twin Axis
                        p_history['Test_ID'] = p_history['Test_ID'].astype(str)
                        p_history = p_history.sort_values('Test_ID')
                        
                        if 'Height' in p_history.columns and 'Weight' in p_history.columns:
                             # Create figure with secondary y-axis
                             from plotly.subplots import make_subplots
                             fig_growth = make_subplots(specs=[[{"secondary_y": True}]])
                             
                             # Add Height
                             fig_growth.add_trace(
                                 go.Scatter(x=p_history['Test_ID'], y=p_history['Height'], name="신장(cm)", mode='lines+markers', line=dict(color='#1B263B')),
                                 secondary_y=False,
                             )
                             # Add Weight
                             fig_growth.add_trace(
                                 go.Bar(x=p_history['Test_ID'], y=p_history['Weight'], name="체중(kg)", marker=dict(color='#8D99AE', opacity=0.3)),
                                 secondary_y=True,
                             )
                             
                             fig_growth.update_layout(
                                 height=400, margin=dict(t=20, b=20, l=20, r=20), # Aligned Height
                                 plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                             )
                             fig_growth.update_yaxes(title_text="신장 (cm)", secondary_y=False, showgrid=False)
                             fig_growth.update_yaxes(title_text="체중 (kg)", secondary_y=True, showgrid=False)
                             
                             st.plotly_chart(fig_growth, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.info("신장/체중 데이터가 없습니다.")

                # --- D. Recent Performance Table ---
                st.write("")
                with st.container(border=True):
                    st.markdown('<div class="section-title">최근 측정 기록 (Latest Metrics)</div>', unsafe_allow_html=True)
                    
                    # Display top 5 key metrics vertically or horizontally
                    disp_cols = ['Test_ID', 'Height', 'Weight', '5m_sec', '10m_sec', '30m_sec', 'CmJ_Height_cm', 'IMTP_N']
                    disp_cols = [c for c in disp_cols if c in p_history.columns]
                    
                    st.dataframe(
                        p_history[disp_cols].sort_values('Test_ID', ascending=False).style.format("{:.1f}", subset=pd.IndexSlice[:, p_history[disp_cols].select_dtypes(include='float').columns]),
                        use_container_width=True,
                        hide_index=True
                    )

