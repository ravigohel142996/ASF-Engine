"""
Email Verification Page - Not Available in Simple Auth Mode
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Verify Email | ASF-Engine",
    page_icon="✉️",
    layout="centered"
)


def render_verify_email_page():
    """Render the email verification page"""
    
    st.title("✉️ Email Verification")
    st.info("Email verification is not required in simple authentication mode.")
    st.markdown("---")
    st.markdown("**Default Credentials:**")
    st.markdown("- Email: `admin@asf.com`")
    st.markdown("- Password: `123456`")
    st.markdown("---")
    
    if st.button("Go to Login", use_container_width=True):
        st.switch_page("pages/login.py")
    
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
