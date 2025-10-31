# Docker Compose Setup Guide

## Overview

This guide covers running the CodeAgent Vulnerability Scanner using Docker Compose for both development and production environments.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                  (codeagent-network)                     │
│                                                          │
│  ┌─────────────────┐         ┌─────────────────┐      │
│  │   Frontend      │         │    Backend      │      │
│  │   (Next.js)     │◄───────►│   (FastAPI)     │      │
│  │   Port 3000     │  CORS   │   Port 8080     │      │
│  │                 │         │                 │      │
│  └─────────────────┘         └─────────────────┘      │
│          │                           │                 │
└──────────┼───────────────────────────┼─────────────────┘
           │                           │
    localhost:3000              localhost:8000
     (Host Port)                 (Host Port)
```

## Prerequisites

1. **Docker Desktop** installed and running

   - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Verify: `docker --version` and `docker-compose --version`

2. **Minimum System Requirements**
   - 4GB RAM
   - 10GB disk space
   - Docker Desktop with WSL2 (Windows)

## Quick Start

### Development Mode (Recommended for Active Development)

**Start services with hot reload:**

```cmd
docker-compose -f docker-compose.dev.yml up
```

**Access:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Features:**

- ✅ Hot reload for both frontend and backend
- ✅ Source code mounted as volumes
- ✅ Debug logging enabled
- ✅ Fast iteration cycle

**Stop services:**

```cmd
docker-compose -f docker-compose.dev.yml down
```

---

### Production Mode

**Build and start services:**

```cmd
docker-compose up -d --build
```

**Access:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

**Features:**

- ✅ Optimized builds
- ✅ Smaller image sizes
- ✅ Production logging
- ✅ Health checks enabled
- ✅ Auto-restart on failure

**Stop services:**

```cmd
docker-compose down
```

---

## Configuration

### Environment Variables

#### Backend Configuration

Create `.env` file in root directory:

```bash
# OpenAI API Key (required for AI analysis)
OPENAI_API_KEY=sk-your-key-here

# Enable AI Analysis (optional)
ENABLE_AI_ANALYSIS=true

# Additional backend settings (optional)
# These have defaults in docker-compose.yml
MAX_CONCURRENT_JOBS=2
DEFAULT_TIMEOUT_SEC=600
LOG_LEVEL=INFO
```

#### Frontend Configuration

Frontend uses `NEXT_PUBLIC_API_URL=http://localhost:8000` by default (configured in docker-compose.yml).

For custom configuration, create `codeagent-scanner-ui/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Common Commands

### View Logs

```cmd
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Check Service Status

```cmd
docker-compose ps
```

### Restart Services

```cmd
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend
```

### Rebuild Images

```cmd
# Rebuild all images
docker-compose build --no-cache

# Rebuild backend only
docker-compose build --no-cache backend
```

### Clean Up

```cmd
# Stop and remove containers
docker-compose down

# Remove containers + volumes (WARNING: deletes data)
docker-compose down -v

# Remove containers + images
docker-compose down --rmi all
```

---

## Troubleshooting

### Issue 1: Port Already in Use

**Error:** `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution:**

```cmd
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
ports:
  - "3001:3000"  # Use 3001 instead
```

### Issue 2: Backend Not Responding

**Error:** Frontend shows "Failed to fetch" errors

**Solution:**

```cmd
# Check backend health
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Issue 3: CORS Errors in Browser Console

**Error:** `Access-Control-Allow-Origin` errors

**Solution:**

1. Verify CORS configuration in `codeagent-scanner/api/app.py`
2. Ensure `CORS_ORIGINS` includes `http://localhost:3000`
3. Restart backend: `docker-compose restart backend`

### Issue 4: Frontend Build Fails

**Error:** `pnpm install` or build errors

**Solution:**

```cmd
# Clear node_modules and rebuild
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

### Issue 5: Storage Permission Errors

**Error:** Permission denied on `/app/storage`

**Solution:**

```cmd
# On Windows, ensure Docker has file sharing enabled
# Docker Desktop → Settings → Resources → File Sharing
# Add your project directory

