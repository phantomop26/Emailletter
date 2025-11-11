# 🏢 VenueHooper - Complete Email Campaign Automation

**The complete solution for venue outreach automation:**
- ✅ Email scraping from venue websites
- ✅ Personalized email campaigns via Resend API
- ✅ Automatic reply monitoring via Gmail API
- ✅ AI-powered reply parsing with OpenAI
- ✅ Beautiful Streamlit web interface

---

## 🚀 Quick Start Guide

### **New Organized Structure!**
✅ **Project reorganized** - Clean directory structure  
✅ **Multiple launchers** - Choose your preferred method  
✅ **System fully functional** - All components working

### 1. **Start the System**
```bash
# Main launcher (recommended)
python3 main.py

# Alternative launcher
python3 scripts/start.py

# Or manually
streamlit run src/ui/streamlit_app.py --server.port 8502
```

### 2. **Project Structure**
```
📦 VenueHooper/
├── 🚀 main.py                     # Main launcher
├── 📁 config/                     # Configuration
│   ├── requirements.txt           # Dependencies  
│   └── .env.example              # API keys template
├── 📁 data/                      # CSV files
├── 📁 scripts/                   # Utility scripts
│   ├── start.py                  # Advanced launcher
│   └── test_system.py           # System validation
└── 📁 src/                       # Source code
    ├── automation/               # Email automation
    ├── ui/                       # Streamlit interface
    └── utils/                    # Helper functions
```

### 3. **Gmail Reply Automation Setup**
To automatically read venue replies:

```bash
# Install Gmail API packages
python setup_gmail_api.py
```

**Then follow the Google Cloud setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable Gmail API
4. Create OAuth credentials (Desktop app)
5. Download as `credentials.json`

### 3. **Run Complete Workflow**
```bash
# Check for replies once
python gmail_reply_automation.py

# Monitor replies continuously (every 10 minutes)
python gmail_reply_automation.py --monitor
```

---

## 📧 How The Complete System Works

### **Step 1: Send Emails via Resend** ✅
- Load venue CSV file
- Scrape email addresses from websites
- Send personalized outreach emails
- Track delivery status

### **Step 2: Venues Reply to Your Email** 📬
- Venues receive your email from `onboarding@resend.dev` (or your domain)
- They reply to your email address
- Replies land in your Gmail inbox

### **Step 3: Gmail API Reads Replies** 🤖
- Scans Gmail inbox every few minutes
- Identifies replies related to your campaign
- Matches replies to specific venues
- Extracts email content automatically

### **Step 4: AI Parses Reply Content** 🧠
- OpenAI analyzes each reply
- Extracts structured booking information:
  - Interest level (interested/not interested/maybe)
  - Available dates
  - Pricing information
  - Special requirements
  - Follow-up actions needed

### **Step 5: Update Results Automatically** 💾
- Saves parsed data to CSV
- Updates Streamlit dashboard
- Provides downloadable reports

---

## 🎯 Current Configuration

**API Keys (Working):**
- ✅ Resend API: `re_7bzjFfrH_4NMdTEbiauwATJzDw1rj54FQ`
- ✅ OpenAI API: `sk-proj-s-ZrswIRSkes9p...`

**Email Settings:**
- 📤 Sender: `onboarding@resend.dev` (Resend test domain)
- 📧 Your inbox: `11k34sahilkumarsingh@gmail.com`
- 🎯 Test recipient: Same email for testing

**Files Generated:**
- `data/venues.csv` - Input venue data
- `data/venues_scraped.csv` - After email scraping
- `data/campaign_results.csv` - After sending campaign
- All data files organized in `data/` directory

---

## 🔧 Advanced Features

### **Continuous Reply Monitoring**
```bash
# Run in background to check Gmail every 10 minutes
python gmail_reply_automation.py --monitor
```

### **Custom Domain Setup** (Optional)
1. Verify your domain in Resend dashboard
2. Update `.env` file: `EMAIL_SENDER=hello@yourdomain.com`
3. Send emails from your professional domain

### **Webhook Integration** (Optional)
Deploy `webhook_handler.py` to receive real-time email delivery notifications from Resend.

---

## 📊 Dashboard Features

### **Tab 1: Upload Venues**
- CSV upload with venue data
- Data validation and preview
- Supports: name, website, category, address, phone

### **Tab 2: Email Scraping**
- Automated website email extraction
- Progress tracking with status updates
- Handles JavaScript-heavy websites via Playwright

### **Tab 3: Email Campaign**
- Preview personalized emails
- Bulk sending with rate limiting
- Real-time delivery status tracking

### **Tab 4: Reply Management**
- **🆕 Automatic Gmail monitoring**
- AI-powered reply parsing
- Manual reply entry (backup option)
- Reply status dashboard

### **Tab 5: Results & Analytics**
- Campaign performance metrics
- Response rate tracking
- Downloadable complete results
- Parsed booking information

---

## 🐛 Troubleshooting

### **Gmail API Issues**
```bash
# Delete old credentials and re-authenticate
rm token.json
python gmail_reply_automation.py
```

### **No Replies Found**
- Check Gmail inbox manually
- Verify venues are replying to the correct email
- Adjust search timeframe (currently 3 days)

### **OpenAI Parsing Errors**
- Verify API key in `.env` file
- Check OpenAI account quota/billing
- Try with shorter email content

### **Resend Delivery Issues**
- Verify API key is correct
- Check recipient email format
- Monitor Resend dashboard for delivery status

---

## 📈 Production Deployment

### **For Production Use:**
1. **Verify your domain** in Resend (enables sending to any email)
2. **Set up Gmail API** for automatic reply processing
3. **Deploy webhook handler** for real-time notifications
4. **Run continuous monitoring** in background
5. **Set up proper logging** and error handling

### **Scaling Up:**
- Process larger venue lists (1000+ venues)
- Multiple email templates for different venue types
- Advanced reply classification and routing
- Integration with CRM systems

---

## 🎉 You're All Set!

Your VenueHooper system can now:
- ✅ **Send** professional venue outreach emails
- 🔄 **Monitor** Gmail for replies automatically  
- 🤖 **Parse** replies with AI intelligence
- 📊 **Track** campaign performance and results

**Next Steps:**
1. Run `python setup_gmail_api.py` to enable reply automation
2. Start sending campaigns via the Streamlit interface
3. Watch as replies get processed automatically!

---

*Built with ❤️ using Resend, OpenAI, Gmail API, and Streamlit*
