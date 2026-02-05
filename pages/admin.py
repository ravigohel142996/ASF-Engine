"""
Admin Panel for ASF-Engine
Administrative interface for managing users, system, and monitoring
"""
import streamlit as st
from auth.firebase_auth import SessionManager
from datetime import datetime
import pandas as pd


def render_admin_panel():
    """Render admin panel page"""
    
    # Initialize session
    SessionManager.init_session()
    
    # Check authentication
    if not SessionManager.check_session_expiry():
        st.warning("⚠️ Please log in to access the admin panel")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        st.stop()
    
    user = SessionManager.get_user()
    
    # Check if user is admin
    if user.get('role') != 'admin':
        st.error("❌ Access Denied: Admin privileges required")
        st.info("Contact your administrator to request admin access")
        st.stop()
    
    # Page header
    st.title("⚙️ Admin Panel")
    st.markdown(f"Welcome, **{user['display_name']}** | Admin Dashboard")
    st.markdown("---")
    
    # Create tabs for different admin sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "👥 Users",
        "🚨 System Health",
        "💳 Billing",
        "⚙️ Settings"
    ])
    
    with tab1:
        render_overview_tab()
    
    with tab2:
        render_users_tab()
    
    with tab3:
        render_system_health_tab()
    
    with tab4:
        render_billing_tab()
    
    with tab5:
        render_settings_tab()


def render_overview_tab():
    """Render overview tab"""
    st.markdown("### 📊 Platform Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "1,247", "+23 this week")
    with col2:
        st.metric("Active Sessions", "89", "+12 today")
    with col3:
        st.metric("Total Revenue", "$12,450", "+$2,340 this month")
    with col4:
        st.metric("System Uptime", "99.9%", "Last 30 days")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### User Growth")
        # Demo chart data
        chart_data = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'Users': range(1000, 1300, 10)
        })
        st.line_chart(chart_data.set_index('Date'))
    
    with col2:
        st.markdown("#### Revenue Trend")
        revenue_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Revenue': [8000, 9500, 10200, 11000, 12450]
        })
        st.bar_chart(revenue_data.set_index('Month'))


def render_users_tab():
    """Render users management tab"""
    st.markdown("### 👥 User Management")
    
    # User search
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search users", placeholder="Email or name...")
    with col2:
        if st.button("🔍 Search", use_container_width=True):
            st.info("Search functionality coming soon")
    
    # Demo users table
    users_data = {
        'Email': ['john@example.com', 'sarah@example.com', 'mike@example.com'],
        'Name': ['John Doe', 'Sarah Smith', 'Mike Johnson'],
        'Plan': ['Professional', 'Starter', 'Free'],
        'Status': ['Active', 'Active', 'Active'],
        'Joined': ['2024-01-15', '2024-02-10', '2024-03-01']
    }
    
    users_df = pd.DataFrame(users_data)
    st.dataframe(users_df, use_container_width=True)
    
    st.markdown("---")
    
    # Actions
    st.markdown("#### User Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add New User", use_container_width=True):
            st.info("User creation form coming soon")
    
    with col2:
        if st.button("📧 Send Announcement", use_container_width=True):
            st.info("Email announcement feature coming soon")
    
    with col3:
        if st.button("📊 Export Users", use_container_width=True):
            st.info("Export functionality coming soon")


def render_system_health_tab():
    """Render system health tab"""
    st.markdown("### 🚨 System Health Monitoring")
    
    # Service status
    st.markdown("#### Service Status")
    
    services = {
        'Frontend (Streamlit)': ('healthy', '🟢'),
        'Backend API': ('healthy', '🟢'),
        'Database': ('healthy', '🟢'),
        'ML Service': ('healthy', '🟢'),
        'Cache': ('healthy', '🟢')
    }
    
    for service, (status, icon) in services.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{service}**")
        with col2:
            st.markdown(f"{icon} {status.upper()}")
        with col3:
            if st.button("Details", key=f"btn_{service}"):
                st.info(f"{service} is operating normally")
    
    st.markdown("---")
    
    # System metrics
    st.markdown("#### System Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CPU Usage", "45%", "-5%")
        st.metric("Memory Usage", "6.2 GB", "+0.3 GB")
    
    with col2:
        st.metric("Disk Usage", "120 GB", "+2 GB")
        st.metric("Network I/O", "125 Mbps", "+15 Mbps")
    
    with col3:
        st.metric("API Requests/min", "1,247", "+123")
        st.metric("Error Rate", "0.02%", "-0.01%")


def render_billing_tab():
    """Render billing tab"""
    st.markdown("### 💳 Billing & Revenue")
    
    # Revenue metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("MRR", "$12,450", "+$2,340")
    with col2:
        st.metric("ARR", "$149,400", "+$28,080")
    with col3:
        st.metric("Churn Rate", "2.1%", "-0.5%")
    with col4:
        st.metric("ARPU", "$49.80", "+$4.20")
    
    st.markdown("---")
    
    # Subscription breakdown
    st.markdown("#### Active Subscriptions")
    
    subscription_data = {
        'Plan': ['Free', 'Starter', 'Professional', 'Enterprise'],
        'Users': [850, 247, 125, 25],
        'Revenue': ['$0', '$12,203', '$24,875', '$12,475']
    }
    
    subs_df = pd.DataFrame(subscription_data)
    st.dataframe(subs_df, use_container_width=True)


def render_settings_tab():
    """Render settings tab"""
    st.markdown("### ⚙️ System Settings")
    
    # General settings
    st.markdown("#### General Settings")
    
    enable_signups = st.checkbox("Enable new user signups", value=True)
    enable_api = st.checkbox("Enable API access", value=True)
    maintenance_mode = st.checkbox("Maintenance mode", value=False)
    
    st.markdown("---")
    
    # Notification settings
    st.markdown("#### Notification Settings")
    
    email_notifications = st.checkbox("Email notifications", value=True)
    slack_integration = st.checkbox("Slack integration", value=False)
    webhook_alerts = st.checkbox("Webhook alerts", value=False)
    
    st.markdown("---")
    
    # Save button
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✓ Settings saved successfully!")


if __name__ == "__main__":
    render_admin_panel()
