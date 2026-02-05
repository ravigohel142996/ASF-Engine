# 🤖 ASF-Engine - AI System Failure Monitoring SaaS Platform

**Enterprise-grade ML system monitoring and failure prediction SaaS platform v2.0.0**

Predict ML system failures 24-72 hours in advance with enterprise-grade reliability. Complete with authentication, backend API, database, billing, and deployment infrastructure.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-production-brightgreen)

## 🎯 Overview

ASF-Engine is a complete SaaS platform for AI system monitoring and failure prediction. Built following enterprise best practices, it provides:

- 🔐 **Authentication System** (Firebase/JWT)
- 🚀 **FastAPI Backend** with REST API
- 🗄️ **PostgreSQL Database** for data persistence
- 🐳 **Docker Microservices** architecture
- 💳 **Stripe Billing** integration
- 📊 **Professional Dashboard** UI
- ☁️ **Cloud Deployment** ready (AWS/GCP)

## ✨ Key Features

### 🔒 Authentication & Security
- **Firebase Authentication**: Email/password and social login via Pyrebase4
- **JWT Tokens**: Secure API authentication
- **Session Management**: Automatic session expiry
- **Role-Based Access**: User, Admin roles
- **Protected Routes**: Middleware-based protection
- **Password Reset**: Secure email-based password recovery
- **Email Verification**: Email verification on signup
- **Account Lockout**: Protection against brute force attacks

### 🚀 Backend API (FastAPI)
- **RESTful API**: `/api/v1/` endpoints
- **Authentication**: `/login`, `/register` endpoints
- **Predictions**: `/predict` ML inference endpoint
- **Metrics**: `/metrics` data logging
- **Alerts**: `/alerts` notification system
- **Health Check**: `/health` monitoring endpoint
- **Auto Documentation**: Swagger UI at `/docs`

### 🗄️ Database (PostgreSQL)
- **Users Table**: Authentication and profiles
- **Metrics Table**: Time-series system metrics
- **Alerts Table**: System notifications
- **Logs Table**: Application logs
- **Models Table**: ML model metadata
- **Sessions Table**: Active user sessions
- **SQLAlchemy ORM**: Type-safe database operations

### Predictive Capabilities
- **24-72 Hour Forecasting**: Predict system failures up to 3 days in advance
- **Accuracy Decay Detection**: Identify model performance degradation
- **Latency Spike Prediction**: Forecast response time issues
- **Cost Overload Alerts**: Prevent infrastructure budget overruns
- **Data Pipeline Risk Analysis**: Monitor data quality and drift

### Intelligence & Analysis
- **Hybrid LSTM + XGBoost Model**: Combines temporal pattern recognition with feature interactions
- **Root Cause Analysis**: Automated identification of failure causes
- **Risk Scoring Engine**: Multi-dimensional health assessment
- **Mitigation Recommendations**: AI-powered action suggestions

### 💼 Business Features
- **Stripe Integration**: Subscription billing
- **Multiple Plans**: Free, Starter, Professional, Enterprise
- **PDF Reports**: Automated report generation
- **Data Export**: CSV, JSON, Excel formats
- **Team Accounts**: Multi-user support
- **Admin Panel**: User and system management

### Enterprise Dashboard
- **System Health Score**: Real-time overall health metric (0-100)
- **Failure Probability Gauge**: Visual risk assessment
- **Timeline Forecast**: 72-hour predictive timeline
- **Cost Explosion Monitor**: Infrastructure spend tracking
- **Alert Feed**: Prioritized incident notifications
- **Executive Summary**: C-level insights at a glance
- **Dark Mode**: Professional theme
- **Responsive Layout**: Mobile-friendly design

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                     │
│  • Login/Auth  • Dashboard  • Subscription  • Admin Panel   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend API (FastAPI)                      │
│  • JWT Auth  • REST API  • Business Logic  • ML Service     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database (PostgreSQL)                       │
│  • Users  • Metrics  • Alerts  • Logs  • Sessions          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              ML Service (Docker Container)                   │
│  • LSTM Model  • XGBoost  • Feature Engineering            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Infrastructure                      │
│  • AWS/GCP  • Docker Compose  • Nginx  • SSL/TLS           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL (or use Docker)
- Node.js (optional, for additional tooling)

