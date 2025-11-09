# 🚀 Quick Start Guide

## Step 1: Inspect Your Upload Form

First, let's understand what your upload form expects:

```bash
python inspect_form.py
```

This will create:
- `upload_page.html` - Full HTML of your upload page
- `form_*_fields.json` - Detailed field information

**Check the output** to see what fields are required!

## Step 2: Test with Dry Run

Before uploading anything, test the automation:

```bash
python automate_upload.py --dry-run
```

This will:
- Download files from Google Drive
- Show what would be uploaded
- NOT actually upload anything

## Step 3: Run the Real Upload

Once you're confident it's working:

```bash
python automate_upload.py
```

Watch the progress! The script will:
- ✅ Track each successful upload
- ♻️ Retry failures automatically
- 💾 Save state so you can resume later
- 📝 Log everything to `logs/` directory

## Step 4: Check Results

After completion:
- Check the summary output
- Review logs in `logs/upload_*.log`
- Check `upload_state.json` to see what was uploaded

## If Something Goes Wrong

### Script crashed or stopped?
Just re-run it - it will resume from where it left off:
```bash
python automate_upload.py
```

### Want to start over?
Reset the state and try again:
```bash
python automate_upload.py --reset-state
```

### Already have the videos downloaded?
Skip the download step:
```bash
python automate_upload.py --skip-download
```

### Need more details?
Check the log files:
```bash
cat logs/upload_*.log | tail -50
```

## Customizing the Upload

If the form fields don't match, edit `automate_upload.py` around line 250-280 (the `build_upload_data` function) to match your form's expected fields.

Common fields:
- `title` - Video title
- `description` - Video description
- `file` - The video file itself
- `tags` - Tags or categories
- `category` - Content category

## Automation with GitHub Actions

After your first successful run, you can set up automated uploads:

1. Push this code to GitHub
2. Go to Actions tab
3. Enable workflows
4. The script will run daily at 2 AM UTC automatically!

Or trigger manually from the Actions tab.

---

**Need help?** Check the main README.md or the logs!
