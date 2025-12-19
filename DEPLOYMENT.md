# Quick Deployment Guide

## Deploy to Vercel (Frontend) + Render (Backend)

This is the recommended deployment setup for your YouTube Clipper app.

### Step 1: Deploy Backend to Render

1. **Create a Render account** at [render.com](https://render.com)

2. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

3. **Configure the service**:
   - **Name**: `youtube-clipper-backend` (or any name)
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Instance Type**: Free (or paid for better performance)

4. **Build settings** (if not using Docker):
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 2 app:app`

5. **Click "Create Web Service"**

6. **Wait for deployment** - Render will:
   - Install FFmpeg
   - Install Python dependencies
   - Start your Flask server
   - You'll get a URL like: `https://youtube-clipper-backend.onrender.com`

7. **Test your backend**:
   ```bash
   curl https://your-backend-url.onrender.com/api/health
   ```

### Step 2: Deploy Frontend to Vercel

1. **Create a Vercel account** at [vercel.com](https://vercel.com)

2. **Install Vercel CLI** (optional but recommended):
   ```bash
   npm install -g vercel
   ```

3. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

4. **Update the API URL**:
   Create a `.env.production` file:
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

5. **Deploy using CLI**:
   ```bash
   vercel
   ```
   
   Or **deploy via Vercel Dashboard**:
   - Go to Vercel dashboard
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Configure:
     - **Root Directory**: `frontend`
     - **Framework Preset**: Vite
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
   - Add Environment Variable:
     - **Key**: `VITE_API_URL`
     - **Value**: `https://your-backend-url.onrender.com`
   - Click "Deploy"

6. **Access your app**:
   - Vercel will give you a URL like: `https://your-app.vercel.app`
   - Your app is now live! 🎉

### Step 3: Update Backend CORS (Important!)

After deploying, update your backend to allow your Vercel domain:

Edit `backend/app.py`:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:3000",  # Development
    "https://your-app.vercel.app",  # Production
])
```

Then redeploy the backend on Render (it auto-redeploys on git push).

---

## Alternative: Deploy to Railway (Backend)

Railway is another great option for backend deployment:

1. **Create a Railway account** at [railway.app](https://railway.app)

2. **Create a new project**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects the Dockerfile

3. **Configure**:
   - Set root directory to `backend` (if needed)
   - Railway automatically uses the Dockerfile
   - No additional config needed!

4. **Get your URL**:
   - Railway provides a URL like: `https://your-app.up.railway.app`

5. **Use this URL in your Vercel environment variable**

---

## Testing Your Deployed App

1. **Visit your Vercel URL**
2. **Enter a YouTube URL**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. **Set times**: Start: `0:10`, End: `0:30`
4. **Click "Create Clip"**
5. **Download your clip** when ready!

---

## Troubleshooting

### Backend not working:
- Check Render/Railway logs
- Verify FFmpeg is installed (it should be via Dockerfile)
- Check if backend URL is accessible: `curl https://your-backend/api/health`

### CORS errors:
- Make sure backend CORS includes your Vercel domain
- Redeploy backend after updating CORS settings

### Frontend can't connect to backend:
- Verify `VITE_API_URL` environment variable is set correctly in Vercel
- Make sure it includes `https://` protocol
- Redeploy frontend after changing environment variables

### Videos taking too long:
- Render free tier may be slow
- Consider upgrading to a paid tier
- Or use Railway which may have better performance

---

## GitHub Repository Setup

Before deploying, push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit: YouTube clipper app"
git branch -M main
git remote add origin https://github.com/yourusername/youtube-clipper.git
git push -u origin main
```

Then both Vercel and Render/Railway can deploy directly from your GitHub repo!

---

## Cost Estimate

- **Render Free Tier**: $0/month (backend sleeps after inactivity)
- **Railway Free Trial**: $5 free credit
- **Vercel Free Tier**: $0/month (perfect for frontend)

For production use:
- **Render**: ~$7/month for always-on server
- **Railway**: Pay-as-you-go (typically $5-10/month)
- **Vercel**: Free for hobby projects

---

## Next Steps

1. ✅ Deploy backend to Render or Railway
2. ✅ Deploy frontend to Vercel  
3. ✅ Update CORS settings
4. ✅ Test the app
5. 🎉 Share with friends!

Need help? Check the main README.md or open an issue on GitHub.
