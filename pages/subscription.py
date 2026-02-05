"""
Subscription Management Page
Allows users to view and manage their subscription plans
"""
import streamlit as st
from auth.simple_auth import SimpleAuth
from business.billing import SubscriptionPlan, BillingService


def render_subscription_page():
    """Render subscription management page"""
    
    # Initialize session
    SimpleAuth.init_session()
    
    # Check authentication
    if not SimpleAuth.is_logged_in():
        st.warning("⚠️ Please log in to access subscription management")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        st.stop()
    
    user = SimpleAuth.get_user()
    
    # Page header
    st.title("💳 Subscription Management")
    st.markdown("---")
    
    # Get all plans
    plans = SubscriptionPlan.get_all_plans()
    
    # Display current plan
    current_plan = user.get('subscription_plan', 'free')
    st.success(f"**Current Plan:** {current_plan.upper()}")
    
    st.markdown("### Available Plans")
    
    # Display plans in columns
    cols = st.columns(len(plans))
    
    for idx, plan in enumerate(plans):
        with cols[idx]:
            is_current = plan['id'] == current_plan
            
            # Plan card
            st.markdown(f"""
            <div style='
                border: {"3px solid #1E88E5" if is_current else "1px solid #ccc"};
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background: {"#E3F2FD" if is_current else "white"};
            '>
                <h3 style='text-align: center; color: #1E88E5;'>{plan['name']}</h3>
                <h2 style='text-align: center;'>
                    {"FREE" if plan['price'] == 0 else f"${plan['price']}/mo"}
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Features
            st.markdown("**Features:**")
            for feature in plan['features']:
                st.markdown(f"✓ {feature}")
            
            # Action button
            if is_current:
                st.success("✓ Active Plan")
            else:
                if st.button(f"Upgrade to {plan['name']}", key=f"btn_{plan['id']}", use_container_width=True):
                    st.info(f"Upgrade to {plan['name']} - Stripe integration pending")
                    st.markdown("Contact sales@asf-engine.io for enterprise plans")
    
    st.markdown("---")
    
    # Billing history section
    st.markdown("### 📄 Billing History")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Spend", "$0.00", "Last 30 days")
    with col2:
        st.metric("Next Billing", "N/A", "Free Plan")
    with col3:
        st.metric("Invoices", "0", "All time")
    
    # Demo invoices table
    st.markdown("#### Recent Invoices")
    st.info("No invoices yet. Upgrade to a paid plan to see billing history.")
    
    st.markdown("---")
    
    # Usage statistics
    st.markdown("### 📊 Usage Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Predictions This Month", "47", "+12 from last month")
    with col2:
        st.metric("API Calls", "234", "+56 from last month")
    with col3:
        st.metric("Data Retention", "7 days", "Free plan limit")
    
    # Progress bars
    st.markdown("#### Plan Limits")
    
    st.progress(0.47, text="Predictions: 47/100")
    st.progress(0.70, text="Storage: 70MB/100MB")
    st.progress(0.33, text="Team Members: 1/1")


if __name__ == "__main__":
    render_subscription_page()
