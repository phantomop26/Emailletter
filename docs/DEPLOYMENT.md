# 🚀 VenueHooper Deployment Guide

Complete guide for hosting VenueHooper on various platforms.

## 🌐 Option 1: Streamlit Cloud (Recommended - FREE)

### ✅ Pros
- **Free hosting** for public repositories
- **Automatic deployments** from GitHub
- **Built-in secrets management**
- **Zero configuration** required

### 📋 Setup Steps

1. **Prepare Repository**
   ```bash
   # Make sure your repo is clean and committed
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file path: `src/ui/streamlit_app.py`
   - Click "Deploy"

3. **Add Secrets**
   In Streamlit Cloud dashboard → Secrets:
   ```toml
   RESEND_API_KEY = "re_your_actual_key_here"
   OPENAI_API_KEY = "sk-your_actual_key_here"
   TEST_EMAIL = "your_test_email@gmail.com"
   ORG_NAME = "Your Company"
   YOUR_NAME = "Your Name"
   YOUR_PHONE = "555-555-5555"
   FORCE_TEST_EMAIL = "true"
   ```

4. **Access Your App**
   - URL: `https://your-repo-name-randomstring.streamlit.app`
   - Automatic updates when you push to GitHub

---

## 🚢 Option 2: Railway (Modern Platform)

### ✅ Pros
- **$5/month** for small apps
- **Easy GitHub integration**
- **Good performance**

### 📋 Setup Steps

1. **Sign up at [Railway](https://railway.app)**

2. **Connect GitHub & Deploy**
   - New Project → Deploy from GitHub
   - Select your repository
   - Railway auto-detects Python and uses `railway.toml`

3. **Add Environment Variables**
   ```
   RESEND_API_KEY=your_key
   OPENAI_API_KEY=your_key
   TEST_EMAIL=your_email
   PORT=8501
   ```

4. **Custom Domain (Optional)**
   - Settings → Domains → Add custom domain

---

## 🔷 Option 3: Heroku

### ⚠️ Note: Heroku discontinued free tier, paid plans start at $7/month

### 📋 Setup Steps

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Login
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   # In your project directory
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set RESEND_API_KEY=your_key
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set TEST_EMAIL=your_email
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

   Heroku uses `Procfile` and `runtime.txt` automatically.

---

## ☁️ Option 4: Google Cloud Run

### ✅ Pros
- **Pay-per-use** (very cheap for low traffic)
- **Highly scalable**
- **Professional grade**

### 📋 Setup Steps

1. **Install Google Cloud SDK**
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   gcloud auth login
   ```

2. **Build & Deploy**
   ```bash
   # Set project
   gcloud config set project your-project-id
   
   # Build image
   gcloud builds submit --tag gcr.io/your-project-id/venuehooper
   
   # Deploy to Cloud Run
   gcloud run deploy venuehooper \
     --image gcr.io/your-project-id/venuehooper \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars RESEND_API_KEY=your_key,OPENAI_API_KEY=your_key
   ```

---

## 🐋 Option 5: DigitalOcean App Platform

### ✅ Pros
- **$5/month** starter plan
- **Easy GitHub integration**
- **Good documentation**

### 📋 Setup Steps

1. **Create DigitalOcean Account**

2. **Create App**
   - Apps → Create App
   - Connect GitHub repository
   - DigitalOcean detects Python automatically

3. **Configure Environment**
   - Add environment variables in dashboard
   - Set run command: `streamlit run src/ui/streamlit_app.py --server.port=$PORT`

---

## 🏠 Option 6: Self-Hosted (VPS)

### ✅ Pros
- **Full control**
- **Cost effective** for high traffic
- **Custom domains**

### 📋 Setup Steps

1. **Get VPS** (DigitalOcean Droplet, AWS EC2, etc.)

2. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python & dependencies
   sudo apt install python3 python3-pip nginx -y
   
   # Clone repository
   git clone https://github.com/yourusername/venuehooper.git
   cd venuehooper
   
   # Install dependencies
   pip3 install -r config/requirements.txt
   playwright install
   ```

3. **Configure Environment**
   ```bash
   # Create .env file
   cp config/.env.example config/.env
   nano config/.env  # Add your API keys
   ```

4. **Run with Process Manager**
   ```bash
   # Install PM2
   npm install -g pm2
   
   # Start application
   pm2 start "streamlit run src/ui/streamlit_app.py --server.port=8501" --name venuehooper
   pm2 startup
   pm2 save
   ```

5. **Configure Nginx** (Optional)
   ```nginx
   # /etc/nginx/sites-available/venuehooper
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 🔧 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `RESEND_API_KEY` | ✅ Yes | Resend email API key | `re_abc123...` |
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key | `sk-proj-abc123...` |
| `TEST_EMAIL` | ✅ Yes | Test email address | `test@gmail.com` |
| `ORG_NAME` | ⚪ Optional | Organization name | `VenueHooper` |
| `YOUR_NAME` | ⚪ Optional | Contact person name | `John Doe` |
| `YOUR_PHONE` | ⚪ Optional | Contact phone | `555-555-5555` |
| `FORCE_TEST_EMAIL` | ⚪ Optional | Redirect all emails to test | `true` |

## 🎯 Deployment Comparison

| Platform | Cost | Ease | Performance | Features |
|----------|------|------|-------------|----------|
| **Streamlit Cloud** | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Auto-deploy, Secrets |
| **Railway** | $5/mo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | GitHub integration |
| **Heroku** | $7/mo | ⭐⭐⭐⭐ | ⭐⭐⭐ | Mature platform |
| **Google Cloud** | Pay-per-use | ⭐⭐ | ⭐⭐⭐⭐⭐ | Enterprise grade |
| **DigitalOcean** | $5/mo | ⭐⭐⭐ | ⭐⭐⭐⭐ | Good balance |
| **Self-hosted** | $5-20/mo | ⭐ | ⭐⭐⭐⭐⭐ | Full control |

## 🚀 Quick Start Recommendation

**For beginners**: Use **Streamlit Cloud** (free, easiest setup)
**For businesses**: Use **Railway** or **DigitalOcean** (professional, affordable)
**For enterprises**: Use **Google Cloud Run** (scalable, enterprise-grade)

## 🔒 Security Notes

1. **Never commit API keys** to GitHub
2. **Use environment variables** or secrets management
3. **Enable HTTPS** in production
4. **Regularly rotate API keys**
5. **Monitor usage** and set up billing alerts

## 🆘 Troubleshooting

### Common Issues

1. **"Module not found"**
   - Check `requirements.txt` is complete
   - Verify Python version compatibility

2. **"Port already in use"**
   - Use environment variable `PORT` for cloud platforms
   - Default Streamlit port is 8501

3. **"API key not found"**
   - Verify environment variables are set correctly
   - Check secrets configuration in cloud platforms

4. **Playwright browser issues**
   - Make sure `playwright install` runs during deployment
   - Use lightweight browser options for cloud deployment

---

**🎉 Your VenueHooper system is now ready for the world!**