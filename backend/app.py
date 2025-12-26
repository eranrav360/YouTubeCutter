from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import subprocess
from pathlib import Path
import time
import threading
import gc

app = Flask(__name__)
CORS(app)

# Create temp directory for downloads
TEMP_DIR = Path('temp_videos')
TEMP_DIR.mkdir(exist_ok=True)

# Cleanup old files on startup
def cleanup_old_files():
    """Remove files older than 1 hour"""
    current_time = time.time()
    for file in TEMP_DIR.glob('*'):
        if current_time - file.stat().st_mtime > 3600:  # 1 hour
            try:
                file.unlink()
            except Exception as e:
                print(f"Error removing {file}: {e}")

# Run cleanup periodically
def periodic_cleanup():
    while True:
        time.sleep(1800)  # Run every 30 minutes
        cleanup_old_files()

cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Check if FFmpeg is available
    ffmpeg_available = False
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        ffmpeg_available = result.returncode == 0
    except FileNotFoundError:
        ffmpeg_available = False

    return jsonify({
        'status': 'healthy',
        'message': 'YouTube Clipper API is running',
        'ffmpeg_available': ffmpeg_available
    })

@app.route('/api/clip', methods=['POST'])
def create_clip():
    """
    Create a video clip from YouTube URL

    Request body:
    {
        "url": "https://youtube.com/watch?v=...",
        "startTime": 30,  # in seconds
        "endTime": 90     # in seconds
    }
    """
    try:
        data = request.json
        url = data.get('url')
        start_time = data.get('startTime', 0)
        end_time = data.get('endTime')

        print(f"Received request - URL: {url}, Start: {start_time}, End: {end_time}")

        # Validate inputs
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400

        if not end_time or end_time <= start_time:
            return jsonify({'success': False, 'error': 'Invalid time range'}), 400

        # Check if FFmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"FFmpeg not found: {e}")
            return jsonify({'success': False, 'error': 'FFmpeg is not installed on the server'}), 500

        # Generate unique ID for this clip
        video_id = str(uuid.uuid4())
        output_path = TEMP_DIR / f'{video_id}.mp4'
        temp_download_path = TEMP_DIR / f'{video_id}_full.%(ext)s'

        # Download video with yt-dlp
        # Check for cookies from environment variable or file
        cookies_file = Path('cookies.txt')
        cookies_env = os.environ.get('YOUTUBE_COOKIES')

        ydl_opts = {
            # Optimized for quality while staying within 512MB memory limit
            # Prefer 1080p MP4, fall back to 720p, then lower qualities
            # Using bestvideo+bestaudio for better quality when possible
            'format': (
                'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/'
                'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/'
                'best[height<=720]/best'
            ),
            'outtmpl': str(temp_download_path),
            'quiet': False,
            'no_warnings': False,
            # Limit buffer size to reduce memory
            'http_chunk_size': 1048576,  # 1MB chunks
            # CRITICAL: Only download single video, not playlists
            'noplaylist': True,
            # Merge video+audio into single file
            'merge_output_format': 'mp4',
        }

        # Add cookies if available
        if cookies_env:
            # Create cookies file from environment variable
            print("Using cookies from environment variable")
            cookies_file.write_text(cookies_env)
            ydl_opts['cookiefile'] = str(cookies_file)
        elif cookies_file.exists():
            print("Using cookies from file")
            ydl_opts['cookiefile'] = str(cookies_file)
        else:
            print("No cookies found, trying without authentication")
            # Try mobile API as fallback
            ydl_opts['extractor_args'] = {
                'youtube': {
                    'player_client': ['android', 'ios'],
                }
            }

        print(f"Downloading video from {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as download_error:
            print(f"Download error: {download_error}")
            return jsonify({'success': False, 'error': f'Failed to download video: {str(download_error)}'}), 500

        # Find the downloaded file
        downloaded_file = None
        for ext in ['mp4', 'webm', 'mkv']:
            potential_file = TEMP_DIR / f'{video_id}_full.{ext}'
            if potential_file.exists():
                downloaded_file = potential_file
                break

        if not downloaded_file:
            print(f"Downloaded file not found. Checked extensions: mp4, webm, mkv")
            print(f"Files in temp dir: {list(TEMP_DIR.glob('*'))}")
            return jsonify({'success': False, 'error': 'Failed to download video - file not found after download'}), 500

        print(f"Downloaded file: {downloaded_file}")

        # Calculate duration
        duration = end_time - start_time

        # Use FFmpeg to extract the clip
        print(f"Extracting clip from {start_time}s to {end_time}s")
        ffmpeg_command = [
            'ffmpeg',
            '-i', str(downloaded_file),
            '-ss', str(start_time),
            '-t', str(duration),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-preset', 'fast',
            '-y',  # Overwrite output file
            str(output_path)
        ]

        result = subprocess.run(ffmpeg_command, capture_output=True, text=True)

        # Remove the full downloaded file
        try:
            downloaded_file.unlink()
        except Exception as e:
            print(f"Error removing temp file: {e}")

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return jsonify({'success': False, 'error': f'Failed to process video with FFmpeg: {result.stderr[:200]}'}), 500

        print(f"Clip created successfully: {output_path}")

        # Force garbage collection to free memory
        gc.collect()

        # Return success with download URL
        return jsonify({
            'success': True,
            'message': 'Clip created successfully',
            'videoId': video_id,
            'downloadUrl': f'/api/download/{video_id}'
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        # Clean up on error
        gc.collect()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<video_id>', methods=['GET'])
def download_clip(video_id):
    """Download the processed clip"""
    try:
        file_path = TEMP_DIR / f'{video_id}.mp4'

        if not file_path.exists():
            return jsonify({'error': 'Video not found'}), 404

        return send_file(
            file_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=f'clip_{video_id}.mp4'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    cleanup_old_files()  # Cleanup on startup
    app.run(host='0.0.0.0', port=5000, debug=True)
