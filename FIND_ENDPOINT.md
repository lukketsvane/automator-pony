# 🔍 How to Find Your Upload Endpoint

The upload page at `https://ponyseeo.vercel.app/upload` is protected (403 Forbidden). Here's how to find the correct API endpoint:

## Method 1: Browser Developer Tools (Easiest)

1. **Open your browser** and go to: https://ponyseeo.vercel.app/upload

2. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)

3. **Go to the Network tab**

4. **Upload a test file** on your website

5. **Look for the upload request** in the Network tab:
   - Look for a POST request
   - Common names: "upload", "create", "add", etc.
   - Click on it to see details

6. **Copy the Request URL** - that's your endpoint!

Example: It might look like:
- `https://ponyseeo.vercel.app/api/upload`
- `https://ponyseeo.vercel.app/api/files`
- `https://ponyseeo.vercel.app/api/videos/create`

## Method 2: Check Page Source

1. Go to https://ponyseeo.vercel.app/upload in your browser
2. Right-click → "View Page Source" or press `Ctrl+U`
3. Search for:
   - `<form` - look for the `action=""` attribute
   - `fetch(` or `axios.post(` - look for API URLs
   - `/api/` - common API path prefix

## Method 3: Test Common Endpoints

Try these common Vercel/Next.js patterns:

```bash
# Test each endpoint with curl:
curl -X POST https://ponyseeo.vercel.app/api/upload -F "file=@test.mp4"
curl -X POST https://ponyseeo.vercel.app/api/files/upload -F "file=@test.mp4"
curl -X POST https://ponyseeo.vercel.app/api/videos/upload -F "file=@test.mp4"
curl -X POST https://ponyseeo.vercel.app/api/media/upload -F "file=@test.mp4"
```

Look for any response other than 404.

## Method 4: Check Your Source Code

If you have access to the website's source code:

1. Look in the `pages/api/` directory (Next.js)
2. Check for upload-related files
3. The filename usually indicates the endpoint

For example:
- `pages/api/upload.js` → `/api/upload`
- `pages/api/videos/upload.js` → `/api/videos/upload`

## Method 5: Share the Info

Once you find it, update the script:

```python
# In automate_upload.py, update these lines (around line 25-26):
UPLOAD_URL = "https://ponyseeo.vercel.app/YOUR_ENDPOINT_HERE"
UPLOAD_API_URL = "https://ponyseeo.vercel.app/api/YOUR_ENDPOINT_HERE"
```

## What Information I Need

Please share:
1. **The endpoint URL** (e.g., `/api/upload`)
2. **Required form fields** (from Network tab → Headers → Request Payload)
3. **The field name for the file** (often "file", "video", "media", etc.)

Example from Network tab:
```
POST /api/upload
Content-Type: multipart/form-data

file: (binary)
title: "My Video"
description: "Test upload"
```

## Quick Test Script

Once you have the endpoint, test it:

```python
import requests

endpoint = "https://ponyseeo.vercel.app/api/YOUR_ENDPOINT"
files = {'file': open('test_video.mp4', 'rb')}
data = {'title': 'Test Video'}

response = requests.post(endpoint, files=files, data=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

Let me know what you find and I'll update the automation script! 🚀
