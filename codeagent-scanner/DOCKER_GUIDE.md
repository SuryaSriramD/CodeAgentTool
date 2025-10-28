# Docker Deployment Guide

## Overview

This guide explains how to build and run the CodeAgent Vulnerability Scanner using Docker. The scanner includes the integrated multi-agent system (CAMEL + CodeAgent) for enhanced security analysis.

## Prerequisites

- Docker Desktop installed and running
- OpenAI API key (for AI-enhanced analysis)
- 4GB+ RAM available for Docker
- Windows PowerShell or Command Prompt

## Quick Start

### 1. Navigate to Project Directory

```powershell
cd d:\MinorProject\codeagent-scanner
```

### 2. Configure Environment Variables

The `.env` file contains all configuration settings. Key settings:

```bash
# AI Configuration
OPENAI_API_KEY=your_actual_api_key_here
ENABLE_AI_ANALYSIS=true
AI_MODEL=GPT_4

# Server Configuration
PORT=8080
MAX_UPLOAD_SIZE=52428800
MAX_CONCURRENT_JOBS=2
```

**Important**: Remove any inline comments from `.env` values (e.g., `# comment`) as they cause parsing errors.

### 3. Build the Docker Image

```powershell
docker build -t codeagent-scanner .
```

This command:
- Reads the `Dockerfile`
- Installs Python 3.11 and all dependencies
- Copies the application code (`api/`, `analyzers/`, `camel/`, `codeagent/`, etc.)
- Creates storage directories
- Tags the image as `codeagent-scanner`

**Build time**: ~2-3 minutes (first build), ~30 seconds (subsequent builds with cache)

### 4. Run the Container

```powershell
docker run -d -p 8000:8080 --env-file .env -v "$(Get-Location)\storage:/app/storage" --name codeagent-scanner-service codeagent-scanner
```

**Command breakdown**:
- `-d` = Run in detached mode (background)
- `-p 8000:8080` = Map host port 8000 to container port 8080
- `--env-file .env` = Load environment variables from `.env` file
- `-v "$(Get-Location)\storage:/app/storage"` = Mount local storage directory
- `--name codeagent-scanner-service` = Name the container for easy reference
- `codeagent-scanner` = The image to run

## Port Mapping Explained

The scanner runs on **port 8080** inside the Docker container, but you access it on **port 8000** on your host machine.

```
Your Browser (localhost:8000) 
    ↓
Docker Port Mapping (-p 8000:8080)
    ↓
Container (0.0.0.0:8080)
```

**Key URLs**:
- API Documentation: http://localhost:8000/docs
- API Endpoints: http://localhost:8000/*
- Health Check: http://localhost:8000/health

## Docker Management Commands

### Check Running Containers

```powershell
docker ps
```

### View All Containers (including stopped)

```powershell
docker ps -a
```

### View Container Logs

```powershell
# View recent logs
docker logs codeagent-scanner-service

# Follow logs in real-time
docker logs -f codeagent-scanner-service

# View last 50 lines
docker logs --tail 50 codeagent-scanner-service
```

### Stop the Container

```powershell
docker stop codeagent-scanner-service
```

### Start a Stopped Container

```powershell
docker start codeagent-scanner-service
```

### Restart the Container

```powershell
docker restart codeagent-scanner-service
```

### Remove the Container

```powershell
# Stop first if running
docker stop codeagent-scanner-service

# Then remove
docker rm codeagent-scanner-service
```

### Execute Commands Inside Container

```powershell
# Open a bash shell
docker exec -it codeagent-scanner-service /bin/bash

# Run a single command
docker exec codeagent-scanner-service ls -la /app
```

### View Container Resource Usage

```powershell
docker stats codeagent-scanner-service
```

## Volume Mounting

The `-v` flag mounts your local `storage/` directory into the container:

```
Local: d:\MinorProject\codeagent-scanner\storage
  ↕
Container: /app/storage
```

This ensures:
- Scan reports persist after container restarts
- Logs are accessible from your host machine
- Workspace files are stored locally

**Storage structure**:
```
storage/
├── workspace/    # Temporary scan workspaces
├── reports/      # JSON scan reports
└── logs/         # Job execution logs
```

## Rebuilding After Code Changes

When you modify the code (e.g., fixing the CamelBridge):

### 1. Stop and Remove Old Container

```powershell
docker stop codeagent-scanner-service
docker rm codeagent-scanner-service
```

### 2. Rebuild the Image