# Create storage directories
mkdir codeagent-scanner\storage\workspace
mkdir codeagent-scanner\storage\reports
mkdir codeagent-scanner\storage\logs
```

### Issue 6: Docker Desktop Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:**

1. Start Docker Desktop application
2. Wait for "Docker Desktop is running" status
3. Retry docker-compose command

---

## Development Workflow

### Typical Development Session

1. **Start services:**

   ```cmd
   docker-compose -f docker-compose.dev.yml up
   ```

2. **Make code changes:**

   - Frontend: Edit files in `codeagent-scanner-ui/` → Auto-reloads in browser
   - Backend: Edit files in `codeagent-scanner/` → Auto-reloads server

3. **Test changes:**

   - Visit http://localhost:3000
   - Check logs: `docker-compose logs -f`

4. **Stop services:**
   ```cmd
   Ctrl+C  # or
   docker-compose -f docker-compose.dev.yml down
   ```

### Hot Reload Behavior

**Frontend (Next.js):**

- ✅ Component changes → Instant hot reload
- ✅ CSS/Tailwind changes → Instant reload
- ⚠️ Config changes (next.config.mjs) → Requires restart
- ⚠️ New dependencies → Run `pnpm install` in container

**Backend (FastAPI):**

- ✅ Python file changes → Auto-reloads server (2-3 seconds)
- ⚠️ New dependencies → Rebuild image
- ⚠️ Environment variable changes → Restart container

---

## Production Deployment

### Build Optimized Images

```cmd
docker-compose build --no-cache
```

### Start in Production Mode

```cmd
docker-compose up -d
```

### Monitor Health

```cmd
# Check health status
docker-compose ps

# View health check logs
docker inspect codeagent-scanner-backend | grep -A 10 "Health"
docker inspect codeagent-scanner-frontend | grep -A 10 "Health"
```

### Update Production Environment

```cmd
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## Performance Optimization

### Development Mode

- **Pros:** Fast iteration, hot reload
- **Cons:** Larger memory usage, slower startup
- **Use when:** Active coding

### Production Mode

- **Pros:** Optimized builds, smaller images, faster runtime
- **Cons:** No hot reload, requires rebuild for changes
- **Use when:** Testing, staging, production

### Resource Limits (Optional)

Add to services in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 2G
        reservations:
          cpus: "1"
          memory: 512M
```

---

## Network Architecture

### Internal Communication

- Frontend container can reach backend via:
  - `http://backend:8080` (internal Docker network)
  - `http://localhost:8000` (from host via port mapping)

### External Access

- **Host Machine:**

  - Frontend: `http://localhost:3000`
  - Backend: `http://localhost:8000`
  - API Docs: `http://localhost:8000/docs`

- **Other Devices on Network:**
  - Frontend: `http://<YOUR_IP>:3000`
  - Backend: `http://<YOUR_IP>:8000`

---

## Security Considerations

### Development

- ✅ CORS allows localhost
- ✅ Debug logging enabled
- ⚠️ Source code mounted as volumes

### Production

- ✅ Set strong `OPENAI_API_KEY`
- ✅ Configure `CORS_ORIGINS` to specific domains
- ✅ Use HTTPS with reverse proxy (Nginx)
- ✅ Enable rate limiting
- ✅ Set `LOG_LEVEL=WARNING` or `ERROR`

### Recommended Production Setup

1. Use Nginx as reverse proxy
2. Enable SSL/TLS certificates
3. Set up authentication layer
4. Implement API rate limiting
5. Use secrets management (Docker secrets, Vault)

---

## Next Steps

✅ **Step 6 Complete** - Docker Compose setup ready

**Continue to:**

- Step 7-11: Update frontend pages with real API integration
- Step 12: Test the full stack together
- Step 13: Add error handling and loading states

**Test the setup:**

```cmd
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Open browser
http://localhost:3000

# Check backend health
curl http://localhost:8000/health
```

---

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
- Backend API Docs: `docs/BACKEND_API_ANALYSIS.md`
- CORS Setup: `docs/CORS_CONFIGURATION.md`
