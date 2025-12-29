# Troubleshooting Guide

## Login/Register Not Working

### Issue 1: Database Connection Failed

**Error**: `Database connection failed. Please try again later.`

**Solution**:
1. **Check MongoDB is running**:
   - If using local MongoDB: `mongod` should be running
   - If using MongoDB Atlas: Check your connection string in `backend/config.py`

2. **Verify MongoDB URI**:
   - Check `backend/config.py` for `MONGODB_URI`
   - Default uses MongoDB Atlas: `mongodb+srv://cursorrp_db_user:...`
   - Make sure the connection string is correct

3. **Test MongoDB Connection**:
   ```python
   from pymongo import MongoClient
   client = MongoClient("your_mongodb_uri")
   client.admin.command('ping')
   ```

4. **If MongoDB is not available**:
   - Install MongoDB locally, OR
   - Use MongoDB Atlas (free tier available), OR
   - Update the connection string in `backend/config.py`

### Issue 2: Email Validation Too Strict

**Error**: `Invalid email address: The domain name ... does not accept email.`

**Solution**: 
- The email validator has been updated to allow test domains in development
- Use a valid email format (e.g., `user@example.com`)
- For testing, you can use: `test@test.local` or `user@gmail.com`

### Issue 3: CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
- CORS is configured for `http://localhost:5173` (Vite default)
- If using a different port, update `backend/app.py` line 34
- Make sure Flask server is restarted after CORS changes

### Issue 4: Server Not Running

**Check if servers are running**:
```bash
# Check Flask (port 5000)
curl http://localhost:5000/api/health

# Check FastAPI (port 5001)
curl http://localhost:5001/health
```

**Start servers**:
```bash
# Terminal 1 - Flask
cd backend
python app.py

# Terminal 2 - FastAPI  
cd backend
python -m uvicorn ecese_app:app --port 5001 --reload

# Terminal 3 - Frontend
cd frontend
npm run dev
```

## Quick Fixes

### 1. Restart All Servers
```bash
# Stop all Python processes
# Then restart Flask and FastAPI

# Start Flask
cd backend && python app.py

# Start FastAPI (in another terminal)
cd backend && python -m uvicorn ecese_app:app --port 5001 --reload
```

### 2. Clear Browser Cache
- Open DevTools (F12)
- Application → Local Storage → Clear all
- Hard refresh (Ctrl+Shift+R)

### 3. Check Browser Console
- Open DevTools (F12) → Console tab
- Look for errors when clicking Login/Register
- Check Network tab for failed requests

### 4. Test API Directly
```bash
# Test registration
curl -X POST http://localhost:5000/api/accounts/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"Test1234","first_name":"Test","last_name":"User"}'

# Test login
curl -X POST http://localhost:5000/api/accounts/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"Test1234"}'
```

## Common Issues

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one digit

Example valid password: `Test1234`

### Email Format
- Must be valid email format
- Use real domains for testing (gmail.com, yahoo.com, etc.)
- Test domains like `test.com` may be rejected by strict validation

### Database Issues
- MongoDB must be accessible
- Check network/firewall if using MongoDB Atlas
- Verify credentials in connection string


