"""
HazWaste Sorter - Quick Launcher
Starts the server and automatically opens the application in your default browser.
"""

import sys
import webbrowser
import threading
import time
import uvicorn
from server import app

def open_browser():
    time.sleep(1.2)
    print("Opening browser at http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 65)
    print("✈️  HazWaste Sorter - Aircraft Maintenance Hangar")
    print("   Starting local server at: http://localhost:8000")
    print("   Press Ctrl+C to stop.")
    print("=" * 65)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
