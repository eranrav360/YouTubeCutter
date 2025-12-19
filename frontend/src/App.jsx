import React, { useState } from 'react';
import { Download, Scissors, Youtube, Clock, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

// Backend API URL - update this based on your deployment
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default function App() {
  const [url, setUrl] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [status, setStatus] = useState('idle'); // idle, processing, success, error
  const [message, setMessage] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');

  const parseTimeToSeconds = (timeStr) => {
    if (!timeStr) return 0;
    const parts = timeStr.split(':').map(p => parseInt(p) || 0);
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    return parts[0] || 0;
  };

  const validateInputs = () => {
    if (!url.trim()) {
      setMessage('Please enter a YouTube URL');
      return false;
    }
    
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    if (!youtubeRegex.test(url)) {
      setMessage('Please enter a valid YouTube URL');
      return false;
    }

    const start = parseTimeToSeconds(startTime);
    const end = parseTimeToSeconds(endTime);
    
    if (end <= start) {
      setMessage('End time must be greater than start time');
      return false;
    }

    return true;
  };

  const handleDownload = async () => {
    if (!validateInputs()) {
      setStatus('error');
      return;
    }

    setStatus('processing');
    setMessage('Processing your video clip...');

    try {
      const response = await fetch(`${API_URL}/api/clip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url,
          startTime: parseTimeToSeconds(startTime),
          endTime: parseTimeToSeconds(endTime)
        })
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        setStatus('success');
        setMessage('Your clip is ready to download!');
        setDownloadUrl(`${API_URL}${data.downloadUrl}`);
      } else {
        setStatus('error');
        setMessage(data.error || 'Failed to process video. Please try again.');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Failed to connect to server. Please try again.');
      console.error('Error:', error);
    }
  };

  const resetForm = () => {
    setStatus('idle');
    setMessage('');
    setDownloadUrl('');
    setUrl('');
    setStartTime('');
    setEndTime('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-neutral-900 to-zinc-950 text-white font-sans relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-red-600/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="relative z-10 container mx-auto px-6 py-12 max-w-4xl">
        {/* Header */}
        <header className="text-center mb-16 animate-fadeIn">
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className="relative">
              <Youtube className="w-16 h-16 text-red-500" strokeWidth={1.5} />
              <Scissors className="w-8 h-8 text-white absolute -bottom-2 -right-2 animate-bounce" strokeWidth={2} />
            </div>
          </div>
          <h1 className="text-6xl font-black mb-4 bg-gradient-to-r from-red-500 via-pink-500 to-purple-500 bg-clip-text text-transparent tracking-tight">
            ClipIt
          </h1>
          <p className="text-xl text-zinc-400 font-light tracking-wide">
            Extract perfect moments from any YouTube video
          </p>
        </header>

        {/* Main Card */}
        <div className="bg-zinc-900/50 backdrop-blur-xl rounded-3xl border border-zinc-800/50 shadow-2xl p-8 animate-slideUp">
          {status === 'idle' || status === 'error' ? (
            <div className="space-y-6">
              {/* URL Input */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
                  <Youtube className="w-4 h-4" />
                  YouTube URL
                </label>
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="w-full bg-zinc-950/50 border border-zinc-700 rounded-xl px-5 py-4 text-white placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300"
                />
              </div>

              {/* Time Inputs */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Start Time
                  </label>
                  <input
                    type="text"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    placeholder="0:00 or 0:00:00"
                    className="w-full bg-zinc-950/50 border border-zinc-700 rounded-xl px-5 py-4 text-white placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    End Time
                  </label>
                  <input
                    type="text"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    placeholder="1:30 or 0:01:30"
                    className="w-full bg-zinc-950/50 border border-zinc-700 rounded-xl px-5 py-4 text-white placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300"
                  />
                </div>
              </div>

              {/* Error Message */}
              {status === 'error' && (
                <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/30 rounded-xl p-4 animate-shake">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-red-300 text-sm">{message}</p>
                </div>
              )}

              {/* Download Button */}
              <button
                onClick={handleDownload}
                className="w-full bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-500 hover:to-pink-500 text-white font-bold py-5 px-8 rounded-xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-red-500/25 flex items-center justify-center gap-3 group"
              >
                <Download className="w-5 h-5 group-hover:animate-bounce" />
                Create Clip
              </button>

              {/* Helper Text */}
              <div className="text-center text-sm text-zinc-500 pt-4">
                <p>Enter times in format: MM:SS or HH:MM:SS</p>
                <p className="mt-1">Example: 1:30 for 1 minute 30 seconds</p>
              </div>
            </div>
          ) : status === 'processing' ? (
            <div className="text-center py-12 space-y-6 animate-fadeIn">
              <Loader2 className="w-16 h-16 text-red-500 mx-auto animate-spin" />
              <div>
                <h3 className="text-2xl font-bold mb-2">Processing Your Clip</h3>
                <p className="text-zinc-400">{message}</p>
                <p className="text-zinc-500 text-sm mt-2">This may take a minute...</p>
              </div>
              <div className="flex gap-2 justify-center">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 space-y-6 animate-fadeIn">
              <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-12 h-12 text-green-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold mb-2">Success!</h3>
                <p className="text-zinc-400">{message}</p>
              </div>
              <div className="flex gap-4 justify-center flex-wrap">
                <a
                  href={downloadUrl}
                  download
                  className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg shadow-green-500/25 flex items-center gap-2"
                >
                  <Download className="w-5 h-5" />
                  Download Clip
                </a>
                <button
                  onClick={resetForm}
                  className="bg-zinc-800 hover:bg-zinc-700 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300"
                >
                  Create Another
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="text-center mt-12 text-zinc-600 text-sm">
          <p>Download MP4 clips from YouTube videos • Fast & Easy</p>
        </footer>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800;900&display=swap');

        * {
          font-family: 'Plus Jakarta Sans', sans-serif;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }

        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out;
        }

        .animate-slideUp {
          animation: slideUp 0.6s ease-out;
        }

        .animate-shake {
          animation: shake 0.3s ease-in-out;
        }
      `}</style>
    </div>
  );
}
