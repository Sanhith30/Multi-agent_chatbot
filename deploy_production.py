#!/usr/bin/env python3
"""
Production Deployment Script for SunnyAI Loan Assistant
This script automates the deployment of the real-time production system
"""

import os
import subprocess
import sys
import json
from pathlib import Path
import time

class ProductionDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        
    def check_prerequisites(self):
        """Check if all required tools are installed"""
        print("🔍 Checking prerequisites...")
        
        required_tools = [
            ("docker", "Docker is required for containerization"),
            ("docker-compose", "Docker Compose is required for orchestration"),
            ("git", "Git is required for version control"),
            ("openssl", "OpenSSL is required for SSL certificates")
        ]
        
        for tool, description in required_tools:
            if not self._command_exists(tool):
                print(f"❌ {tool} not found. {description}")
                return False
            else:
                print(f"✅ {tool} found")
        
        return True
    
    def setup_environment(self):
        """Set up production environment variables"""
        print("\n🔧 Setting up environment...")
        
        if not self.env_file.exists():
            print("Creating .env file...")
            env_template = """
# AI Services
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Database
DATABASE_URL=postgresql://sunnyai_user:secure_password_123@db:5432/sunnyai_prod
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your_super_secure_jwt_secret_key_here_change_this
ENCRYPTION_KEY=your_encryption_key_here_change_this

# External APIs (Optional - for real integrations)
CREDIT_BUREAU_API_KEY=your_credit_bureau_api_key
SMS_GATEWAY_API_KEY=your_sms_gateway_api_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
WORKERS=4
ENVIRONMENT=production

# Monitoring
SENTRY_DSN=your_sentry_dsn_for_error_tracking
PROMETHEUS_PORT=9090
GRAFANA_PASSWORD=admin123
DB_PASSWORD=secure_password_123
"""
            with open(self.env_file, 'w') as f:
                f.write(env_template.strip())
            
            print("⚠️  Please edit .env file with your actual API keys and passwords")
            print("📝 Required: OPENAI_API_KEY for real AI functionality")
            return False
        else:
            print("✅ .env file exists")
            return True
    
    def create_production_dockerfile(self):
        """Create production-optimized Dockerfile"""
        print("\n🐳 Creating production Dockerfile...")
        
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
"""
        
        with open(self.project_root / "Dockerfile.prod", 'w') as f:
            f.write(dockerfile_content.strip())
        
        print("✅ Production Dockerfile created")
    
    def create_docker_compose_prod(self):
        """Create production Docker Compose file"""
        print("\n🐙 Creating production Docker Compose...")
        
        compose_content = """
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://sunnyai_user:${DB_PASSWORD}@db:5432/sunnyai_prod
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    volumes:
      - ./generated_docs:/app/generated_docs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "3001:80"
    depends_on:
      - app
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=sunnyai_prod
      - POSTGRES_USER=sunnyai_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sunnyai_user -d sunnyai_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
      - frontend
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/var/lib/grafana/dashboards
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  grafana_data:
"""
        
        with open(self.project_root / "docker-compose.prod.yml", 'w') as f:
            f.write(compose_content.strip())
        
        print("✅ Production Docker Compose created")
    
    def create_nginx_config(self):
        """Create production Nginx configuration"""
        print("\n🌐 Creating Nginx configuration...")
        
        nginx_config = """
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server app:8000;
    }
    
    upstream frontend {
        server frontend:80;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    server {
        listen 80;
        server_name localhost;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
        
        # Metrics (restrict access)
        location /metrics {
            allow 127.0.0.1;
            deny all;
            proxy_pass http://backend/metrics;
        }
    }
}
"""
        
        with open(self.project_root / "nginx.prod.conf", 'w') as f:
            f.write(nginx_config.strip())
        
        print("✅ Nginx configuration created")
    
    def create_monitoring_config(self):
        """Create monitoring configuration"""
        print("\n📊 Setting up monitoring...")
        
        # Create monitoring directory
        monitoring_dir = self.project_root / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        # Prometheus configuration
        prometheus_config = """
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sunnyai-backend'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
"""
        
        with open(monitoring_dir / "prometheus.yml", 'w') as f:
            f.write(prometheus_config.strip())
        
        print("✅ Monitoring configuration created")
    
    def update_requirements(self):
        """Update requirements.txt for production"""
        print("\n📦 Updating requirements for production...")
        
        production_requirements = """
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
websockets==12.0
pydantic==2.5.0

