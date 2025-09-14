#!/usr/bin/env python3
"""
RCA Agent Web Server Launcher

This script starts the FastAPI server for the RCA Agent web interface.

Usage:
    python serve.py

The server will start on http://127.0.0.1:8000
Open web/index.html in your browser to access the dashboard.
"""
import uvicorn
import sys
from pathlib import Path

def main():
    """Start the RCA Agent API server."""
    print("🚀 Starting RCA Agent Web Server...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("🌐 Open web/index.html in your browser to access the dashboard")
    print("📚 API documentation available at: http://127.0.0.1:8000/docs")
    print("🔄 Server will auto-reload on code changes")
    print("-" * 60)
    
    try:
        uvicorn.run(
            "rca.api:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
