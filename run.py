# run.py
import subprocess
import sys
import os
import threading
import webbrowser
import time

def run_backend():
    os.chdir('backend')
    subprocess.run([sys.executable, '-m', 'uvicorn', 'main:app', '--reload'])

def run_frontend():
    os.chdir('frontend')
    subprocess.run([sys.executable, '-m', 'http.server', '3000'])

if __name__ == "__main__":
    print("🚀 Starting Personal Finance Tracker...")
    
    # Start backend in background
    threading.Thread(target=run_backend, daemon=True).start()
    time.sleep(2)
    
    # Start frontend in background
    threading.Thread(target=run_frontend, daemon=True).start()
    time.sleep(2)
    
    # Open browser automatically
    webbrowser.open('http://localhost:3000')
    
    print("✅ Running at http://localhost:3000")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)
