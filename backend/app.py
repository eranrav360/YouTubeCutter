from flask import Flask, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import os
import uuid
import subprocess
from pathlib import Path
import time
import threading
import gc
import re
import json

app = Flask(__name__)
# Configure CORS to allow requests from Vercel frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://you-tube-cutter.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Create temp directory for downloads
TEMP_DIR = Path('temp_videos')
TEMP_DIR.mkdir(exist_ok=True)

# Progress tracking dictionary
progress_tracker = {}

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

        # Calculate duration and add buffer for segmented download
        duration = end_time - start_time
        # Add 5 second buffer before and after for better quality
        download_start = max(0, start_time - 5)
        download_end = end_time + 5

        ydl_opts = {
            # Download only needed segment to reduce memory usage
            # Use 720p max to balance quality and memory on free tier
            'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[height<=720]',
            'outtmpl': str(temp_download_path),
            'quiet': False,
            'no_warnings': False,
            # Limit buffer size to reduce memory
            'http_chunk_size': 1048576,  # 1MB chunks
            # CRITICAL: Only download single video, not playlists
            'noplaylist': True,
            # Merge video+audio into single file
            'merge_output_format': 'mp4',
            # Download only the segment we need (massive memory savings)
            'download_ranges': lambda info_dict, *args: [{
                'start_time': download_start,
                'end_time': download_end,
            }],
            'force_keyframes_at_cuts': True,
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

        # Get direct video URL using yt-dlp (much faster than downloading)
        print(f"Getting video URL from {url}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info['url']
                print(f"Got direct video URL, processing clip directly")
        except Exception as extract_error:
            print(f"URL extraction error: {extract_error}")
            return jsonify({'success': False, 'error': f'Failed to get video URL: {str(extract_error)}'}), 500

        # Use FFmpeg to download and extract clip in one step (much faster!)
        # Seek to start_time in the original video, extract clip_duration
        clip_duration = end_time - start_time

        print(f"FFmpeg: streaming from {start_time}s, extracting {clip_duration}s clip")
        ffmpeg_command = [
            'ffmpeg',
            '-ss', str(start_time),  # Seek before input (faster)
            '-i', video_url,  # Stream directly from YouTube
            '-t', str(clip_duration),  # Duration to extract
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-preset', 'ultrafast',  # Faster encoding
            '-progress', 'pipe:1',  # Output progress to stdout
            '-y',  # Overwrite output file
            str(output_path)
        ]

        # Initialize progress tracking for this video
        progress_tracker[video_id] = {'progress': 0, 'status': 'processing', 'message': 'Starting...'}

        # Function to process video in background with progress tracking
        def process_video():
            try:
                progress_tracker[video_id] = {'progress': 10, 'status': 'processing', 'message': 'Extracting video URL...'}

                # Run FFmpeg with progress tracking
                process = subprocess.Popen(
                    ffmpeg_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )

                progress_tracker[video_id] = {'progress': 30, 'status': 'processing', 'message': 'Processing video...'}

                # Parse FFmpeg output for progress
                total_duration = clip_duration
                for line in process.stderr:
                    # Extract time from FFmpeg output
                    time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                    if time_match:
                        hours, minutes, seconds = time_match.groups()
                        current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                        progress_percent = min(int((current_time / total_duration) * 60) + 30, 90)
                        progress_tracker[video_id] = {
                            'progress': progress_percent,
                            'status': 'processing',
                            'message': f'Encoding... {progress_percent}%'
                        }

                process.wait()

                if process.returncode == 0:
                    progress_tracker[video_id] = {'progress': 100, 'status': 'completed', 'message': 'Clip ready!'}
                else:
                    stderr_output = process.stderr.read() if hasattr(process.stderr, 'read') else "Unknown error"
                    progress_tracker[video_id] = {
                        'progress': 0,
                        'status': 'error',
                        'message': f'FFmpeg error: {stderr_output[:200]}'
                    }
            except Exception as e:
                progress_tracker[video_id] = {'progress': 0, 'status': 'error', 'message': str(e)}

        # Start background processing
        thread = threading.Thread(target=process_video)
        thread.start()

        # Return immediately with video ID for progress tracking
        return jsonify({
            'success': True,
            'message': 'Processing started',
            'videoId': video_id
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        # Clean up on error
        gc.collect()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progress/<video_id>', methods=['GET'])
def get_progress(video_id):
    """Get processing progress for a video"""
    try:
        if video_id in progress_tracker:
            return jsonify(progress_tracker[video_id])
        else:
            return jsonify({'progress': 0, 'status': 'not_found', 'message': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
