#!/bin/bash

###############################################################################
# AWS Deployment Script for ASF-Engine SaaS Platform
# This script automates deployment to AWS EC2
###############################################################################

set -e  # Exit on error

echo "🚀 ASF-Engine AWS Deployment Script"
echo "===================================="

# Configuration
APP_NAME="asf-engine"
DOCKER_COMPOSE_VERSION="2.23.0"
DOMAIN="${DOMAIN:-your-domain.com}"
EMAIL="${EMAIL:-admin@your-domain.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_info "Step 1: Updating system packages..."
apt-get update
apt-get upgrade -y
print_status "System updated"

print_info "Step 2: Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_status "Docker installed"
else
    print_status "Docker already installed"
fi

print_info "Step 3: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
else
    print_status "Docker Compose already installed"
fi

print_info "Step 4: Installing Nginx..."
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    systemctl start nginx
    systemctl enable nginx
    print_status "Nginx installed"
else
    print_status "Nginx already installed"
fi

print_info "Step 5: Installing Certbot for SSL..."
apt-get install -y certbot python3-certbot-nginx
print_status "Certbot installed"

print_info "Step 6: Creating application directory..."
mkdir -p /opt/${APP_NAME}
cd /opt/${APP_NAME}
print_status "Application directory created"

print_info "Step 7: Cloning repository..."
if [ ! -d ".git" ]; then
    git clone https://github.com/ravigohel142996/ASF-Engine.git .
else
    git pull origin main
fi
print_status "Repository cloned/updated"

print_info "Step 8: Creating environment file..."
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)

cat > .env << EOF
# Database Configuration
POSTGRES_DB=asf_engine
POSTGRES_USER=asf_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET}

# Application Configuration
DOMAIN=${DOMAIN}
EMAIL=${EMAIL}

# CORS Configuration
CORS_ORIGINS=http://${DOMAIN},https://${DOMAIN},http://www.${DOMAIN},https://www.${DOMAIN}
EOF

# Save credentials to a secure file
cat > /root/asf-credentials.txt << EOF
ASF-Engine Credentials
=====================
Generated: $(date)

Database:
- Host: localhost
- Port: 5432
- Database: asf_engine
- User: asf_user
- Password: ${POSTGRES_PASSWORD}

JWT Secret: ${JWT_SECRET}

IMPORTANT: Keep this file secure and delete after noting credentials!
EOF

chmod 600 /root/asf-credentials.txt
print_status "Environment file created"
print_info "Credentials saved to /root/asf-credentials.txt"

print_info "Step 9: Configuring Nginx..."
cat > /etc/nginx/sites-available/${APP_NAME} << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend (Streamlit)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
EOF

# Replace domain in Nginx config
sed -i "s/your-domain.com/${DOMAIN}/g" /etc/nginx/sites-available/${APP_NAME}

# Enable site
ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl reload nginx
print_status "Nginx configured"

print_info "Step 10: Setting up SSL with Let's Encrypt..."
if [ "$DOMAIN" != "your-domain.com" ]; then
    certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos -m ${EMAIL}
    print_status "SSL certificate obtained"
else
    print_info "Skipping SSL setup (using default domain)"
fi

print_info "Step 11: Starting application with Docker Compose..."
docker-compose down
docker-compose up -d --build
print_status "Application started"

print_info "Step 12: Setting up auto-restart on boot..."
cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=ASF-Engine SaaS Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/${APP_NAME}
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${APP_NAME}.service
print_status "Auto-restart configured"

print_info "Step 13: Setting up log rotation..."
cat > /etc/logrotate.d/${APP_NAME} << EOF
/opt/${APP_NAME}/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker-compose -f /opt/${APP_NAME}/docker-compose.yml restart > /dev/null 2>&1 || true
    endscript
}
EOF
print_status "Log rotation configured"

print_info "Step 14: Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    print_status "Firewall configured"
fi

echo ""
print_status "============================================"
print_status "🎉 Deployment Complete!"
print_status "============================================"
echo ""
print_info "Your application is now running at:"
echo "  Frontend: http://${DOMAIN}"
echo "  API: http://${DOMAIN}/api/v1"
echo "  API Docs: http://${DOMAIN}/docs"
echo ""
print_info "Useful commands:"
echo "  View logs: cd /opt/${APP_NAME} && docker-compose logs -f"
echo "  Restart: cd /opt/${APP_NAME} && docker-compose restart"
echo "  Update: cd /opt/${APP_NAME} && git pull && docker-compose up -d --build"
echo ""
print_info "Note: It may take a few minutes for all services to fully start"
