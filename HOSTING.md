# 🚀 RCA Agent Hosting Guide

Complete guide for hosting the RCA Agent web interface on various platforms.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Cloud Hosting Options](#cloud-hosting-options)
- [Production Configuration](#production-configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 2GB RAM minimum, 4GB recommended
- 10GB disk space for artifacts

### One-Command Deployment
```bash
# Docker deployment (requires Docker Desktop to be running)
./scripts/deploy.sh

# Production deployment with Nginx
./scripts/deploy.sh production

# Simple deployment (no Docker required)
./scripts/host-simple.sh
```

### If Docker Daemon is Not Running
If you see "Cannot connect to the Docker daemon" error:

**macOS**: Open Docker Desktop application
**Linux**: `sudo systemctl start docker`
**Windows**: Start Docker Desktop

Or use the simple hosting option: `./scripts/host-simple.sh`

## 🐳 Docker Deployment

### Local Development
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production with Nginx
```bash
# Deploy with reverse proxy
docker-compose --profile production up -d

# Access at http://localhost/
```

### Environment Variables
Create `.env` file for configuration:
```bash
# Optional: Linear API integration
LINEAR_API_KEY=your_linear_api_key
LINEAR_TEAM_KEY=your_team_key

# Server configuration
PYTHONUNBUFFERED=1
```

## ☁️ Cloud Hosting Options

### 1. AWS ECS (Recommended for Production)

#### Setup Steps:
1. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name rca-agent
   ```

2. **Build and Push to ECR**
   ```bash
   # Create ECR repository
   aws ecr create-repository --repository-name rca-agent
   
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push
   docker build -t rca-agent .
   docker tag rca-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rca-agent:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rca-agent:latest
   ```

3. **Create Task Definition**
   ```json
   {
     "family": "rca-agent",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "rca-agent",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/rca-agent:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/rca-agent",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

4. **Create Service with Load Balancer**
   ```bash
   aws ecs create-service \
     --cluster rca-agent \
     --service-name rca-agent-service \
     --task-definition rca-agent \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

### 2. Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/rca-agent
gcloud run deploy --image gcr.io/PROJECT-ID/rca-agent --platform managed --port 8000
```

### 3. Azure Container Instances

```bash
# Create resource group
az group create --name rca-agent-rg --location eastus

# Deploy container
az container create \
  --resource-group rca-agent-rg \
  --name rca-agent \
  --image your-registry/rca-agent:latest \
  --dns-name-label rca-agent-unique \
  --ports 8000
```

### 4. DigitalOcean App Platform

Create `app.yaml`:
```yaml
name: rca-agent
services:
- name: api
  source_dir: /
  github:
    repo: your-username/rca-agent
    branch: main
  run_command: python serve.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8000
  routes:
  - path: /
```

### 5. Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-rca-agent

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

Create `Procfile`:
```
web: python serve.py
```

### 6. Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## 🔧 Production Configuration

### SSL/HTTPS Setup

1. **Using Let's Encrypt with Nginx**
   ```bash
   # Install certbot
   sudo apt-get install certbot python3-certbot-nginx
   
   # Get certificate
   sudo certbot --nginx -d your-domain.com
   ```

2. **Update nginx.conf for HTTPS**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       # Include SSL security headers
       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
   }
   ```

### Environment Configuration

Create production `.env`:
```bash
# Production settings
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=your-secret-key-here

# Database (if using external storage)
DATABASE_URL=postgresql://user:pass@host:port/db

# Monitoring
SENTRY_DSN=your-sentry-dsn

# Linear integration
LINEAR_API_KEY=your-production-linear-key
LINEAR_TEAM_KEY=your-team-key
```

### Resource Limits

Update `docker-compose.yml` for production:
```yaml
services:
  rca-agent:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    restart: unless-stopped
```

## 📊 Monitoring & Maintenance

### Health Checks

The application includes built-in health checks:
- **Endpoint**: `GET /health`
- **Docker**: Automatic health checks configured
- **Response**: JSON with service status

### Logging

```bash
# View application logs
docker-compose logs -f rca-agent

# View Nginx logs (production)
docker-compose logs -f nginx

# Export logs
docker-compose logs --since 24h > rca-agent.log
```

### Backup Strategy

```bash
# Backup artifacts and tickets
tar -czf backup-$(date +%Y%m%d).tar.gz out/ linear_mock/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "$BACKUP_DIR/rca-agent-$DATE.tar.gz" out/ linear_mock/
find "$BACKUP_DIR" -name "rca-agent-*.tar.gz" -mtime +7 -delete
```

### Updates

```bash
# Update deployment
./scripts/deploy.sh update

# Manual update
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   # Fix file permissions
   chmod +x scripts/deploy.sh
   sudo chown -R $USER:$USER out/ linear_mock/
   ```

3. **Out of Memory**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   ```

4. **Git Repository Issues**
   ```bash
   # Reinitialize git in container
   docker-compose exec rca-agent git init
   docker-compose exec rca-agent git add .
   docker-compose exec rca-agent git commit -m "Reset"
   ```

### Debug Mode

Enable debug logging:
```bash
# Set environment variable
export DEBUG=true

# Or in docker-compose.yml
environment:
  - DEBUG=true
  - LOG_LEVEL=debug
```

### Performance Tuning

1. **Increase Worker Processes**
   ```python
   # In serve.py
   uvicorn.run(
       "rca.api:app",
       host="0.0.0.0",
       port=8000,
       workers=4  # Increase workers
   )
   ```

2. **Enable Caching**
   ```nginx
   # In nginx.conf
   location ~* \.(pdf|md|json)$ {
       expires 1h;
       add_header Cache-Control "public";
   }
   ```

## 🌐 Domain & DNS Setup

### Custom Domain Configuration

1. **Point DNS to your server**
   ```
   A record: your-domain.com -> your-server-ip
   CNAME: www.your-domain.com -> your-domain.com
   ```

2. **Update Nginx configuration**
   ```nginx
   server_name your-domain.com www.your-domain.com;
   ```

3. **Get SSL certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  rca-agent:
    deploy:
      replicas: 3
    
  nginx:
    depends_on:
      - rca-agent
    # Nginx will load balance automatically
```

### Load Balancer Configuration

```nginx
upstream rca_backend {
    server rca-agent-1:8000;
    server rca-agent-2:8000;
    server rca-agent-3:8000;
}
```

## 🔐 Security Considerations

1. **Firewall Rules**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw deny 8000  # Block direct API access
   ```

2. **Environment Variables**
   - Never commit `.env` files
   - Use secrets management in production
   - Rotate API keys regularly

3. **Container Security**
   ```dockerfile
   # Run as non-root user
   RUN adduser --disabled-password --gecos '' appuser
   USER appuser
   ```

## 📞 Support

For hosting issues:
1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs
3. Verify health check endpoints
4. Check resource usage and limits

**Ready to host your RCA Agent? Choose your preferred platform and follow the guide above!** 🚀
