# Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring & Observability](#monitoring--observability)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying the **Robot Flower Princess API** in various environments:
- Local development (Poetry)
- Docker containerization
- Production deployment (cloud platforms)
- Environment configuration
- Security best practices

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.13+ | Runtime environment |
| **Poetry** | 1.7+ | Dependency management |
| **Docker** | 20.10+ | Containerization (optional) |
| **Docker Compose** | 2.0+ | Multi-container orchestration (optional) |
| **Make** | Any | Build automation (optional) |

### System Requirements

**Minimum**:
- CPU: 1 core
- RAM: 512 MB
- Disk: 1 GB

**Recommended**:
- CPU: 2 cores
- RAM: 2 GB
- Disk: 5 GB

---

## Local Development

### 1. Install Dependencies

#### Install pyenv (Python Version Manager)

**macOS**:
```bash
brew install pyenv
```

**Linux**:
```bash
curl https://pyenv.run | bash
```

**Add to shell** (`~/.zshrc` or `~/.bashrc`):
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

#### Install Python 3.13

```bash
pyenv install 3.13.0
pyenv global 3.13.0
```

#### Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Add Poetry to PATH** (`~/.zshrc` or `~/.bashrc`):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/robot-flower-princess-api.git
cd robot-flower-princess-api
```

### 3. Install Project Dependencies

```bash
# Set Python version for this project
pyenv local 3.13.0

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 4. Run Development Server

**Using Poetry**:
```bash
poetry run uvicorn robot_flower_princess.main:app --reload --host 0.0.0.0 --port 8000
```

**Using Makefile**:
```bash
make run
```

**Access API**:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Development Workflow

```bash
# Format code
make format

# Lint code
make lint

# Run tests
make test-all

# Run tests with coverage
make coverage
make coverage-combine

# View coverage report
open .coverage/coverage_html/index.html
```

---

## Docker Deployment

### 1. Build Docker Image

**Using Docker**:
```bash
docker build -t robot-flower-princess:latest .
```

**Using Makefile**:
```bash
make docker-build
```

### 2. Run Container

**Basic Run**:
```bash
docker run -d \
  --name robot-flower-princess-api \
  -p 8000:8000 \
  robot-flower-princess:latest
```

**With Environment Variables**:
```bash
docker run -d \
  --name robot-flower-princess-api \
  -p 8000:8000 \
  -e LOG_LEVEL=info \
  -e CORS_ORIGINS="https://your-frontend.com" \
  robot-flower-princess:latest
```

**Check Health**:
```bash
curl http://localhost:8000/health
```

### 3. Docker Compose (Recommended)

**Create `docker-compose.yml`**:
```yaml
version: '3.9'

services:
  api:
    build: .
    container_name: robot-flower-princess-api
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - CORS_ORIGINS=*
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

**Run with Docker Compose**:
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Multi-Stage Docker Build (Production)

The `Dockerfile` uses multi-stage builds for optimized images:

```dockerfile
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy dependency files
COPY README.md ./
COPY pyproject.toml ./

# Install dependencies (no dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Copy source code
COPY src/ ./src/

# Install the package
RUN poetry install --no-interaction --no-ansi --only main

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "robot_flower_princess.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Benefits**:
- ✅ Smaller image size (~150MB)
- ✅ Only production dependencies
- ✅ No dev tools in production
- ✅ Faster deployment

---

## Production Deployment

### 1. Cloud Platform Options

#### AWS (Amazon Web Services)

**Option A: ECS (Elastic Container Service)**

1. **Build and push Docker image**:
```bash
# Tag image for ECR
docker tag robot-flower-princess:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/robot-flower-princess:latest

# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/robot-flower-princess:latest
```

2. **Create ECS Task Definition** (`task-definition.json`):
```json
{
  "family": "robot-flower-princess",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/robot-flower-princess:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "LOG_LEVEL", "value": "info" }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

3. **Create ECS Service**:
```bash
aws ecs create-service \
  --cluster robot-flower-princess-cluster \
  --service-name robot-flower-princess-service \
  --task-definition robot-flower-princess \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**Option B: Lambda + API Gateway**

1. Package application for Lambda
2. Deploy with AWS SAM or Serverless Framework
3. Configure API Gateway

**Cost**: ~$10-50/month depending on traffic

---

#### Google Cloud Platform (GCP)

**Cloud Run (Recommended)**

