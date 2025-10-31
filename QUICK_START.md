# CodeAgent Vulnerability Scanner - Quick Start

## 🚀 Fastest Way to Run

### Option 1: Docker Compose (Development Mode) ⭐ **RECOMMENDED**

```cmd
# Start both frontend and backend with hot reload
docker-compose -f docker-compose.dev.yml up
```

**Access:**

- 🌐 Frontend UI: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

**Stop:**

```cmd
Ctrl+C
# or
docker-compose -f docker-compose.dev.yml down
```

---

### Option 2: Docker Compose (Production Mode)

```cmd
# Build and start optimized containers
docker-compose up -d --build
```

**View logs:**

```cmd
docker-compose logs -f
```

**Stop:**

```cmd
docker-compose down
```

---

### Option 3: Run Services Separately (Native)

**Terminal 1 - Backend:**

```cmd
cd codeagent-scanner
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8080
```

**Terminal 2 - Frontend:**

```cmd
cd codeagent-scanner-ui
npm install --legacy-peer-deps
npm run dev
```

**Access:**

- Frontend: http://localhost:3000
- Backend: http://localhost:8080

---

## 🔧 Configuration

### Required (Optional for AI features)

Create `.env` file in root:

```bash
OPENAI_API_KEY=sk-your-key-here
ENABLE_AI_ANALYSIS=true
```

### Already Configured ✅

- ✅ Frontend API URL: `http://localhost:8000`
- ✅ CORS: Allows `http://localhost:3000`
- ✅ Port mapping: 8000→8080 (backend), 3000→3000 (frontend)

---

## 📋 Quick Health Check

```cmd
# Backend
curl http://localhost:8000/health

# Expected: {"status":"ok","version":"0.1.0",...}
```

```cmd
# Frontend (in browser console at localhost:3000)
fetch('http://localhost:8000/health').then(r=>r.json()).then(console.log)
```

---

## 🎯 What's Next?

Current status: **Frontend-Backend Integration 60% Complete**

✅ **Completed:**

- Backend API with 20+ endpoints
- Frontend UI with mock data
- API client with TypeScript types
- CORS configuration
- Docker Compose setup

⏳ **Next Steps:**

- Update frontend pages to use real API calls (Steps 7-11)
- Add error handling and loading states
- Test full integration

See: `docs/DOCKER_COMPOSE_GUIDE.md` for detailed setup

---

## 📚 Documentation

- **Setup Guide:** `docs/DOCKER_COMPOSE_GUIDE.md`
- **API Reference:** `docs/BACKEND_API_ANALYSIS.md`
- **CORS Config:** `docs/CORS_CONFIGURATION.md`
- **API Client:** `codeagent-scanner-ui/lib/api-client.ts`

---

## 🐛 Common Issues

**Port already in use:**

```cmd
# Windows - Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**CORS errors:**

```cmd
# Restart backend to reload CORS config
docker-compose restart backend
```

**Build errors:**

```cmd
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 💡 Tips

- Use **Docker Dev mode** for active development (hot reload)
- Use **Docker Prod mode** for testing/deployment
- Use **Native mode** if you prefer traditional setup
- Check logs: `docker-compose logs -f backend`
- Frontend errors: Check browser console (F12)

---

**Need help?** See `docs/DOCKER_COMPOSE_GUIDE.md` for troubleshooting.
