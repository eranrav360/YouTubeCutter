# 🍪 YouTube Cookies Setup Guide

YouTube now requires authentication to prevent bot access. This guide will help you export your YouTube cookies so the application can download videos.

## Why Do I Need This?

YouTube's anti-bot protection now blocks automated downloads. By providing your browser cookies, the app can authenticate as if you're logged in, allowing downloads to work.

**Important:** Cookies are like a temporary password. Keep them secure!

---

## Method 1: Using Browser Extension (Easiest)

### For Chrome/Edge:

1. **Install "Get cookies.txt LOCALLY" Extension:**
   - Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   - Edge: Same link (Edge uses Chrome store)

2. **Go to YouTube:**
   - Open https://youtube.com
   - Make sure you're **logged in**

3. **Export Cookies:**
   - Click the extension icon (cookie icon in toolbar)
   - Click **"Export"**
   - Save the file as `cookies.txt`

4. **Upload to Render:**
   - See "Uploading Cookies to Render" section below

### For Firefox:

1. **Install "cookies.txt" Extension:**
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

2. **Go to YouTube:**
   - Open https://youtube.com
   - Make sure you're **logged in**

3. **Export Cookies:**
   - Click the extension icon
   - Click **"Current Site"**
   - Save as `cookies.txt`

---

## Method 2: Manual Export (Advanced)

If you can't use extensions, you can manually export cookies:

### Using yt-dlp Directly:

```bash
# This will extract cookies from your browser
yt-dlp --cookies-from-browser chrome --cookies cookies.txt https://youtube.com
```

Replace `chrome` with your browser: `chrome`, `firefox`, `edge`, `safari`, `opera`

---

## Uploading Cookies to Render

Once you have `cookies.txt`, you need to upload it to your Render server.

### Option 1: Using Render Shell (Recommended)

1. **Go to Render Dashboard:**
   - Open https://dashboard.render.com
   - Click on your backend service

2. **Open Shell:**
   - Click **"Shell"** tab in the left sidebar
   - Wait for terminal to connect

3. **Create Cookies File:**
   ```bash
   # Create the cookies file
   cat > cookies.txt << 'EOF'
   # Paste your cookies.txt content here
   # (Press Ctrl+V to paste)
   # Then type EOF on a new line
   EOF
   ```

4. **Verify:**
   ```bash
   ls -la cookies.txt
   ```

### Option 2: Add to Repository (Less Secure)

⚠️ **WARNING:** Only do this for PRIVATE repositories!

1. **Copy cookies.txt to backend folder:**
   ```bash
   cp cookies.txt YouTubeCut/backend/
   ```

2. **Update .gitignore to EXCLUDE cookies:**
   Make sure `.gitignore` contains:
   ```
   cookies.txt
   ```

3. **Manually upload via Render:**
   - You'll need to use Render's shell to create the file

### Option 3: Environment Variable (Most Secure for Deployment)

1. **Convert cookies.txt to base64:**
   ```bash
   base64 cookies.txt > cookies_base64.txt
   ```

2. **Add to Render Environment Variables:**
   - In Render dashboard → Environment
   - Add variable: `YOUTUBE_COOKIES_BASE64`
   - Paste the base64 content

3. **Update app.py to decode:**
   (This would require code changes - let me know if you want this option)

---

## Testing After Adding Cookies

### Test Locally First:

1. **Copy cookies.txt to backend folder:**
   ```bash
   cp cookies.txt YouTubeCut/backend/
   ```

2. **Restart your local backend:**
   ```bash
   cd YouTubeCut/backend
   python app.py
   ```

3. **Try creating a clip:**
   - Visit http://localhost:3000
   - Try the same video that failed before

4. **Check backend logs:**
   - Should see: `Using cookies for authentication`

### Test on Render:

After uploading cookies to Render:

1. **Restart the service:**
   - Render Dashboard → Your service
   - Click **"Manual Deploy"** → **"Clear build cache & deploy"**

2. **Test via your Vercel app:**
   - Visit your Vercel URL
   - Try creating a clip

---

## Cookie Security Notes

### Important:

- ✅ Cookies expire after a few weeks/months
- ✅ You'll need to refresh them periodically
- ⚠️ Never share your cookies file publicly
- ⚠️ Don't commit cookies.txt to a public GitHub repo
- ⚠️ Cookies give access to your YouTube account

### Best Practices:

1. **Use a dedicated Google account** for this app
2. **Regenerate cookies monthly**
3. **Keep cookies.txt in .gitignore**
4. **Use environment variables in production**

---

## Troubleshooting

### "Still getting bot detection error"

- Cookies might be expired → Export fresh ones
- Cookies format might be wrong → Use the browser extension method
- You might not be logged into YouTube → Log in first, then export

### "Cookies file not found"

- Make sure file is named exactly `cookies.txt`
- Make sure it's in the `backend` folder on Render
- Check Render Shell: `ls -la cookies.txt`

### "Downloads work locally but not on Render"

- You uploaded cookies locally but forgot to upload to Render
- Render service needs to be restarted after adding cookies

---

## Alternative: Use Without Cookies

If you don't want to use cookies, limitations apply:

- ❌ Many videos won't work (bot detection)
- ✅ Some old/popular videos might still work
- ✅ Videos from other platforms (Vimeo, etc.) work fine

---

## Quick Setup Checklist

- [ ] Install browser extension
- [ ] Go to YouTube and log in
- [ ] Export cookies as `cookies.txt`
- [ ] Test locally (copy to `backend/cookies.txt`)
- [ ] Upload to Render (via Shell or environment variable)
- [ ] Restart Render service
- [ ] Test on deployed app

---

## Need Help?

1. Check that cookies.txt is in Netscape format (not JSON)
2. Make sure you're logged into YouTube when exporting
3. Try a fresh export if cookies are old
4. Check Render logs for authentication messages

---

**Once cookies are set up, your YouTube Clipper will work reliably! 🎉**
