#!/usr/bin/env python3
"""
Direct Google Drive to Website Upload Automator
Streams video files directly from Google Drive to ponyseeo.vercel.app
without downloading to local storage - much faster and more efficient!
"""

import os
import sys
import json
import logging
import hashlib
import requests
from pathlib import Path
import time
from typing import List, Dict, Optional, Set, Generator
from datetime import datetime
from tqdm import tqdm
import argparse
from io import BytesIO

# HARDCODED CONFIGURATION
GOOGLE_DRIVE_FOLDER_ID = "1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf"
GOOGLE_DRIVE_API_KEY = "AIzaSyA-r4BkJ30DoyB7xALj3q-n1WTavtBYqRM"
UPLOAD_URL = "https://ponyseeo.vercel.app/upload"
UPLOAD_API_URL = "https://ponyseeo.vercel.app/api/upload"

# Google Drive API endpoints
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
DRIVE_FILES_LIST = f"{DRIVE_API_BASE}/files"
DRIVE_FILE_GET = f"{DRIVE_API_BASE}/files/{{file_id}}"

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.mpeg', '.mpg']
LOG_DIR = "./logs"
STATE_FILE = "./upload_state.json"
MAX_RETRIES = 3
RETRY_DELAY = 5
UPLOAD_TIMEOUT = 600
RATE_LIMIT_DELAY = 2

# Setup logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = os.path.join(LOG_DIR, f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class UploadState:
    """Manages upload state for resume capability"""

    def __init__(self, state_file: str = STATE_FILE):
        self.state_file = state_file
        self.uploaded_files: Set[str] = set()
        self.failed_files: Dict[str, str] = {}
        self.load_state()

    def load_state(self):
        """Load previous upload state"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.uploaded_files = set(data.get('uploaded', []))
                    self.failed_files = data.get('failed', {})
                logger.info(f"Loaded state: {len(self.uploaded_files)} uploaded, {len(self.failed_files)} failed")
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")

    def save_state(self):
        """Save current upload state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'uploaded': list(self.uploaded_files),
                    'failed': self.failed_files,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save state file: {e}")

    def mark_uploaded(self, file_id: str):
        """Mark file as successfully uploaded"""
        self.uploaded_files.add(file_id)
        if file_id in self.failed_files:
            del self.failed_files[file_id]
        self.save_state()

    def mark_failed(self, file_id: str, error: str):
        """Mark file as failed"""
        self.failed_files[file_id] = error
        self.save_state()

    def is_uploaded(self, file_id: str) -> bool:
        """Check if file was already uploaded"""
        return file_id in self.uploaded_files


