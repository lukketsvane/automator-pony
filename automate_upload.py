#!/usr/bin/env python3
"""
Automate uploading video files from Google Drive to ponyseeo.vercel.app/upload
"""

import os
import re
import requests
from pathlib import Path
import gdown
import time
from typing import List, Dict
from bs4 import BeautifulSoup

# Configuration
GOOGLE_DRIVE_FOLDER_ID = "1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf"
UPLOAD_URL = "https://ponyseeo.vercel.app/upload"
UPLOAD_API_URL = "https://ponyseeo.vercel.app/api/upload"  # Common pattern
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
DOWNLOAD_DIR = "./downloaded_videos"

class DriveUploadAutomator:
    def __init__(self):
        self.session = requests.Session()
        self.downloaded_files = []

    def get_drive_files(self) -> List[Dict]:
        """
        Get list of all files from public Google Drive folder
        """
        print(f"📂 Fetching files from Google Drive folder...")

        # Use gdown to list files in the folder
        url = f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}"

        try:
            # Download folder contents
            gdown.download_folder(
                url=url,
                output=DOWNLOAD_DIR,
                quiet=False,
                use_cookies=False
            )

            # Get all video files from downloaded directory
            video_files = []
            download_path = Path(DOWNLOAD_DIR)

            if download_path.exists():
                for file_path in download_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                        video_files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'size': file_path.stat().st_size
                        })

            print(f"✅ Found {len(video_files)} video files")
            return video_files

        except Exception as e:
            print(f"❌ Error accessing Google Drive: {e}")
            return []

    def inspect_upload_form(self) -> Dict:
        """
        Inspect the upload page to understand the form structure
        """
        print(f"🔍 Inspecting upload form at {UPLOAD_URL}...")

        try:
            response = self.session.get(UPLOAD_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find form
            form = soup.find('form')
            if not form:
                print("⚠️  No form found on upload page")
                return {}

            # Extract form fields
            fields = {}
            for input_field in form.find_all(['input', 'textarea', 'select']):
                field_name = input_field.get('name')
                field_type = input_field.get('type', 'text')
                if field_name:
                    fields[field_name] = {
                        'type': field_type,
                        'required': input_field.get('required') is not None
                    }

            # Get form action
            form_action = form.get('action', '')
            form_method = form.get('method', 'post').upper()

            print(f"📋 Form fields found: {list(fields.keys())}")

            return {
                'action': form_action,
                'method': form_method,
                'fields': fields
            }

        except Exception as e:
            print(f"⚠️  Could not inspect form: {e}")
            return {}

    def upload_file(self, file_info: Dict, form_info: Dict = None) -> bool:
        """
        Upload a single video file to the website
        """
        file_path = file_info['path']
        file_name = file_info['name']

        print(f"\n📤 Uploading: {file_name}")

        try:
            # Try multiple upload strategies

            # Strategy 1: Multipart form upload to /api/upload
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'video/*')}

                # Add common form fields
                data = {
                    'title': Path(file_name).stem,
                    'description': f'Uploaded from Google Drive: {file_name}',
                }

                # Try API endpoint first
                try:
                    response = self.session.post(
                        UPLOAD_API_URL,
                        files=files,
                        data=data,
                        timeout=300  # 5 minutes timeout for large files
                    )

                    if response.status_code in [200, 201]:
                        print(f"✅ Successfully uploaded: {file_name}")
                        return True
                    else:
                        print(f"⚠️  API upload failed with status {response.status_code}")

                except Exception as e:
                    print(f"⚠️  API upload error: {e}")

            # Strategy 2: Try the main upload URL
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'video/*')}
                data = {
                    'title': Path(file_name).stem,
                    'description': f'Uploaded from Google Drive: {file_name}',
                }

                response = self.session.post(
                    UPLOAD_URL,
                    files=files,
                    data=data,
                    timeout=300
                )

                if response.status_code in [200, 201]:
                    print(f"✅ Successfully uploaded: {file_name}")
                    return True
                else:
                    print(f"❌ Upload failed with status {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    return False

        except Exception as e:
            print(f"❌ Error uploading {file_name}: {e}")
            return False

    def run(self):
        """
        Main automation workflow
        """
        print("🚀 Starting Google Drive to Website Upload Automation\n")

        # Step 1: Inspect upload form
        form_info = self.inspect_upload_form()

        # Step 2: Get files from Google Drive
        video_files = self.get_drive_files()

        if not video_files:
            print("❌ No video files found to upload")
            return

        # Step 3: Upload each file
        successful = 0
        failed = 0

        for i, file_info in enumerate(video_files, 1):
            print(f"\n[{i}/{len(video_files)}]")

            if self.upload_file(file_info, form_info):
                successful += 1
            else:
                failed += 1

            # Rate limiting - wait between uploads
            if i < len(video_files):
                time.sleep(2)

        # Summary
        print("\n" + "="*50)
        print(f"📊 Upload Summary:")
        print(f"   Total files: {len(video_files)}")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print("="*50)

if __name__ == "__main__":
    automator = DriveUploadAutomator()
    automator.run()
