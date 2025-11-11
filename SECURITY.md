# 🔐 Security Setup Instructions

This guide will help you securely configure your API keys and credentials.

## 🚨 Important Security Notes

⚠️ **NEVER commit your actual API keys to GitHub**  
⚠️ **Always use environment variables for sensitive data**  
⚠️ **Keep your `.env` file local only**

## 📋 Required API Keys

You'll need to obtain the following API keys:

### 1. Resend API Key
- Visit: https://resend.com/
- Sign up and get your API key
- Format: `re_xxxxxxxxxx`

### 2. OpenAI API Key  
- Visit: https://platform.openai.com/
- Create an account and get API key
- Format: `sk-proj-xxxxx` or `sk-xxxxx`

### 3. Gmail API Credentials
- Visit: https://console.developers.google.com/
- Create a project and enable Gmail API
- Download credentials JSON file
- Get client ID and client secret

## 🔧 Setup Instructions

### Step 1: Copy Environment Template
```bash
cp .env.example config/.env
```

### Step 2: Fill in Your API Keys
Edit `config/.env` and replace all placeholder values:
```env
RESEND_API_KEY=your_actual_resend_key_here
OPENAI_API_KEY=your_actual_openai_key_here
GMAIL_CLIENT_ID=your_actual_client_id_here
GMAIL_CLIENT_SECRET=your_actual_client_secret_here
# ... update all other values
```

### Step 3: Gmail API Setup
1. Download your Gmail API credentials JSON
2. Save it as `config/credentials.json`
3. The app will guide you through OAuth setup

### Step 4: Test Configuration
```bash
python scripts/test_system.py
```

## 🛡️ Security Best Practices

✅ **DO:**
- Keep `.env` files local only
- Use strong, unique API keys
- Regularly rotate your keys
- Use different keys for production/development
- Enable 2FA on all accounts

❌ **DON'T:**
- Commit `.env` files to version control
- Share API keys in chat/email
- Use production keys in development
- Store keys in code comments
- Use weak passwords for API accounts

## 🚨 If You Accidentally Commit Keys

If you accidentally commit API keys to GitHub:

1. **Immediately revoke/regenerate** all exposed keys
2. Remove the commit from Git history:
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch config/.env' --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push to overwrite history:
   ```bash
   git push origin --force --all
   ```
4. Contact the API providers if needed

## 📞 Support

If you need help with setup:
1. Check the main README.md
2. Review docs/SETUP_GUIDE.md  
3. Create an issue on GitHub (without sharing keys!)

---
🔒 **Remember: Security is not optional!**