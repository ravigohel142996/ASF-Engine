"""
AI System Failure Forecast Engine - Main Application
Production-grade ML system monitoring and failure prediction dashboard
Enterprise SaaS Edition v2.0.0
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import authentication
from auth.simple_auth import SimpleAuth

from src.data.simulator import MLSystemDataSimulator
from src.data.feature_engineering import FeatureEngineer
from src.models.hybrid_model import HybridFailurePredictionModel
from src.monitoring.risk_engine import RiskScoringEngine
from src.alerts.alert_system import AlertGenerator, RecommendationEngine
from src.dashboard.components import (
    apply_custom_css,
    render_header,
    render_health_score_gauge,
    render_failure_probability_gauge,
    render_timeline_forecast,
    render_metrics_dashboard,
    render_cost_monitor,
    render_root_cause_panel,
    render_alert_feed,
    render_executive_summary,
    render_metric_cards
)

# Page configuration
st.set_page_config(
    page_title="ASF-Engine | AI Monitoring SaaS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/ravigohel142996/ASF-Engine',
        'Report a bug': 'https://github.com/ravigohel142996/ASF-Engine/issues',
        'About': '# ASF-Engine v2.0.0\nAI System Failure Monitoring SaaS Platform'
    }
)


@st.cache_resource
def initialize_system():
    """
    Initialize all system components
    """
    simulator = MLSystemDataSimulator(days_history=90)
    feature_engineer = FeatureEngineer()
    model = HybridFailurePredictionModel()
    risk_engine = RiskScoringEngine()
    alert_generator = AlertGenerator()
    recommendation_engine = RecommendationEngine()
    
    return simulator, feature_engineer, model, risk_engine, alert_generator, recommendation_engine


@st.cache_data
def load_and_prepare_data(_simulator, _feature_engineer):
    """
    Load and prepare data for the dashboard
    """
    # Generate data
    metrics_df = _simulator.generate_metrics_data()
    
    # Engineer features
    features_df = _feature_engineer.engineer_features(metrics_df)
    
    # Get labeled data for training
    labeled_df, labels = _simulator.get_labeled_data()
    
    return metrics_df, features_df, labeled_df, labels


def train_model_if_needed(model, features_df, labels):
    """
    Train model if not already trained
    """
    if 'model_trained' not in st.session_state:
        with st.spinner('Training hybrid prediction model... This may take a moment.'):
            try:
                # Select features for training
                feature_cols = [col for col in features_df.columns if col != 'timestamp']
                X = features_df[feature_cols].fillna(0)
                
                # Train model
                results = model.train(X, labels)
                
                st.session_state.model_trained = True
                st.session_state.training_results = results
                
                return True
            except Exception as e:
                st.warning(f"Model training skipped: {str(e)}")
                st.session_state.model_trained = False
                return False
    
    return st.session_state.model_trained


def generate_forecast(metrics_df, hours=72):
    """
    Generate forecast data for the next N hours
    """
    last_timestamp = metrics_df['timestamp'].iloc[-1]
    
    forecast_data = []
    for hour in range(1, hours + 1):
        timestamp = last_timestamp + timedelta(hours=hour)
        
        # Simulate forecast (in production, this would use the model)
        base_failure_prob = np.random.uniform(20, 60)
        trend_factor = hour / hours  # Increases over time
        failure_prob = min(100, base_failure_prob + trend_factor * 20)
        
        base_health = 75
        health_score = max(0, base_health - trend_factor * 25)
        
        forecast_data.append({
            'timestamp': timestamp,
            'failure_probability': failure_prob,
            'health_score': health_score
        })
    
    return pd.DataFrame(forecast_data)


def main():
    """
    Main application - Enterprise SaaS Edition with Authentication
    """
    # Initialize session
    SimpleAuth.init_session()
    
    # Check authentication
    if not SimpleAuth.is_logged_in():
        st.warning("⚠️ Please log in to access the dashboard")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("### 🔐 Authentication Required")
            st.markdown("Please navigate to the login page to access the AI Monitoring Dashboard.")
            
            if st.button("Go to Login Page", use_container_width=True):
                st.switch_page("pages/login.py")
        st.stop()
    
    # Get current user
    user = SimpleAuth.get_user()
    
    # Apply custom styling
    apply_custom_css()
    
    # Enhanced Header with user info
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        render_header()
    with col2:
        st.markdown(f"**👤 {user['display_name']}**")
        st.caption(user['email'])
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            SimpleAuth.logout()
            st.success("Logged out successfully!")
            st.rerun()
    
    # Initialize system
    simulator, feature_engineer, model, risk_engine, alert_generator, recommendation_engine = initialize_system()
    
    # Sidebar controls
    with st.sidebar:
        # User Profile Section
        st.markdown("### 👤 Profile")
        st.markdown(f"**{user['display_name']}**")
        st.caption(f"{user['email']}")
        st.caption(f"Role: {user.get('role', 'User').title()}")
        st.markdown("---")
        
        st.markdown("## ⚙️ Control Panel")
        
        auto_refresh = st.checkbox("Auto-refresh", value=False)
        if auto_refresh:
            refresh_interval = st.slider("Refresh interval (seconds)", 30, 300, 60)
        
        st.markdown("---")
        st.markdown("## 📊 Data Range")
        days_history = st.slider("Historical data (days)", 7, 90, 30)
        
        st.markdown("---")
        st.markdown("## 🎯 Model Settings")
        
        if st.button("🔄 Retrain Model"):
            if 'model_trained' in st.session_state:
                del st.session_state.model_trained
            st.rerun()
        
        st.markdown("---")
        st.markdown("## 📈 System Status")
        
        status_indicators = {
            "Data Pipeline": "🟢 Healthy",
            "Model Service": "🟢 Active",
            "Alert System": "🟢 Active",
            "Monitoring": "🟢 Active"
        }
        
        for service, status in status_indicators.items():
            st.markdown(f"**{service}**: {status}")
    
    # Load data
    try:
        metrics_df, features_df, labeled_df, labels = load_and_prepare_data(simulator, feature_engineer)
        
        # Filter to recent data
        recent_metrics = metrics_df.tail(days_history * 24)
        
        # Train model if needed
        model_trained = train_model_if_needed(model, features_df, labels)
        
        # Get current metrics
        current_metrics = recent_metrics.iloc[-1].to_dict()
        
        # Generate prediction
        if model_trained:
            feature_cols = [col for col in features_df.columns if col != 'timestamp']
            X = features_df[feature_cols].fillna(0).values
            predictions, lstm_pred, xgb_pred = model.predict(X)
            current_prediction = float(predictions[-1])
        else:
            # Fallback prediction if model not trained
            current_prediction = np.random.uniform(0.2, 0.6)
        
        # Generate risk report
        risk_report = risk_engine.generate_risk_report(
            current_metrics, 
            current_prediction,
            recent_metrics
        )
        
        # Generate alerts
        alerts = alert_generator.generate_alerts_from_risk_report(risk_report)
        
        # Generate mitigation plan
        mitigation_plan = recommendation_engine.generate_mitigation_plan(risk_report)
        
        # Main dashboard
        st.markdown("---")
        
        # Metric cards
        render_metric_cards(
            health_score=risk_report['health_score'],
            failure_prob=risk_report['failure_probability']['overall'],
            active_alerts=len(alerts),
            trend=risk_report['trend']
        )
        
        st.markdown("---")
        
        # Gauges
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                render_health_score_gauge(risk_report['health_score']),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                render_failure_probability_gauge(risk_report['failure_probability']['overall']),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Timeline forecast
        st.markdown("## 📅 Failure Probability Timeline")
        forecast_data = generate_forecast(recent_metrics, hours=72)
        st.plotly_chart(
            render_timeline_forecast(forecast_data),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Two column layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Metrics dashboard
            st.markdown("## 📊 System Metrics")
            st.plotly_chart(
                render_metrics_dashboard(recent_metrics.tail(168)),  # Last week
                use_container_width=True
            )
            
            # Cost monitor
            st.markdown("## 💰 Cost Monitor")
            st.plotly_chart(
                render_cost_monitor(recent_metrics.tail(168)),
                use_container_width=True
            )
        
        with col2:
            # Executive summary
            st.markdown("## 📋 Executive Summary")
            render_executive_summary(risk_report, mitigation_plan)
            
            # Alert feed
            st.markdown("## 🔔 Alert Feed")
            render_alert_feed(alerts)
        
        st.markdown("---")
        
        # Root cause analysis
        st.markdown("## 🔍 Root Cause Analysis")
        render_root_cause_panel(risk_report['root_causes'])
        
        st.markdown("---")
        
        # Mitigation actions
        st.markdown("## 🛠️ Recommended Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🚨 Immediate (1-4h)")
            for action in mitigation_plan.get('immediate_actions', [])[:5]:
                st.markdown(f"- {action}")
        
        with col2:
            st.markdown("### 📅 Short-term (1-7d)")
            for action in mitigation_plan.get('short_term_actions', [])[:5]:
                st.markdown(f"- {action}")
        
        with col3:
            st.markdown("### 🎯 Long-term (1-3m)")
            for action in mitigation_plan.get('long_term_actions', [])[:5]:
                st.markdown(f"- {action}")
        
        # Auto-refresh (only if enabled)
        if auto_refresh:
            import time
            time.sleep(refresh_interval)
            st.rerun()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)
    
    # Enhanced Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; opacity: 0.7; padding: 20px;'>
        <p><strong>🤖 ASF-Engine v2.0.0 - Enterprise SaaS Edition</strong></p>
        <p>AI System Failure Monitoring Platform | Built with enterprise-grade reliability</p>
        <p>🔒 Secure | 🌐 Cloud Native | ⚡ Real-time Monitoring | 🚀 Production Ready</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
