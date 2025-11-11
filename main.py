#!/usr/bin/env python3
"""
VenueHooper - Main Application Launcher
Starts the Streamlit web application for venue email campaigns
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Add src to Python path
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    # Change to project directory
    os.chdir(project_root)
    
    # Launch Streamlit app
    app_path = project_root / "src" / "ui" / "streamlit_app.py"
    
    print("🚀 Starting VenueHooper Email Campaign System...")
    print(f"📁 Project directory: {project_root}")
    print(f"🎯 App path: {app_path}")
    print("🌐 Opening in browser...")
    
    # Run streamlit (cloud deployment will use default port)
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        str(app_path)
    ])

if __name__ == "__main__":
    main()
