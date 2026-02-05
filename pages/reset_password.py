"""
Password Reset Page - Not Available in Simple Auth Mode
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Reset Password | ASF-Engine",
    page_icon="🔑",
    layout="centered"
)


def render_reset_password_page():
    """Render the password reset page"""
    
    st.title("🔑 Password Reset")
    st.info("Password reset is not available in simple authentication mode.")
    st.markdown("---")
    st.markdown("**Default Credentials:**")
    st.markdown("- Email: `admin@asf.com`")
    st.markdown("- Password: `123456`")
    st.markdown("---")
    
    if st.button("Go to Login", use_container_width=True):
        st.switch_page("pages/login.py")
    
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
