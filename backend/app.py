from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import subprocess
import uuid
from pathlib import Path
import tempfile
import logging
import time
import base64

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Temporary directory for storing processed videos
TEMP_DIR = Path(tempfile.gettempdir()) / "youtube_clips"
TEMP_DIR.mkdir(exist_ok=True)

# Setup cookies for age-restricted/private videos
COOKIE_FILE = None

# Try to load cookies from environment variable (base64 encoded)
COOKIES_BASE64 = os.environ.get('YOUTUBE_COOKIES_BASE64')
if COOKIES_BASE64:
    try:
        logger.info("Loading cookies from environment variable...")
        cookie_data = base64.b64decode(COOKIES_BASE64)
        COOKIE_FILE = TEMP_DIR / 'youtube_cookies.txt'
        COOKIE_FILE.write_bytes(cookie_data)
        logger.info("✅ Cookies loaded successfully from environment")
    except Exception as e:
        logger.warning(f"Failed to load cookies from environment: {e}")

# Fallback: try to use local cookie file
elif os.path.exists('youtube_cookies.txt'):
    COOKIE_FILE = 'youtube_cookies.txt'
    logger.info("✅ Using local cookie file: youtube_cookies.txt")
else:
    logger.info("ℹ️ No cookies configured - age-restricted videos may not work")

def cleanup_old_files():
    """Remove files older than 1 hour"""
    try:
        current_time = time.time()
        count = 0
        for file in TEMP_DIR.glob("*"):
            if file.name == 'youtube_cookies.txt':
                continue  # Don't delete cookies
            if file.stat().st_mtime < (current_time - 3600):
                file.unlink()
                count += 1
        if count > 0:
            logger.info(f"Cleaned up {count} old file(s)")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def download_and_clip(url, start_time, end_time):
    """Download YouTube video and extract clip using Android client + cookies"""
    video_id = str(uuid.uuid4())
    output_file = TEMP_DIR / f"{video_id}.mp4"
    
    try:
        # Calculate duration
        duration = end_time - start_time
        
        logger.info(f"Processing video - URL: {url}, Start: {start_time}s, End: {end_time}s, Duration: {duration}s")
        
        # yt-dlp options - use web client when cookies are available
        ydl_opts = {
            # Format selection - limit to 720p for faster downloads
            'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',
            'outtmpl': str(TEMP_DIR / f"{video_id}_full.%(ext)s"),
            # Logging
            'quiet': False,
            'no_warnings': False,
            # Network settings
            'socket_timeout': 30,
            'retries': 5,
            'fragment_retries': 5,
            # Headers
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
        }
        
        # Configure client based on cookie availability
        if COOKIE_FILE:
            # Use web client with cookies (best compatibility)
            ydl_opts['cookiefile'] = str(COOKIE_FILE)
            logger.info("🔐 Using web client with cookies for authentication")
        else:
            # Use Android client without cookies
            ydl_opts['extractor_args'] = {
                'youtube': {
                    'player_client': ['android'],
                }
            }
            ydl_opts['http_headers']['User-Agent'] = 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip'
            logger.info("📱 Using Android client (no cookies)")
        
        # Download video
        logger.info(f"Starting download for video ID: {video_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                logger.info(f"✅ Successfully downloaded to: {downloaded_file}")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"yt-dlp error: {error_msg}")
                
                # Provide helpful error messages
                if "age" in error_msg.lower() or "restricted" in error_msg.lower():
                    if not COOKIE_FILE:
                        raise Exception("This video is age-restricted. Cookies are required. See documentation on how to add cookies.")
                    else:
                        raise Exception("Age-restricted video failed even with cookies. Your cookies may be expired.")
                elif "private" in error_msg.lower():
                    raise Exception("This video is private or unlisted and cannot be accessed.")
                elif "available" in error_msg.lower():
                    raise Exception("Video is not available. It may be deleted or region-blocked.")
                else:
                    raise Exception(f"Failed to download video: {error_msg}")
        
        # Verify downloaded file exists
        if not os.path.exists(downloaded_file):
            raise Exception(f"Downloaded file not found: {downloaded_file}")
        
        # Get file size for logging
        file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
        logger.info(f"Downloaded file size: {file_size_mb:.2f} MB")
        
        # Use ffmpeg to extract the clip
        logger.info(f"✂️ Extracting clip: {start_time}s to {end_time}s ({duration}s)")
        cmd = [
            'ffmpeg',
            '-i', downloaded_file,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',  # Faster encoding
            '-crf', '23',  # Quality setting (lower = better quality)
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',  # Overwrite output file
            str(output_file)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"✅ FFmpeg completed successfully")
        
        # Verify output file was created
        if not os.path.exists(output_file):
            raise Exception("FFmpeg failed to create output file")
        
        output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        logger.info(f"Output clip size: {output_size_mb:.2f} MB")
        
        # Clean up the full downloaded video
        try:
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
                logger.info(f"🗑️ Cleaned up temporary file")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")
        
        logger.info(f"🎉 Clip created successfully: {output_file}")
        return str(output_file), video_id
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        # Clean up any partial files
        for file in TEMP_DIR.glob(f"{video_id}*"):
            try:
                file.unlink()
            except:
                pass
        raise Exception(f"FFmpeg processing failed: {e.stderr}")
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        # Clean up any partial files
        for file in TEMP_DIR.glob(f"{video_id}*"):
            try:
                file.unlink()
            except:
                pass
        raise

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "YouTube Clipper API is running",
        "temp_dir": str(TEMP_DIR),
        "files_count": len([f for f in TEMP_DIR.glob("*") if f.name != 'youtube_cookies.txt']),
        "cookies_configured": COOKIE_FILE is not None
    })

