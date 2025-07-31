#!/usr/bin/env python3
"""Simple script to test if the backend is running"""
import requests
import sys

def test_backend():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Backend is running! Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT running - Connection refused")
        print("Please start the backend with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

if __name__ == "__main__":
    if not test_backend():
        sys.exit(1)