import streamlit as st
from database import get_user

def login():
    """Handle user authentication and session initialization"""
    st.title("🎓EDUPORTFOLIO-Empowering Minds,Shaping Futures")
    st.markdown("#### Please select your role and credentials to continue")

    with st.form("login_form"):
        role = st.selectbox(
            "Select Your Role",
            ["Student", "Teacher", "Admin"],
            index=None,
            placeholder="Choose account type..."
        )
        username = st.text_input("Username").strip()
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

    if submit_button:
        if not all([role, username, password]):
            st.error("Please fill in all fields")
            return

        user = get_user(username)
        
        # Authentication checks
        if not user:
            st.error("❌ User not found")
            return
            
        if user['password'] != password:
            st.error("🔐 Incorrect password")
            return
            
        if user['role'].lower() != role.lower():
            st.error(f"⚠️ Account is not registered as {role}")
            return

        # Set session state
        st.session_state.update({
            'user_id': user['id'],
            'role': user['role'],
            'username': user['username'],
            'authenticated': True
        })
        
        # Force application rerun
        st.rerun()

def logout():
    """Clean up session state and return to login page"""
    keys_to_remove = ['user_id', 'role', 'username', 'authenticated']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def authentication_guard():
    """Protect routes from unauthorized access"""
    if not st.session_state.get('authenticated'):
        st.error("⛔ Unauthorized access! Please login first.")
        login()
        st.stop()