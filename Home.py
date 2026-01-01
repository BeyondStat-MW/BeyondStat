
import streamlit as st

# --- Page Config (Global) ---
# This must be the first Streamlit command
from utils import auth

# --- Page Config (Global) ---
# This must be the first Streamlit command
st.set_page_config(
    page_title="BeyondStat Portal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force reload signal
st.toast("👋 환영합니다! (Welcome)", icon="✨")

# --- Login Logic (Gatekeeper) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def handle_login():
    username = st.session_state.get('username_input', '')
    password = st.session_state.get('password_input', '')
    role = auth.authenticate_user(username, password) # Admin portal accepts any valid user
    
    if role:
        st.session_state['logged_in'] = True
        st.session_state['role'] = role
        st.session_state['current_user'] = username
    else:
        st.session_state['login_error'] = "아이디 또는 비밀번호가 잘못되었습니다."

if not st.session_state['logged_in']:
    st.markdown("""
    <style>
        .login-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            margin-top: 100px;
        }
        .login-box {
            background-color: white; padding: 40px; border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 400px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("## 🔒 BeyondStat Team Login")
        if 'login_error' in st.session_state:
            st.error(st.session_state['login_error'])
            del st.session_state['login_error']
            
        st.text_input("아이디 (ID)", key="username_input")
        st.text_input("비밀번호 (Password)", type="password", key="password_input", on_change=handle_login)
        st.button("로그인 (Login)", on_click=handle_login, type="primary", use_container_width=True)
    st.stop()

if st.button("로그아웃 (Logout)", key="logout_btn_home"):
    auth.logout()

# --- Portal Dashboard (Landing Page) ---
st.markdown("""
<style>
    .portal-card {
        padding: 30px; border-radius: 16px; background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;
        text-align: center; transition: transform 0.2s;
        cursor: pointer; height: 100%;
    }
    .portal-card:hover {
        transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .card-title { font-size: 24px; font-weight: bold; color: #1B263B; margin-bottom: 15px; }
    .card-desc { font-size: 16px; color: #415A77; margin-bottom: 25px; }
    a { text-decoration: none; color: inherit; }
</style>
""", unsafe_allow_html=True)

st.title("🗂️ BeyondStat Service Portal")
st.markdown("접속할 플랫폼을 선택해주세요.")

st.divider()

col_k, col_y, col_g = st.columns(3, gap="large")

role = st.session_state.get('role')

# --- K-League Card ---
if role in ['kleague', 'admin']:
    with col_k:
        st.markdown("""
        <div class="portal-card">
            <div style="font-size: 50px; margin-bottom: 20px;">⚽</div>
            <div class="card-title">K-League Youth Platform</div>
            <div class="card-desc">
                K리그 유스 선수들의 피지컬 데이터를 분석하고<br>
                협회 차원의 인사이트를 제공합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("입장하기 (Enter)", key="btn_k", type="primary", use_container_width=True):
            st.switch_page("pages/1_K_League.py")

# --- Yoon Center Card ---
if role in ['yoon', 'admin']:
    with col_y:
        st.markdown("""
        <div class="portal-card">
            <div style="font-size: 50px; margin-bottom: 20px;">🏋️</div>
            <div class="card-title">Yoon Chung-gu Center</div>
            <div class="card-desc">
                윤청구 퍼포먼스 트레이닝 센터 전용<br>
                선수 관리 및 재활 모니터링 시스템입니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("입장하기 (Enter)", key="btn_y", type="primary", use_container_width=True):
            st.switch_page("pages/2_Yoon_Center.py")

# --- Gangwon FC Card ---
if role in ['gangwon', 'admin']:
    with col_g:
        st.markdown("""
        <div class="portal-card">
            <div style="font-size: 50px; margin-bottom: 20px;">🐻</div>
            <div class="card-title">Gangwon FC Dashboard</div>
            <div class="card-desc">
                강원 FC 선수단 퍼포먼스 모니터링 시스템.<br>
                VALD 측정 장비 데이터 및 부상 위험도 분석.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("입장하기 (Enter)", key="btn_g", type="primary", use_container_width=True):
            st.switch_page("pages/3_Gangwon_FC.py")

st.sidebar.success(f"로그인 계정: {st.session_state.get('current_user', 'Unknown')} ({role})")
