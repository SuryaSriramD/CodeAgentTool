# Environment Setup Quick Reference

## � Docker Setup (Recommended)

```bash
# 1. Start Backend in Docker
cd codeagent-scanner
docker build -t codeagent-scanner .
docker run -d -p 8000:8080 --env-file .env \
  -v "$(Get-Location)\storage:/app/storage" \
  --name codeagent-scanner-service codeagent-scanner

# 2. Setup Frontend
cd ../codeagent-scanner-ui
cp .env.example .env.local  # Uses port 8000 by default
pnpm install
pnpm dev  # → http://localhost:3000
```

## 🔧 Native Setup (Alternative)

```bash
# 1. Setup Frontend
cd codeagent-scanner-ui
cp .env.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8080
pnpm install
pnpm dev  # → http://localhost:3000

# 2. Setup Backend
cd ../codeagent-scanner
cp .env.example .env
# Add your OPENAI_API_KEY to .env
pip install -r requirements.txt
python api/app.py  # → http://localhost:8080
```

## 🔑 Essential Variables

### Frontend (.env.local)

```bash
# For Docker Backend (Recommended)
NEXT_PUBLIC_API_URL=http://localhost:8000  # ← Docker host port

# For Native Backend (Alternative)
# NEXT_PUBLIC_API_URL=http://localhost:8080
```

### Backend (.env)

```bash
OPENAI_API_KEY=sk-your-key-here  # Required for AI features
PORT=8080                        # Port inside container
```

## 🐳 Docker Port Mapping

```
Frontend (localhost:3000)
    ↓
Calls: http://localhost:8000  ← Host port (what you access)
    ↓
Docker Mapping: -p 8000:8080
    ↓
Container: 0.0.0.0:8080  ← Backend listens here
```

**Key Point:** Backend runs on port **8080 inside** Docker, exposed as **8000 on host**

## 🌐 URLs

| Service     | Docker Setup               | Native Setup               | Docker Compose             |
| ----------- | -------------------------- | -------------------------- | -------------------------- |
| Frontend    | http://localhost:3000      | http://localhost:3000      | http://localhost:3000      |
| Backend API | http://localhost:8000      | http://localhost:8080      | http://localhost:8000      |
| API Docs    | http://localhost:8000/docs | http://localhost:8080/docs | http://localhost:8000/docs |

**Note:** Docker uses port mapping `8000:8080` (host→container)

## 📂 File Locations

```
MinorProject/
├── .env.example                      # Root template (reference)
├── codeagent-scanner/
│   └── .env.example                  # Backend template
└── codeagent-scanner-ui/
    ├── .env.local                    # Active config (gitignored)
    └── .env.example                  # Frontend template
```

## ⚠️ Common Issues

**Frontend can't connect to backend (Docker):**

```bash
# Check API URL in frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000  # Must be 8000 for Docker!

# Verify Docker container is running
docker ps | findstr codeagent-scanner

# Test backend directly
curl http://localhost:8000/health
```

**Frontend can't connect to backend (Native):**

```bash
# Check API URL in frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8080  # Must be 8080 for native!

# Verify backend is running
netstat -ano | findstr :8080
```

**Wrong port configured:**

| Backend Type | Correct Port | Fix                                         |
| ------------ | ------------ | ------------------------------------------- |
| Docker       | 8000         | `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| Native       | 8080         | `NEXT_PUBLIC_API_URL=http://localhost:8080` |

**AI features not working:**

```bash
# Add OpenAI key to backend .env
OPENAI_API_KEY=sk-...
ENABLE_AI_ANALYSIS=true
```

## 🔒 Security Notes

- ✅ `.env.local` and `.env` are gitignored
- ✅ `.env.example` files are committed (templates only)
- ❌ Never put secrets in `NEXT_PUBLIC_*` variables
- ❌ Never commit actual `.env` files

## 📚 Full Documentation

See: `docs/STEP_3_ENVIRONMENT_CONFIG.md`