# AI Integration
openai==1.3.0

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1

# Caching & Background Tasks
redis==5.0.1
celery==5.3.4

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==41.0.8

# File Handling
python-multipart==0.0.6
reportlab==4.0.7

# HTTP Client
httpx==0.25.2

# Monitoring & Logging
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.38.0

# Development & Testing
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
"""
        
        with open(self.project_root / "requirements.prod.txt", 'w') as f:
            f.write(production_requirements.strip())
        
        print("✅ Production requirements created")
    
    def create_frontend_dockerfile(self):
        """Create production Dockerfile for frontend"""
        print("\n🎨 Creating frontend production Dockerfile...")
        
        frontend_dir = self.project_root / "frontend"
        dockerfile_content = """
# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open(frontend_dir / "Dockerfile.prod", 'w') as f:
            f.write(dockerfile_content.strip())
        
        # Frontend nginx config
        frontend_nginx = """
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Handle React routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
"""
        
        with open(frontend_dir / "nginx.conf", 'w') as f:
            f.write(frontend_nginx.strip())
        
        print("✅ Frontend production setup created")
    
    def deploy(self):
        """Deploy the production system"""
        print("\n🚀 Deploying production system...")
        
        try:
            # Build and start services
            print("Building Docker images...")
            subprocess.run(["docker-compose", "-f", "docker-compose.prod.yml", "build"], check=True)
            
            print("Starting services...")
            subprocess.run(["docker-compose", "-f", "docker-compose.prod.yml", "up", "-d"], check=True)
            
            # Wait for services to be ready
            print("Waiting for services to be ready...")
            time.sleep(30)
            
            # Health checks
            print("Running health checks...")
            self._check_service_health()
            
            print("\n🎉 Production deployment completed successfully!")
            print("\n📊 Access your application:")
            print("🌐 Frontend: http://localhost:3001")
            print("🔧 Backend API: http://localhost:8000")
            print("📈 Grafana: http://localhost:3000 (admin/admin123)")
            print("📊 Prometheus: http://localhost:9090")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            return False
        
        return True
    
    def _check_service_health(self):
        """Check if all services are healthy"""
        services = [
            ("Backend", "http://localhost:8000/health"),
            ("Frontend", "http://localhost:3001/health"),
            ("Prometheus", "http://localhost:9090/-/healthy"),
            ("Grafana", "http://localhost:3000/api/health")
        ]
        
        for service_name, url in services:
            try:
                import requests
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {service_name} is healthy")
                else:
                    print(f"⚠️  {service_name} returned status {response.status_code}")
            except Exception as e:
                print(f"❌ {service_name} health check failed: {e}")
    
    def _command_exists(self, command):
        """Check if a command exists in the system"""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

def main():
    """Main deployment function"""
    print("🚀 SunnyAI Production Deployment Script")
    print("=" * 50)
    
    deployer = ProductionDeployer()
    
    # Step 1: Check prerequisites
    if not deployer.check_prerequisites():
        print("❌ Prerequisites check failed. Please install required tools.")
        sys.exit(1)
    
    # Step 2: Setup environment
    if not deployer.setup_environment():
        print("⚠️  Please configure your .env file and run the script again.")
        sys.exit(1)
    
    # Step 3: Create production files
    deployer.create_production_dockerfile()
    deployer.create_docker_compose_prod()
    deployer.create_nginx_config()
    deployer.create_monitoring_config()
    deployer.update_requirements()
    deployer.create_frontend_dockerfile()
    
    # Step 4: Deploy
    print("\n🤔 Ready to deploy to production?")
    response = input("Type 'yes' to continue: ").lower().strip()
    
    if response == 'yes':
        if deployer.deploy():
            print("\n🎉 Deployment successful!")
            print("\n📋 Next steps:")
            print("1. Configure your domain name and SSL certificates")
            print("2. Set up monitoring alerts")
            print("3. Configure backup strategies")
            print("4. Set up CI/CD pipeline")
        else:
            print("❌ Deployment failed. Check the logs above.")
            sys.exit(1)
    else:
        print("Deployment cancelled.")

if __name__ == "__main__":
    main()