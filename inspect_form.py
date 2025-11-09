#!/usr/bin/env python3
"""
Form Inspector - Analyzes your upload page to understand its structure
Run this first to see what fields your form expects
"""

import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint

UPLOAD_URL = "https://ponyseeo.vercel.app/upload"

def inspect_upload_page():
    """Inspect the upload page and extract all relevant information"""

    print("🔍 Inspecting upload page...")
    print(f"URL: {UPLOAD_URL}\n")

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        response = session.get(UPLOAD_URL, timeout=30)
        response.raise_for_status()

        print(f"✅ Page loaded successfully (Status: {response.status_code})\n")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Save full HTML for inspection
        with open('upload_page.html', 'w') as f:
            f.write(response.text)
        print("💾 Saved full HTML to: upload_page.html\n")

        # Find all forms
        forms = soup.find_all('form')
        print(f"📋 Found {len(forms)} form(s)\n")

        for idx, form in enumerate(forms, 1):
            print(f"{'='*60}")
            print(f"FORM #{idx}")
            print(f"{'='*60}")

            # Form attributes
            print(f"Action: {form.get('action', 'N/A')}")
            print(f"Method: {form.get('method', 'N/A')}")
            print(f"Enctype: {form.get('enctype', 'N/A')}")
            print(f"ID: {form.get('id', 'N/A')}")
            print(f"Class: {form.get('class', 'N/A')}\n")

            # Find all input fields
            fields = []
            for field in form.find_all(['input', 'textarea', 'select', 'button']):
                field_info = {
                    'tag': field.name,
                    'name': field.get('name'),
                    'type': field.get('type', 'text'),
                    'id': field.get('id'),
                    'required': field.get('required') is not None,
                    'placeholder': field.get('placeholder'),
                    'accept': field.get('accept'),
                    'value': field.get('value'),
                }
                fields.append(field_info)

            print("📝 Form Fields:")
            for field in fields:
                print(f"  - {field['name'] or field['id'] or 'unnamed'}")
                print(f"    Type: {field['type']}")
                if field['required']:
                    print(f"    ⚠️  REQUIRED")
                if field['placeholder']:
                    print(f"    Placeholder: {field['placeholder']}")
                if field['accept']:
                    print(f"    Accepts: {field['accept']}")
                print()

            # Save as JSON
            with open(f'form_{idx}_fields.json', 'w') as f:
                json.dump(fields, f, indent=2)
            print(f"💾 Saved form fields to: form_{idx}_fields.json\n")

        # Look for API endpoints in script tags
        print(f"{'='*60}")
        print("🔌 Looking for API endpoints in JavaScript...")
        print(f"{'='*60}")

        scripts = soup.find_all('script')
        api_patterns = [
            'api/upload',
            '/upload',
            'endpoint',
            'action',
            'fetch(',
            'axios.',
            'post('
        ]

        found_endpoints = set()
        for script in scripts:
            script_text = script.string or ''
            for pattern in api_patterns:
                if pattern in script_text.lower():
                    # Try to extract the line
                    lines = script_text.split('\n')
                    for line in lines:
                        if pattern in line.lower():
                            line = line.strip()
                            if len(line) < 200:  # Don't print huge lines
                                found_endpoints.add(line)

        if found_endpoints:
            print("Found potential API endpoints/calls:")
            for endpoint in list(found_endpoints)[:10]:
                print(f"  {endpoint}")
        else:
            print("No obvious API endpoints found in JavaScript")

        print(f"\n{'='*60}")
        print("✅ Inspection complete!")
        print(f"{'='*60}")
        print("\nFiles created:")
        print("  - upload_page.html (full HTML)")
        print("  - form_*_fields.json (form field details)")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        print("\nTroubleshooting:")
        print("1. Check if the URL is accessible in your browser")
        print("2. Check if you need authentication/login")
        print("3. Check if there's CAPTCHA or bot protection")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_upload_page()
