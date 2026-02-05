"""
Streamlit Dashboard Components
Enterprise-grade UI components with glassmorphism design
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List


def apply_custom_css():
    """
    Apply custom CSS for glassmorphism and dark mode
    """
    st.markdown("""
    <style>
    /* Dark theme and glassmorphism */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glass card effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
    }
    
    /* Alert cards */
    .alert-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.2));
        border-left: 4px solid #ef4444;
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.2));
        border-left: 4px solid #fbbf24;
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Text */
    p, label, .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 500;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
    }
    
    /* Gauges and charts */
    .plotly-graph-div {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 15px;
        padding: 10px;
    }
    
    /* Executive summary box */
    .executive-summary {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.1));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 20px;
        margin: 20px 0;
    }
    
    /* Status indicators */
    .status-healthy {
        color: #10b981;
        font-weight: bold;
    }
    
    .status-warning {
        color: #fbbf24;
        font-weight: bold;
    }
    
    .status-critical {
        color: #ef4444;
        font-weight: bold;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """
    Render dashboard header
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <h1 style='margin-bottom: 0;'>🤖 AI System Failure Forecast Engine</h1>
        <p style='font-size: 1.1em; opacity: 0.8; margin-top: 5px;'>
        Production-Grade ML System Monitoring & Prediction
        </p>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='text-align: right; padding-top: 20px;'>
        <p style='font-size: 0.9em; opacity: 0.6;'>
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        </div>
        """, unsafe_allow_html=True)


