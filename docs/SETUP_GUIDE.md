# VenueHooper Email Setup Guide

## 🚀 Quick Start (Recommended)

### Option A: Use Resend Webhooks (Easiest - No Gmail API needed!)

1. **Verify your domain in Resend Dashboard**
   - Go to https://resend.com/domains
   - Add your domain (e.g., `yourdomain.com`)
   - Add the DNS records they provide
   - Wait for verification (usually 5-15 minutes)

2. **Update your sender email**
   - Change `EMAIL_SENDER` in `.env` from `onboarding@resend.dev` to `hello@yourdomain.com`
   - Restart the Streamlit app

3. **Set up webhooks (for automatic reply processing)**
   - In Resend dashboard, go to Webhooks
   - Add webhook URL: `https://your-domain.com/webhook/resend`
   - Select events: `email.bounced`, `email.complained`, `email.delivered`, `email.opened`
   - Deploy the `webhook_handler.py` to your server

4. **Done!** 
   - Send emails from your domain
   - Replies automatically processed via webhooks
   - No Gmail API setup needed

---

## 🔧 Advanced Setup (If you want Gmail API)

### Option B: Gmail API Integration

1. **Create Google Cloud Project**
   ```bash
   # Go to https://console.cloud.google.com/
   # Create new project or select existing
   ```

2. **Enable Gmail API**
   ```bash
   # In Google Cloud Console:
   # APIs & Services > Library > Search "Gmail API" > Enable
   ```

3. **Create OAuth Credentials**
   ```bash
   # APIs & Services > Credentials > Create Credentials > OAuth client ID
   # Application type: Desktop application
   # Download the JSON file as 'credentials.json'
   ```

4. **Place credentials in project**
   ```bash
   # Move downloaded file to:
   cp ~/Downloads/credentials.json /Users/funda/Desktop/VenueHooper/emailletter/
   ```

5. **Install Google packages**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

6. **Test Gmail connection**
   ```bash
   cd /Users/funda/Desktop/VenueHooper/emailletter
   python gmail_reply_fetcher.py
   ```

---

## 📧 Current Configuration

**Working now:**
- ✅ Resend API: `re_7bzjFfrH_4NMdTEbiauwATJzDw1rj54FQ`
- ✅ OpenAI API: `sk-proj-s-ZrswIRSkes9p...`
- ✅ Email sending from: `onboarding@resend.dev`
- ✅ Test recipient: `11k34sahilkumarsingh@gmail.com`

**Next steps:**
- 🔄 Verify custom domain in Resend
- 🔄 Update sender email to your domain
- 🔄 Deploy webhook handler (optional but recommended)

---

## 🎯 Recommendation

**Start with Option A (Resend Webhooks)** because:
- Simpler setup (no Google Cloud complexity)
- Real-time reply processing
- Works perfectly for business outreach
- Gmail API can be added later if needed

The webhook approach is actually more professional for business email campaigns!
