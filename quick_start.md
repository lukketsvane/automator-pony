# 🚀 Quick Start Guide

## Installation & First Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test First (Recommended)
```bash
python automate_upload.py --dry-run
```

This will:
- ✅ Scan your Google Drive folder (including subdirectories)
- ✅ Show you what would be uploaded
- ❌ NOT actually upload anything

### Step 3: Run for Real
```bash
python automate_upload.py
```

Watch the magic happen! 🎉

## What to Expect

### First Run Output:
```
🚀 Direct Google Drive to Website Upload Automator
======================================================================
📁 Google Drive Folder: 1pWTzEYJQh5hl63IDsz34mUrDO7_Aygtf
🌐 Upload URL: https://ponyseeo.vercel.app/upload
======================================================================

📂 Step 1: Fetching videos from Google Drive (including subdirectories)...
📂 Scanning folder: root...
  Found 15 items
  📁 Entering subfolder: FolderA
  📁 Entering subfolder: FolderB

✅ Found 28 video files total

📊 Files to process:
   Total videos found: 28
   Already uploaded: 0
   Pending upload: 28

📁 Directory structure:
   FolderA: 12 videos
   FolderB: 8 videos
   FolderB/Subfolder: 6 videos
   Root folder: 2 videos

📤 Step 2: Uploading 28 files (streaming directly)...

[1/28] FolderA/video1.mp4
📤 Uploading: FolderA/video1.mp4 (15.23 MB)
✅ Successfully uploaded: video1.mp4

[2/28] FolderA/video2.mp4
📤 Uploading: FolderA/video2.mp4 (22.45 MB)
✅ Successfully uploaded: video2.mp4
...
```

## Common Scenarios

### Script Gets Interrupted?
No problem! Just run it again:
```bash
python automate_upload.py
```

It will:
- ✅ Skip already uploaded files
- ✅ Continue from where it stopped
- ✅ Retry previously failed uploads

### Want to Start Over Completely?
```bash
python automate_upload.py --reset-state
```

This forgets all previous uploads and starts fresh.

### Check What's Been Uploaded?
Look at the state file:
```bash
cat upload_state.json
```

### Check the Logs?
```bash
ls logs/
cat logs/upload_*.log | tail -50
```

## Understanding the Output

- 📂 **Blue folder icon** = Scanning directory
- 📤 **Upload arrow** = Currently uploading
- ✅ **Green checkmark** = Success
- ❌ **Red X** = Failed (will retry)
- ⏭️ **Skip icon** = Already uploaded (skipping)

## Troubleshooting

### "No videos found"
- Check that your Google Drive folder contains video files
- Verify the folder is publicly accessible
- Supported formats: .mp4, .avi, .mov, .mkv, .webm, .flv, .wmv, .m4v, .3gp, .mpeg, .mpg

### "API error" or "403 Forbidden"
- API key may be invalid
- Check folder permissions
- Verify folder ID is correct

### Uploads failing
1. Run with `--dry-run` first to test
2. Check the logs in `logs/` directory
3. Verify the website is accessible
4. Try uploading just one file manually to test

### Script is slow
- This is normal for large files
- Direct streaming is still faster than download→upload
- Check your internet connection speed

## Advanced Usage

### Integration with Cron (Linux/Mac)
Run automatically every day at 2 AM:
```bash
crontab -e
# Add this line:
0 2 * * * cd /path/to/automator-pony && /usr/bin/python3 automate_upload.py
```

### Integration with Task Scheduler (Windows)
Create a scheduled task to run `automate_upload.py` daily.

### GitHub Actions
The included workflow file automatically runs the script daily when pushed to GitHub.

## Tips for Success

1. **Test with `--dry-run` first** - Always a good idea!
2. **Check logs if something fails** - They're detailed and helpful
3. **Don't interrupt during upload** - Let files finish uploading
4. **Re-run if interrupted** - The script handles it gracefully
5. **Monitor the first few uploads** - Make sure everything works

## Need Help?

1. Check the main `README.md`
2. Review the logs in `logs/`
3. Run with `--dry-run` to test
4. Check your Google Drive folder permissions

---

Happy uploading! 🎬
