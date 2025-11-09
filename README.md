# 🎬 Direct Google Drive to Website Upload Automator

Streams video files **directly** from Google Drive to ponyseeo.vercel.app without downloading to local storage. Fast, efficient, and handles subdirectories!

## ✨ Key Features

- 🚀 **Direct streaming** - No local download required! Streams from Drive → Website
- 📂 **Recursive scanning** - Automatically processes all subdirectories
- 🔄 **Resume capability** - Tracks uploaded files and resumes from where it left off
- ♻️ **Automatic retry** - Retries failed uploads up to 3 times
- 📊 **Progress tracking** - Real-time progress bars and detailed logging
- 🎯 **Smart endpoints** - Tries multiple API endpoints automatically
- 📝 **Comprehensive logging** - All operations logged to `logs/` directory

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Automation

```bash
# Basic usage - stream and upload all videos
python automate_upload.py

# Dry run - see what would be uploaded without actually uploading
python automate_upload.py --dry-run

# Reset state and start fresh
python automate_upload.py --reset-state
```

That's it! No configuration needed - everything is hardcoded and ready to go.

## 📋 Hardcoded Configuration

The script is pre-configured with:

- **Google Drive Folder**: `1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf`
- **API Key**: `AIzaSyA-r4BkJ30DoyB7xALj3q-n1WTavtBYqRM`
- **Upload Site**: `https://ponyseeo.vercel.app/upload`
- **Subdirectories**: ✅ Enabled (recursive scanning)

## 🎯 Supported Video Formats

`.mp4` `.avi` `.mov` `.mkv` `.webm` `.flv` `.wmv` `.m4v` `.3gp` `.mpeg` `.mpg`

## 📊 How It Works

1. **Scan Drive** - Recursively scans Google Drive folder and all subdirectories
2. **List Videos** - Finds all video files using Google Drive API
3. **Stream & Upload**:
   - Streams file directly from Google Drive
   - Uploads to website in one operation
   - No local storage used!
4. **Track Progress** - Saves state after each upload
5. **Summary Report** - Shows detailed statistics

## 🔄 Resume Capability

The script tracks uploaded files in `upload_state.json` by Google Drive file ID. If interrupted:

```bash
python automate_upload.py  # Just re-run - it remembers!
```

## 📁 Directory Structure Support

The script automatically:
- Scans all subdirectories recursively
- Preserves folder paths in upload metadata
- Shows directory structure before uploading
- Handles nested folders of any depth

Example output:
```
📁 Directory structure:
   Folder1/SubfolderA: 5 videos
   Folder1/SubfolderB: 3 videos
   Folder2: 8 videos
   Root folder: 2 videos
```

## 📝 Logs

All operations logged to `logs/upload_YYYYMMDD_HHMMSS.log`:
- File streaming progress
- Upload attempts and results
- Error messages
- Summary statistics

## 💡 Command Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Test without uploading (shows what would be uploaded) |
| `--reset-state` | Forget previous uploads and start fresh |

## 🐛 Troubleshooting

### No videos found
- Verify folder ID: `1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf`
- Check folder is publicly accessible
- Verify API key is valid

### Upload failures
- Check logs in `logs/` directory
- Verify website is accessible
- Try `--dry-run` first
- Check network connectivity

### Reset and retry
```bash
python automate_upload.py --reset-state
```

## ⚡ Performance

**Why direct streaming is better:**
- ✅ No disk space needed
- ✅ Faster (no download/upload cycle)
- ✅ Lower bandwidth (single transfer)
- ✅ Works on systems with limited storage
- ✅ Suitable for cloud environments

## 🔗 Links

- Website: https://ponyseeo.vercel.app
- Google Drive Folder: https://drive.google.com/drive/folders/1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf

---

Made with ❤️ for efficient video streaming