class GoogleDriveUploader:
    def __init__(self, dry_run: bool = False):
        self.api_key = GOOGLE_DRIVE_API_KEY
        self.folder_id = GOOGLE_DRIVE_FOLDER_ID
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.state = UploadState()
        self.dry_run = dry_run

    def list_files_in_folder(self, folder_id: str, path: str = "") -> Generator[Dict, None, None]:
        """
        Recursively list all video files in a Google Drive folder and its subdirectories
        """
        logger.info(f"📂 Scanning folder: {path or 'root'}...")

        params = {
            'key': self.api_key,
            'q': f"'{folder_id}' in parents and trashed=false",
            'fields': 'files(id,name,mimeType,size,parents)',
            'pageSize': 1000
        }

        try:
            response = requests.get(DRIVE_FILES_LIST, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            files = data.get('files', [])
            logger.info(f"  Found {len(files)} items")

            for file in files:
                file_name = file['name']
                file_id = file['id']
                mime_type = file['mimeType']
                file_size = int(file.get('size', 0))

                # If it's a folder, recurse into it
                if mime_type == 'application/vnd.google-apps.folder':
                    logger.info(f"  📁 Entering subfolder: {file_name}")
                    new_path = f"{path}/{file_name}" if path else file_name
                    yield from self.list_files_in_folder(file_id, new_path)

                # If it's a video file, yield it
                else:
                    file_ext = Path(file_name).suffix.lower()
                    if file_ext in VIDEO_EXTENSIONS:
                        yield {
                            'id': file_id,
                            'name': file_name,
                            'size': file_size,
                            'path': f"{path}/{file_name}" if path else file_name,
                            'mime_type': mime_type
                        }

        except Exception as e:
            logger.error(f"Error listing files in folder {folder_id}: {e}")

    def get_all_videos(self) -> List[Dict]:
        """Get all video files from the Google Drive folder (including subdirectories)"""
        logger.info(f"🔍 Fetching all videos from Google Drive folder...")
        logger.info(f"Folder ID: {self.folder_id}\n")

        videos = list(self.list_files_in_folder(self.folder_id))

        logger.info(f"\n✅ Found {len(videos)} video files total")

        # Sort by size (smallest first)
        videos.sort(key=lambda x: x['size'])

        return videos

    def stream_file_from_drive(self, file_id: str) -> requests.Response:
        """
        Get a streaming response for a file from Google Drive
        This allows us to stream directly to the upload endpoint without downloading
        """
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={self.api_key}"

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        return response

    def detect_api_endpoints(self) -> List[str]:
        """Detect possible API endpoints"""
        endpoints = [
            UPLOAD_API_URL,
            UPLOAD_URL,
            "https://ponyseeo.vercel.app/api/videos/upload",
            "https://ponyseeo.vercel.app/api/media/upload",
        ]
        return endpoints

    def upload_file_with_retry(self, file_info: Dict) -> bool:
        """Upload a single file with retry logic"""
        file_id = file_info['id']
        file_name = file_info['name']
        file_path = file_info['path']

        # Check if already uploaded
        if self.state.is_uploaded(file_id):
            logger.info(f"⏭️  Skipping {file_name} (already uploaded)")
            return True

        if self.dry_run:
            logger.info(f"🔍 [DRY RUN] Would upload: {file_path} ({file_info['size']} bytes)")
            return True

        logger.info(f"📤 Uploading: {file_path} ({file_info['size'] / (1024*1024):.2f} MB)")

        # Try upload with retries
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if self.upload_file_direct(file_info):
                    self.state.mark_uploaded(file_id)
                    logger.info(f"✅ Successfully uploaded: {file_name}")
                    return True
                else:
                    if attempt < MAX_RETRIES:
                        wait_time = RETRY_DELAY * attempt
                        logger.warning(f"⚠️  Upload failed, retrying in {wait_time}s (attempt {attempt}/{MAX_RETRIES})")
                        time.sleep(wait_time)

            except Exception as e:
                logger.error(f"❌ Error on attempt {attempt}/{MAX_RETRIES}: {e}")
                if attempt < MAX_RETRIES:
                    wait_time = RETRY_DELAY * attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        # All retries failed
        error_msg = f"Failed after {MAX_RETRIES} attempts"
        self.state.mark_failed(file_id, error_msg)
        logger.error(f"❌ Failed to upload {file_name}: {error_msg}")
        return False

    def upload_file_direct(self, file_info: Dict) -> bool:
        """
        Upload file by streaming directly from Google Drive to website
        No local download required!
        """
        file_id = file_info['id']
        file_name = file_info['name']
        file_path = file_info['path']

        # Get streaming response from Google Drive
        logger.debug(f"Streaming file from Google Drive: {file_id}")

        try:
            # Stream the file from Google Drive
            drive_response = self.stream_file_from_drive(file_id)

            # Prepare upload data
            file_stem = Path(file_name).stem
            data = {
                'title': file_stem,
                'description': f'Uploaded from Google Drive: {file_path}',
                'tags': 'google-drive,automated-upload',
            }

            # Try each endpoint
            endpoints = self.detect_api_endpoints()

            for endpoint in endpoints:
                try:
                    logger.debug(f"Trying endpoint: {endpoint}")

                    # Create file-like object from streamed content
                    # We need to read the content for each attempt
                    file_content = drive_response.content

                    files = {
                        'file': (file_name, BytesIO(file_content), f'video/{Path(file_name).suffix[1:]}')
                    }

                    response = self.session.post(
                        endpoint,
                        files=files,
                        data=data,
                        timeout=UPLOAD_TIMEOUT
                    )

                    logger.debug(f"Response status: {response.status_code}")

                    if response.status_code in [200, 201, 202]:
                        logger.info(f"✅ Upload succeeded via {endpoint}")
                        return True
                    elif response.status_code == 413:
                        logger.error(f"File too large for endpoint {endpoint}")
                        continue
                    elif response.status_code >= 500:
                        logger.warning(f"Server error on {endpoint}: {response.status_code}")
                        continue
                    else:
                        logger.warning(f"Upload to {endpoint} returned {response.status_code}: {response.text[:200]}")

                except requests.exceptions.Timeout:
                    logger.warning(f"Timeout on endpoint {endpoint}")
                    continue
                except Exception as e:
                    logger.debug(f"Error with endpoint {endpoint}: {e}")
                    continue

            return False

        except Exception as e:
            logger.error(f"Error streaming file: {e}")
            return False

    def run(self):
        """Main automation workflow"""
        logger.info("="*70)
        logger.info("🚀 Direct Google Drive to Website Upload Automator")
        logger.info("="*70)
        logger.info(f"📁 Google Drive Folder: {self.folder_id}")
        logger.info(f"🌐 Upload URL: {UPLOAD_URL}")
        logger.info(f"🔑 API Key: {self.api_key[:10]}...{self.api_key[-5:]}")
        logger.info("="*70)

        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No actual uploads will be performed\n")

        # Get all videos from Google Drive (including subdirectories)
        logger.info("\n📂 Step 1: Fetching videos from Google Drive (including subdirectories)...")
        video_files = self.get_all_videos()

        if not video_files:
            logger.error("❌ No video files found to upload")
            return

        # Filter out already uploaded files
        pending_files = [f for f in video_files if not self.state.is_uploaded(f['id'])]

        logger.info(f"\n📊 Files to process:")
        logger.info(f"   Total videos found: {len(video_files)}")
        logger.info(f"   Already uploaded: {len(video_files) - len(pending_files)}")
        logger.info(f"   Pending upload: {len(pending_files)}")

        if not pending_files:
            logger.info("✅ All files already uploaded!")
            return

        # Show directory structure
        logger.info(f"\n📁 Directory structure:")
        paths = set()
        for f in pending_files:
            path = str(Path(f['path']).parent)
            if path and path != '.':
                paths.add(path)

        if paths:
            for path in sorted(paths):
                count = sum(1 for f in pending_files if str(Path(f['path']).parent) == path)
                logger.info(f"   {path}: {count} videos")
        else:
            logger.info(f"   Root folder: {len(pending_files)} videos")

        # Upload each file
        logger.info(f"\n📤 Step 2: Uploading {len(pending_files)} files (streaming directly)...")

        successful = 0
        failed = 0
        start_time = time.time()

        with tqdm(total=len(pending_files), desc="Uploading", unit="file") as pbar:
            for i, file_info in enumerate(pending_files, 1):
                logger.info(f"\n[{i}/{len(pending_files)}] {file_info['path']}")

                if self.upload_file_with_retry(file_info):
                    successful += 1
                else:
                    failed += 1

                pbar.update(1)

                # Rate limiting
                if i < len(pending_files) and not self.dry_run:
                    time.sleep(RATE_LIMIT_DELAY)

        elapsed_time = time.time() - start_time

        # Summary
        logger.info("\n" + "="*70)
        logger.info("📊 UPLOAD SUMMARY")
        logger.info("="*70)
        logger.info(f"   Total files:     {len(pending_files)}")
        logger.info(f"   ✅ Successful:   {successful}")
        logger.info(f"   ❌ Failed:       {failed}")
        logger.info(f"   ⏱️  Time taken:   {elapsed_time/60:.2f} minutes")
        logger.info(f"   📁 Log file:     {log_file}")
        logger.info("="*70)

        if failed > 0:
            logger.warning(f"\n⚠️  {failed} files failed to upload. Check the log for details.")
            logger.info("You can re-run the script to retry failed uploads.")


def main():
    parser = argparse.ArgumentParser(
        description='Direct upload from Google Drive to website (no local download)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without actually uploading files'
    )
    parser.add_argument(
        '--reset-state',
        action='store_true',
        help='Reset upload state and start fresh'
    )

    args = parser.parse_args()

    if args.reset_state:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            logger.info("✅ Upload state reset")

    uploader = GoogleDriveUploader(dry_run=args.dry_run)
    uploader.run()


if __name__ == "__main__":
    main()
