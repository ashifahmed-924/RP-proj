# API Setup Documentation

## Overview

This application uses **TWO separate API servers**:

### 1. Flask API (Port 5000)
**Purpose**: Authentication, User Management, PMSAS (Progress Management System)

**Base URL**: `http://localhost:5000/api`

**Routes**:
- `/api/accounts/login` - User login
- `/api/accounts/register` - User registration
- `/api/accounts/me` - Get current user
- `/api/accounts/me` (PUT) - Update profile
- `/api/pmsas/*` - Progress, badges, streaks, leaderboard

**Frontend Config**: `frontend/src/config/api.js`
- Uses `VITE_API_URL` or defaults to `http://localhost:5000/api`

**Start Command**: 
```bash
cd backend
python app.py
```

---

### 2. FastAPI (Port 5001)
**Purpose**: ECESE (Education Content Extraction and Structuring Engine), Student Modules

**Base URL**: `http://localhost:5001`

**Routes**:
- `/ecese/*` - Teacher content upload and processing
- `/modules/*` - Student enrollment and content access

**Frontend Config**: `frontend/src/services/eceseService.js`
- Uses `VITE_ECESE_API_URL` or defaults to `http://localhost:5001/ecese`

**Start Command**:
```bash
cd backend
python -m uvicorn ecese_app:app --port 5001 --reload
```

---

## Running Both Servers

### Option 1: Run in separate terminals
```bash
# Terminal 1 - Flask API
cd backend
python app.py

# Terminal 2 - FastAPI
cd backend
python -m uvicorn ecese_app:app --port 5001 --reload

# Terminal 3 - Frontend
cd frontend
npm run dev
```

### Option 2: Run in background (current setup)
Both servers are configured to run in the background.

---

## API Endpoints Summary

### Authentication (Flask - Port 5000)
- `POST /api/accounts/login` - Login
- `POST /api/accounts/register` - Register
- `GET /api/accounts/me` - Get current user
- `PUT /api/accounts/me` - Update profile

### ECESE (FastAPI - Port 5001)
- `POST /ecese/upload` - Upload textbook and teacher guide
- `GET /ecese/review/{module_name}` - Get unapproved content
- `POST /ecese/approve/{content_id}` - Approve content

### Modules (FastAPI - Port 5001)
- `POST /modules/enroll` - Student enrolls in module
- `GET /modules/{module_name}/content` - Get approved content

---

## Troubleshooting

### Login Not Working
1. **Check Flask server is running**: `curl http://localhost:5000/api/health`
2. **Check CORS**: Flask CORS allows `http://localhost:5173`
3. **Check browser console**: Look for CORS or network errors
4. **Verify database**: MongoDB should be connected

### ECESE Features Not Working
1. **Check FastAPI server**: `curl http://localhost:5001/health`
2. **Check API URL**: Verify `VITE_ECESE_API_URL` in frontend

### Both Servers Must Run
- **Flask (5000)**: Required for login/authentication
- **FastAPI (5001)**: Required for content upload and viewing

---

## Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
VITE_ECESE_API_URL=http://localhost:5001/ecese
```

### Backend
- MongoDB connection configured in `backend/config.py`
- JWT secret key configured in `backend/config.py`