1. **Build and push to Container Registry**:
```bash
# Tag image
docker tag robot-flower-princess:latest \
  gcr.io/<project-id>/robot-flower-princess:latest

# Authenticate
gcloud auth configure-docker

# Push image
docker push gcr.io/<project-id>/robot-flower-princess:latest
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy robot-flower-princess-api \
  --image gcr.io/<project-id>/robot-flower-princess:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars LOG_LEVEL=info
```

3. **Access URL**:
```
https://robot-flower-princess-api-xxxxx-uc.a.run.app
```

**Cost**: Pay-per-use, ~$5-20/month for moderate traffic

---

#### Azure

**Azure Container Instances**

```bash
az container create \
  --resource-group robot-flower-princess-rg \
  --name robot-flower-princess-api \
  --image <registry>.azurecr.io/robot-flower-princess:latest \
  --cpu 1 \
  --memory 1 \
  --registry-login-server <registry>.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label robot-flower-princess \
  --ports 8000
```

**Cost**: ~$15-30/month

---

#### Heroku

**Deploy with Heroku CLI**:

1. **Create `Procfile`**:
```
web: uvicorn robot_flower_princess.main:app --host 0.0.0.0 --port $PORT
```

2. **Deploy**:
```bash
heroku login
heroku create robot-flower-princess-api
git push heroku main
heroku ps:scale web=1
heroku open
```

**Cost**: Free tier available, $7/month for hobby dynos

---

#### DigitalOcean

**App Platform**:

1. Connect GitHub repository
2. Select Python 3.13
3. Add build command: `poetry install --only main`
4. Add run command: `uvicorn robot_flower_princess.main:app --host 0.0.0.0 --port 8080`
5. Deploy

**Cost**: $5/month for basic droplet

---

### 2. Reverse Proxy (Nginx)

**Why Use Nginx**:
- SSL/TLS termination
- Load balancing
- Static file serving
- Rate limiting
- Caching

**Nginx Configuration** (`/etc/nginx/sites-available/robot-flower-princess`):
```nginx
upstream robot_flower_princess {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://robot_flower_princess;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint (no rate limit)
    location /health {
        proxy_pass http://robot_flower_princess;
        access_log off;
    }
}
```

**Enable Site**:
```bash
sudo ln -s /etc/nginx/sites-available/robot-flower-princess /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 3. SSL/TLS Certificates (Let's Encrypt)

**Install Certbot**:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

**Obtain Certificate**:
```bash
sudo certbot --nginx -d api.yourdomain.com
```

**Auto-Renewal**:
```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal is automatically configured via cron
```

---

### 4. Process Manager (systemd)

**Create systemd service** (`/etc/systemd/system/robot-flower-princess.service`):

```ini
[Unit]
Description=Robot Flower Princess API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/robot-flower-princess
Environment="PATH=/opt/robot-flower-princess/.venv/bin"
ExecStart=/opt/robot-flower-princess/.venv/bin/uvicorn robot_flower_princess.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Manage Service**:
```bash
# Enable service
sudo systemctl enable robot-flower-princess

# Start service
sudo systemctl start robot-flower-princess

# Check status
sudo systemctl status robot-flower-princess

# View logs
sudo journalctl -u robot-flower-princess -f
```

---

## Environment Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Server port |
| `HOST` | 0.0.0.0 | Server host |
| `LOG_LEVEL` | info | Logging level (debug, info, warning, error) |
| `CORS_ORIGINS` | * | Allowed CORS origins (comma-separated) |
| `WORKERS` | 1 | Number of Uvicorn workers |

### Configuration Files

**Development** (`.env.development`):
```bash
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=debug
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
WORKERS=1
```

**Production** (`.env.production`):
```bash
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info
CORS_ORIGINS=https://yourdomain.com
WORKERS=4
```

**Load Environment Variables**:
```python
# src/robot_flower_princess/configurator/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "info"
    cors_origins: str = "*"
    workers: int = 1

    class Config:
        env_file = ".env"
```

---

## Monitoring & Observability

### 1. Logging

**Structured Logging** (JSON format):

```python
# src/robot_flower_princess/logging.py
import logging
import sys

def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
```

**Log Aggregation**:
- **Datadog**: Collect and analyze logs
- **Papertrail**: Simple log aggregation
- **CloudWatch Logs**: AWS logging service
- **Stackdriver**: GCP logging service

### 2. Metrics

**Prometheus Metrics**:

```python
# Add prometheus-fastapi-instrumentator
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

**Metrics to Track**:
- Request count
- Request duration
- Error rate
- Active games
- AI solver success rate

### 3. Health Checks

**Liveness Probe**: Is the app running?
```bash
GET /health
```

**Readiness Probe**: Is the app ready to serve traffic?
```python
@app.get("/ready")
def readiness():
    # Check dependencies (database, external services)
    return {"status": "ready"}
