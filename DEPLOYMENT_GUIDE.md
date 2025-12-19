# 🚀 Deployment Guide for YouTube Clipper

This guide will walk you through deploying your YouTube Clipper application to production using GitHub, Vercel (frontend), and Render (backend).

## Prerequisites

- GitHub account
- Vercel account (free tier available)
- Render account (free tier available) OR Railway account

---

## Step 1: Push to GitHub

### 1.1 Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Name it `youtube-clipper` (or any name you prefer)
5. Keep it **Public** or **Private** (your choice)
6. **Do NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

### 1.2 Push Your Code to GitHub

Open your terminal in the YouTubeCut directory and run:

```bash
# Navigate to your project
cd YouTubeCut

# Add all files to git
git add .

# Create your first commit
git commit -m "Initial commit: YouTube Clipper application"

# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/youtube-clipper.git

# Push to GitHub
git push -u origin main
```

If you get an error about the branch name, try:
```bash
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Render

### 2.1 Create Render Account

1. Go to [Render](https://render.com)
2. Sign up with your GitHub account (recommended for easier deployment)

### 2.2 Deploy the Backend

1. Click **"New +"** button in the top right
2. Select **"Web Service"**
3. Connect your GitHub repository
   - Click **"Connect account"** if you haven't already
   - Select your `youtube-clipper` repository
4. Configure the service:
   - **Name**: `youtube-clipper-backend` (or any name)
   - **Region**: Choose the closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Instance Type**: `Free` (for testing)

5. Render will automatically detect the Dockerfile and use it

6. Click **"Create Web Service"**

7. Wait for deployment to complete (5-10 minutes)
   - You'll see build logs in real-time
   - When complete, you'll get a URL like: `https://youtube-clipper-backend.onrender.com`

8. **IMPORTANT**: Copy this URL - you'll need it for the frontend!

### 2.3 Test the Backend

Visit: `https://your-backend-url.onrender.com/api/health`

You should see:
```json
{
  "status": "healthy",
  "message": "YouTube Clipper API is running"
}
```

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account

1. Go to [Vercel](https://vercel.com)
2. Sign up with your GitHub account

### 3.2 Deploy the Frontend

#### Option A: Using Vercel Dashboard (Recommended)

1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository
   - Click **"Import"** next to your `youtube-clipper` repository
3. Configure the project:
   - **Project Name**: `youtube-clipper` (or any name)
   - **Framework Preset**: Vite
   - **Root Directory**: Click **"Edit"** and select `frontend`
   - **Build Command**: `npm run build` (should be auto-detected)
   - **Output Directory**: `dist` (should be auto-detected)

4. **Add Environment Variable**:
   - Click **"Environment Variables"**
   - Add the following:
     - **Name**: `VITE_API_URL`
     - **Value**: `https://your-backend-url.onrender.com` (the URL from Step 2)
   - Click **"Add"**

5. Click **"Deploy"**

6. Wait for deployment (2-5 minutes)

7. You'll get a URL like: `https://youtube-clipper.vercel.app`

#### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - What's your project's name? youtube-clipper
# - In which directory is your code located? ./
# - Want to override settings? No

# Add environment variable
vercel env add VITE_API_URL
# When prompted, enter: https://your-backend-url.onrender.com

# Deploy to production
vercel --prod
```

---

## Step 4: Update CORS Settings (Important!)

After deploying your frontend, you need to update the backend's CORS settings to allow requests from your Vercel domain.

### 4.1 Update app.py

If you're using a custom domain or want to restrict CORS, update [backend/app.py](backend/app.py):

```python
# Change this line:
CORS(app)

# To this (replace with your actual Vercel URL):
CORS(app, origins=[
    "https://youtube-clipper.vercel.app",
    "http://localhost:3000"  # Keep this for local development
])
```

### 4.2 Push Changes

```bash
git add backend/app.py
git commit -m "Update CORS settings for production"
git push
```

Render will automatically redeploy your backend.

---

## Step 5: Test Your Deployed Application

1. Visit your Vercel URL: `https://youtube-clipper.vercel.app`
2. Try creating a clip:
   - Enter a YouTube URL
   - Set start and end times
   - Click "Create Clip"
   - Download the clip

---

## Alternative: Deploy to Railway

Railway is another excellent option that can host both frontend and backend.

### Deploy Backend to Railway

1. Go to [Railway](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway will auto-detect the Dockerfile
7. Click on the service → **Settings** → **Generate Domain**
8. Copy the domain URL

### Deploy Frontend to Railway

1. Create another service in the same project
2. Add environment variable: `VITE_API_URL` = your backend Railway URL
3. Add build command: `cd frontend && npm install && npm run build`
4. Add start command: You'll need to add a simple server (like `serve`)

For Vercel frontend deployment, Railway is better suited for the backend only.

---

## Troubleshooting

### Backend Issues

**Build fails on Render:**
- Check the logs in Render dashboard
- Ensure Dockerfile is in the `backend` directory
- Verify FFmpeg installation in Dockerfile

**Video processing timeout:**
- Upgrade to a paid Render plan (free tier has 512MB RAM limit)
- Or reduce video quality in app.py

### Frontend Issues

**API connection fails:**
- Verify `VITE_API_URL` environment variable is set correctly
- Check browser console for CORS errors
- Ensure backend URL doesn't have trailing slash

**Build fails on Vercel:**
- Check Node.js version (should be 18+)
- Verify package.json is in frontend directory
- Clear cache and redeploy

### CORS Errors

If you see CORS errors in the browser console:
1. Update backend CORS settings
2. Ensure frontend URL is whitelisted
3. Redeploy backend

---

## Environment Variables Summary

### Frontend (.env for local, Vercel environment variables for production)
```
VITE_API_URL=https://your-backend-url.onrender.com
```

### Backend (optional, Render environment variables)
```
FLASK_ENV=production
FLASK_DEBUG=0
```

---

## Next Steps

### Optional Enhancements

1. **Custom Domain**:
   - Add a custom domain in Vercel settings
   - Update CORS in backend

2. **Add Rate Limiting**:
   - Install `flask-limiter`
   - Limit requests per IP

3. **Add Analytics**:
   - Add Google Analytics to frontend
   - Track usage metrics

4. **Improve Error Handling**:
   - Better error messages
   - Retry logic for failed downloads

5. **Add Features**:
   - Video preview before download
   - Multiple quality options
   - Playlist support
   - User accounts

---

## Cost Breakdown

### Free Tier (Suitable for personal use)

- **GitHub**: Free for public/private repos
- **Vercel**: Free (includes 100GB bandwidth/month)
- **Render**: Free (with limitations: spins down after 15min inactivity, 512MB RAM)

### If You Need More (Paid Options)

- **Render**: $7/month for always-on service with 512MB RAM
- **Vercel**: Free tier is usually sufficient for most uses
- **Railway**: $5/month minimum spend (usage-based)

---

## Support

If you encounter issues:

1. Check the logs:
   - Render: Dashboard → Logs tab
   - Vercel: Dashboard → Deployments → Click deployment → Logs

2. Common issues in [README.md](README.md)

3. GitHub Issues for bug reports

---

## Security Notes

- The free Render tier spins down after 15 minutes of inactivity (first request takes 30-60 seconds to wake up)
- Consider adding rate limiting for production
- No API keys are exposed in the frontend (all processing happens on backend)
- Temporary files are auto-deleted after 1 hour

---

## Congratulations! 🎉

Your YouTube Clipper is now live and accessible to anyone with the URL!

**Share it with friends and enjoy clipping videos!**
