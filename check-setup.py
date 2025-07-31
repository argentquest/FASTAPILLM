#!/usr/bin/env python3
"""
Setup verification script for AI Story Generator
"""
import sys
import subprocess
import os
from pathlib import Path

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    return True

def check_virtual_env():
    """Check if in virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ Virtual environment active")
        return True
    else:
        print("⚠️  Virtual environment not detected")
        print("   Activate with: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Linux/Mac)")
        return False

def check_python_deps():
    """Check Python dependencies"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn installed")
        return True
    except ImportError:
        print("❌ Python dependencies missing")
        print("   Install with: pip install -r requirements.txt")
        return False

def check_node():
    """Check Node.js version"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version}")
            # Check if version is 18+
            major_version = int(version.lstrip('v').split('.')[0])
            if major_version >= 18:
                return True
            else:
                print("❌ Node.js 18+ required for React frontend")
                return False
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        print("   Download from: https://nodejs.org/")
        return False

def check_npm():
    """Check npm"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npm {version}")
            return True
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not installed")
        return False

def check_react_deps():
    """Check React frontend dependencies"""
    package_lock = Path("frontendReact/package-lock.json")
    node_modules = Path("frontendReact/node_modules")
    
    if package_lock.exists() and node_modules.exists():
        print("✅ React dependencies installed")
        return True
    else:
        print("⚠️  React dependencies not installed")
        print("   Install with: cd frontendReact && npm install")
        return False

def check_directories():
    """Check if required directories exist"""
    dirs = ["frontend", "frontendReact", "backend", "routes", "services"]
    all_exist = True
    
    for dir_name in dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            all_exist = False
    
    return all_exist

def main():
    print("🔍 AI Story Generator - Setup Check")
    print("=" * 40)
    
    checks = []
    
    # Basic checks
    checks.append(("Python Version", check_python()))
    checks.append(("Virtual Environment", check_virtual_env()))
    checks.append(("Python Dependencies", check_python_deps()))
    checks.append(("Project Structure", check_directories()))
    
    # Node.js checks (for React frontend)
    print("\n📱 React Frontend Requirements:")
    node_ok = check_node()
    npm_ok = check_npm() if node_ok else False
    react_deps_ok = check_react_deps() if npm_ok else False
    
    checks.append(("Node.js", node_ok))
    checks.append(("npm", npm_ok))
    checks.append(("React Dependencies", react_deps_ok))
    
    # Summary
    print("\n📋 Summary:")
    print("-" * 40)
    
    backend_ready = all([checks[i][1] for i in range(4)])  # First 4 checks
    react_ready = all([checks[i][1] for i in range(4, 7)])  # Node.js checks
    
    if backend_ready:
        print("✅ Backend ready - you can run:")
        print("   python run-backends.py")
        print("   python main.py  (original app)")
    else:
        print("❌ Backend not ready - fix the issues above")
    
    print("\n✅ Alpine.js Frontend ready - you can run:")
    print("   cd frontend && python -m http.server 3000")
    
    if react_ready:
        print("\n✅ React Frontend ready - you can run:")
        print("   cd frontendReact && npm run dev")
    else:
        print("\n❌ React Frontend not ready - install Node.js and run 'npm install'")
    
    print("\n🚀 Next Steps:")
    if backend_ready:
        print("1. Start backend: python run-backends.py")
        print("2. Choose a frontend:")
        print("   - Alpine.js: cd frontend && python -m http.server 3000")
        if react_ready:
            print("   - React: cd frontendReact && npm run dev")
    else:
        print("1. Fix the issues above")
        print("2. Then run this check again")

if __name__ == "__main__":
    main()