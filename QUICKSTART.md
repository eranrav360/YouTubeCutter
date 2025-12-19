# 🚀 Quick Start Guide

Get your YouTube Clipper running in 5 minutes!

## Local Development

### Prerequisites

Make sure you have installed:
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **FFmpeg** - [Installation Guide](#installing-ffmpeg)

### Installing FFmpeg

#### Windows
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract the ZIP file
3. Add the `bin` folder to your PATH
4. Verify: `ffmpeg -version`

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

---

## Step 1: Clone or Download

If you haven't already, get the project files:

```bash
cd YouTubeCut
```

---

## Step 2: Start the Backend

Open a terminal window:

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

**Keep this terminal open!**

---

## Step 3: Start the Frontend

Open a **NEW** terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies (first time only)
npm install

# Start the development server
npm run dev
```

You should see:
```
Local: http://localhost:3000
```

---

## Step 4: Use the App

1. Open your browser and go to: **http://localhost:3000**
2. Enter a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Enter start time (e.g., `0:10`)
4. Enter end time (e.g., `0:30`)
5. Click **"Create Clip"**
6. Wait for processing (usually 30-60 seconds)
7. Click **"Download Clip"**

---

## Troubleshooting

### "FFmpeg not found"
- Make sure FFmpeg is installed and in your PATH
- Test with: `ffmpeg -version`

### Backend won't start
- Make sure Python 3.8+ is installed: `python --version`
- Try: `python3 app.py` instead of `python app.py`

### Frontend won't start
- Make sure Node.js is installed: `node --version`
- Delete `node_modules` and run `npm install` again

### "Failed to connect to server"
- Make sure the backend is running on port 5000
- Check if another application is using port 5000
- Verify `VITE_API_URL` in frontend/.env (should be `http://localhost:5000`)

---

## Next Steps

- ✅ Test locally
- 📤 Deploy to production: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- 🎨 Customize the UI
- 🚀 Add new features

---

## Project Structure

```
YouTubeCut/
├── backend/              # Python Flask API
│   ├── app.py           # Main backend code
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # For deployment
│
├── frontend/            # React application
│   ├── src/
│   │   ├── App.jsx     # Main UI component
│   │   ├── main.jsx    # React entry point
│   │   └── index.css   # Tailwind imports
│   └── package.json    # Node dependencies
│
└── README.md           # Full documentation
```

---

## Tips

- **Start time** must be less than **end time**
- Time format: `MM:SS` (e.g., `1:30`) or `HH:MM:SS` (e.g., `0:01:30`)
- Processing time depends on video length and your internet speed
- Downloaded clips are saved to your browser's default download folder

---

## Need Help?

- Check [README.md](README.md) for detailed documentation
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment instructions
- Open an issue on GitHub if you encounter bugs

---

**Happy Clipping! ✂️🎬**
