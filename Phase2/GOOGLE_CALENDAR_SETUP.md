# Google Calendar Setup Guide

Complete guide to setting up Google Calendar integration for Phase 2.

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter project name: "Appointment Agent" (or your choice)
5. Click "Create"
6. Wait for project creation (~30 seconds)

### 2. Enable Google Calendar API

1. In the Google Cloud Console, make sure your new project is selected
2. Click the hamburger menu (☰) → "APIs & Services" → "Library"
3. Search for "Google Calendar API"
4. Click on "Google Calendar API" in results
5. Click "Enable"
6. Wait for API to enable (~10 seconds)

### 3. Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" at the top
3. Select "Service Account"
4. Fill in details:
   - **Service account name**: `appointment-agent`
   - **Service account ID**: (auto-filled, e.g., `appointment-agent@...`)
   - **Description**: "Service account for appointment scheduling agent"
5. Click "Create and Continue"
6. Skip "Grant this service account access to project" (optional)
7. Click "Continue"
8. Skip "Grant users access to this service account" (optional)
9. Click "Done"

### 4. Create and Download Key

1. You'll see your service account in the credentials list
2. Click on the service account email (e.g., `appointment-agent@...iam.gserviceaccount.com`)
3. Go to the "Keys" tab
4. Click "Add Key" → "Create New Key"
5. Select "JSON" format
6. Click "Create"
7. A JSON file will download automatically
8. **Important**: Save this file securely. You cannot download it again!

### 5. Move Key to Project

```bash
# Create credentials directory if it doesn't exist
mkdir -p Phase2/credentials

# Move the downloaded JSON file
mv ~/Downloads/appointment-agent-*.json Phase2/credentials/google-calendar-service-account.json

# Verify it's there
ls -l Phase2/credentials/
```

### 6. Share Your Calendar with Service Account

**This is critical** - the service account needs permission to access your calendar.

1. Open [Google Calendar](https://calendar.google.com)
2. On the left sidebar, find the calendar you want to use
3. Click the three dots (⋮) next to the calendar name
4. Select "Settings and sharing"
5. Scroll down to "Share with specific people"
6. Click "+ Add people"
7. **Enter the service account email**:
   - Find this in the downloaded JSON file: look for `"client_email"`
   - Or find it in Google Cloud Console → Service Accounts
   - Example: `appointment-agent@your-project.iam.gserviceaccount.com`
8. Set permission: "Make changes to events"
9. Click "Send"

### 7. Get Calendar ID (Optional)

If you want to use a specific calendar (not the primary one):

1. In Google Calendar, go to calendar settings (same as step 6)
2. Scroll down to "Integrate calendar"
3. Copy the "Calendar ID"
4. Update `.env`:
   ```bash
   GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
   ```

For your primary calendar, just use:
```bash
GOOGLE_CALENDAR_ID=primary
```

### 8. Verify .env Configuration

Your `.env` file should have:

```bash
# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google-calendar-service-account.json
GOOGLE_CALENDAR_ID=primary
```

### 9. Test the Integration

```bash
cd Phase2
source venv/bin/activate
python -c "from agent.tools.calendar import CalendarTool; c = CalendarTool(); print('✅ Calendar initialized successfully!')"
```

If you see the success message, you're ready to go!

## Troubleshooting

### "Credentials not found"

**Error**: `google_calendar_credentials_not_found`

**Fix**:
```bash
# Check if file exists
ls -l Phase2/credentials/google-calendar-service-account.json

# If missing, make sure you moved it from Downloads
# Check Downloads folder
ls -l ~/Downloads/appointment-agent-*.json

# Move it
mv ~/Downloads/appointment-agent-*.json Phase2/credentials/google-calendar-service-account.json
```

### "Permission denied" or "Forbidden"

**Error**: `403 Forbidden` when trying to access calendar

**Cause**: Service account doesn't have permission to access your calendar

**Fix**:
1. Double-check you shared the calendar (Step 6 above)
2. Verify the service account email is correct
3. Ensure permission is "Make changes to events" (not just "See all event details")
4. Wait 1-2 minutes for permissions to propagate

### "Invalid credentials"

**Error**: Invalid JSON or authentication error

**Possible causes**:
- JSON file is corrupted
- Wrong JSON file (not a service account key)
- File permissions issue

**Fix**:
```bash
# Check JSON file is valid
python -c "import json; print(json.load(open('Phase2/credentials/google-calendar-service-account.json'))['type'])"
# Should output: service_account

# Check file permissions
chmod 600 Phase2/credentials/google-calendar-service-account.json
```

### "API not enabled"

**Error**: `Google Calendar API has not been used in project...`

**Fix**:
1. Go back to Step 2 above
2. Make sure you're in the correct project
3. Enable Google Calendar API
4. Wait a few minutes for it to fully activate

### Testing Without Calendar

If you don't have Google Calendar set up yet, the agent will work in **mock mode**:
- Returns fake availability (10am, 2pm, 4pm)
- Simulates booking (doesn't create real events)
- Logs will show "mock_appointment_booked"

This lets you test the conversation flow before connecting the real calendar.

## Security Best Practices

1. **Never commit credentials**:
   - `.gitignore` already excludes `credentials/` directory
   - Double-check before git commits

2. **Limit service account permissions**:
   - Only share the specific calendar needed
   - Use "Make changes to events" (not "Make changes AND manage sharing")

3. **Rotate keys periodically**:
   - Delete old keys from Google Cloud Console
   - Generate new ones every 90 days

4. **Store securely in production**:
   - Use secrets manager (AWS Secrets Manager, Google Secret Manager)
   - Never store in plain text in production

## Calendar Configuration

Customize in `agent/config.py`:

```python
# Business hours for appointment booking
business_hours_start: int = 8  # 8 AM
business_hours_end: int = 18   # 6 PM

# Default appointment duration
default_appointment_duration_minutes: int = 30

# Calendar to use
google_calendar_id: str = "primary"  # or specific calendar ID
```

## Next Steps

Once calendar is working:
1. ✅ Test with `check_availability`
2. ✅ Book a test appointment
3. ✅ Verify it appears in Google Calendar
4. ✅ Test rescheduling
5. ✅ Test cancellation

Then you're ready for the full Phase 2 conversation testing!

---

**Need help?** Check the [README.md](./README.md) or [tactical-design.md](../tactical-design.md)
