# 🔧 Troubleshooting Guide

## Common Errors and Solutions

### Backend Error: 500 Internal Server Error

This is the most common error when testing locally. Here are the possible causes:

---

### 1. FFmpeg Not Installed ⚠️ MOST COMMON

**Error Message:** `FFmpeg is not installed on the server`

**Solution:**

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract the ZIP file
3. Add FFmpeg to your PATH:
   - Right-click "This PC" → Properties
   - Advanced System Settings → Environment Variables
   - Under "System Variables", find "Path" → Edit
   - Click "New" and add the path to FFmpeg's `bin` folder (e.g., `C:\ffmpeg\bin`)
   - Click OK on all windows
   - **Restart your terminal**
4. Verify installation:
   ```bash
   ffmpeg -version
   ```

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**After installing FFmpeg, restart your backend server!**

---

### 2. Python Dependencies Not Installed

**Error Message:** `ModuleNotFoundError: No module named 'flask'` (or yt_dlp, flask_cors)

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

If you get permission errors, try:
```bash
pip install --user -r requirements.txt
```

Or create a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

### 3. Port 5000 Already in Use

**Error Message:** `Address already in use` or `OSError: [Errno 48]`

**Solution:**

Find what's using port 5000:

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**macOS/Linux:**
```bash
lsof -ti:5000 | xargs kill -9
```

Or change the port in [backend/app.py](backend/app.py:160):
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

And update frontend `.env`:
```
VITE_API_URL=http://localhost:5001
```

---

### 4. YouTube Download Fails

**Error Message:** `Failed to download video` or yt-dlp error

**Possible Causes:**
- Invalid YouTube URL
- Video is age-restricted or private
- YouTube blocking requests
- Network issues

**Solutions:**

1. **Try a different video** - Use a public, non-restricted video first
2. **Update yt-dlp:**
   ```bash
   pip install --upgrade yt-dlp
   ```
3. **Check your internet connection**
4. **Try with cookies** (if video requires sign-in):
   - Export your YouTube cookies using a browser extension
   - Update [backend/app.py](backend/app.py) to include cookies

---

### 5. CORS Error in Browser

**Error Message:** `Access to fetch at 'http://localhost:5000/api/clip' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution:**

This should already be fixed in the code, but if you see this error:

1. Make sure `flask-cors` is installed:
   ```bash
   pip install flask-cors
   ```

2. Check [backend/app.py](backend/app.py) has:
   ```python
   from flask_cors import CORS
   CORS(app)
   ```

3. Restart the backend server

---

### 6. Frontend Build Errors

**Error Message:** `npm ERR!` or module not found

**Solution:**
```bash
cd frontend

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try running again
npm run dev
```

If you still have issues:
```bash
# Clear npm cache
npm cache clean --force

# Try again
npm install
npm run dev
```

---

### 7. Video Processing Takes Too Long / Times Out

**Possible Causes:**
- Large video file
- Slow internet connection
- Computer is under heavy load

**Solutions:**

1. **Try a shorter time range** - Extract 10-30 seconds instead of minutes
2. **Use a smaller video** - Try with a short YouTube video first
3. **Increase timeout** in [backend/app.py](backend/app.py):
   ```python
   # In FFmpeg command, add timeout parameter
   result = subprocess.run(ffmpeg_command, capture_output=True, text=True, timeout=600)
   ```

---

### 8. "Cannot GET /api/download/..." Error

**Error Message:** 404 or video not found

**Possible Causes:**
- Video was already deleted (auto-cleanup after 1 hour)
- Video processing failed but frontend shows success
- File permissions issue

**Solutions:**

1. **Check backend logs** for the actual error
2. **Verify temp_videos folder exists:**
   ```bash
   cd backend
   ls temp_videos/
   ```
3. **Check file permissions** on the temp_videos folder

---

## Debugging Steps

### 1. Check Backend Health

Visit: http://localhost:5000/api/health

You should see:
```json
{
  "status": "healthy",
  "message": "YouTube Clipper API is running",
  "ffmpeg_available": true
}
```

If `ffmpeg_available` is `false`, install FFmpeg!

---

### 2. Check Backend Logs

Look at your backend terminal for detailed error messages. The updated [backend/app.py](backend/app.py) now shows:
- Received request details
- Download progress
- FFmpeg processing status
- Specific error messages

---

### 3. Test with a Simple Video

Try this known working video:
- URL: `https://www.youtube.com/watch?v=aqz-KE-bpKQ` (Big Buck Bunny)
- Start: `0:05`
- End: `0:15`

This is a short, public domain video that should always work.

---

### 4. Test Backend Directly

You can test the backend API directly using curl or Postman:

```bash
curl -X POST http://localhost:5000/api/clip \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
    "startTime": 5,
    "endTime": 15
  }'
```

This helps determine if the issue is with backend or frontend.

---

## Platform-Specific Issues

### Windows

**Issue:** `python` command not found
**Solution:** Use `py` instead:
```bash
py app.py
```

**Issue:** Permission denied when creating temp_videos folder
**Solution:** Run terminal as Administrator

---

### macOS

**Issue:** SSL certificate verification errors
**Solution:**
```bash
pip install --upgrade certifi
/Applications/Python\ 3.x/Install\ Certificates.command
```

---

### Linux

**Issue:** `libav` errors with FFmpeg
**Solution:** Ensure you have the full FFmpeg package:
```bash
sudo apt-get install ffmpeg libavcodec-extra
```

---

## Still Having Issues?

### Collect This Information:

1. **Operating System:**
2. **Python Version:** `python --version`
3. **Node Version:** `node --version`
4. **FFmpeg Version:** `ffmpeg -version`
5. **Error Message:** (copy the full error from terminal)
6. **Backend Logs:** (copy relevant lines from backend terminal)
7. **Browser Console:** (press F12, check Console tab for errors)

### Quick Sanity Check:

```bash
# Check Python
python --version  # Should be 3.8+

# Check Node
node --version    # Should be 16+

# Check FFmpeg (MOST IMPORTANT!)
ffmpeg -version   # Should show FFmpeg version

# Check pip packages
pip list | grep flask
pip list | grep yt-dlp

# Check if backend starts
cd backend
python app.py     # Should start without errors

# Check if frontend starts
cd frontend
npm run dev       # Should start without errors
```

---

## Getting More Help

If you've tried all of the above:

1. Check [QUICKSTART.md](QUICKSTART.md) for setup instructions
2. Review [README.md](README.md) for detailed documentation
3. Make sure all prerequisites are installed correctly
4. Try creating a fresh virtual environment for Python

---

## Success Checklist

Before you open an issue, verify:

- [ ] FFmpeg is installed and `ffmpeg -version` works
- [ ] Python 3.8+ is installed
- [ ] Node.js 16+ is installed
- [ ] All Python packages are installed (`pip install -r requirements.txt`)
- [ ] All Node packages are installed (`npm install`)
- [ ] Backend starts without errors on port 5000
- [ ] Frontend starts without errors on port 3000
- [ ] `/api/health` returns `ffmpeg_available: true`
- [ ] Tried with a simple, public YouTube video
- [ ] Checked both backend terminal and browser console for errors

---

**Most issues are solved by:**
1. ✅ Installing FFmpeg
2. ✅ Restarting both servers after installing dependencies
3. ✅ Using a simple, public YouTube video for testing