def render_health_score_gauge(health_score: float):
    """
    Render system health score gauge
    """
    # Determine color based on health score
    if health_score >= 80:
        color = "green"
    elif health_score >= 60:
        color = "yellow"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = health_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "System Health Score", 'font': {'size': 24, 'color': 'white'}},
        delta = {'reference': 85, 'increasing': {'color': "green"}, 'decreasing': {'color': 'red'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.3)",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [50, 70], 'color': 'rgba(251, 191, 36, 0.3)'},
                {'range': [70, 85], 'color': 'rgba(34, 197, 94, 0.3)'},
                {'range': [85, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"},
        height=300
    )
    
    return fig


def render_failure_probability_gauge(failure_prob: float):
    """
    Render failure probability gauge
    """
    # Inverse color scheme (low failure = green)
    if failure_prob <= 30:
        color = "green"
    elif failure_prob <= 60:
        color = "yellow"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = failure_prob,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Failure Probability (72h)", 'font': {'size': 24, 'color': 'white'}},
        number = {'suffix': "%"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.3)",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.3)'},
                {'range': [30, 60], 'color': 'rgba(251, 191, 36, 0.3)'},
                {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"},
        height=300
    )
    
    return fig


def render_timeline_forecast(forecast_data: pd.DataFrame):
    """
    Render timeline forecast chart
    """
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=forecast_data['timestamp'],
        y=forecast_data['failure_probability'],
        mode='lines',
        name='Failure Probability',
        line=dict(color='#ef4444', width=3),
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.2)'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_data['timestamp'],
        y=forecast_data['health_score'],
        mode='lines',
        name='Health Score',
        line=dict(color='#10b981', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title={'text': '24-72 Hour Forecast', 'font': {'size': 20, 'color': 'white'}},
        xaxis=dict(
            title='Time',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        yaxis=dict(
            title='Failure Probability (%)',
            gridcolor='rgba(255,255,255,0.1)',
            color='white',
            range=[0, 100]
        ),
        yaxis2=dict(
            title='Health Score',
            overlaying='y',
            side='right',
            color='white',
            range=[0, 100]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        font={'color': 'white'},
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=400
    )
    
    return fig


def render_metrics_dashboard(metrics_df: pd.DataFrame):
    """
    Render key metrics over time
    """
    fig = go.Figure()
    
    # Accuracy
    fig.add_trace(go.Scatter(
        x=metrics_df['timestamp'],
        y=metrics_df['accuracy'] * 100,
        mode='lines',
        name='Accuracy (%)',
        line=dict(color='#3b82f6', width=2)
    ))
    
    # Latency (scaled)
    fig.add_trace(go.Scatter(
        x=metrics_df['timestamp'],
        y=metrics_df['latency_ms'] / 5,  # Scale for visibility
        mode='lines',
        name='Latency (ms/5)',
        line=dict(color='#f59e0b', width=2)
    ))
    
    # Error rate
    fig.add_trace(go.Scatter(
        x=metrics_df['timestamp'],
        y=metrics_df['error_rate'] * 100,
        mode='lines',
        name='Error Rate (%)',
        line=dict(color='#ef4444', width=2)
    ))
    
    fig.update_layout(
        title={'text': 'System Metrics Timeline', 'font': {'size': 20, 'color': 'white'}},
        xaxis=dict(
            title='Time',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        yaxis=dict(
            title='Value',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        font={'color': 'white'},
        hovermode='x unified',
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=400
    )
    
    return fig


def render_cost_monitor(cost_data: pd.DataFrame):
    """
    Render cost explosion monitor
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cost_data['timestamp'],
        y=cost_data['cost_per_hour'],
        mode='lines',
        name='Cost per Hour',
        line=dict(color='#8b5cf6', width=3),
        fill='tozeroy',
        fillcolor='rgba(139, 92, 246, 0.2)'
    ))
    
    # Add threshold line
    avg_cost = cost_data['cost_per_hour'].mean()
    fig.add_hline(
        y=avg_cost * 1.5,
        line_dash="dash",
        line_color="red",
        annotation_text="Alert Threshold",
        annotation_position="right"
    )
    
    fig.update_layout(
        title={'text': 'Infrastructure Cost Monitor', 'font': {'size': 20, 'color': 'white'}},
        xaxis=dict(
            title='Time',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        yaxis=dict(
            title='Cost ($/hour)',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.2)',
        font={'color': 'white'},
        hovermode='x unified',
        height=300
    )
    
    return fig


def render_root_cause_panel(root_causes: List[Dict]):
    """
    Render root cause analysis panel
    """
    if not root_causes:
        st.info("✅ No critical issues detected")
        return
    
    for cause in root_causes:
        severity_class = f"alert-{cause['severity']}"
        severity_icon = "🚨" if cause['severity'] == 'critical' else "⚠️"
        
        st.markdown(f"""
        <div class="{severity_class}">
            <h4>{severity_icon} {cause['issue']}</h4>
            <p><strong>Category:</strong> {cause['category']}</p>
            <p><strong>Current:</strong> {cause['current_value']} | <strong>Threshold:</strong> {cause['threshold']}</p>
            <p><strong>Impact:</strong> {cause['impact']}</p>
            <p>{cause['description']}</p>
        </div>
        """, unsafe_allow_html=True)


def render_alert_feed(alerts: List[Dict]):
    """
    Render alert feed
    """
    if not alerts:
        st.success("✅ No active alerts")
        return
    
    for alert in alerts[:10]:  # Show latest 10
        severity_class = f"alert-{alert['severity']}"
        severity_icon = "🚨" if alert['severity'] == 'critical' else "⚠️" if alert['severity'] == 'warning' else "ℹ️"
        
        timestamp = datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        st.markdown(f"""
        <div class="{severity_class}">
            <p><strong>{severity_icon} {alert['title']}</strong></p>
            <p style='font-size: 0.9em;'>{alert['description']}</p>
            <p style='font-size: 0.8em; opacity: 0.7;'>{timestamp}</p>
        </div>
        """, unsafe_allow_html=True)


def render_executive_summary(risk_report: Dict, mitigation_plan: Dict):
    """
    Render executive summary
    """
    st.markdown("""
    <div class="executive-summary">
        <h3>📊 Executive Summary</h3>
    """, unsafe_allow_html=True)
    
    # Risk assessment
    risk_level = mitigation_plan.get('risk_level', 'UNKNOWN')
    risk_color = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }.get(risk_level, '⚪')
    
    st.markdown(f"""
        <p><strong>Risk Level:</strong> {risk_color} {risk_level}</p>
        <p><strong>Priority:</strong> {mitigation_plan.get('priority', 'Unknown')}</p>
        <p><strong>Estimated MTTR:</strong> {mitigation_plan.get('estimated_mttr', 'Unknown')}</p>
        <p><strong>System Trend:</strong> {risk_report.get('trend', 'Unknown').title()}</p>
    """, unsafe_allow_html=True)
    
    # Key recommendations
    if mitigation_plan.get('immediate_actions'):
        st.markdown("<p><strong>Immediate Actions Required:</strong></p>", unsafe_allow_html=True)
        for action in mitigation_plan['immediate_actions'][:3]:
            st.markdown(f"<p style='margin-left: 20px;'>• {action}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_metric_cards(health_score: float, failure_prob: float, 
                       active_alerts: int, trend: str):
    """
    Render metric summary cards
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style='margin: 0; font-size: 2em;'>{health_score:.1f}</h2>
            <p style='margin: 5px 0; opacity: 0.8;'>Health Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style='margin: 0; font-size: 2em;'>{failure_prob:.1f}%</h2>
            <p style='margin: 5px 0; opacity: 0.8;'>Failure Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style='margin: 0; font-size: 2em;'>{active_alerts}</h2>
            <p style='margin: 5px 0; opacity: 0.8;'>Active Alerts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        trend_icon = "📈" if trend == "improving" else "📉" if trend == "degrading" else "➡️"
        st.markdown(f"""
        <div class="metric-card">
            <h2 style='margin: 0; font-size: 2em;'>{trend_icon}</h2>
            <p style='margin: 5px 0; opacity: 0.8;'>{trend.title()}</p>
        </div>
        """, unsafe_allow_html=True)
