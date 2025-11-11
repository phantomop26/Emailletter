#!/usr/bin/env python3
"""
Gmail API Setup Script
Installs required packages and guides through authentication setup
"""

import subprocess
import sys
import os

def install_packages():
    """Install required Google API packages"""
    packages = [
        'google-auth',
        'google-auth-oauthlib', 
        'google-auth-httplib2',
        'google-api-python-client'
    ]
    
    print("🔧 Installing Google API packages...")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    return True

def check_credentials():
    """Check if Gmail credentials are set up"""
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found")
        return True
    else:
        print("❌ credentials.json not found")
        print("\n📋 To set up Gmail API:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project (or select existing)")
        print("3. Enable Gmail API:")
        print("   - Go to 'APIs & Services' > 'Library'")
        print("   - Search 'Gmail API' and click Enable")
        print("4. Create credentials:")
        print("   - Go to 'APIs & Services' > 'Credentials'")
        print("   - Click 'Create Credentials' > 'OAuth client ID'")
        print("   - Choose 'Desktop application'")
        print("   - Download the JSON file")
        print("5. Save the downloaded file as 'credentials.json' in this folder")
        print("\n🔄 Run this script again after setting up credentials.json")
        return False

def test_authentication():
    """Test Gmail API authentication"""
    try:
        from gmail_reply_automation import authenticate_gmail
        service = authenticate_gmail()
        
        if service:
            print("✅ Gmail authentication successful!")
            
            # Test basic API call
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress')
            print(f"📧 Connected to Gmail account: {email}")
            return True
        else:
            print("❌ Gmail authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 VenueHooper Gmail API Setup")
    print("=" * 40)
    
    # Step 1: Install packages
    if not install_packages():
        print("❌ Package installation failed")
        return
    
    # Step 2: Check credentials
    if not check_credentials():
        return
    
    # Step 3: Test authentication
    print("\n🔐 Testing Gmail authentication...")
    if test_authentication():
        print("\n🎉 Gmail API setup complete!")
        print("\n📧 You can now:")
        print("- Run 'python gmail_reply_automation.py' to check for replies")
        print("- Use the 'Check Gmail' button in the Streamlit app")
        print("- Run continuous monitoring with 'python gmail_reply_automation.py --monitor'")
    else:
        print("\n❌ Setup incomplete. Please check the credentials and try again.")

if __name__ == '__main__':
    main()