```powershell
docker build -t codeagent-scanner .
```

### 3. Run the New Container

```powershell
docker run -d -p 8000:8080 --env-file .env -v "$(Get-Location)\storage:/app/storage" --name codeagent-scanner-service codeagent-scanner
```

**Tip**: You can combine these commands:

```powershell
docker stop codeagent-scanner-service; docker rm codeagent-scanner-service; docker build -t codeagent-scanner .; docker run -d -p 8000:8080 --env-file .env -v "$(Get-Location)\storage:/app/storage" --name codeagent-scanner-service codeagent-scanner
```

## Troubleshooting

### Container Exits Immediately

Check the logs:
```powershell
docker logs codeagent-scanner-service
```

Common causes:
- **Environment variable parsing errors**: Remove inline comments from `.env` file
- **Port already in use**: Change the host port (e.g., `-p 8001:8080`)
- **Missing dependencies**: Rebuild the image with `docker build --no-cache -t codeagent-scanner .`

### Can't Access the API

1. **Check if container is running**:
   ```powershell
   docker ps
   ```
   
2. **Verify port mapping**: Look for `0.0.0.0:8000->8080/tcp` in the `PORTS` column

3. **Test with curl**:
   ```powershell
   curl http://localhost:8000/health
   ```

4. **Check firewall**: Ensure Windows Firewall allows Docker

### Multi-Agent Bridge Warning

If you see:
```
WARNING:api.app:Failed to initialize Multi-Agent Bridge: 'CamelBridge' object has no attribute 'config_path'
```

This is **non-critical**. The basic scanner works, but AI-enhanced analysis may fail. To fix:

1. Update `integration/camel_bridge.py` (fix already provided)
2. Rebuild the Docker image
3. Restart the container

### "Cannot connect to Docker daemon"

Ensure Docker Desktop is running:
- Open Docker Desktop application
- Wait for "Docker Desktop is running" status
- Try the command again

## Docker Compose (Alternative)

For easier management, create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  codeagent-scanner:
    build: .
    container_name: codeagent-scanner-service
    ports:
      - "8000:8080"
    env_file:
      - .env
    volumes:
      - ./storage:/app/storage
    restart: unless-stopped
```

Then use:

```powershell
# Start
docker-compose up -d

# Stop
docker-compose down

# Rebuild and start
docker-compose up -d --build

# View logs
docker-compose logs -f
```

## Production Deployment

For production environments:

### 1. Use Docker Secrets for API Keys

Don't store API keys in `.env`. Use Docker secrets or environment variables from a secure vault.

### 2. Enable Health Checks

The Dockerfile includes a health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:8080/health || exit 1
```

### 3. Use a Reverse Proxy

Place the container behind Nginx or Traefik:
```nginx
server {
    listen 80;
    server_name scanner.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Resource Limits

Add resource constraints:
```powershell
docker run -d \
  -p 8000:8080 \
  --memory="4g" \
  --cpus="2" \
  --env-file .env \
  -v "$(Get-Location)\storage:/app/storage" \
  --name codeagent-scanner-service \
  codeagent-scanner
```

### 5. Logging

Configure log rotation:
```powershell
docker run -d \
  -p 8000:8080 \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --env-file .env \
  -v "$(Get-Location)\storage:/app/storage" \
  --name codeagent-scanner-service \
  codeagent-scanner
```

## Dockerfile Structure

```dockerfile
FROM python:3.11-slim          # Base image
ENV PYTHONPATH="/app"          # Set module path
WORKDIR /app                   # Working directory

# Install system dependencies
RUN apt-get update && apt-get install -y git curl

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY analyzers/ ./analyzers/
COPY camel/ ./camel/           # Multi-agent framework
COPY codeagent/ ./codeagent/   # CodeAgent system
# ... other directories

# Set environment
ENV STORAGE_BASE=/app/storage

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Summary

✅ **Build once**: `docker build -t codeagent-scanner .`  
✅ **Run easily**: `docker run -d -p 8000:8080 --env-file .env -v "$(Get-Location)\storage:/app/storage" --name codeagent-scanner-service codeagent-scanner`  
✅ **Access at**: http://localhost:8000  
✅ **Manage with**: `docker logs/stop/start/restart codeagent-scanner-service`  
✅ **Update code**: Stop → Rebuild → Run  

The Docker setup provides a consistent, portable, and isolated environment for the CodeAgent Vulnerability Scanner with integrated multi-agent AI analysis. 🐳
