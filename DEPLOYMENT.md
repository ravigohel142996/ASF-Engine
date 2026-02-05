# ASF-Engine Deployment Guide

## Overview

This guide covers deploying ASF-Engine SaaS Platform to various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
4. [Render Deployment](#render-deployment)
5. [Docker Deployment](#docker-deployment)
6. [AWS EC2 Deployment](#aws-ec2-deployment)
7. [Google Cloud Platform](#google-cloud-platform)
8. [Kubernetes Deployment](#kubernetes-deployment)
9. [Environment Configuration](#environment-configuration)
10. [Post-Deployment](#post-deployment)
11. [Monitoring & Maintenance](#monitoring--maintenance)

## Prerequisites

- Server/VM with minimum 4GB RAM, 2 CPU cores
- Root/sudo access
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt free option available)

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/ravigohel142996/ASF-Engine.git
cd ASF-Engine

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run services separately
streamlit run app.py              # Terminal 1
uvicorn backend.main:app --reload # Terminal 2
```

### Docker Compose (Recommended for Development)

```bash
# Set required environment variables
export JWT_SECRET_KEY=$(openssl rand -base64 32)
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Streamlit Cloud Deployment

### Setup Instructions

1. **Fork or Push Repository to GitHub**

2. **Configure Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`

3. **Configure Secrets**
   - In Streamlit Cloud, go to App Settings > Secrets
   - Add your environment variables in TOML format:

```toml
# Database (use managed PostgreSQL or Supabase)
DATABASE_URL = "postgresql://user:password@host:5432/database"

# JWT Secret (generate with: openssl rand -base64 32)
JWT_SECRET_KEY = "your-jwt-secret-key-at-least-32-characters"

# Firebase Configuration (Optional)
FIREBASE_API_KEY = "your_firebase_api_key"
FIREBASE_AUTH_DOMAIN = "your-project.firebaseapp.com"
FIREBASE_PROJECT_ID = "your-project-id"

# Email Configuration (Optional - for verification)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"
BASE_URL = "https://your-app.streamlit.app"

# Demo Credentials
DEMO_EMAIL = "admin@test.com"
DEMO_PASSWORD = "1234"
```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your app will be available at `https://your-app-name.streamlit.app`

### Database Options for Streamlit Cloud

**Option 1: Supabase (Recommended)**
```bash
# Free PostgreSQL hosting
# 1. Create account at supabase.com
# 2. Create new project
# 3. Copy connection string from Settings > Database
# 4. Add to Streamlit secrets as DATABASE_URL
```

**Option 2: ElephantSQL**
```bash
# Free PostgreSQL hosting
# 1. Create account at elephantsql.com
# 2. Create new instance
# 3. Copy connection URL
# 4. Add to Streamlit secrets as DATABASE_URL
```

**Option 3: Neon**
```bash
# Free serverless PostgreSQL
# 1. Create account at neon.tech
# 2. Create new project
# 3. Copy connection string
# 4. Add to Streamlit secrets as DATABASE_URL
```

### Important Notes

- ✅ No PYTHONPATH issues - imports work automatically
- ✅ Pyrebase4 is included in requirements.txt
- ✅ Environment variables are read from Streamlit secrets
- ✅ System works with or without Firebase configured
- ✅ Demo mode available for testing without Firebase

## Render Deployment

### Frontend (Streamlit) on Render

1. **Create New Web Service**
   - Go to [render.com](https://render.com)
   - Click "New" > "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Name: `asf-engine-frontend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

3. **Environment Variables**
   Add these in Render dashboard:
   ```
   DATABASE_URL=postgresql://user:password@host/database
   JWT_SECRET_KEY=your-jwt-secret-key
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   BASE_URL=https://your-app.onrender.com
   DEMO_EMAIL=admin@test.com
   DEMO_PASSWORD=1234
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment
   - Your app will be at `https://your-app.onrender.com`

### Backend (FastAPI) on Render

1. **Create Another Web Service**
   - Name: `asf-engine-backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

2. **Add Same Environment Variables**

3. **Update Frontend Environment**
   - Add `BACKEND_API_URL=https://your-backend.onrender.com` to frontend

### Database on Render

**Option 1: Render PostgreSQL (Paid)**
```bash
# Create new PostgreSQL database in Render
# Copy internal connection string
# Use in DATABASE_URL
```

**Option 2: External Database**
- Use Supabase, ElephantSQL, or Neon (free options)
- Add connection string to both frontend and backend

### Production Considerations

- ✅ Free tier available on Render (with limitations)
- ✅ Automatic SSL certificates
- ✅ Auto-deploy on git push
- ✅ Health checks and monitoring
- ⚠️ Free tier services sleep after inactivity
- 💡 Use paid tier for production workloads

## Docker Deployment

### Single Host Deployment

```bash
# On your server
git clone https://github.com/ravigohel142996/ASF-Engine.git
cd ASF-Engine

# Create production .env
cat > .env << EOF
DATABASE_URL=postgresql://asf_user:$(openssl rand -base64 32)@database:5432/asf_engine
POSTGRES_DB=asf_engine
POSTGRES_USER=asf_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)
CORS_ORIGINS=http://yourdomain.com,https://yourdomain.com
STRIPE_API_KEY=sk_live_your_key
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Production Docker Setup

1. **Setup Nginx Reverse Proxy**

```nginx
# /etc/nginx/sites-available/asf-engine
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **Enable SSL with Let's Encrypt**

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## AWS EC2 Deployment

### Automated Deployment

```bash
# On AWS EC2 Ubuntu instance
wget https://raw.githubusercontent.com/ravigohel142996/ASF-Engine/main/deploy.sh
chmod +x deploy.sh
sudo DOMAIN=yourdomain.com EMAIL=admin@yourdomain.com ./deploy.sh
```

The script will:
- Install Docker and Docker Compose
- Setup PostgreSQL
- Configure Nginx with SSL
- Start all services
- Configure auto-restart

### Manual AWS Deployment

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Minimum t3.medium (2 vCPU, 4GB RAM)
   - Configure security groups:
     - SSH: 22
     - HTTP: 80
     - HTTPS: 443

2. **Connect and Setup**

```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone https://github.com/ravigohel142996/ASF-Engine.git
cd ASF-Engine
# Follow Docker deployment steps above
```

## Google Cloud Platform

### Using Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/your-project/asf-engine-frontend
gcloud builds submit --tag gcr.io/your-project/asf-engine-backend --file Dockerfile.backend

# Deploy services
gcloud run deploy asf-frontend \
  --image gcr.io/your-project/asf-engine-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy asf-backend \
  --image gcr.io/your-project/asf-engine-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Using Compute Engine

Similar to AWS EC2 deployment - follow manual AWS steps.

## Kubernetes Deployment

### Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: asf-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: asf-engine
  template:
    metadata:
      labels:
        app: asf-engine
    spec:
      containers:
      - name: frontend
        image: your-registry/asf-engine:latest
        ports:
        - containerPort: 8501
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: asf-secrets
              key: database-url
      - name: backend
        image: your-registry/asf-engine-backend:latest
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: asf-engine
spec:
  selector:
    app: asf-engine
  ports:
  - name: frontend
    port: 80
    targetPort: 8501
  - name: backend
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f secrets.yaml
kubectl get services
```

## Environment Configuration

### Production Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/db
JWT_SECRET_KEY=<32+ character secret>
POSTGRES_PASSWORD=<32+ character password>
CORS_ORIGINS=https://yourdomain.com

# Optional
FIREBASE_API_KEY=<your-key>
STRIPE_API_KEY=<your-key>
AWS_ACCESS_KEY_ID=<your-key>
```

### Generating Secure Secrets

```bash
# Strong password
openssl rand -base64 32

# UUID
uuidgen

# Hex secret
openssl rand -hex 32
```

## Post-Deployment

### 1. Verify Services

```bash
# Check all services
curl https://yourdomain.com
curl https://yourdomain.com/api/v1/health

# Check SSL
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### 2. Database Initialization

```bash
# Connect to database
docker-compose exec database psql -U asf_user -d asf_engine

# Verify tables
\dt

# Create admin user (if needed)
INSERT INTO users (email, hashed_password, full_name, is_admin, role)
VALUES ('admin@yourdomain.com', 'hashed_password', 'Admin User', true, 'admin');
```

### 3. Configure Monitoring

```bash
# Setup log rotation
sudo nano /etc/logrotate.d/asf-engine

# Add monitoring
# - CloudWatch (AWS)
# - Stackdriver (GCP)
# - Prometheus + Grafana
# - Datadog
```

## Monitoring & Maintenance

### Health Checks

```bash
# API health
curl https://yourdomain.com/api/v1/health

# Container health
docker-compose ps
docker-compose logs --tail=100

# Database health
docker-compose exec database pg_isready
```

### Backup Strategy

```bash
# Database backup
docker-compose exec database pg_dump -U asf_user asf_engine > backup.sql

# Automated daily backups
cat > /root/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T database pg_dump -U asf_user asf_engine | gzip > /backups/asf_$DATE.sql.gz
find /backups -name "asf_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /root/backup.sh

# Add to crontab
0 2 * * * /root/backup.sh
```

### Updates

```bash
# Update application
cd ASF-Engine
git pull origin main
docker-compose down
docker-compose up -d --build

# Update dependencies
pip install -r requirements.txt --upgrade
```

### Scaling

```bash
# Scale services with Docker Compose
docker-compose up -d --scale backend=3

# Load balancer configuration needed for multi-instance
```

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   docker-compose logs
   # Check environment variables
   # Verify ports are not in use
   ```

2. **Database connection failed**
   ```bash
   # Check DATABASE_URL
   # Verify PostgreSQL is running
   docker-compose ps database
   ```

3. **SSL certificate issues**
   ```bash
   # Renew certificate
   sudo certbot renew
   # Restart nginx
   sudo systemctl restart nginx
   ```

4. **High memory usage**
   ```bash
   # Check container stats
   docker stats
   # Optimize database
   docker-compose exec database vacuumdb -U asf_user -d asf_engine -z
   ```

## Security Checklist

- [ ] All environment variables use strong, unique values
- [ ] SSL/TLS enabled with valid certificate
- [ ] CORS restricted to production domains
- [ ] Database password rotated regularly
- [ ] Firewall configured (only 80, 443, 22 open)
- [ ] SSH key authentication (password login disabled)
- [ ] Regular security updates applied
- [ ] Backups tested and working
- [ ] Monitoring and alerting configured
- [ ] Rate limiting enabled on API
- [ ] DDoS protection configured (CloudFlare/AWS Shield)

## Support

For deployment assistance:
- GitHub Issues: https://github.com/ravigohel142996/ASF-Engine/issues
- Documentation: README.md and TESTING.md
- Logs: `docker-compose logs -f`

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [AWS EC2 Guide](https://aws.amazon.com/ec2/getting-started/)