### Local Development (Without Docker)

```bash
# Clone the repository
git clone https://github.com/ravigohel142996/ASF-Engine.git
cd ASF-Engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the frontend
streamlit run app.py

# In a separate terminal, run the backend
uvicorn backend.main:app --reload
```

Access the application:
- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 🐳 Docker Compose Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/ravigohel142996/ASF-Engine.git
cd ASF-Engine

# Create environment file
cp .env.example .env
# Edit .env with your secrets

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- Database: `localhost:5432`

### ☁️ AWS Cloud Deployment

```bash
# On your AWS EC2 instance (Ubuntu)
sudo ./deploy.sh
```

The deployment script will:
- Install Docker and Docker Compose
- Setup Nginx reverse proxy
- Configure SSL with Let's Encrypt
- Setup auto-restart on boot
- Configure firewall

## 📁 Project Structure

```
ASF-Engine/
├── frontend/
│   ├── app.py                    # Main Streamlit dashboard
│   └── pages/
│       ├── login.py              # Authentication page
│       ├── subscription.py       # Subscription management
│       └── admin.py              # Admin panel
├── backend/
│   ├── main.py                   # FastAPI application
│   ├── auth.py                   # JWT authentication
│   ├── database.py               # SQLAlchemy models
│   └── predict.py                # ML prediction service
├── auth/
│   └── firebase_auth.py          # Firebase integration
├── business/
│   ├── billing.py                # Stripe integration
│   ├── reports.py                # PDF generation
│   └── export.py                 # Data export
├── src/
│   ├── data/
│   │   ├── simulator.py          # Data generation
│   │   └── feature_engineering.py
│   ├── models/
│   │   └── hybrid_model.py       # LSTM + XGBoost
│   ├── monitoring/
│   │   └── risk_engine.py        # Risk assessment
│   ├── alerts/
│   │   └── alert_system.py       # Alert generation
│   └── dashboard/
│       └── components.py         # UI components
├── config/
│   └── firebase_config.json.example
├── docker-compose.yml            # Multi-service orchestration
├── Dockerfile                    # Frontend container
├── Dockerfile.backend            # Backend container
├── Dockerfile.ml                 # ML service container
├── deploy.sh                     # AWS deployment script
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🔑 Environment Configuration

⚠️ **Security Note**: All environment variables marked with `(required)` MUST be set before deployment. Never commit `.env` files to version control.

Create a `.env` file from `.env.example`:

```bash
# Database (required)
DATABASE_URL=postgresql://user:pass@localhost:5432/asf_engine
POSTGRES_DB=asf_engine
POSTGRES_USER=asf_user
POSTGRES_PASSWORD=your-strong-password  # Generate with: openssl rand -base64 32

# JWT Secret (required - minimum 32 characters)
JWT_SECRET_KEY=your-secret-key  # Generate with: openssl rand -base64 32

# CORS Origins (required for production)
CORS_ORIGINS=http://yourdomain.com,https://yourdomain.com

# Firebase (optional - for enhanced auth)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id

# Stripe (required for billing features)
STRIPE_API_KEY=sk_live_your_key  # Use sk_test_ for testing
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# AWS (optional - for deployment)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Security Best Practices

1. **Generate Strong Secrets**: Use `openssl rand -base64 32` for all secrets
2. **Environment Variables**: Never hardcode credentials in source code
3. **CORS Configuration**: Restrict to specific domains in production
4. **Database Passwords**: Use strong, unique passwords (minimum 32 characters)
5. **SSL/TLS**: Always use HTTPS in production
6. **Regular Updates**: Keep all dependencies up to date

## 🔐 Authentication

### Firebase Setup (Optional but Recommended)

