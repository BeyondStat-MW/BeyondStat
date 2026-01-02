
import streamlit as st

# Centralized User Database
# In production, this should be moved to st.secrets or a secure DB
USERS = {
    "admin":   {"password": "team1234",    "role": "admin"},
    "kleague": {"password": "kleague1234", "role": "kleague"},
    "yoon":    {"password": "yoon1234",    "role": "yoon"},
    "gangwon": {"password": "gangwon1234", "role": "gangwon"}
}

def authenticate_user(username, password, required_roles=None):
    """
    Authenticates a user and returns their role if successful and authorized.
    
    Args:
        username (str): User ID
        password (str): User Password
        required_roles (list, optional): List of allowed roles. If None, any valid user is allowed.
    
    Returns:
        str: Role name (e.g., 'admin', 'yoon') if successful.
        None: If authentication fails or role is not authorized.
    """
    if username in USERS and USERS[username]["password"] == password:
        role = USERS[username]["role"]
        
        # Check authorization if specific roles are required
        if required_roles and role not in required_roles:
            return None
            
        return role
    return None

def logout():
    """Clears session state for logout."""
    keys = ['logged_in', 'role', 'current_user', 'username_input', 'password_input']
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def inject_custom_css():
    """
    Injects CSS to hide the sidebar and Streamlit header for a cleaner 'App-like' feel.
    Used for standalone client pages.
    """
    """
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stHeader"] {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
