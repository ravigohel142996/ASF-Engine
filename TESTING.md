# ASF-Engine Testing Guide

## Overview

This document provides testing instructions for the ASF-Engine SaaS Platform.

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- Access to terminal/command line

## Local Testing

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/ravigohel142996/ASF-Engine.git
cd ASF-Engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with test values
```

### 2. Test Frontend (Streamlit)

```bash
# Run Streamlit app
streamlit run app.py

# Access at http://localhost:8501
```

**Test Cases:**
- [ ] Login page loads correctly
- [ ] Can navigate to dashboard (with mock auth)
- [ ] Dashboard displays metrics and charts
- [ ] Sidebar controls work
- [ ] Logout functionality works

### 3. Test Backend API (FastAPI)

```bash
# Run backend server
uvicorn backend.main:app --reload

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Test Cases:**
- [ ] Health check: `GET /health` returns 200
- [ ] Register: `POST /api/v1/register` creates user
- [ ] Login: `POST /api/v1/login` returns JWT token
- [ ] Protected endpoint requires valid token
- [ ] API documentation loads at /docs

**Example API Tests:**

```bash
# Health check
curl http://localhost:8000/health

# Register (with proper env vars set)
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123", "full_name": "Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

### 4. Test Database Connection

```bash
# If using Docker PostgreSQL
docker-compose up -d database

# Test connection
docker-compose exec database psql -U asf_user -d asf_engine -c "SELECT 1;"
```

## Docker Testing

### 1. Build and Run All Services

```bash
# Set required environment variables
export JWT_SECRET_KEY=$(openssl rand -base64 32)
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Verify Services

```bash
# Check running containers
docker-compose ps

# Expected output:
# - asf-frontend (running)
# - asf-backend (running)
# - asf-database (healthy)
# - asf-ml-service (running)
```

### 3. Test Service Communication

```bash
# Test frontend can reach backend
docker-compose exec frontend curl http://backend:8000/health

# Test backend can reach database
docker-compose exec backend python -c "from backend.database import engine; print(engine.connect())"
```

## Integration Testing

### 1. End-to-End User Flow

1. Open browser to `http://localhost:8501`
2. Navigate to login page
3. Create account with email/password
4. Login with credentials
5. View dashboard
6. Navigate to subscription page
7. Navigate to admin panel (if admin role)
8. Test logout

### 2. API Integration Test

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/api/v1/register", json={
    "email": "test@example.com",
    "password": "secure123",
    "full_name": "Test User"
})
print(f"Register: {response.status_code}")

# Login
response = requests.post(f"{BASE_URL}/api/v1/login", json={
    "email": "test@example.com",
    "password": "secure123"
})
token = response.json()["access_token"]
print(f"Login: {response.status_code}")

# Make prediction (with token)
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/api/v1/predict", 
    headers=headers,
    json={
        "metrics": {
            "accuracy": 0.95,
            "latency_ms": 50,
            "error_rate": 0.01,
            "cpu_usage": 0.5,
            "memory_usage": 0.6
        }
    }
)
print(f"Predict: {response.status_code}")
print(f"Response: {response.json()}")
```

## Security Testing

### 1. Environment Variable Validation

```bash
# Test missing JWT_SECRET_KEY
unset JWT_SECRET_KEY
uvicorn backend.main:app

# Expected: ValueError about missing JWT_SECRET_KEY
```

### 2. CORS Testing

```bash
# Test CORS with unauthorized origin
curl -X OPTIONS http://localhost:8000/api/v1/predict \
  -H "Origin: http://malicious-site.com" \
  -H "Access-Control-Request-Method: POST"

# Expected: CORS error or rejection
```

### 3. Authentication Testing

```bash
# Test protected endpoint without token
curl http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"metrics": {}}'

# Expected: 401 Unauthorized
```

## Performance Testing

### 1. Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Review results for:
# - Requests per second
# - Response times
# - Failed requests (should be 0)
```

### 2. Database Performance

```bash
# Monitor database performance
docker-compose exec database psql -U asf_user -d asf_engine -c "
SELECT 
  schemaname,
  tablename,
  n_tup_ins as inserts,
  n_tup_upd as updates,
  n_tup_del as deletes
FROM pg_stat_user_tables;
"
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :8501
   # Kill process
   kill -9 <PID>
   ```

2. **Database Connection Failed**
   ```bash
   # Check database is running
   docker-compose ps database
   # Restart database
   docker-compose restart database
   ```

3. **Module Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

4. **Docker Build Fails**
   ```bash
   # Clean docker cache
   docker-compose down -v
   docker system prune -a
   docker-compose up -d --build
   ```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Test ASF-Engine

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: asf_engine
          POSTGRES_USER: asf_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Set environment
      run: |
        echo "DATABASE_URL=postgresql://asf_user:test_password@localhost:5432/asf_engine" >> $GITHUB_ENV
        echo "JWT_SECRET_KEY=$(openssl rand -base64 32)" >> $GITHUB_ENV
    
    - name: Run tests
      run: |
        # Add your test commands here
        python -m pytest tests/ -v
```

## Test Checklist

- [ ] All services start successfully with docker-compose
- [ ] Frontend loads and displays correctly
- [ ] Backend API responds to all endpoints
- [ ] Database connections work
- [ ] Authentication flow works end-to-end
- [ ] Protected routes require authentication
- [ ] CORS restrictions work as expected
- [ ] Environment variables are validated
- [ ] Error messages are sanitized
- [ ] Security scanner (CodeQL) passes
- [ ] No hardcoded credentials in code
- [ ] Documentation is accurate and complete

## Production Readiness Checklist

Before deploying to production:

- [ ] All environment variables set with strong values
- [ ] Database password is strong (32+ characters)
- [ ] JWT secret is strong (32+ characters)
- [ ] CORS restricted to production domains only
- [ ] Firebase configured (if using)
- [ ] Stripe configured (if using billing)
- [ ] SSL/TLS certificates configured
- [ ] Nginx reverse proxy configured
- [ ] Auto-restart on boot configured
- [ ] Log rotation configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented

## Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in README.md
- Review logs: `docker-compose logs -f`
