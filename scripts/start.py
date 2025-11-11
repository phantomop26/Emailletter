#!/usr/bin/env python3
"""
VenueHooper Startup Script
Easy way to launch the complete email campaign system
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def check_playwright_browsers():
    """Check if Playwright browsers are installed"""
    try:
        result = subprocess.run(['playwright', 'install', '--dry-run'], 
                              capture_output=True, text=True)
        if 'is already installed' not in result.stdout and result.returncode != 0:
            print("🔧 Installing Playwright browsers...")
            subprocess.run(['playwright', 'install'], check=True)
            print("✅ Playwright browsers installed")
    except Exception as e:
        print(f"⚠️  Playwright check failed: {e}")

def start_streamlit():
    """Start the Streamlit application"""
    print("🚀 Starting VenueHooper Email Campaign System...")
    print("=" * 50)
    
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check environment
    env_file = project_root / 'config' / '.env'
    if not env_file.exists():
        print("⚠️  .env file not found in config/. Using default configuration.")
    
    # Add src to Python path
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    # Check Playwright
    check_playwright_browsers()
    
    # Start Streamlit
    print("📱 Launching Streamlit web interface...")
    try:
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:8502')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start Streamlit with the new app location
        app_path = project_root / "src" / "ui" / "streamlit_app.py"
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', str(app_path), '--server.port', '8502'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n👋 VenueHooper stopped by user")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        print("\n🔧 Try running manually:")
        print("streamlit run streamlit_app.py")

def show_help():
    """Show available commands"""
    print("🏢 VenueHooper Email Campaign System")
    print("=" * 40)
    print("Available commands:")
    print("  python scripts/start.py           - Start web interface")
    print("  python scripts/start.py --test    - Run system test")
    print("  python scripts/start.py --gmail   - Setup Gmail API")
    print("  python scripts/start.py --help    - Show this help")
    print("\n🚀 Alternative launchers:")
    print("  python main.py                    - Direct app launcher")
    print("\n📚 Documentation:")
    print("  docs/README.md                    - Complete setup guide")
    print("  docs/SETUP_GUIDE.md              - Quick start instructions")

def main():
    """Main startup function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            show_help()
        elif sys.argv[1] == '--test':
            # Get project root and run test from there
            project_root = Path(__file__).parent.parent
            test_script = project_root / 'scripts' / 'test_system.py'
            subprocess.run([sys.executable, str(test_script)])
        elif sys.argv[1] == '--gmail':
            # Get project root and run gmail setup from there
            project_root = Path(__file__).parent.parent
            gmail_script = project_root / 'src' / 'automation' / 'setup_gmail_api.py'
            subprocess.run([sys.executable, str(gmail_script)])
        else:
            print("❌ Unknown command. Use --help for available options.")
    else:
        start_streamlit()

if __name__ == '__main__':
    main()
