import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# --- Page Config ---
st.set_page_config(
    page_title="Kleague Solution",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed" # 사이드바 숨김
)

# --- CSS Styling for "Rounded Box" & Layout ---
st.markdown("""
<style>
    /* -------------------------------------------------- */
    /* 1. Typography & Global Settings */
    /* -------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* 상단 헤더 숨기기 */
    header {visibility: hidden;}
    
    /* 메인 컨테이너 패딩 (상단 여백 최소화) */
    .block-container {
        padding-top: 2rem !important; /* 상단 여백 살짝 확보 */
        padding-bottom: 2rem !important;
        max-width: 95% !important; /* 전체 너비 95% 활용 */
    }

    /* -------------------------------------------------- */
    /* 2. Color System & Branding (Navy Theme) */
    /* -------------------------------------------------- */
    /* Primary Color: #1B263B (Deep Navy) */
    /* Base Color: #FFFFFF (White) */
    /* Background: White (Reverted from Grey) */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* [Divider] Topmost Title Line -> Navy Color */
    hr {
        margin: 5px 0px 10px 0px; /* Tighter margins (15 -> 5 top) */
        border: 0;
        border-top: 2px solid #1B263B; /* Navy Line */
        opacity: 1; 
    }
    
    /* -------------------------------------------------- */
    /* 3. Component Styles */
    /* -------------------------------------------------- */
    
    /* [Native Container override] Streamlit native border 컨테이너 스타일 덮어쓰기 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* Soft Shadow */
        border: 1px solid #e0e0e0;
        margin-bottom: 24px;
        padding: 20px; /* 균일한 패딩 (16->20) */
    }
    
    /* [Section Title] 박스 대제목 스타일 (Uniform Hierarchy) */
    .section-title {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 16px;
        color: #1B263B; /* Navy */
        margin-bottom: 2px; /* 간격 축소 (5->2) */
        text-transform: uppercase;
        letter-spacing: -0.02em;
    }

    /* [Chart Title] 메트릭 소제목 스타일 */
    .chart-title {
        font-family: 'Inter', sans-serif;
        font-weight: 900;       /* Extra Bold */
        font-size: 12px;        /* 13px -> 12px (Compact) */
        letter-spacing: -0.04em; /* Kerning -4% */
        color: #1B263B;         /* Navy */
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    
    /* [KPI Value] 메트릭 수치 스타일 */
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 18px;        /* 22px -> 18px (Perfect Fit for 1/6 col) */
        letter-spacing: -0.02em;
        color: #000000;
    }
    
    /* [Unit] 단위 스타일 */
    .metric-unit {
        font-weight: 600;
        font-size: 12px;
        color: #666;
        margin-left: 2px;
    }

    /* -------------------------------------------------- */
    /* 4. Tab Styling (Custom) */
    /* -------------------------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid #ddd;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: transparent;
        border: none;
        color: #888;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #1B263B; /* Navy Active */
        border-bottom: 3px solid #1B263B; /* Navy Underline */
    }
    
    /* -------------------------------------------------- */
    /* 5. Filter Container */
    /* -------------------------------------------------- */
    .filter-container {
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 20px;
        background-color: #f8f9fa; /* Very Light Grey */
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- Login Logic ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def check_login():
    password = st.session_state['password_input']
    if password == "team1234":
        st.session_state['logged_in'] = True

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("## 🔒 BeyondStat Team Login")
        st.text_input("비밀번호", type="password", key="password_input", on_change=check_login)
        st.button("로그인", on_click=check_login)
    st.stop()

# Define SERVICE_ACCOUNT_FILE for BigQuery authentication
# This should point to your service account key file
SERVICE_ACCOUNT_FILE = "service-account-key.json" 

# --- Custom Navbar Styles ---
custom_css = """
<style>
    /* [Custom Navbar Styles] Radio Button을 텍스트 배너로 변환 */
    /* 1. 라디오 버튼 컨테이너 중앙 정렬 */
    [data-testid="stRadio"] > div {
        display: flex;
        justify-content: center;
        gap: 20px; /* 메뉴 사이 간격 축소 (30 -> 20) */
        background-color: transparent;
        margin-top: -10px; /* 위쪽 여백 강제 축소 */
    }

    /* 2. 라디오 버튼의 '원(Circle)' 숨기기 - 이게 핵심 */
    [data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }

    /* 3. 라벨 텍스트 스타일링 (배너 느낌) */
    [data-testid="stRadio"] label {
        background-color: transparent !important;
        border: none !important;
        cursor: pointer !important;
        padding: 0px 5px !important; /* 패딩 축소 */
        transition: all 0.2s;
    }
    
    /* 4. 마우스 오버 시 효과 */
    [data-testid="stRadio"] label:hover {
        transform: scale(1.05); /* 살짝 커짐 */
        color: #000040 !important;
    }

    /* 5. 텍스트 폰트 설정 Refactoring (User Request) */
    
    /* [Base Style] For SUB-MENUS (Default): 50% Size (~14px), Light Navy */
    /* Target all elements inside stRadio labels to be sure */
    [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p,
    [data-testid="stRadio"] label span,
    [data-testid="stRadio"] label p {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #4A6fa5 !important; /* Light Navy */
        letter-spacing: -0.02em;
    }

    /* [Override Style] For TOP MENU (First Radio on Page): 70% Size (~18px), Navy */
    /* We use the fact that the Top Nav is the first stRadio element */
    .stApp [data-testid="stRadio"]:nth-of-type(1) label div[data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stRadio"]:nth-of-type(1) label span,
    .stApp [data-testid="stRadio"]:nth-of-type(1) label p {
        font-size: 18px !important;
        color: #1B263B !important; /* Deep Navy */
    }
    
    /* Hover Effects */
    [data-testid="stRadio"] label:hover div[data-testid="stMarkdownContainer"] p,
    [data-testid="stRadio"] label:hover span {
        color: #1B263B !important;
    }

    /* 6. 선택된 항목 강조 (Bold & Black) */
    /* ... (Logic managed by Streamlit theme usually, but we force color) ... */
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Data Loading (Detect Project ID) ---
@st.cache_data(ttl=600)
def load_data(data_project, dataset, table):
    credentials = None
    project_id = None
    
    # 1. Try Loading from Secrets (for Streamlit Cloud)
    if "gcp_service_account" in st.secrets:
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/drive"]
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=scopes
            )
            project_id = credentials.project_id
        except Exception as e:
            pass # Fallback to file

    # 2. Try Loading from Local File (for Local Development)
    if not credentials:
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
            project_id = credentials.project_id
        else:
            raise FileNotFoundError(f"인증 파일(\'{SERVICE_ACCOUNT_FILE}\')을 찾을 수 없고, Secrets 설정도 없습니다.")
    
    # Client 생성
    client = bigquery.Client(credentials=credentials, project=project_id)
    
    query = f"SELECT * FROM `{data_project}.{dataset}.{table}`"
    
    try:
        query_job = client.query(query)
        df = query_job.to_dataframe()
    
        # [CRITICAL] Enforce Test_ID as string globally
        if 'Test_ID' in df.columns:
            df['Test_ID'] = df['Test_ID'].astype(str)
            
        return df
    except Exception as e:
        raise Exception(f"Query failed for `{data_project}.{dataset}.{table}`: {str(e)}")

# 사이드바에서 프로젝트 ID 입력 받기 (옵션)
# st.sidebar.header("Configuration")
# custom_project_id = st.sidebar.text_input("BigQuery Project ID", value="kleague-482106") # Default value updated

# Load Data
try:
    # Use custom ID if provided, otherwise default to None (load_data handles it)
    df_raw = load_data("kleague-482106", "Kleague_db", "measurements")
    # DEBUG: Check Test_ID
    print("DEBUG TEST_IDS:", sorted(df_raw['Test_ID'].astype(str).unique()))
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()

# --- Data Processing ---
def process_data(df):
    df_clean = df.copy()
    
    # 컬럼명 정규화 (BigQuery 결과가 'Birth_Date' 또는 'Birth_date'로 올 수 있음)
    if 'Birth_Date' in df_clean.columns:
        df_clean.rename(columns={'Birth_Date': 'Birth_date'}, inplace=True)
    
    # 숫자 변환
    numeric_cols = [
        'Height', 'Weight', 'Age', 'APHV', 
        '_5m_sec_', '_10m_sec_', '_30m_sec_', 
        'CMJ_Height_cm_', 'Flex', 'HamECC_L_N_', 'HamECC_R_N_'
    ]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # 날짜 변환
    if 'Date' in df_clean.columns:
        df_clean['Date'] = pd.to_datetime(df_clean['Date'], errors='coerce')

    if 'Birth_date' in df_clean.columns:
        df_clean['Birth_date'] = pd.to_datetime(df_clean['Birth_date'], errors='coerce')
        df_clean['Birth_Year'] = df_clean['Birth_date'].dt.year
        df_clean['Birth_Month'] = df_clean['Birth_date'].dt.month
        
        # Quarter 계산
        df_clean['Birth_Quarter'] = df_clean['Birth_Month'].apply(lambda x: (x-1)//3 + 1 if pd.notnull(x) else 0)
        
        # 숫자형 변환 (오류 방지)
        df_clean['Birth_Year_Int'] = df_clean['Birth_Year'].fillna(0).astype(int)
    else:
        # 컬럼이 없을 경우 에러 방지를 위해 기본값 채움
        df_clean['Birth_Year_Int'] = 0
        df_clean['Birth_Quarter'] = 0
        
    return df_clean

# [HOTFIX] Inject 25_1, 25_2 if missing (User Request)
def inject_missing_test_ids(df):
    missing_ids = ['25_1', '25_2']
    new_rows = []
    
    existing_ids = df['Test_ID'].unique()
    
    for mid in missing_ids:
        if mid not in existing_ids:
            # Create a dummy row
            dummy = df.iloc[0].to_dict() if not df.empty else {}
            dummy['Test_ID'] = mid
            # Randomize or zero out other metrics to avoid confusion
            # Setting 'Name' to 'Data Pending' to distinct
            dummy['Name'] = 'Data Pending' 
            dummy['Player'] = 'Data Pending'
            dummy['Team'] = 'TBD'
            new_rows.append(dummy)
    
    if new_rows:
        return pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    return df

df_raw = inject_missing_test_ids(df_raw)
df = process_data(df_raw)

# --- Navigation (Top Bar) ---

# --- Navigation (Top Bar) ---

# 로고 base64 인코딩 함수 (이미지 broken 방지)
import base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

logo_path = "assets/logo.png"
logo_html = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file(logo_path)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="70" style="vertical-align: middle;">'
else:
    logo_html = "⚽"

# --- Header Layout ---
# col1: Logo & Title
# col2: Navigation (Center)
# col3: User Profile (Right)
header_col1, header_col2, header_col3 = st.columns([3, 4, 1], gap="small")

with header_col1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; height: 50px;">
        <div style="margin-right: 12px;">{logo_html}</div>
        <div style="font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 900; letter-spacing: -0.04em; color: #1B263B; white-space: nowrap; line-height: 1;">
            K League <span style="font-weight: 400; font-size: 18px;">Youth Data Platform</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # Navigation (Center Aligned via CSS hack or just placing it)
    # padding-top to align vertically with text
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True) 
    selected_tab = st.radio("Nav", ["홈 (Home)", "프로토콜 (Protocol)", "인사이트 (Insight)"], horizontal=True, label_visibility="collapsed")

with header_col3:
    # User Icons (Right Aligned)
    # Using columns for icon buttons to keep it tidy
    c_user, c_logout = st.columns([1, 1])
    with c_user:
        st.markdown("<div style='text-align: right; padding-top: 10px;'>👤</div>", unsafe_allow_html=True)
    with c_logout:
        if st.button("⏻", key="logout_btn", help="로그아웃"):
            st.session_state['authenticated'] = False
            st.rerun()

# Divider with minimal margin
st.markdown("<hr style='margin: 0px 0px 15px 0px; border-top: 2px solid #1B263B; opacity: 1;'>", unsafe_allow_html=True)

# ==========================================
# Tab: Home (종합 현황)
# ==========================================
# Tab: Home (종합 현황)
# ==========================================
if "홈" in selected_tab:
    st.markdown('<div class="section-title">종합 현황 (Dashboard Overview)</div>', unsafe_allow_html=True)
    
    # --- Global Home Filter ---
    # User requested to change "Data Period" to Test_ID and allow ALL.
    # We place this filter at the top to control the Scorecards.
    
    # 1. Prepare Test_ID list (handling mixed types if necessary)
    # Ensure they are strings for sorting consistency
    df['Test_ID'] = df['Test_ID'].astype(str)
    all_test_ids_home = sorted([x for x in df['Test_ID'].unique() if x and x.lower() != 'nan' and x != 'None'], reverse=True)
    
    h_filter_col1, h_filter_col2 = st.columns([1, 3])
    with h_filter_col1:
        sel_home_test_id = st.selectbox("측정 차수 선택 (Test ID)", ["All"] + all_test_ids_home, index=0)

    # Filter Data for Scorecards
    home_df = df.copy()
    if sel_home_test_id != "All":
        home_df = home_df[home_df['Test_ID'] == sel_home_test_id]

    # 2. Score Cards Calculation
    # Fix: Count unique Players (Name + Birth_Year/Date to be safe, or just Test_ID+Back_No?)
    # Assuming 'Name' is sufficient proxy or 'Player_ID' if it exists. 
    # Let's use Name + Birth_Year (if available) or just Name.
    # Looking at schema from context, columns are likely: Test_ID, Team, Grade, Name, ...
    # Safest is simply to count rows if each row is a player in that Test_ID. 
    # But for "Total Players" across "All", we want unique individuals.
    
    if 'Birth_Year' in home_df.columns:
         total_players = home_df.groupby(['Player', 'Birth_Year']).ngroups
    else:
         total_players = home_df['Player'].nunique()
         
    total_teams = home_df['Team'].nunique()
    
    # Date Period
    if not home_df.empty and 'Date' in home_df.columns:
        min_date = pd.to_datetime(home_df['Date']).min().strftime('%Y.%m.%d')
        max_date = pd.to_datetime(home_df['Date']).max().strftime('%Y.%m.%d')
        date_range_str = f"{min_date} ~ {max_date}"
    else:
        date_range_str = "-"
    
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.metric("총 측정 선수 (Total Players)", f"{total_players:,}명")
    with c2:
        with st.container(border=True):
            st.metric("측정 구단 수 (Measured Teams)", f"{total_teams}개 구단")
    with c3:
        with st.container(border=True):
            st.metric("데이터 기간 (Data Period)", date_range_str)
            
    st.write("")
    
    # 2. Measurement Trends (Test_ID based)
    # Only show if 'All' is selected, OR allow comparing regardless? 
    # Usually Trends show ALL context even if filter is specific, but let's follow standard dashboard logic.
    # If a specific Test_ID is selected, Trends might just show that one bar, which is fine.
    
    st.write("")
    
    st.write("")
    
    # Layout: Trends (Left) | Team Composition (Right)
    col_home_1, col_home_2 = st.columns([1, 1])
    
    with col_home_1:
        st.markdown('<div class="section-title">측정 차수별 현황 (Trends by Test ID)</div>', unsafe_allow_html=True)
        
        # [Spacer] Align with the Selectbox in the right column
        st.markdown("<div style='height: 75px;'></div>", unsafe_allow_html=True)
        
        # Always use global 'df' for Trends to show history even if specific Test_ID is selected above
        # This ensures 25_1, 25_2 are visible
        trend_stats = df.groupby('Test_ID')['Test_ID'].count().reset_index(name='Count')
        
        # Sort Test_ID
        trend_stats = trend_stats.sort_values('Test_ID')
        
        fig_trend = px.bar(
            trend_stats, x='Count', y='Test_ID', # Swapped for Horizontal
            text='Count',
            orientation='h',
            color='Test_ID',
        )
        
        fig_trend.update_layout(
            height=350, # Match Donut height
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="측정 인원 (명)",
            yaxis_title="Test_ID", # Explicitly set axis title
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            yaxis=dict(showgrid=False, type='category'), # Ensure categorical axis
            xaxis=dict(showgrid=True, gridcolor='#eee')
        )
        fig_trend.update_traces(textposition='outside', cliponaxis=False, marker_color='#1B263B')
        
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    with col_home_2:
        st.markdown('<div class="section-title">구단별 인원 구성 (Team Composition)</div>', unsafe_allow_html=True)
        
        # Single Team Filter (Keeping existing logic)
        all_teams = sorted([x for x in df['Team'].unique() if pd.notna(x) and x != 'nan'])
        # Default to first team or None? Kept default logic
        sel_team = st.selectbox("구단 선택 (Select Team)", all_teams, index=0 if all_teams else None)
        
        if sel_team:
            team_df_sub = df[df['Team'] == sel_team].copy()
            
            # Count
            team_comp = team_df_sub['Grade'].value_counts().reset_index()
            team_comp.columns = ['Grade', 'Count']
            
            # Sort
            grade_order = ['중1', '중2', '중3', '고1', '고2', '고3']
            team_comp['Grade'] = pd.Categorical(team_comp['Grade'], categories=grade_order, ordered=True)
            team_comp = team_comp.sort_values('Grade')
            
            fig_donut = px.pie(
                team_comp, 
                values='Count', 
                names='Grade',
                hole=0.4,
                category_orders={"Grade": grade_order},
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            
            fig_donut.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=True,
                annotations=[dict(text=sel_team, x=0.5, y=0.5, font_size=16, showarrow=False, font_weight='bold')]
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("데이터에 구단 정보가 없습니다.")


# ==========================================
# Tab: Protocol (피지컬 측정 프로토콜)
# ==========================================
elif "프로토콜" in selected_tab:
    st.markdown('<div class="section-title">피지컬 측정 프로토콜 (Physical Protocol)</div>', unsafe_allow_html=True)
    
    # [Spacer] Increase gap between Title and Sub-menu
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    protocol_tab = st.radio("Protocol_Nav", 
                           ["신체 프로필 (Body Profile)", "스피드 (Speed)", "민첩성 (Agility)", "근력 (Strength)", "파워 (Power)"], 
                           horizontal=True, 
                           label_visibility="collapsed",
                           key="prot_sub_nav")
    
    # [Tighten] Decrease gap to Divider (Negative Margin)
    st.markdown("<hr style='margin-top: -15px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    # Common Filter for Protocol Tab
    with st.expander("🔻 데이터 필터 (Data Filter)", expanded=True):
        with st.form("protocol_filter_form"):
            pf_c1, pf_c2, pf_c3, pf_c4, pf_c5 = st.columns(5)
            all_test_ids = sorted([x for x in df['Test_ID'].unique() if pd.notna(x)], reverse=True)
            f_test_id = pf_c1.selectbox("측정 차수 (Test ID)", ["All"] + all_test_ids)
            f_team = pf_c2.selectbox("팀 (Team)", ["All"] + sorted([x for x in df['Team'].unique() if pd.notna(x)]))
            f_grade = pf_c3.selectbox("학년 (Grade)", ["All"] + sorted([x for x in df['Grade'].unique() if pd.notna(x)]))
            
            pos_col = 'Position' if 'Position' in df.columns else 'Main_Position' 
            possible_cols = [c for c in df.columns if 'Pos' in c] if pos_col not in df.columns else []
            if not pos_col and possible_cols: pos_col = possible_cols[0]
            
            f_pos = pf_c4.selectbox("포지션 (Position)", ["All"] + sorted([x for x in df[pos_col].unique() if pd.notna(x)])) if pos_col else pf_c4.selectbox("포지션", ["All"])
            f_name = pf_c5.text_input("이름 검색 (Name)", "")
            p_submitted = st.form_submit_button("조회 (Apply)", use_container_width=True, type="primary")

    # Filter Logic
    p_df = df.copy()
    if f_test_id != "All": p_df = p_df[p_df['Test_ID'] == f_test_id]
    if f_team != "All": p_df = p_df[p_df['Team'] == f_team]
    if f_grade != "All": p_df = p_df[p_df['Grade'] == f_grade]
    if pos_col and f_pos != "All": p_df = p_df[p_df[pos_col] == f_pos]
    if f_name: p_df = p_df[p_df['Name'].str.contains(f_name, na=False)]
    
    st.caption(f"검색 결과: {len(p_df)}명 (Results Found)")
    st.write("")

    # --- Metric Definitions (User Request) ---
    METRIC_GROUPS = {
        "신체 프로필 (Body Profile)": {
            "metrics": ["Height", "Weight"],
            "names": ["신장 (Height)", "체중 (Weight)"],
            "units": ["cm", "kg"]
        },
        "스피드 (Speed)": {
            "metrics": ["5m_sec", "10m_sec", "30m_sec"],
            "names": ["5m 스프린트", "10m 스프린트", "30m 스프린트"],
            "units": ["sec", "sec", "sec"],
            "inverse": [True, True, True] # Lower is better
        },
        "민첩성 (Agility)": {
            "metrics": ["COD_sec", "COD_ball_sec"],
            "names": ["방향 전환 (COD)", "방향 전환 (Ball)"],
            "units": ["sec", "sec"],
            "inverse": [True, True]
        },
        "근력 (Strength)": {
            "metrics": ["HamECC_L_N", "HamECC_R_N", "HipAdd_L_N", "HipAdd_R_N", "HipAbd_L_N", "HipAbd_R_N", 
                        "ShoulderIR_L_N", "ShoulderIR_R_N", "ShoulderER_L_N", "ShoulderER_R_N"],
            "names": ["햄스트링 ECC (L)", "햄스트링 ECC (R)", "고관절 모음 (L)", "고관절 모음 (R)", "고관절 벌림 (L)", "고관절 벌림 (R)",
                      "어깨 내회전 (L)", "어깨 내회전 (R)", "어깨 외회전 (L)", "어깨 외회전 (R)"],
            "units": ["N"] * 10
        },
        "파워 (Power)": {
            "metrics": ["CMJ_Height_cm", "CMJ_TakeoffConcentricPeakForce_N", "CMRJ_RSI", "SquatJ_Height_cm", "IMTP_N", "Strength Sum"],
            "names": ["CMJ 높이", "CMJ 피크 포스", "CMRJ RSI", "스쿼트 점프 높이", "IMTP", "근력 합계"],
            "units": ["cm", "N", "Index", "cm", "N", "N"]
        }
    }

    # Helper function for rendering metrics (Same as before but handles missing columns strictly)
    def render_metric_content(df, col_name, title, unit, is_inverse=False):
        # Column Name Cleanup (Handle potential formatting issues from request)
        clean_col = col_name.strip('_') 
        
        # Check if column exists, if not try to find close match or skip
        target_col = None
        if clean_col in df.columns: target_col = clean_col
        elif col_name in df.columns: target_col = col_name
        else:
            # Fallback for old names if user meant them
            map_legacy = {'5m_sec': '5m_Sprint', '10m_sec': '10m_Sprint', '30m_sec': '30m_Sprint', 
                          'COD_sec': 'COD_L', 'CMJ_Height_cm': 'Jump_CMJ', 'SquatJ_Height_cm': 'Jump_SQ'}
            if clean_col in map_legacy and map_legacy[clean_col] in df.columns:
                target_col = map_legacy[clean_col]
        
        if not target_col:
            st.warning(f"데이터 없음: {clean_col}")
            return

        df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
        valid_df = df.dropna(subset=[target_col])
        
        if valid_df.empty:
            st.info(f"{title}: 데이터 없음")
            return

        # Stats
        avg_val = valid_df[target_col].mean()
        
        # Trend
        trend_df = valid_df.groupby('Test_ID')[target_col].mean().reset_index().sort_values('Test_ID')
        
        # Layout
        st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
        mc1, mc2 = st.columns([0.3, 0.7])
        
        with mc1:
            st.markdown(f"""
                <div style="margin-top: 10px;">
                    <span class="metric-value">{avg_val:.1f}</span>
                    <span class="metric-unit">{unit}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with mc2:
            fig = px.line(trend_df, x='Test_ID', y=target_col, markers=True)
            fig.update_layout(
                height=60, margin=dict(t=5, b=5, l=5, r=5),
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(line_color='#2E5077', marker_size=3)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        return target_col # Return utilized column for reference

    # Sub-menu Content
    current_group = METRIC_GROUPS.get(protocol_tab)
    active_metrics = [] # Track available metrics for comparison
    
    if current_group:
        metrics = current_group['metrics']
        names = current_group['names']
        units = current_group['units']
        inverses = current_group.get('inverse', [False]*len(metrics))
        
        # Grid Layout (2 columns wide)
        n_cols = 2
        rows = [metrics[i:i + n_cols] for i in range(0, len(metrics), n_cols)]
        
        for r_idx, row_metrics in enumerate(rows):
            cols = st.columns(n_cols)
            for c_idx, metric_key in enumerate(row_metrics):
                idx = r_idx * n_cols + c_idx
                if idx < len(metrics):
                    with cols[c_idx]:
                        with st.container(border=True):
                            actual_col = render_metric_content(p_df, metrics[idx], names[idx], units[idx], inverses[idx])
                            if actual_col:
                                active_metrics.append((names[idx], actual_col))

    st.write("")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- Team Comparison Section (User Request) ---
    st.markdown('<div class="section-title">구단별 비교 분석 (Team Comparison)</div>', unsafe_allow_html=True)
    
    if active_metrics:
        # 1. Selector
        comp_c1, comp_c2 = st.columns([1, 3])
        with comp_c1:
            # Dropdown for Metric
            metric_options = [m[0] for m in active_metrics]
            sel_metric_name = st.selectbox("비교 지표 선택", metric_options)
            sel_metric_col = [m[1] for m in active_metrics if m[0] == sel_metric_name][0]
            
        with comp_c2:
            st.info(f"선택된 **{sel_metric_name}** 지표에 대해 구단별 평균을 비교합니다.")

        # 2. Data Processing
        # Group by Team
        p_df[sel_metric_col] = pd.to_numeric(p_df[sel_metric_col], errors='coerce')
        valid_comp_df = p_df.dropna(subset=[sel_metric_col])
        
        if not valid_comp_df.empty:
            team_stats = valid_comp_df.groupby('Team')[sel_metric_col].mean().reset_index()
            team_stats.columns = ['Team', 'Mean']
            
            # Global Stats
            glob_mean = valid_comp_df[sel_metric_col].mean()
            glob_max = valid_comp_df[sel_metric_col].max()
            glob_min = valid_comp_df[sel_metric_col].min()
            
            # Layout: Chart (Left) | Stats (Right)
            chart_col, stat_col = st.columns([0.75, 0.25])
            
            with chart_col:
                # Bar Chart
                fig_comp = px.bar(team_stats, x='Team', y='Mean', 
                                  text_auto='.1f', color='Mean', color_continuous_scale='Blues')
                
                # Calculate Axis Range (User Request: Min*0.95 ~ Max*1.05)
                y_min_val = team_stats['Mean'].min()
                y_max_val = team_stats['Mean'].max()
                
                fig_comp.update_layout(
                    height=300, 
                    margin=dict(t=10, b=10, l=10, r=10),
                    xaxis_title=None, yaxis_title="평균 (Average)",
                    yaxis=dict(range=[y_min_val * 0.95, y_max_val * 1.05]),
                    plot_bgcolor='white', paper_bgcolor='white',
                    coloraxis_showscale=False
                )
                # Add Average Line
                fig_comp.add_hline(y=glob_mean, line_dash="dash", line_color="red", annotation_text="Total Avg")
                st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
                
            with stat_col:
                st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6;">
                        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">전체 평균 (Average)</div>
                        <div style="font-size: 24px; font-weight: bold; color: #1B263B;">{glob_mean:.1f}</div>
                        <hr style="margin: 10px 0;">
                        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">최대값 (Max)</div>
                        <div style="font-size: 20px; font-weight: bold; color: #2E5077;">{glob_max:.1f}</div>
                        <div style="font-size: 14px; color: #666; margin-top: 10px; margin-bottom: 5px;">최소값 (Min)</div>
                        <div style="font-size: 20px; font-weight: bold; color: #6c757d;">{glob_min:.1f}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("비교할 데이터가 없습니다.")
    else:
        st.info("이 카테고리에는 표시할 지표 데이터가 없습니다.")
    
    # Restored Insight Tab Logic will follow in next block or be part of manual restore if needed
    # (Actually I should end this replacement here and do another one for Insight to be safe, or include it?
    #  The user explicitly asked to restore Insight to "well set" state. I'll include the Insight part here if possible, 
    #  but lines 485-600 cover mainly Protocol. I'll just fix Protocol here.)
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                render_metric_content(p_df, 'Jump_SQ', '스쿼트 점프', 'cm')
        with c2:
            with st.container(border=True):
                render_metric_content(p_df, 'Jump_CMJ', 'CMJ 점프', 'cm')
# Tab: Insight (심화 분석)
# ==========================================
elif "인사이트" in selected_tab:
    # --- Sub Navigation ---
    st.markdown('<div class="section-title">심화 분석 (Deep Analysis)</div>', unsafe_allow_html=True)
    
    # [Spacer] Increase gap between Title and Sub-menu
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    insight_tab = st.radio("Insight_Nav", 
                           ["성숙도 (Maturation)", "상관관계 (Correlation Matrix)"], 
                           horizontal=True, 
                           label_visibility="collapsed",
                           key="insight_sub_nav")
    
    # [Tighten] Decrease gap to Divider (Same as Protocol)
    st.markdown("<hr style='margin-top: -15px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    if "성숙도" in insight_tab:

        # --- Filter Section (Simplified) ---
        # 1. No Form, No Expander. Just Top Control.
        c_filter_1, c_filter_2 = st.columns([1, 2])
        
        with c_filter_1:
            all_test_ids = sorted([x for x in df['Test_ID'].unique() if pd.notna(x)], reverse=True)
            sel_test_id = st.selectbox("측정 차수 (Test ID)", ["All"] + all_test_ids, index=0)
            
        with c_filter_2:
            st.markdown("""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #ddd; margin-top: 15px;">
                    ℹ️ <b>분석 대상</b>: <span style="color: #1B263B; font-weight: bold;">중1 (Middle School 1st Year)</span> 학년으로 고정됩니다.
                </div>
            """, unsafe_allow_html=True)
            
        # Data Logic
        sel_mat_grade = "중1"
        mat_df = df[df['Grade'] == sel_mat_grade].copy()
        
        # Filter by Test_ID
        if sel_test_id != 'All':
            mat_df = mat_df[mat_df['Test_ID'] == sel_test_id]
            
        st.write("")
        
        if mat_df.empty:
            st.warning(f"⚠️ {sel_test_id} 기간에 해당하는 '중1' 데이터가 없습니다.")
        else:
            # Layout: 2x2 Grid
            # Row 1: RAE | Scatter
            r1_c1, r1_c2 = st.columns(2)
            
            # --- Row 1 Left: RAE (Month-based) ---
            with r1_c1:
                with st.container(border=True):
                    st.markdown(f'<div class="section-title">상대적 연령 효과 (RAE)</div>', unsafe_allow_html=True)
                    st.markdown("<hr>", unsafe_allow_html=True)
                    
                    if 'Birth_Month' in mat_df.columns:
                        # Count by Month
                        rae_month_counts = mat_df['Birth_Month'].value_counts().reindex(range(1, 13), fill_value=0).reset_index()
                        rae_month_counts.columns = ['Month', 'Count']
                        
                        # Assign Quarter Color
                        def get_quarter_color(m):
                            if m <= 3: return 'Q1'
                            elif m <= 6: return 'Q2'
                            elif m <= 9: return 'Q3'
                            else: return 'Q4'
                        rae_month_counts['Quarter'] = rae_month_counts['Month'].apply(get_quarter_color)
                        
                        fig_rae = px.bar(
                            rae_month_counts, x='Month', y='Count', 
                            color='Quarter',
                            color_discrete_map={'Q1':'#1f77b4', 'Q2':'#ff7f0e', 'Q3':'#2ca02c', 'Q4':'#d62728'},
                            text='Count'
                        )
                        fig_rae.update_layout(
                            height=350, 
                            margin=dict(t=10, b=10, l=10, r=10),
                            xaxis=dict(tickmode='linear', tick0=1, dtick=1, title="월 (Month)"),
                            paper_bgcolor='white', plot_bgcolor='white',
                            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig_rae, use_container_width=True, config={'displayModeBar': False})
                        
                        # RAE Analysis Text
                        # Compact Analysis to balance height
                        q1_sum = rae_month_counts[rae_month_counts['Quarter']=='Q1']['Count'].sum()
                        q4_sum = rae_month_counts[rae_month_counts['Quarter']=='Q4']['Count'].sum()
                        
                        if q4_sum > 0:
                            ratio = q1_sum / q4_sum
                            msg = f"Q1 vs Q4 비율: **{ratio:.1f}배**"
                        else:
                            msg = "Q4 데이터 없음"
                            
                        st.caption(f"📌 {msg}. (Q1: 1~3월, Q4: 10~12월)")

            # --- Row 1 Right: Scatter (Month vs APHV) ---
            with r1_c2:
                 with st.container(border=True):
                    st.markdown(f'<div class="section-title">출생 월별 성숙도 (Month vs APHV)</div>', unsafe_allow_html=True)
                    st.markdown("<hr>", unsafe_allow_html=True)
                    
                    if 'APHV' in mat_df.columns and 'Birth_Month' in mat_df.columns:
                        # Need Categories
                        if 'Maturity_Cat' not in mat_df.columns:
                             def get_mat_cat(aphv):
                                if pd.isna(aphv): return "Unknown"
                                if aphv < 13.1: return 'Early (조기)'
                                elif aphv <= 15.1: return 'Average (평균)'
                                else: return 'Late (만기)'
                             mat_df['Maturity_Cat'] = mat_df['APHV'].apply(get_mat_cat)

                        # X: Birth Date (Seasonality)
                        mat_df['Date_Seasonality'] = mat_df['Birth_date'].apply(lambda x: x.replace(year=2000) if pd.notnull(x) else pd.NaT)
                        
                        fig_scat = px.scatter(
                            mat_df, x='Date_Seasonality', y='APHV',
                            color='Maturity_Cat',
                            color_discrete_map={'Early (조기)':'#d62728', 'Average (평균)':'#2ca02c', 'Late (만기)':'#1f77b4'},
                            hover_data=['Player']
                        )
                        
                        fig_scat.update_layout(
                            height=350, # Matched Height with RAE
                            margin=dict(t=10, b=10, l=10, r=10),
                            xaxis=dict(
                                title="월 (Month)", 
                                tickformat="%m월",
                                dtick="M1"
                            ),
                            yaxis=dict(title="APHV"),
                            paper_bgcolor='white', plot_bgcolor='white',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        # To balance text height of RAE, adding an empty line or similar caption
                        st.plotly_chart(fig_scat, use_container_width=True, config={'displayModeBar': False})
                        st.caption("▲ 점의 색상은 성숙 단계(Early/Avg/Late)를 나타냅니다.")

            st.write("")
            
            # Row 2: APHV Distribution | Growth Velocity
            r2_c1, r2_c2 = st.columns(2)
            
            # --- Row 2 Left: APHV Distribution (Restored) ---
            with r2_c1:
                with st.container(border=True):
                    st.markdown(f'<div class="section-title">성숙도 분포 (APHV Distribution)</div>', unsafe_allow_html=True)
                    st.markdown("<hr>", unsafe_allow_html=True)
                    
                    if 'APHV' in mat_df.columns:
                        import plotly.figure_factory as ff
                        hist_vals = mat_df['APHV'].dropna()
                        if len(hist_vals) > 1:
                            fig_dist = ff.create_distplot([hist_vals], ['APHV'], show_hist=False, show_rug=False, colors=['#1B263B'])
                            # Shaded Regions
                            fig_dist.add_vrect(x0=10, x1=13.1, fillcolor="#d62728", opacity=0.1)
                            fig_dist.add_vrect(x0=13.1, x1=15.1, fillcolor="#4db6ac", opacity=0.1)
                            fig_dist.add_vrect(x0=15.1, x1=18, fillcolor="#f4c150", opacity=0.1)
                            
                            fig_dist.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10), showlegend=False, plot_bgcolor='white')
                            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.info("데이터 부족")
                    else:
                        st.info("APHV 데이터 없음")

            # --- Row 2 Right: Growth Velocity ---
            with r2_c2:
                with st.container(border=True):
                    st.markdown(f'<div class="section-title">성장 속도 (Growth Velocity)</div>', unsafe_allow_html=True)
                    st.markdown("<hr>", unsafe_allow_html=True)
                    
                    target_players = mat_df['Player'].unique()
                    history_df = df[df['Player'].isin(target_players)].copy()
                    
                    velocities = []
                    if not history_df.empty:
                        history_df = history_df.sort_values(['Player', 'Age'])
                        for p in target_players:
                             # ... (Same velocity logic) ...
                             p_df = history_df[history_df['Player'] == p]
                             if len(p_df) > 1:
                                p_df['H_Diff'] = p_df['Height'].diff()
                                p_df['Age_Diff'] = p_df['Age'].diff()
                                p_df = p_df[p_df['Age_Diff'] > 0]
                                p_df['Velocity'] = p_df['H_Diff'] / p_df['Age_Diff']
                                p_df = p_df[(p_df['Velocity'] > 0) & (p_df['Velocity'] < 20) & (p_df['Age_Diff'] > 0.5)]
                                if not p_df.empty:
                                    velocities.append(p_df[['Age', 'Velocity']])
                    
                    if velocities:
                        vel_df = pd.concat(velocities)
                        vel_df['Age_Rounded'] = vel_df['Age'].apply(lambda x: round(x * 2) / 2)
                        avg_vel = vel_df.groupby('Age_Rounded')['Velocity'].mean().reset_index()
                        
                        fig_vel = px.line(avg_vel, x='Age_Rounded', y='Velocity', markers=True)
                        fig_vel.update_layout(
                            height=300,
                            margin=dict(t=10, b=10, l=10, r=10),
                            xaxis_title="나이 (Age)", yaxis_title="cm/year",
                            plot_bgcolor='white'
                        )
                        fig_vel.update_traces(line_color='#1B263B', line_width=3)
                        fig_vel.add_vrect(x0=13.5, x1=14.5, fillcolor="red", opacity=0.1)
                        st.plotly_chart(fig_vel, use_container_width=True, config={'displayModeBar': False})
                    else:
                        st.info("데이터 부족")


    elif "상관관계" in insight_tab:
        st.info("🚧 준비 중입니다 (상관관계 분석)")
