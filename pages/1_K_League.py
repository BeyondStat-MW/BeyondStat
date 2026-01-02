
import streamlit as st
from utils.data_loader import load_data, process_data, inject_missing_test_ids
from templates import template_association

# Page Config
from utils import auth

# Page Config
st.set_page_config(page_title="K-League Platform", page_icon="⚽", layout="wide")

# --- Authentication Logic ---
# Strict Isolation: Always hide sidebar/header on this client page
auth.inject_custom_css()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def handle_login():
    username = st.session_state.get('kleague_user', '')
    password = st.session_state.get('kleague_pass', '')
    role = auth.authenticate_user(username, password, required_roles=['kleague', 'admin'])
    
    if role:
        st.session_state['logged_in'] = True
        st.session_state['role'] = role
        st.session_state['current_user'] = username
    else:
        st.session_state['login_error'] = "인증 실패: 아이디 또는 비밀번호를 확인하세요. (K-League/Admin Only)"

# If not logged in, show embedded login form
if not st.session_state['logged_in']:
    auth.inject_custom_css() # Hide sidebar for login screen
    
    st.markdown("""
    <style>
        .login-super { display: flex; justify-content: center; margin-top: 100px; }
        .login-box { background: #f8f9fa; padding: 40px; border-radius: 10px; width: 400px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    <div class='login-super'><h2 style='text-align: center; color: #1B263B;'>⚽ K-League Youth Platform</h2></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if 'login_error' in st.session_state:
            st.error(st.session_state['login_error'])
            del st.session_state['login_error']
            
        st.text_input("아이디 (ID)", key="kleague_user")
        st.text_input("비밀번호 (PW)", type="password", key="kleague_pass", on_change=handle_login)
        st.button("로그인 (Login)", on_click=handle_login, type="primary", use_container_width=True)
    st.stop()

# If valid session but Unauthorized role (e.g. came from other session)
if st.session_state.get('role') not in ['kleague', 'admin']:
    auth.inject_custom_css()
    st.error("⛔ 접근 권한이 없습니다. (Access Denied)")
    if st.button("로그아웃 (Logout)", key="logout_btn_denied"):
        auth.logout()
    st.stop()

# --- Access Granted ---
# Hide sidebar for non-admin users to simulate standalone app
if st.session_state.get('role') != 'admin':
    auth.inject_custom_css()

if st.button("로그아웃 (Logout)", key="logout_btn_granted"):
    auth.logout()

st.divider()

# Core Logic
try:
    # Load Raw Data from BigQuery
    df_raw = load_data("kleague-482106", "Kleague_db", "measurements")
    df_raw = inject_missing_test_ids(df_raw)
    df = process_data(df_raw)
    
    # Show Dashboard
    template_association.show_dashboard(df)
    
except Exception as e:
    st.error(f"시스템 오류 (데이터 로드 실패): {e}")
