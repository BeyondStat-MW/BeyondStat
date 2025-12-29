
import streamlit as st

# [User Roles Configuration]
# Define who has access and what their role is.
# role: 'admin' (All Access), 'association' (K League View), 'club' (Specific Team View)
AUTHORIZED_USERS = {
    "mw.seo@beyondstat.ai": {"role": "admin", "name": "Minwoo Seo (Admin)"},
    "mwseo815@gmail.com": {"role": "association", "name": "Viewer"},
}

def get_current_user():
    """
    Returns the email of the current user.
    Handles both Streamlit Cloud (st.user) and Localhost (Session State).
    """
    # 1. Streamlit Cloud Auth (Production)
    # st.experimental_user is the standard for Community Cloud
    try:
        user_info = st.experimental_user
        if user_info and hasattr(user_info, 'email') and user_info.email:
            return user_info.email
    except:
        pass
        
    # 2. Localhost Fallback (Session State)
    if 'debug_user_email' in st.session_state:
        return st.session_state['debug_user_email']
        
    return None

def check_access():
    """
    Checks if the user is authorized.
    Returns: (is_authorized, user_role, user_email)
    """
    email = get_current_user()
    
    if not email:
        return False, None, None
        
    if email in AUTHORIZED_USERS:
        return True, AUTHORIZED_USERS[email]['role'], email
    else:
        # Deny access if email is not in list
        return False, "unauthorized", email