@app.route('/api/clip', methods=['POST'])
def create_clip():
    """Create a video clip from YouTube URL"""
    try:
        data = request.json
        logger.info(f"📥 Received clip request: {data}")
        
        # Validate input
        if not data or 'url' not in data:
            return jsonify({"error": "YouTube URL is required"}), 400
        
        url = data['url']
        start_time = data.get('startTime', 0)
        end_time = data.get('endTime')
        
        if not end_time or end_time <= start_time:
            return jsonify({"error": "Valid end time is required (must be greater than start time)"}), 400
        
        # Validate time values
        if start_time < 0 or end_time < 0:
            return jsonify({"error": "Time values must be positive"}), 400
        
        if end_time - start_time > 600:  # Max 10 minutes
            return jsonify({"error": "Clip duration cannot exceed 10 minutes"}), 400
        
        # Clean up old files before processing
        cleanup_old_files()
        
        # Process the video
        logger.info(f"🎬 Processing clip - URL: {url}, Start: {start_time}, End: {end_time}")
        output_file, video_id = download_and_clip(url, start_time, end_time)
        
        # Return success with download URL
        return jsonify({
            "success": True,
            "message": "Clip created successfully",
            "videoId": video_id,
            "downloadUrl": f"/api/download/{video_id}"
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Error in create_clip: {error_msg}")
        
        # Provide helpful error messages based on the error type
        if "age-restricted" in error_msg.lower() or "cookies are required" in error_msg.lower():
            return jsonify({
                "error": "This video is age-restricted. Cookies are required to download it. Contact admin to enable cookie support.",
                "hint": "Age-restricted videos require authentication"
            }), 403
        elif "cookies may be expired" in error_msg.lower():
            return jsonify({
                "error": "Authentication failed. Cookies may be expired. Please contact admin to refresh cookies.",
                "hint": "Cookies need to be refreshed periodically"
            }), 403
        elif "sign in to confirm" in error_msg.lower() or "bot" in error_msg.lower():
            return jsonify({
                "error": "YouTube requires verification. This video may be age-restricted or region-blocked. Try a different video.",
                "hint": "Some videos require authentication or are blocked in your region"
            }), 403
        elif "video unavailable" in error_msg.lower() or "not available" in error_msg.lower():
            return jsonify({
                "error": "Video is unavailable. It may be private, deleted, or region-restricted.",
                "hint": "Check if the video is accessible on YouTube directly"
            }), 404
        elif "private" in error_msg.lower():
            return jsonify({
                "error": "This video is private and cannot be accessed.",
                "hint": "Private videos cannot be downloaded"
            }), 403
        else:
            return jsonify({
                "error": f"Failed to process video: {error_msg}",
                "hint": "Try a different video or check if the URL is correct"
            }), 500

@app.route('/api/download/<video_id>', methods=['GET'])
def download_clip(video_id):
    """Download the processed video clip"""
    try:
        file_path = TEMP_DIR / f"{video_id}.mp4"
        
        if not file_path.exists():
            logger.warning(f"⚠️ Video not found: {video_id}")
            return jsonify({"error": "Video not found or expired"}), 404
        
        logger.info(f"📤 Serving download for: {video_id}")
        return send_file(
            file_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'youtube_clip_{video_id}.mp4'
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({"error": "Failed to download video"}), 500

if __name__ == '__main__':
    # Make sure ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info("✅ FFmpeg is installed and ready")
    except FileNotFoundError:
        logger.error("❌ FFmpeg is not installed. Please install it first.")
        exit(1)
    
    logger.info(f"📁 Temporary directory: {TEMP_DIR}")
    if COOKIE_FILE:
        logger.info(f"🔐 Cookies: Enabled (supports age-restricted videos)")
    else:
        logger.info(f"ℹ️  Cookies: Not configured (age-restricted videos may not work)")
    logger.info("🚀 Starting YouTube Clipper API...")
    app.run(host='0.0.0.0', port=5000, debug=False)
