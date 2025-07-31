#!/usr/bin/env python3
"""Diagnose backend issues"""
import subprocess
import sys
import os
import socket

def check_port(port=8000):
    """Check if port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import structlog
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_env():
    """Check environment variables"""
    required = ["OPENROUTER_API_KEY", "AZURE_OPENAI_KEY"]
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"⚠️  Missing environment variables: {', '.join(missing)}")
        print("   This may prevent some features from working")
    else:
        print("✅ Environment variables configured")

def main():
    print("🔍 Diagnosing backend setup...\n")
    
    # Check if backend is already running
    if check_port(8000):
        print("✅ Backend is already running on port 8000!")
        print("   Try accessing: http://localhost:8000/health")
        return
    
    print("❌ Backend is NOT running on port 8000\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\n📦 Install dependencies with:")
        print("   pip install -r requirements.txt")
        return
    
    # Check environment
    check_env()
    
    print("\n🚀 To start the backend, run ONE of these commands:")
    print("   1. python main.py")
    print("   2. python run-backends.py")
    print("   3. uvicorn main:app --reload")
    
    print("\n💡 Make sure you're in the root directory:")
    print(f"   cd {os.path.dirname(os.path.abspath(__file__))}")

if __name__ == "__main__":
    main()