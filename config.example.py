"""
Configuration file for Google Drive Upload Automator
Copy this to config.py and customize as needed
"""

# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID = "1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf"
GOOGLE_DRIVE_URL = f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}"

# Website Configuration
UPLOAD_URL = "https://ponyseeo.vercel.app/upload"
UPLOAD_API_URL = "https://ponyseeo.vercel.app/api/upload"

# Additional API endpoints to try (in order)
ADDITIONAL_ENDPOINTS = [
    "https://ponyseeo.vercel.app/api/videos/upload",
    "https://ponyseeo.vercel.app/api/media/upload",
]

# Video file extensions to process
VIDEO_EXTENSIONS = [
    '.mp4', '.avi', '.mov', '.mkv', '.webm',
    '.flv', '.wmv', '.m4v', '.3gp', '.mpeg', '.mpg'
]

# Directory Configuration
DOWNLOAD_DIR = "./downloaded_videos"
LOG_DIR = "./logs"
STATE_FILE = "./upload_state.json"

# Upload Configuration
MAX_RETRIES = 3              # Number of retry attempts per file
RETRY_DELAY = 5              # Base delay between retries (seconds)
UPLOAD_TIMEOUT = 600         # Upload timeout (seconds) - 10 minutes
RATE_LIMIT_DELAY = 2         # Delay between uploads (seconds)
MAX_PARALLEL_DOWNLOADS = 3   # Max parallel downloads from Google Drive

# Logging Configuration
LOG_LEVEL = "INFO"           # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Form Field Mappings
# Customize these based on your upload form fields
FORM_FIELD_MAPPINGS = {
    'title': lambda filename: Path(filename).stem,
    'description': lambda filename: f'Video uploaded from Google Drive: {filename}',
    'tags': lambda filename: 'google-drive,automated-upload',
    'category': lambda filename: 'video',
}

# User Agent for HTTP requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
