# 🚀 Streamlit Cloud Deployment Guide

Deploy your VenueHooper Email Campaign System to Streamlit Community Cloud for free hosting.

## 📋 Prerequisites

1. **GitHub Repository**: https://github.com/phantomop26/Emailletter
2. **Streamlit Account**: Sign up at https://share.streamlit.io/
3. **API Keys**: Resend, OpenAI, Gmail API credentials

## 🎯 Step-by-Step Deployment

### Step 1: Connect to Streamlit Cloud

1. Go to **https://share.streamlit.io/**
2. Click **"Sign up with GitHub"**
3. Authorize Streamlit to access your GitHub repositories
4. Click **"New app"**

### Step 2: Configure Your App

1. **Repository**: Select `phantomop26/Emailletter`
2. **Branch**: `main` 
3. **Main file path**: `src/ui/streamlit_app.py`
4. **App URL**: Choose your custom subdomain (e.g., `venuehooper-email`)

### Step 3: Add Environment Variables (Secrets)

In the Streamlit Cloud app settings, add these secrets:

#### Required API Keys:
```toml
RESEND_API_KEY = "re_your_actual_key_here"
OPENAI_API_KEY = "sk-proj-your_actual_key_here"
```

#### Gmail API Configuration:
```toml
GMAIL_CLIENT_ID = "your_gmail_client_id.apps.googleusercontent.com"
GMAIL_CLIENT_SECRET = "your_gmail_client_secret"
```

#### Email Settings:
```toml
EMAIL_SENDER = "onboarding@resend.dev"
TEST_EMAIL = "your_test_email@gmail.com"
BACKUP_TEST_EMAIL = "your_backup_email@gmail.com"
ORG_NAME = "VenueHooper"
YOUR_NAME = "Your Name"
YOUR_PHONE = "555-555-5555"
FORCE_TEST_EMAIL = "true"
```

### Step 4: Deploy

1. Click **"Deploy!"**
2. Wait for installation (may take 3-5 minutes)
3. Your app will be available at: `https://your-app-name.streamlit.app/`

## 🔧 Configuration Files

### `requirements.txt`
```txt
streamlit==1.28.0
pandas==2.0.3
playwright==1.40.0
openai==1.3.0
requests==2.31.0
python-dotenv==1.0.0
resend==0.6.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

### `packages.txt`
```txt
playwright
```

This file tells Streamlit Cloud to install Playwright browsers for web scraping.

## 🌐 Your Deployed App Features

Once deployed, your app will include:

### 📊 **Dashboard Tab**
- Campaign overview and metrics
- Real-time progress tracking

### 📝 **Venue Input Tab** 
- CSV upload functionality
- Manual venue entry
- Data validation

### 🔍 **Email Scraper Tab**
- Automated email discovery
- Hybrid scraping methods
- Results export

### 🤖 **AI Analysis Tab**
- OpenAI-powered venue analysis
- Intelligent categorization
- Personalization insights

### ✉️ **Email Generator Tab**
- AI-generated personalized emails
- Template customization
- Preview before sending

### 📧 **Email Sender Tab**
- Professional email delivery via Resend
- Batch sending capabilities
- Delivery tracking

### 📬 **Reply Parser Tab**
- Gmail integration
- AI reply analysis
- Structured results export

### 🧪 **Step Testing Tab**
- Complete workflow testing
- Individual step validation
- Performance monitoring

## 🚨 Important Notes

### Browser Limitations
- Streamlit Cloud has some limitations with Playwright browsers
- Email scraping may be slower than local deployment
- Consider using backup scraping methods for production

### Gmail API Setup
- Gmail OAuth requires additional configuration for cloud deployment
- You may need to add your Streamlit app domain to authorized origins
- Consider using service account for production deployments

### Performance Considerations
- Free Streamlit Cloud has resource limitations
- For high-volume campaigns, consider upgrading to Streamlit Cloud Pro
- Monitor usage and optimize batch sizes accordingly

## 🔄 Updates and Maintenance

### Automatic Deployments
- Any push to your `main` branch triggers automatic redeployment
- Changes typically take 1-2 minutes to reflect
- Check deployment logs in Streamlit Cloud dashboard

### Managing Secrets
- Update secrets in Streamlit Cloud app settings
- Restart app after changing environment variables
- Never commit secrets to your repository

## 🔗 Useful Links

- **Your GitHub Repo**: https://github.com/phantomop26/Emailletter
- **Streamlit Cloud**: https://share.streamlit.io/
- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Deployment Status**: Check your app dashboard for real-time status

## 🆘 Troubleshooting

### Common Issues:

1. **Playwright Installation Fails**
   - Check that `packages.txt` contains `playwright`
   - Restart the app from Streamlit Cloud dashboard

2. **Import Errors**
   - Verify all dependencies in `requirements.txt`
   - Check Python path configuration in `main.py`

3. **API Key Issues** 
   - Ensure secrets are properly configured in Streamlit Cloud
   - Check for typos in secret names
   - Verify API keys are valid and active

4. **Gmail API Errors**
   - Add Streamlit app domain to Google Cloud Console
   - Update OAuth consent screen settings
   - Check client ID and secret configuration

## 🎉 Success!

Your VenueHooper Email Campaign System is now live on Streamlit Cloud! 

Share your app URL with team members and start automating your venue outreach campaigns in the cloud! 🚀