#!/usr/bin/env python3
"""
Start the Project AI Governance Backend

Usage:
    python start_api.py              # Development mode
    python start_api.py --prod       # Production mode
"""

import sys
import subprocess

def start_dev():
    """Start in development mode with auto-reload"""
    print("🚀 Starting Project AI Governance Backend (Development)")
    print("📍 API: http://localhost:8001")
    print("📚 Docs: http://localhost:8001/docs")
    print("")
    
    subprocess.run([
        "uvicorn",
        "api.main:app",
        "--host", "0.0.0.0",
        "--port", "8001",
        "--reload",
        "--log-level", "info"
    ])

def start_prod():
    """Start in production mode"""
    print("🚀 Starting Project AI Governance Backend (Production)")
    print("📍 API: http://localhost:8001")
    print("")
    
    subprocess.run([
        "gunicorn",
        "api.main:app",
        "--workers", "4",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--bind", "0.0.0.0:8001",
        "--log-level", "info"
    ])

if __name__ == "__main__":
    if "--prod" in sys.argv:
        start_prod()
    else:
        start_dev()
