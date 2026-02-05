"""
Login page for ASF-Engine SaaS Platform
"""
import streamlit as st
from auth.firebase_auth import FirebaseAuth, SessionManager


def render_login_page():
    """Render the login/signup page"""
    
    # Initialize session
    SessionManager.init_session()
    
    # If already authenticated, redirect to main app
    if SessionManager.is_authenticated():
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
    
    # Initialize Firebase Auth
    auth = FirebaseAuth()
    
    # Tabs for Login/Signup
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### Welcome Back!")
            email = st.text_input("Email", placeholder="your.email@company.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                remember_me = st.checkbox("Remember me")
            
            submit = st.form_submit_button("🚀 Login")
            
            if submit:
                if not email or not password:
                    st.error("❌ Please enter both email and password")
                else:
                    with st.spinner("Authenticating..."):
                        user_data = auth.sign_in_with_email_password(email, password)
                        
                        if user_data:
                            SessionManager.login(user_data)
                            st.success(f"✅ Welcome back, {user_data['display_name']}!")
                            
                            # Show email verification warning if not verified
                            if not user_data.get('email_verified', False):
                                st.warning("⚠️ Your email is not verified. Please check your inbox for the verification link.")
                            
                            st.balloons()
                            st.rerun()
        
        # Forgot password link
        if st.button("🔑 Forgot Password?", key="forgot_pass_btn"):
            st.session_state.show_forgot_password = True
            st.rerun()
        
        # Demo credentials info
        st.info(f"💡 **Demo Mode**: Use `{auth.demo_email}` / `{auth.demo_password}` for testing (if Firebase not configured).")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            st.markdown("### Create Account")
            
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your.email@company.com", key="signup_email")
            password = st.text_input("Password", type="password", placeholder="Minimum 6 characters", key="signup_password")
            password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            submit = st.form_submit_button("📝 Create Account")
            
            if submit:
                if not all([name, email, password, password_confirm]):
                    st.error("❌ Please fill in all fields")
                elif password != password_confirm:
                    st.error("❌ Passwords don't match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif not agree_terms:
                    st.error("❌ Please agree to the Terms of Service")
                else:
                    with st.spinner("Creating account..."):
                        user_data = auth.sign_up_with_email_password(email, password, name)
                        
                        if user_data:
                            SessionManager.login(user_data)
                            st.success(f"✅ Account created successfully! Welcome, {name}!")
                            st.info("📧 Please check your email to verify your account.")
                            st.balloons()
                            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Forgot Password Modal
    if st.session_state.get('show_forgot_password', False):
        st.markdown("---")
        st.markdown("### 🔑 Reset Password")
        
        with st.form("forgot_password_form"):
            st.markdown("Enter your email address and we'll send you a link to reset your password.")
            reset_email = st.text_input("Email", placeholder="your.email@company.com", key="reset_email")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_reset = st.form_submit_button("📧 Send Reset Link")
            with col2:
                cancel_reset = st.form_submit_button("Cancel")
            
            if submit_reset:
                if reset_email:
                    auth.request_password_reset(reset_email)
                else:
                    st.error("❌ Please enter your email address")
            
            if cancel_reset:
                st.session_state.show_forgot_password = False
                st.rerun()
        
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