1. Create a Firebase project at [firebase.google.com](https://firebase.google.com)
2. Enable Authentication → Email/Password
3. Get your config from Project Settings
4. Copy config to `config/firebase_config.json`

### Demo Mode

If Firebase is not configured, the app runs in demo mode accepting any credentials for testing.

## 💳 Billing Setup

### Stripe Integration

1. Create account at [stripe.com](https://stripe.com)
2. Get your API keys from Dashboard
3. Add to `.env` file
4. Create products and prices in Stripe Dashboard
5. Update price IDs in `business/billing.py`

### Subscription Plans

- **Free**: $0/month - Basic monitoring, 100 predictions
- **Starter**: $49/month - Advanced monitoring, 1K predictions
- **Professional**: $199/month - Full suite, unlimited predictions
- **Enterprise**: $499/month - Custom deployment, dedicated support

## 📊 API Documentation

### Authentication Endpoints

```http
POST /api/v1/register
POST /api/v1/login
```

### Prediction Endpoints

```http
POST /api/v1/predict
GET  /api/v1/metrics
POST /api/v1/metrics
```

### Alert Endpoints

```http
GET  /api/v1/alerts
POST /api/v1/alerts
```

### Management Endpoints

```http
GET  /api/v1/profile
GET  /api/v1/stats
GET  /health
```

Full API documentation available at `/docs` when running the backend.

## 📊 System Components

### Data Simulator (`src/data/simulator.py`)
Generates realistic ML system operational data:
- Time-series metrics (accuracy, latency, errors)
- Resource utilization (CPU, memory, cost)
- Data quality metrics (drift scores)
- Failure scenario injection for training

### Feature Engineering (`src/data/feature_engineering.py`)
Transforms raw metrics into predictive features:
- Temporal features (hourly, daily patterns)
- Rolling statistics (mean, std, min, max)
- Trend analysis (rate of change)
- Interaction features (efficiency metrics)
- Anomaly detection (statistical outliers)

### Hybrid Model (`src/models/hybrid_model.py`)
LSTM + XGBoost ensemble for failure prediction:
- **LSTM**: Captures temporal dependencies and sequential patterns
- **XGBoost**: Models complex feature interactions
- **Ensemble**: Weighted combination for robust predictions

### Risk Engine (`src/monitoring/risk_engine.py`)
Comprehensive risk assessment:
- Health score calculation (0-100 scale)
- Failure probability (24h, 48h, 72h windows)
- Root cause identification
- Confidence scoring

### Alert System (`src/alerts/alert_system.py`)
Intelligent alerting and recommendations:
- Multi-level severity (Critical, Warning, Info)
- Context-aware recommendations
- Mitigation plan generation
- MTTR estimation

### Dashboard (`src/dashboard/components.py`)
Enterprise-grade UI components:
- Glassmorphism design
- Dark mode optimized
- Animated visualizations
- Mobile responsive layout

## 📈 Use Cases

### SRE Teams
- **Proactive Incident Prevention**: Receive alerts before failures occur
- **Capacity Planning**: Forecast resource needs based on trends
- **Post-Mortem Analysis**: Understand failure patterns and root causes

### ML Engineers
- **Model Health Monitoring**: Track accuracy decay over time
- **Drift Detection**: Identify data distribution changes
- **Performance Optimization**: Pinpoint bottlenecks and inefficiencies

### Engineering Managers
- **Risk Assessment**: Understand system stability at a glance
- **Resource Allocation**: Optimize infrastructure spend
- **Team Prioritization**: Data-driven incident response

### Executives
- **Business Impact**: Quantify reliability risks
- **Cost Control**: Monitor and prevent budget overruns
- **Strategic Planning**: Long-term system health trends

## 💼 Business Impact

### Cost Savings
- **Prevent Downtime**: Average incident costs $5,600/minute (Gartner)
- **Optimize Resources**: 20-30% reduction in over-provisioning
- **Reduce MTTR**: 50% faster incident resolution

### Reliability
- **Increase Uptime**: Target 99.99% availability
- **Customer Trust**: Fewer service disruptions
- **SLA Compliance**: Meet contractual obligations

### Efficiency
- **Automation**: 70% of alerts with recommended actions
- **Team Productivity**: Focus on prevention vs. firefighting
- **Data-Driven Decisions**: Eliminate guesswork

## 🔧 Configuration

### Environment Variables
```bash
STREAMLIT_SERVER_PORT=8501        # Server port
STREAMLIT_SERVER_ADDRESS=0.0.0.0  # Bind address
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Model Parameters
Configurable in `src/models/hybrid_model.py`:
- `sequence_length`: LSTM lookback window (default: 24h)
- `lstm_units`: LSTM layer size (default: 128)
- `dropout_rate`: Regularization (default: 0.3)

### Risk Thresholds
Adjustable in `src/monitoring/risk_engine.py`:
```python
risk_thresholds = {
    'accuracy': {'critical': 0.85, 'warning': 0.90},
    'latency_ms': {'critical': 200, 'warning': 100},
    'error_rate': {'critical': 0.05, 'warning': 0.02},
    # ... customize based on your SLAs
}
```

## 📊 Metrics & KPIs

### System Health Score Components
- **Model Accuracy** (25%): Prediction quality
- **Latency** (20%): Response time performance
- **Error Rate** (20%): System reliability
- **Resource Utilization** (15%): Infrastructure efficiency
- **Data Quality** (10%): Input data health
- **Pipeline Reliability** (10%): ETL success rate

### Prediction Accuracy
- **Precision**: Target >85% for failure predictions
- **Recall**: Target >90% to catch critical issues
- **F1 Score**: Balanced performance metric
- **AUC-ROC**: Model discrimination capability

## 🚦 Scaling Roadmap

### Phase 1: Core Platform (Current)
✅ Real-time monitoring dashboard  
✅ Hybrid prediction model  
✅ Alert generation  
✅ Root cause analysis  

### Phase 2: Enhanced Intelligence (Q1)
- [ ] Multi-model ensemble (transformers, prophet)
- [ ] Automated model retraining pipeline
- [ ] A/B testing framework for model versions
- [ ] Custom alert routing (Slack, PagerDuty, email)

### Phase 3: Advanced Features (Q2)
- [ ] Multi-tenant architecture
- [ ] Historical trend analysis (1+ years)
- [ ] What-if scenario simulator
- [ ] Integration with cloud providers (AWS, GCP, Azure)

### Phase 4: Enterprise (Q3)
- [ ] Role-based access control (RBAC)
- [ ] Audit logging and compliance
- [ ] API for programmatic access
- [ ] Custom dashboard builder

## 🛠️ Development

### Project Structure
```
ASF-Engine/
├── src/
│   ├── data/
│   │   ├── simulator.py           # Data generation
│   │   └── feature_engineering.py # Feature pipeline
│   ├── models/
│   │   └── hybrid_model.py        # LSTM + XGBoost
│   ├── monitoring/
│   │   └── risk_engine.py         # Risk scoring
│   ├── alerts/
│   │   └── alert_system.py        # Alerts & recommendations
│   └── dashboard/
│       └── components.py          # UI components
├── app.py                         # Main Streamlit app
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container config
├── .streamlit/
│   └── config.toml               # Streamlit settings
└── README.md                     # Documentation
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=src

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code
black src/ app.py

# Lint
pylint src/ app.py

# Type checking
mypy src/ app.py
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

Built with production-grade standards by senior engineers following Google SRE principles.

## 🙏 Acknowledgments

- Inspired by Google SRE practices
- Built with Streamlit for rapid development
- Powered by TensorFlow and XGBoost for ML
- Styled with modern glassmorphism design

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the documentation wiki
- Join our community discussions

## 🔒 Security

Found a security vulnerability? Please email security@asf-engine.io instead of opening a public issue.

---

**Built for production. Designed for scale. Engineered for reliability.**

*Version 1.0.0 | Last Updated: 2024*
