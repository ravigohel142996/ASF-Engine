"""
Login page for ASF-Engine SaaS Platform
Simple Local Authentication
"""
import streamlit as st
from auth.simple_auth import SimpleAuth


def render_login_page():
    """Render the login page"""
    
    # Initialize session
    SimpleAuth.init_session()
    
    # If already authenticated, redirect to main app
    if SimpleAuth.is_logged_in():
        st.success(f"✅ Already logged in as {st.session_state.user['email']}")
        if st.button("Go to Dashboard"):
            st.switch_page("app.py")
        return
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    .login-header h1 {
        color: #1E88E5;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .login-header p {
        color: #666;
        font-size: 1.2em;
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
    .tab-content {
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="login-header">
        <h1>🤖 ASF-Engine</h1>
        <p>AI System Failure Monitoring Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("### Welcome Back!")
        email = st.text_input("Email", placeholder="admin@asf.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submit = st.form_submit_button("🚀 Login")
        
        if submit:
            if not email or not password:
                st.error("❌ Please enter both email and password")
            else:
                with st.spinner("Authenticating..."):
                    if SimpleAuth.login(email, password):
                        st.success("✅ Login successful! Welcome back!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
    
    # Demo credentials info
    st.info("💡 **Demo Credentials**: Email: `admin@asf.com` | Password: `123456`")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; opacity: 0.6; padding: 20px;'>
        <p>ASF-Engine v2.0.0 - Enterprise SaaS Edition</p>
        <p>🔒 Secure Authentication | 🌐 Cloud Native | ⚡ Real-time Monitoring</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    render_login_page()
