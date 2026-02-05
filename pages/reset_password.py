"""
Password Reset Page
"""
import streamlit as st
from auth.firebase_auth import FirebaseAuth

# Page configuration
st.set_page_config(
    page_title="Reset Password | ASF-Engine",
    page_icon="🔑",
    layout="centered"
)


def render_reset_password_page():
    """Render the password reset page"""
    
    # Custom CSS
    st.markdown("""
    <style>
    .reset-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    .reset-header {
        text-align: center;
        margin-bottom: 40px;
    }
    .reset-header h1 {
        color: #1E88E5;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        margin-top: 10px;
    }
    .stButton > button:hover {
        background-color: #1565C0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="reset-header">
        <h1>🔑 Reset Password</h1>
        <p>Enter your new password</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get token from URL parameters
    query_params = st.query_params
    token = query_params.get("token", None)
    
    if not token:
        st.error("❌ Invalid or missing reset token")
        if st.button("← Back to Login"):
            st.switch_page("pages/login.py")
        return
    
    # Initialize Firebase Auth
    auth = FirebaseAuth()
    
    # Reset form
    with st.form("reset_password_form"):
        st.markdown("### Create New Password")
        
        new_password = st.text_input(
            "New Password", 
            type="password", 
            placeholder="Minimum 6 characters"
        )
        confirm_password = st.text_input(
            "Confirm Password", 
            type="password", 
            placeholder="Re-enter new password"
        )
        
        submit = st.form_submit_button("🔒 Reset Password")
        
        if submit:
            if not new_password or not confirm_password:
                st.error("❌ Please fill in all fields")
            elif new_password != confirm_password:
                st.error("❌ Passwords don't match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                with st.spinner("Resetting password..."):
                    success = auth.reset_password_with_token(token, new_password)
                    
                    if success:
                        st.balloons()
                        if st.button("✅ Go to Login"):
                            st.switch_page("pages/login.py")
    
    # Cancel button
    if st.button("← Back to Login", key="cancel_btn"):
        st.switch_page("pages/login.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; opacity: 0.6; padding: 20px;'>
        <p>ASF-Engine v2.0.0 - Enterprise SaaS Edition</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_reset_password_page()
