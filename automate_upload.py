#!/usr/bin/env python3
"""
Advanced Google Drive to Website Upload Automator
Uploads video files from Google Drive to ponyseeo.vercel.app with retry logic,
progress tracking, logging, and resume capability.
"""

import os
import sys
import json
import logging
import hashlib
import requests
from pathlib import Path
import gdown
import time
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argparse

# Configuration
GOOGLE_DRIVE_FOLDER_ID = "1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf"
UPLOAD_URL = "https://ponyseeo.vercel.app/upload"
UPLOAD_API_URL = "https://ponyseeo.vercel.app/api/upload"
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.mpeg', '.mpg']
DOWNLOAD_DIR = "./downloaded_videos"
LOG_DIR = "./logs"
STATE_FILE = "./upload_state.json"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
UPLOAD_TIMEOUT = 600  # 10 minutes
RATE_LIMIT_DELAY = 2  # seconds between uploads
MAX_PARALLEL_DOWNLOADS = 3

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

    def mark_uploaded(self, file_hash: str):
        """Mark file as successfully uploaded"""
        self.uploaded_files.add(file_hash)
        if file_hash in self.failed_files:
            del self.failed_files[file_hash]
        self.save_state()

    def mark_failed(self, file_hash: str, error: str):
        """Mark file as failed"""
        self.failed_files[file_hash] = error
        self.save_state()

    def is_uploaded(self, file_hash: str) -> bool:
        """Check if file was already uploaded"""
        return file_hash in self.uploaded_files


