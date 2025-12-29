
import streamlit as st
import pandas as pd
from utils.data_loader import load_data, process_data, inject_missing_test_ids
from templates import template_association

# --- Page Config (Global) ---
st.set_page_config(
    page_title="Kleague Solution",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force reload signal
st.toast("📏 레이아웃 정렬 완료 (Layout Aligned)", icon="📐")

# --- Login Logic (Gatekeeper: Password Base) ---
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

# --- 1. Data Loading ---
try:
    # Load Raw Data from BigQuery
    df_raw = load_data("kleague-482106", "Kleague_db", "measurements")
    
    # Pre-process Data (Cleaning & Injection)
    df_raw = inject_missing_test_ids(df_raw)
    df = process_data(df_raw)
    
except Exception as e:
    st.error(f"시스템 오류 (데이터 로드 실패): {e}")
    st.stop()

# --- 2. Template Router ---
# 현재는 템플릿 하나만 사용 (template_association)
template_association.show_dashboard(df)
