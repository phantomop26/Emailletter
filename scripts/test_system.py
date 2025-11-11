#!/usr/bin/env python3
"""
VenueHooper System Test
Tests all components of the email campaign workflow
"""

import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add project root and src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_environment():
    """Test if environment is set up correctly"""
    print("🧪 Testing VenueHooper Environment")
    print("=" * 40)
    
    # Check for .env file in config directory
    env_file = project_root / 'config' / '.env'
    if env_file.exists():
        print("✅ .env file found in config/")
        # Try to load it
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print("⚠️  .env file not found in config/ - using environment variables")
    
    # Check API keys
    if os.getenv('RESEND_API_KEY'):
        print("✅ Resend API key found")
    else:
        print("❌ Resend API key missing in environment")
    
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API key found")
    else:
        print("❌ OpenAI API key missing in environment")
    
    # Check required files in new structure
    required_files = [
        ('src/ui/streamlit_app.py', 'Main Streamlit app'),
        ('src/automation/gmail_reply_automation.py', 'Gmail automation'),
        ('src/utils/email_scraper_utils.py', 'Email scraping utilities'),
        ('config/requirements.txt', 'Requirements file')
    ]
    
    for file_path, description in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {description} found at {file_path}")
        else:
            print(f"❌ {description} missing at {file_path}")
    
    # Check data directory
    data_dir = project_root / 'data'
    if data_dir.exists():
        print(f"✅ Data directory found")
        data_files = list(data_dir.glob('*.csv'))
        print(f"   📊 Found {len(data_files)} CSV files")
    else:
        print(f"⚠️  Data directory not found (will be created during workflow)")

def test_imports():
    """Test if all required packages can be imported"""
    print("\n📦 Testing Package Imports")
    print("=" * 40)
    
    required_packages = [
        'streamlit',
        'pandas', 
        'playwright',
        'openai',
        'requests'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Run: pip install {package}")
    
    # Test Gmail packages (optional)
    gmail_packages = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient'
    ]
    
    print("\n📧 Gmail API Packages (Optional):")
    for package in gmail_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  {package} - Run: python setup_gmail_api.py")

def test_workflow_functions():
    """Test key workflow functions"""
    print("\n⚙️ Testing Workflow Functions")
    print("=" * 40)
    
    try:
        from src.ui.streamlit_app import VenueHooperWorkflow
        workflow = VenueHooperWorkflow()
        print("✅ VenueHooperWorkflow class loaded")
    except Exception as e:
        print(f"❌ VenueHooperWorkflow error: {e}")
    
    try:
        from src.automation import gmail_reply_automation
        print("✅ Gmail automation module loaded")
    except Exception as e:
        print(f"❌ Gmail automation error: {e}")

def test_data_structure():
    """Test data file structure"""
    print("\n📊 Testing Data Structure")
    print("=" * 40)
    
    # Change to project root for data access
    os.chdir(project_root)
    
    # Test venues file
    venues_file = project_root / 'data' / 'venues.csv'
    if venues_file.exists():
        try:
            df = pd.read_csv(venues_file)
            print(f"✅ data/venues.csv loaded ({len(df)} venues)")
            
            required_columns = ['name', 'website']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                print(f"⚠️  Missing columns in venues.csv: {missing_cols}")
            else:
                print("✅ venues.csv has required columns")
                
        except Exception as e:
            print(f"❌ venues.csv error: {e}")
    
    # Test results file if it exists
    if os.path.exists('data/venues_email_send_results.csv'):
        try:
            df = pd.read_csv('data/venues_email_send_results.csv')
            sent_count = len(df[df['send_status'] == 'sent']) if 'send_status' in df.columns else 0
            print(f"✅ Found {sent_count} sent emails in results file")
        except Exception as e:
            print(f"❌ Results file error: {e}")

def show_current_status():
    """Show current campaign status"""
    print("\n📈 Current Campaign Status")
    print("=" * 40)
    
    if os.path.exists('data/venues_email_send_results.csv'):
        df = pd.read_csv('data/venues_email_send_results.csv')
        
        total_venues = len(df)
        sent_emails = len(df[df['send_status'] == 'sent']) if 'send_status' in df.columns else 0
        
        # Count replies if available
        replies = 0
        if 'reply_raw' in df.columns:
            replies = len(df[df['reply_raw'].notna() & (df['reply_raw'] != '')])
        
        print(f"📊 Total Venues: {total_venues}")
        print(f"📤 Emails Sent: {sent_emails}")
        print(f"📬 Replies Received: {replies}")
        
        if sent_emails > 0:
            response_rate = (replies / sent_emails) * 100
            print(f"📈 Response Rate: {response_rate:.1f}%")
        
    else:
        print("⚠️  No campaign results found yet")

def main():
    """Run all tests"""
    print("🚀 VenueHooper System Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    test_environment()
    test_imports()
    test_workflow_functions()
    test_data_structure()
    show_current_status()
    
    print("\n🎯 Next Steps:")
    print("1. Run: streamlit run streamlit_app.py")
    if not os.path.exists('credentials.json'):
        print("2. Run: python setup_gmail_api.py (for Gmail integration)")
    print("3. Upload venues CSV and start campaign!")
    
    print("\n✅ System test complete!")

if __name__ == '__main__':
    main()
