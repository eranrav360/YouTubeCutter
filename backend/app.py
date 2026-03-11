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

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Temporary directory for storing processed videos
TEMP_DIR = Path(tempfile.gettempdir()) / "youtube_clips"
TEMP_DIR.mkdir(exist_ok=True)

def cleanup_old_files():
    """Remove files older than 1 hour"""
    try:
        current_time = time.time()
        for file in TEMP_DIR.glob("*"):
            if file.stat().st_mtime < (current_time - 3600):
                file.unlink()
                logger.info(f"Cleaned up old file: {file}")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def download_and_clip(url, start_time, end_time):
    """Download YouTube video and extract clip using Android client"""
    video_id = str(uuid.uuid4())
    output_file = TEMP_DIR / f"{video_id}.mp4"
    
    try:
        # Calculate duration
        duration = end_time - start_time
        
        logger.info(f"Processing video - URL: {url}, Start: {start_time}s, End: {end_time}s, Duration: {duration}s")
        
        # yt-dlp options using Android client (bypasses most restrictions)
        ydl_opts = {
            # Use Android client which bypasses bot detection
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],  # Android client works without cookies
                }
            },
            # Format selection
            'format': 'best[ext=mp4][height<=720]/best[ext=mp4]/best',  # Limit to 720p for faster downloads
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
                'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
            },
        }
        
        # Download video
        logger.info(f"Starting download for video ID: {video_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                logger.info(f"Successfully downloaded to: {downloaded_file}")
            except Exception as e:
                logger.error(f"yt-dlp error: {str(e)}")
                raise Exception(f"Failed to download video: {str(e)}")
        
        # Verify downloaded file exists
        if not os.path.exists(downloaded_file):
            raise Exception(f"Downloaded file not found: {downloaded_file}")
        
        # Use ffmpeg to extract the clip
        logger.info(f"Extracting clip: {start_time}s to {end_time}s ({duration}s)")
        cmd = [
            'ffmpeg',
            '-i', downloaded_file,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'fast',  # Faster encoding
            '-crf', '23',  # Quality setting
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',  # Overwrite output file
            str(output_file)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"FFmpeg completed successfully")
        
        # Verify output file was created
        if not os.path.exists(output_file):
            raise Exception("FFmpeg failed to create output file")
        
        # Clean up the full downloaded video
        try:
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
                logger.info(f"Cleaned up temporary file: {downloaded_file}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")
        
        logger.info(f"Clip created successfully: {output_file}")
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
        "files_count": len(list(TEMP_DIR.glob("*")))
    })

@app.route('/api/clip', methods=['POST'])
def create_clip():
    """Create a video clip from YouTube URL"""
    try:
        data = request.json
        logger.info(f"Received clip request: {data}")
        
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
        logger.info(f"Processing clip request - URL: {url}, Start: {start_time}, End: {end_time}")
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
        logger.error(f"Error in create_clip: {error_msg}")
        
        # Provide more helpful error messages
        if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
            return jsonify({
                "error": "YouTube requires verification. This video may be age-restricted or region-blocked. Try a different video."
            }), 403
        elif "Video unavailable" in error_msg:
            return jsonify({
                "error": "Video is unavailable. It may be private, deleted, or region-restricted."
            }), 404
        else:
            return jsonify({"error": f"Failed to process video: {error_msg}"}), 500

@app.route('/api/download/<video_id>', methods=['GET'])
def download_clip(video_id):
    """Download the processed video clip"""
    try:
        file_path = TEMP_DIR / f"{video_id}.mp4"
        
        if not file_path.exists():
            logger.warning(f"Video not found: {video_id}")
            return jsonify({"error": "Video not found or expired"}), 404
        
        logger.info(f"Serving download for: {video_id}")
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
        logger.info("FFmpeg is installed and ready")
    except FileNotFoundError:
        logger.error("FFmpeg is not installed. Please install it first.")
        exit(1)
    
    logger.info(f"Temporary directory: {TEMP_DIR}")
    logger.info("Starting YouTube Clipper API...")
    app.run(host='0.0.0.0', port=5000, debug=False)