```

### 4. Distributed Tracing

**OpenTelemetry**:

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
```

---

## Security

### 1. API Security Best Practices

**Authentication**:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "your-secret-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
```

**Rate Limiting**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/games")
@limiter.limit("10/minute")
async def create_game(request: Request):
    pass
```

### 2. CORS Configuration

**Restrict Origins** (production):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Security Headers

Add security headers with middleware:
```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### 4. Input Validation

Pydantic automatically validates inputs, but add custom validators for complex rules:
```python
class CreateGameRequest(BaseModel):
    rows: int = Field(ge=3, le=50)
    cols: int = Field(ge=3, le=50)

    @validator('rows', 'cols')
    def validate_board_size(cls, v):
        if v % 2 == 0:
            raise ValueError("Board size must be odd")
        return v
```

### 5. Secrets Management

**AWS Secrets Manager**:
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

**Environment Variables** (for simple deployments):
```bash
export API_KEY=$(openssl rand -hex 32)
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use a different port
uvicorn robot_flower_princess.main:app --port 8001
```

#### 2. Poetry Installation Fails

**Error**: `ModuleNotFoundError: No module named 'poetry'`

**Solution**:
```bash
# Reinstall Poetry
curl -sSL https://install.python-poetry.org | python3 - --uninstall
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

#### 3. Docker Build Fails

**Error**: `ERROR [stage-0 4/7] RUN poetry install`

**Solution**:
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t robot-flower-princess:latest .
```

#### 4. Uvicorn Workers Not Starting

**Error**: `Worker process died unexpectedly`

**Solution**:
```bash
# Check logs
journalctl -u robot-flower-princess -n 50

# Reduce workers
uvicorn robot_flower_princess.main:app --workers 1

# Check memory
free -h
```

#### 5. CORS Errors in Browser

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
```python
# Update CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Optimization

### 1. Uvicorn Workers

Run multiple workers for production:
```bash
uvicorn robot_flower_princess.main:app --workers 4
```

**Rule of thumb**: `workers = (2 x CPU cores) + 1`

### 2. Connection Pooling

For database connections (future):
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@host/db",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 3. Caching

Add Redis for caching game states:
```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379)

@lru_cache(maxsize=128)
def get_game_state(game_id: str):
    # Cache game states
    pass
```

### 4. Asynchronous Operations

Use async/await for I/O operations:
```python
@app.post("/api/games")
async def create_game(request: CreateGameRequest):
    # Use async operations
    pass
```

---

## Backup & Recovery

### In-Memory Data Persistence

Since the app uses in-memory storage, consider:

1. **Regular Snapshots**:
```python
import pickle

def save_snapshot():
    with open('games_snapshot.pkl', 'wb') as f:
        pickle.dump(repository._games, f)

def load_snapshot():
    with open('games_snapshot.pkl', 'rb') as f:
        return pickle.load(f)
```

2. **Database Migration** (recommended for production):
   - Migrate to PostgreSQL or Redis
   - Add persistence layer
   - Enable regular backups

---

## Summary

### Deployment Checklist

- [ ] Install Python 3.13+ and Poetry
- [ ] Clone repository and install dependencies
- [ ] Configure environment variables
- [ ] Run tests to ensure everything works
- [ ] Build Docker image (optional)
- [ ] Choose cloud platform and deploy
- [ ] Configure Nginx reverse proxy (if applicable)
- [ ] Obtain SSL/TLS certificates
- [ ] Set up monitoring and logging
- [ ] Configure health checks
- [ ] Implement rate limiting and security
- [ ] Test API endpoints
- [ ] Set up CI/CD pipeline (see [CI/CD Guide](CI_CD.md))

### Recommended Production Stack

- **Hosting**: Google Cloud Run or AWS ECS
- **Reverse Proxy**: Nginx with Let's Encrypt SSL
- **Monitoring**: Datadog or Prometheus + Grafana
- **Logging**: CloudWatch or Stackdriver
- **Security**: API Gateway with rate limiting
- **CI/CD**: GitHub Actions (see [CI/CD Guide](CI_CD.md))

---

## Next Steps

- [CI/CD Workflow](CI_CD.md) - Automate deployments
- [Monitoring Guide](#monitoring--observability) - Set up observability
- [API Documentation](API.md) - API reference
- [Architecture](ARCHITECTURE.md) - System design