class DriveUploadAutomator:
    def __init__(self, dry_run: bool = False, skip_download: bool = False, parallel: bool = False):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.state = UploadState()
        self.dry_run = dry_run
        self.skip_download = skip_download
        self.parallel = parallel
        self.form_info = None

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Get SHA256 hash of file for tracking"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_drive_files(self) -> List[Dict]:
        """Download and catalog all video files from Google Drive folder"""
        logger.info(f"📂 Fetching files from Google Drive folder...")

        url = f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}"
        video_files = []

        try:
            if not self.skip_download:
                logger.info("Downloading files from Google Drive...")
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)

                # Download folder contents with progress
                gdown.download_folder(
                    url=url,
                    output=DOWNLOAD_DIR,
                    quiet=False,
                    use_cookies=False,
                    remaining_ok=True
                )
            else:
                logger.info("Skipping download, using existing files...")

            # Catalog all video files
            download_path = Path(DOWNLOAD_DIR)

            if download_path.exists():
                all_files = list(download_path.rglob('*'))
                logger.info(f"Scanning {len(all_files)} files for videos...")

                for file_path in all_files:
                    if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                        file_hash = self.get_file_hash(str(file_path))
                        video_files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'size': file_path.stat().st_size,
                            'hash': file_hash,
                            'relative_path': str(file_path.relative_to(download_path))
                        })

            logger.info(f"✅ Found {len(video_files)} video files")

            # Sort by size (smallest first for faster initial uploads)
            video_files.sort(key=lambda x: x['size'])

            return video_files

        except Exception as e:
            logger.error(f"❌ Error accessing Google Drive: {e}", exc_info=True)
            return []

    def inspect_upload_form(self) -> Dict:
        """Inspect the upload page to understand the form structure"""
        if self.form_info:
            return self.form_info

        logger.info(f"🔍 Inspecting upload form at {UPLOAD_URL}...")

        try:
            response = self.session.get(UPLOAD_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find form
            form = soup.find('form')
            fields = {}
            form_action = ''
            form_method = 'POST'

            if form:
                # Extract form fields
                for input_field in form.find_all(['input', 'textarea', 'select']):
                    field_name = input_field.get('name')
                    field_type = input_field.get('type', 'text')
                    if field_name:
                        fields[field_name] = {
                            'type': field_type,
                            'required': input_field.get('required') is not None,
                            'id': input_field.get('id', ''),
                            'accept': input_field.get('accept', '')
                        }

                # Get form action
                form_action = form.get('action', '')
                form_method = form.get('method', 'post').upper()

                logger.info(f"📋 Form fields found: {list(fields.keys())}")
            else:
                logger.warning("⚠️  No traditional form found, will try API endpoints")

            self.form_info = {
                'action': form_action,
                'method': form_method,
                'fields': fields
            }

            return self.form_info

        except Exception as e:
            logger.warning(f"⚠️  Could not inspect form: {e}")
            return {'action': '', 'method': 'POST', 'fields': {}}

    def detect_api_endpoints(self) -> List[str]:
        """Detect possible API endpoints from the page"""
        endpoints = [
            UPLOAD_API_URL,
            f"{UPLOAD_URL}/api/upload",
            f"{UPLOAD_URL.rsplit('/', 1)[0]}/api/upload",
            "https://ponyseeo.vercel.app/api/videos/upload",
            "https://ponyseeo.vercel.app/api/media/upload"
        ]

        # Add form action if available
        if self.form_info and self.form_info.get('action'):
            action = self.form_info['action']
            if action.startswith('/'):
                base_url = '/'.join(UPLOAD_URL.split('/')[:3])
                endpoints.insert(0, base_url + action)
            elif action.startswith('http'):
                endpoints.insert(0, action)

        return list(dict.fromkeys(endpoints))  # Remove duplicates while preserving order

    def build_upload_data(self, file_name: str, file_path: str) -> Dict:
        """Build upload data based on detected form fields"""
        data = {}

        # Get the file stem (name without extension)
        file_stem = Path(file_name).stem

        # Common field mappings
        field_mappings = {
            'title': file_stem,
            'name': file_stem,
            'filename': file_name,
            'description': f'Video uploaded from Google Drive',
            'tags': 'google-drive,automated-upload',
            'category': 'video',
            'type': 'video'
        }

        # Use detected form fields or common defaults
        if self.form_info and self.form_info.get('fields'):
            for field_name, field_info in self.form_info['fields'].items():
                if field_info['type'] != 'file' and field_name in field_mappings:
                    data[field_name] = field_mappings[field_name]
        else:
            # Use common defaults
            data = {
                'title': file_stem,
                'description': f'Video uploaded from Google Drive'
            }

        return data

    def upload_file_with_retry(self, file_info: Dict) -> bool:
        """Upload a single file with retry logic"""
        file_path = file_info['path']
        file_name = file_info['name']
        file_hash = file_info['hash']

        # Check if already uploaded
        if self.state.is_uploaded(file_hash):
            logger.info(f"⏭️  Skipping {file_name} (already uploaded)")
            return True

        if self.dry_run:
            logger.info(f"🔍 [DRY RUN] Would upload: {file_name} ({file_info['size']} bytes)")
            return True

        logger.info(f"📤 Uploading: {file_name} ({file_info['size'] / (1024*1024):.2f} MB)")

        # Try upload with retries
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if self.upload_file_attempt(file_info):
                    self.state.mark_uploaded(file_hash)
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
        self.state.mark_failed(file_hash, error_msg)
        logger.error(f"❌ Failed to upload {file_name}: {error_msg}")
        return False

    def upload_file_attempt(self, file_info: Dict) -> bool:
        """Single upload attempt to the website"""
        file_path = file_info['path']
        file_name = file_info['name']

        # Prepare upload data
        data = self.build_upload_data(file_name, file_path)

        # Try multiple endpoints
        endpoints = self.detect_api_endpoints()

        for endpoint in endpoints:
            try:
                with open(file_path, 'rb') as f:
                    files = {
                        'file': (file_name, f, f'video/{Path(file_name).suffix[1:]}'),
                    }

                    logger.debug(f"Trying endpoint: {endpoint}")
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

    def run(self):
        """Main automation workflow"""
        logger.info("="*70)
        logger.info("🚀 Google Drive to Website Upload Automator")
        logger.info("="*70)

        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No actual uploads will be performed")

        # Step 1: Inspect upload form
        logger.info("\n📋 Step 1: Inspecting upload form...")
        self.inspect_upload_form()

        # Step 2: Get files from Google Drive
        logger.info("\n📂 Step 2: Fetching video files...")
        video_files = self.get_drive_files()

        if not video_files:
            logger.error("❌ No video files found to upload")
            return

        # Filter out already uploaded files
        pending_files = [f for f in video_files if not self.state.is_uploaded(f['hash'])]

        logger.info(f"\n📊 Files to process:")
        logger.info(f"   Total videos found: {len(video_files)}")
        logger.info(f"   Already uploaded: {len(video_files) - len(pending_files)}")
        logger.info(f"   Pending upload: {len(pending_files)}")

        if not pending_files:
            logger.info("✅ All files already uploaded!")
            return

        # Step 3: Upload each file
        logger.info(f"\n📤 Step 3: Uploading {len(pending_files)} files...")

        successful = 0
        failed = 0
        start_time = time.time()

        with tqdm(total=len(pending_files), desc="Uploading", unit="file") as pbar:
            for i, file_info in enumerate(pending_files, 1):
                logger.info(f"\n[{i}/{len(pending_files)}] Processing: {file_info['name']}")

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
        description='Automate uploading videos from Google Drive to website'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without actually uploading files'
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Skip downloading from Google Drive, use existing files'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel uploads (experimental)'
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

    automator = DriveUploadAutomator(
        dry_run=args.dry_run,
        skip_download=args.skip_download,
        parallel=args.parallel
    )
    automator.run()


if __name__ == "__main__":
    main()
