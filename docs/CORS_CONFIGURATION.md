# CORS Configuration Guide

## Overview

Cross-Origin Resource Sharing (CORS) is configured to allow the Next.js frontend (port 3000) to communicate with the FastAPI backend (port 8000/8080).

## Development Setup

### Backend Configuration

The backend now accepts requests from localhost frontend origins by default:

**File:** `codeagent-scanner/api/app.py`

```python
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000").split(",")
```

### Environment Variables

**Backend (.env or Docker environment):**

```bash
# Default development origins (already configured)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

**Frontend (.env.local):**

```bash
# Points to backend (already configured)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production Setup

### Step 1: Update Backend CORS Origins

Set the `CORS_ORIGINS` environment variable to your production domain(s):

```bash
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com,https://www.yourdomain.com
```

### Step 2: Update Frontend API URL

Update the frontend environment variable:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Step 3: Restart Services

```bash
# Backend (Docker)
docker restart codeagent-scanner-service

# Frontend
npm run build
npm start
```

## Testing CORS Configuration

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "analyzers": ["bandit", "semgrep", "depcheck"]
}
```

### 2. Test CORS from Browser Console

Open frontend at `http://localhost:3000` and run in browser console:

```javascript
fetch("http://localhost:8000/health")
  .then((r) => r.json())
  .then((data) => console.log("✅ CORS working:", data))
  .catch((err) => console.error("❌ CORS error:", err));
```

### 3. Check Network Tab

- Open browser DevTools → Network tab
- Look for requests to `http://localhost:8000`
- Should see:
  - ✅ Status: 200 OK
  - ✅ Response headers include `Access-Control-Allow-Origin: http://localhost:3000`
  - ❌ NO CORS errors in console

## Common Issues

### Issue 1: CORS Error "No 'Access-Control-Allow-Origin' header"

**Solution:**

- Ensure backend is running: `docker ps` should show `codeagent-scanner-service`
- Check `CORS_ORIGINS` includes your frontend URL (including protocol and port)
- Restart backend after changing environment variables

### Issue 2: Backend Returns 404

**Solution:**

- Verify API endpoint exists: Check `docs/BACKEND_API_ANALYSIS.md`
- Verify API base URL is correct: `http://localhost:8000` (not 8080)

### Issue 3: Credentials/Cookies Not Working

**Solution:**

- Ensure `allow_credentials=True` is set in backend CORS config (already configured)
- Frontend requests must include `credentials: 'include'` if using cookies

## Security Best Practices

### Development

✅ Allow localhost origins (already configured)
✅ Keep `allow_credentials=True` for session support
✅ Log CORS rejections for debugging

### Production

✅ **NEVER** use `allow_origins=["*"]` with `allow_credentials=True`
✅ Explicitly list all valid domains (no wildcards)
✅ Use HTTPS for all origins
✅ Consider rate limiting and API keys
✅ Monitor CORS rejection logs

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│   Next.js Frontend  │         │   FastAPI Backend   │
│   localhost:3000    │◄───────►│   localhost:8000    │
│                     │  CORS   │   (container:8080)  │
│  - API Client       │ Allowed │                     │
│  - TanStack Query   │         │  - CORS Middleware  │
│  - React Components │         │  - API Endpoints    │
└─────────────────────┘         └─────────────────────┘
```

## Next Steps

After configuring CORS:

1. ✅ Backend accepts requests from `http://localhost:3000`
2. ⏳ Start frontend: `npm run dev` (if not already running)
3. ⏳ Test API connection from browser console
4. ⏳ Proceed to Step 6: Create docker-compose.yml for orchestration
5. ⏳ Update frontend pages to use real API calls (Steps 7-11)

## References

- [FastAPI CORS Docs](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- Backend API: `docs/BACKEND_API_ANALYSIS.md`
- Frontend API Client: `codeagent-scanner-ui/lib/api-client.ts`
