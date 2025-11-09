# Google Drive to Website Upload Automator

Automates uploading video files from a Google Drive folder to ponyseeo.vercel.app/upload

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the automation script:
```bash
python automate_upload.py
```

The script will:
1. Download all video files from the Google Drive folder (including subdirectories)
2. Inspect the upload form on your website
3. Upload each video file to your site
4. Show a summary of successful and failed uploads

## Supported Video Formats

- .mp4
- .avi
- .mov
- .mkv
- .webm
- .flv
- .wmv
- .m4v

## Configuration

Edit `automate_upload.py` to customize:
- `GOOGLE_DRIVE_FOLDER_ID`: The Google Drive folder ID
- `UPLOAD_URL`: The upload page URL
- `VIDEO_EXTENSIONS`: Supported video file extensions
