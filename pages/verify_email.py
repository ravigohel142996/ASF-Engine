"""
Email Verification Page
"""
import streamlit as st
from auth.firebase_auth import FirebaseAuth

# Page configuration
st.set_page_config(
    page_title="Verify Email | ASF-Engine",
    page_icon="✉️",
    layout="centered"
)


def render_verify_email_page():
    """Render the email verification page"""
    
    # Custom CSS
    st.markdown("""
    <style>
    .verify-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    .verify-header {
        text-align: center;
        margin-bottom: 40px;
    }
    .verify-header h1 {
        color: #1E88E5;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .stButton > button {
        width: 100%;
        background-color: #28a745;
        color: white;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        margin-top: 10px;
    }
    .stButton > button:hover {
        background-color: #218838;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="verify-header">
        <h1>✉️ Email Verification</h1>
        <p>Verifying your email address...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get token from URL parameters
    query_params = st.query_params
    token = query_params.get("token", None)
    
    if not token:
        st.error("❌ Invalid or missing verification token")
        if st.button("← Back to Login"):
            st.switch_page("pages/login.py")
        return
    
    # Initialize Firebase Auth
    auth = FirebaseAuth()
    
    # Verify email
    with st.spinner("Verifying email..."):
        success = auth.verify_email_with_token(token)
        
        if success:
            st.balloons()
            st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h2>🎉 Email Verified!</h2>
                <p>Your email has been successfully verified. You can now access all features.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ Go to Dashboard", use_container_width=True):
                st.switch_page("app.py")
            
            if st.button("← Back to Login", use_container_width=True, key="login_btn"):
                st.switch_page("pages/login.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; opacity: 0.6; padding: 20px;'>
        <p>ASF-Engine v2.0.0 - Enterprise SaaS Edition</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_verify_email_page()
