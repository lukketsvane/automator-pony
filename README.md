# 🎬 Google Drive to Website Upload Automator

Professional automation tool for uploading video files from Google Drive to ponyseeo.vercel.app with advanced features like retry logic, progress tracking, resume capability, and comprehensive logging.

## ✨ Features

- 📂 **Recursive folder scanning** - Automatically finds all videos in folders and subfolders
- 🔄 **Resume capability** - Tracks uploaded files and resumes from where it left off
- ♻️ **Automatic retry logic** - Retries failed uploads up to 3 times with exponential backoff
- 📊 **Progress tracking** - Real-time progress bars and detailed logging
- 🎯 **Smart endpoint detection** - Tries multiple API endpoints automatically
- 📝 **Comprehensive logging** - Detailed logs saved to `logs/` directory
- 🔍 **Dry run mode** - Test the automation without actually uploading
- ⚡ **Skip download mode** - Reuse already downloaded files
- 🎨 **Beautiful console output** - Clear progress indicators and status messages
- 🔐 **File hash tracking** - Uses SHA-256 hashing to track uploaded files reliably

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Automation

```bash
# Basic usage - download and upload all videos
python automate_upload.py

# Dry run - see what would be uploaded without actually uploading
python automate_upload.py --dry-run

# Skip download - use already downloaded files
python automate_upload.py --skip-download

# Reset state and start fresh
python automate_upload.py --reset-state
```

## 📋 Command Line Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Perform a dry run without actually uploading files |
| `--skip-download` | Skip downloading from Google Drive, use existing files |
| `--parallel` | Enable parallel uploads (experimental) |
| `--reset-state` | Reset upload state and start fresh |

## 📁 File Structure

```
automator-pony/
├── automate_upload.py       # Main automation script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
├── downloaded_videos/       # Downloaded videos (created automatically)
├── logs/                    # Upload logs (created automatically)
└── upload_state.json        # Upload state tracking (created automatically)
```

## 🎯 Supported Video Formats

- `.mp4` - MPEG-4 Video
- `.avi` - Audio Video Interleave
- `.mov` - QuickTime Movie
- `.mkv` - Matroska Video
- `.webm` - WebM Video
- `.flv` - Flash Video
- `.wmv` - Windows Media Video
- `.m4v` - iTunes Video
- `.3gp` - 3GPP Video
- `.mpeg` / `.mpg` - MPEG Video

## 🔧 Configuration

Edit the following constants in `automate_upload.py` to customize:

```python
GOOGLE_DRIVE_FOLDER_ID = "1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf"
UPLOAD_URL = "https://ponyseeo.vercel.app/upload"
UPLOAD_API_URL = "https://ponyseeo.vercel.app/api/upload"
MAX_RETRIES = 3                # Number of retry attempts
RETRY_DELAY = 5                # Seconds between retries
UPLOAD_TIMEOUT = 600           # Upload timeout in seconds
RATE_LIMIT_DELAY = 2           # Delay between uploads
```

## 📊 How It Works

1. **Form Inspection** - Analyzes the upload page to understand form structure
2. **Download Files** - Downloads all videos from Google Drive folder (including subdirectories)
3. **Hash Calculation** - Calculates SHA-256 hash for each file to track uploads
4. **Upload Process**:
   - Checks if file was already uploaded (via hash)
   - Tries multiple API endpoints automatically
   - Retries failed uploads with exponential backoff
   - Saves state after each upload
5. **Summary Report** - Shows detailed statistics and saves to log file

## 🔄 Resume Capability

The script automatically tracks which files have been uploaded in `upload_state.json`. If the script is interrupted or fails, simply re-run it and it will:

- Skip already uploaded files
- Retry previously failed uploads
- Continue from where it left off

## 📝 Logs

All uploads are logged to `logs/upload_YYYYMMDD_HHMMSS.log` with:
- Timestamp for each operation
- Success/failure status
- Error messages and stack traces
- API endpoint attempts
- Upload statistics

## 🐛 Troubleshooting

### No videos found
- Check that your Google Drive folder is publicly accessible
- Verify the folder ID in the script
- Ensure video files have supported extensions

### Upload failures
- Check the log file in `logs/` for detailed error messages
- Verify your website is accessible
- Try running with `--dry-run` first to test
- Check network connectivity

### Reset and start over
```bash
python automate_upload.py --reset-state
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📜 License

MIT License - feel free to use and modify as needed.

## 🔗 Links

- Website: https://ponyseeo.vercel.app
- Google Drive Folder: https://drive.google.com/drive/folders/1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf

---

Made with ❤️ for automated video uploads
