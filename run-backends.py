#!/usr/bin/env python3
"""
Simple script to run backend from the correct directory with proper imports
"""
import sys
import os

# Add the current directory to Python path so imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import and run the original main
from main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AI Story Generator Backend API")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/api/docs")
    print("💡 Press Ctrl+C to stop")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Use our custom logging
        log_level="debug"  # Enable debug logging
    )