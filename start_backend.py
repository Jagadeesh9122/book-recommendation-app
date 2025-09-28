#!/usr/bin/env python3
"""
Startup script for the Book Recommendation System Backend
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing backend requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Backend requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def start_server():
    """Start the FastAPI server"""
    print("Starting FastAPI server...")
    try:
        # Change to backend directory
        os.chdir("backend")
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    print("🚀 Starting Book Recommendation System Backend")
    print("=" * 50)
    
    if install_requirements():
        start_server()
    else:
        print("❌ Failed to start backend. Please check the error messages above.")
        sys.exit(1)
