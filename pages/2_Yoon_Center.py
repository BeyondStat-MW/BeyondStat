
import streamlit as st
from templates import template_center

# Page Config
st.set_page_config(page_title="Yoon Chung-gu Center", page_icon="🏋️", layout="wide")

from utils import auth

# Page Config
st.set_page_config(page_title="Yoon Chung-gu Center", page_icon="🏋️", layout="wide")

# --- Authentication Logic ---
# Strict Isolation: Always hide sidebar/header on this client page
auth.inject_custom_css()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def handle_login():
    username = st.session_state.get('yoon_user', '')
    password = st.session_state.get('yoon_pass', '')
    role = auth.authenticate_user(username, password, required_roles=['yoon', 'admin'])
    
    if role:
        st.session_state['logged_in'] = True
        st.session_state['role'] = role
        st.session_state['current_user'] = username
    else:
        st.session_state['login_error'] = "인증 실패: 아이디 또는 비밀번호를 확인하세요. (Yoon/Admin Only)"

# If not logged in, show embedded login form
if not st.session_state['logged_in']:
    auth.inject_custom_css() # Hide sidebar for login screen
    
    st.markdown("""
    <style>
        .login-super { display: flex; justify-content: center; margin-top: 100px; }
        .login-box { background: #f8f9fa; padding: 40px; border-radius: 10px; width: 400px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    <div class='login-super'><h2 style='text-align: center; color: #415A77;'>🏋️ Yoon Performance Center</h2></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if 'login_error' in st.session_state:
            st.error(st.session_state['login_error'])
            del st.session_state['login_error']
            
        st.text_input("아이디 (ID)", key="yoon_user")
        st.text_input("비밀번호 (PW)", type="password", key="yoon_pass", on_change=handle_login)
        st.button("로그인 (Login)", on_click=handle_login, type="primary", use_container_width=True)
    st.stop()

# If valid session but Unauthorized role (e.g. came from other session)
if st.session_state.get('role') not in ['yoon', 'admin']:
    auth.inject_custom_css()
    st.error("⛔ 접근 권한이 없습니다. (Access Denied)")
    if st.button("로그아웃 (Logout)"):
        auth.logout()
    st.stop()

# --- Access Granted ---
# Hide sidebar for non-admin users to simulate standalone app
if st.session_state.get('role') != 'admin':
    auth.inject_custom_css()

if st.button("로그아웃 (Logout)", key="logout_btn"):
    auth.logout()

st.divider()

# Core Logic
# The template_center handles its own data loading via SQLite now
try:
    import importlib
    importlib.reload(template_center)
    template_center.show_dashboard() 
except Exception as e:
    st.error(f"시스템 오류: {e}")
