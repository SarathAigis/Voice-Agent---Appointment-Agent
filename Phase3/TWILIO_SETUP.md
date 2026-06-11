# Twilio Setup Guide - Complete Walkthrough

Step-by-step guide to setting up Twilio for Phase 3.

## Step 1: Create Twilio Account (5 minutes)

1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Click "Sign up and start building"
3. Fill in your information:
   - Email
   - Password
   - First/Last Name
4. Click "Start your free trial"
5. Verify your email (check inbox)
6. Verify your phone number (SMS code)

**Free Trial Benefits:**
- $15 credit (no credit card required)
- ~115 minutes of voice calls
- ~2000 SMS messages
- Full API access

**Limitation**: Can only call/text numbers you've verified in trial mode

## Step 2: Get a Phone Number (2 minutes)

1. In Twilio Console, click "Get a trial phone number"
   - Or go to: Phone Numbers → Manage → Buy a number
2. You'll be assigned a number automatically (US number if in US)
3. **Important**: Verify it has:
   - ✅ Voice capability
   - ✅ SMS capability (recommended)
4. Click "Choose this number"
5. Copy the phone number (format: `+1234567890`)

**Cost after trial**: ~$1-2/month for the number

## Step 3: Get API Credentials (1 minute)

1. In Twilio Console, go to: Account → API keys & tokens
2. Copy these values:
   - **Account SID**: Starts with `AC...` (visible by default)
   - **Auth Token**: Click "Show" to reveal

**Keep these secret!** They give full access to your Twilio account.

## Step 4: Verify Test Phone Numbers (Trial Only)

If you're on a free trial, you can only call verified numbers.

1. Go to: Phone Numbers → Manage → Verified Caller IDs
2. Click "Add a new Caller ID"
3. Enter the phone you want to test with (your personal phone)
4. Click "Call this number"
5. Answer and enter the verification code
6. ✅ This number can now receive test calls

**Note**: Upgrade to paid account to call any number.

## Step 5: Configure Environment Variables

Edit `Phase3/.env`:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+12345678901

# SMS (optional - uses TWILIO_PHONE_NUMBER by default)
TWILIO_ENABLE_SMS=true

# Call Configuration
ENABLE_VOICEMAIL_DETECTION=true
VOICEMAIL_MESSAGE="Hi, this is the scheduling assistant. Please call us back or check your text messages."
MAX_CALL_DURATION_SECONDS=300
CALL_TIMEOUT_SECONDS=30
```

## Step 6: Expose Your API Server (Development)

Twilio needs to reach your API server to send webhook events. In development, use ngrok.

### Install ngrok

**Mac:**
```bash
brew install ngrok
```

**Linux:**
```bash
snap install ngrok
```

**Windows/Other:**
Download from [ngrok.com/download](https://ngrok.com/download)

### Run ngrok

```bash
# Terminal 1: Start API server
cd Phase3
source venv/bin/activate
python -m api.server

# Terminal 2: Start ngrok
ngrok http 8000
```

You'll see:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Configure Twilio Webhooks

1. Go to Twilio Console: Phone Numbers → Manage → Active numbers
2. Click your phone number
3. Scroll to "Voice Configuration"
4. **A CALL COMES IN**:
   - Select "Webhook"
   - URL: `https://abc123.ngrok.io/api/calls/twiml/test-room`
   - Method: HTTP GET
5. **STATUS CALLBACK URL**:
   - URL: `https://abc123.ngrok.io/api/calls/status`
   - Method: HTTP POST
6. Click "Save"

**Note**: ngrok URL changes each time you restart it. Update Twilio webhooks if URL changes.

## Step 7: Test Your Setup

### Verify API Server

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### Verify ngrok

```bash
curl https://your-ngrok-url.ngrok.io/health
# Should return: {"status": "healthy"}
```

### Make a Test Call

```bash
curl -X POST http://localhost:8000/api/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "driver_id": "TEST-001",
    "driver_name": "Test Driver",
    "driver_phone": "+1YOUR_VERIFIED_NUMBER",
    "truck_number": "T-TEST",
    "call_purpose": "test call"
  }'
```

**Your phone should ring!**

## Step 8: Monitor Calls

### Twilio Console

1. Go to: Monitor → Logs → Calls
2. You'll see your call listed
3. Click to see details:
   - Duration
   - Status
   - Cost
   - Recordings (if enabled)

### Your API Logs

Check terminal running `python -m api.server`:
```
INFO call_initiated call_sid=CAxxxxx
INFO twilio_status_webhook status=ringing
INFO twilio_status_webhook status=in-progress
INFO twilio_status_webhook status=completed
```

## Production Deployment

For production, replace ngrok with a real domain:

### Option 1: Deploy to Cloud

**Heroku:**
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login and create app
heroku login
heroku create your-app-name

# Deploy
git push heroku main

# Your URL: https://your-app-name.herokuapp.com
```

**AWS/GCP/Azure:**
- Deploy FastAPI server to EC2/Cloud Run/App Service
- Get public domain/IP
- Update Twilio webhooks

### Option 2: Use Permanent ngrok

Upgrade to ngrok paid plan:
- Get permanent domain
- Don't need to update Twilio webhooks

## Troubleshooting

### "Account not active"

**Solution**: Complete phone verification in Twilio Console

### "Permission to send an SMS has not been enabled"

**Solution**:
1. Go to: Messaging → Try it out → Get set up
2. Complete SMS setup wizard
3. Or upgrade to paid account

### "Unable to create record: Number is not a valid phone number"

**Solution**:
- Use E.164 format: `+1234567890`
- Include country code (+1 for US)
- No spaces, dashes, or parentheses

### "Webhook returned invalid content-type"

**Solution**:
- Ensure endpoint returns `application/xml` for TwiML
- Check `/api/calls/twiml/{room}` endpoint

### Calls work but no webhook events

**Solution**:
- Verify ngrok is running
- Check Twilio webhook configuration
- Test webhook URL: `curl https://your-url.com/api/calls/status`
- Check firewall/security group settings

### "Free trial account limitation"

**Solution**:
- Verify destination number in Twilio Console
- Or upgrade to paid account ($20 minimum)

## Cost Calculator

### Free Trial
- $15 credit included
- ~115 minutes of calls
- ~2000 SMS messages

### After Trial

**Voice Calls:**
- Outbound (US): $0.013/min
- Inbound (US): $0.0085/min

**SMS:**
- Outbound (US): $0.0075/msg
- Inbound (US): $0.0075/msg

**Phone Number:**
- Local (US): $1.15/month
- Toll-free (US): $2/month

**Example: 100 calls/day**
- 5 min/call average
- 1 SMS/call
- Total: ~$250/month

## Security Best Practices

1. **Keep credentials secret**:
   - Never commit `.env` to git
   - Use environment variables in production
   - Rotate auth token periodically

2. **Validate webhooks**:
   - Check Twilio signature
   - Verify request origin

3. **Rate limiting**:
   - Limit API calls per IP
   - Prevent spam/abuse

4. **Monitor usage**:
   - Set up billing alerts
   - Check daily usage in console

## Next Steps

Once Twilio is working:
1. ✅ Test outbound calls
2. ✅ Verify SMS confirmations
3. ✅ Test voicemail detection
4. ✅ Complete Phase 3 validation checklist
5. → Move to Phase 4 (RAG + Fallback)

---

**Need help?** Check Twilio Docs: [twilio.com/docs](https://www.twilio.com/docs)
