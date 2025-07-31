#!/usr/bin/env python3
"""
Development script to start both frontend and backend services
"""
import subprocess
import sys
import os
import time
import signal
from threading import Thread

def run_backend():
    """Run the backend service"""
    print("🚀 Starting Backend on http://localhost:8000")
    os.chdir("backend")
    subprocess.run([sys.executable, "main.py"])

def run_frontend():
    """Run the frontend service"""
    print("🌐 Starting Frontend on http://localhost:3000")
    os.chdir("frontend")
    subprocess.run([sys.executable, "-m", "http.server", "3000"])

def main():
    print("🔧 Starting AI Story Generator - Development Mode")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(2)
    
    # Start frontend in a separate thread
    frontend_thread = Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    
    print("\n✅ Services started!")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/api/docs")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        sys.exit(0)

if __name__ == "__main__":
    main()