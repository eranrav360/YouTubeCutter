# ClipIt - YouTube Video Clipper

A modern web application that allows users to extract specific clips from YouTube videos and download them as MP4 files.

## Features

- 🎬 Extract clips from any YouTube video
- ⏰ Specify start and end times (supports MM:SS and HH:MM:SS formats)
- 📥 Download clips as MP4 files
- 🎨 Beautiful, modern UI with dark theme
- ⚡ Fast processing using yt-dlp and FFmpeg

## Architecture

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Flask (Python) + yt-dlp + FFmpeg
- **Icons**: Lucide React

## Prerequisites

### Backend
- Python 3.8+
- FFmpeg installed on your system
- pip (Python package manager)

### Frontend
- Node.js 16+
- npm or yarn

## Local Development

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg (if not already installed):
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

5. Run the Flask backend:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Deployment

### Deploy Backend to Render/Railway/Heroku

#### Option 1: Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --timeout 300 app:app`
   - **Environment**: Python 3
4. Add the following environment variable:
   - `PYTHON_VERSION`: `3.11.0`
5. Under "Advanced", add a Dockerfile (optional but recommended)

#### Option 2: Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect the Dockerfile and deploy
4. Add environment variables if needed

#### Option 3: Docker Deployment

Build and run using Docker:
```bash
cd backend
docker build -t youtube-clipper-backend .
docker run -p 5000:5000 youtube-clipper-backend
```

### Deploy Frontend to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Navigate to frontend directory:
```bash
cd frontend
```

3. Deploy to Vercel:
```bash
vercel
```

4. Set environment variable:
   - `VITE_API_URL`: Your backend API URL (e.g., `https://your-backend.onrender.com`)

5. For subsequent deploys:
```bash
vercel --prod
```

#### Alternative: Deploy via Vercel Dashboard

1. Go to [Vercel](https://vercel.com)
2. Import your GitHub repository
3. Select the `frontend` directory as the root
4. Add environment variable: `VITE_API_URL`
5. Deploy

### Deploy Frontend to GitHub Pages (Static Only)

Note: This requires a separate backend deployment since GitHub Pages only serves static content.

1. Update `package.json` to include:
```json
"homepage": "https://yourusername.github.io/youtube-clipper",
"scripts": {
  "predeploy": "npm run build",
  "deploy": "gh-pages -d dist"
}
```

2. Install gh-pages:
```bash
npm install --save-dev gh-pages
```

3. Deploy:
```bash
npm run deploy
```

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000
```

### Backend (.env)
```
FLASK_ENV=production
FLASK_DEBUG=0
```

## API Endpoints

### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "YouTube Clipper API is running"
}
```

### `POST /api/clip`
Create a video clip

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "startTime": 30,
  "endTime": 90
}
```

**Response:**
```json
{
  "success": true,
  "message": "Clip created successfully",
  "videoId": "unique-id",
  "downloadUrl": "/api/download/unique-id"
}
```

### `GET /api/download/:videoId`
Download the processed clip

**Response:** MP4 video file

## Project Structure

```
youtube-clipper/
├── backend/
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Docker configuration
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Tailwind styles
│   ├── index.html            # HTML template
│   ├── package.json          # Node dependencies
│   ├── vite.config.js        # Vite configuration
│   ├── tailwind.config.js    # Tailwind configuration
│   └── vercel.json           # Vercel configuration
└── README.md
```

## Technologies Used

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Plus Jakarta Sans** - Google Font

### Backend
- **Flask** - Python web framework
- **yt-dlp** - YouTube video downloader
- **FFmpeg** - Video processing
- **Flask-CORS** - Cross-origin resource sharing
- **Gunicorn** - Production WSGI server

## Troubleshooting

### Backend Issues

**FFmpeg not found:**
```bash
# Check if FFmpeg is installed
ffmpeg -version

# Install if missing (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

**Port already in use:**
```bash
# Change port in app.py
app.run(host='0.0.0.0', port=5001)
```

**Video processing timeout:**
- Increase timeout in Dockerfile: `--timeout 600`
- Check internet connection
- Verify YouTube URL is accessible

### Frontend Issues

**API connection failed:**
- Verify backend is running
- Check `VITE_API_URL` environment variable
- Verify CORS is enabled on backend

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Security Considerations

- The backend uses temporary storage that auto-cleans files older than 1 hour
- No user authentication required (consider adding for production)
- Rate limiting recommended for production deployment
- Consider adding input validation and sanitization
- Use HTTPS in production

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Lucide](https://lucide.dev/) - Icons
