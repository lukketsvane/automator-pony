#!/usr/bin/env python3
"""
Quick tool to inspect your upload page and find the correct API endpoint
"""

import requests
from bs4 import BeautifulSoup
import json
import re

UPLOAD_PAGE = "https://ponyseeo.vercel.app/upload"

def inspect_page():
    print("🔍 Inspecting your upload page...\n")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        # Fetch the page
        print(f"Fetching: {UPLOAD_PAGE}")
        response = session.get(UPLOAD_PAGE, timeout=30)
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Save HTML for manual inspection
        with open('upload_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("✅ Saved HTML to: upload_page.html\n")

        # Look for forms
        print("=" * 60)
        print("FORMS FOUND:")
        print("=" * 60)
        forms = soup.find_all('form')
        for idx, form in enumerate(forms, 1):
            print(f"\nForm #{idx}:")
            print(f"  Action: {form.get('action', 'N/A')}")
            print(f"  Method: {form.get('method', 'POST')}")
            print(f"  Enctype: {form.get('enctype', 'N/A')}")

            # Find file inputs
            file_inputs = form.find_all('input', {'type': 'file'})
            if file_inputs:
                print(f"  File inputs: {len(file_inputs)}")
                for fi in file_inputs:
                    print(f"    - name: {fi.get('name')}, accept: {fi.get('accept')}")

        # Look for API endpoints in scripts
        print("\n" + "=" * 60)
        print("POTENTIAL API ENDPOINTS:")
        print("=" * 60)

        endpoints = set()

        # Check script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for fetch/axios calls
                api_matches = re.findall(r'["\']([/\w]+/api/[^"\']+)["\']', script.string)
                endpoints.update(api_matches)

                # Look for action URLs
                action_matches = re.findall(r'action[:\s=]+["\']([^"\']+)["\']', script.string)
                endpoints.update(action_matches)

        # Check for data attributes
        for elem in soup.find_all(attrs={'data-endpoint': True}):
            endpoints.add(elem['data-endpoint'])

        for elem in soup.find_all(attrs={'data-api': True}):
            endpoints.add(elem['data-api'])

        if endpoints:
            for ep in sorted(endpoints):
                print(f"  {ep}")
        else:
            print("  No obvious endpoints found in JavaScript")

        # Look for Next.js API routes
        print("\n" + "=" * 60)
        print("COMMON VERCEL/NEXT.JS PATTERNS TO TRY:")
        print("=" * 60)
        possible_endpoints = [
            "/api/upload",
            "/api/files/upload",
            "/api/videos/upload",
            "/api/media/upload",
            "/api/upload-video",
            "/upload/api",
        ]
        for ep in possible_endpoints:
            print(f"  https://ponyseeo.vercel.app{ep}")

        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Check upload_page.html to see the form structure")
        print("2. Look in your browser's Network tab when uploading a file")
        print("3. Or share the HTML and I'll find the endpoint")
        print("\nTo test an endpoint manually:")
        print("  curl -X POST https://ponyseeo.vercel.app/api/upload \\")
        print("       -F 'file=@test.mp4'")

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Status Code: {e.response.status_code}")
        if e.response.status_code == 404:
            print("\nThe upload page might not exist at this URL.")
            print("Please verify: https://ponyseeo.vercel.app/upload")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_page()
