import sys
import traceback
import os
from datetime import datetime

LOG_FILE = "error.log"

def setup_exception_hook():
    sys.excepthook = exception_hook

def exception_hook(exctype, value, tb):
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(error_msg, file=sys.stderr)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] CRITICAL ERROR:\n")
            f.write(error_msg)
            f.write("-" * 80 + "\n")
    except Exception as e:
        print(f"Failed to write to log: {e}", file=sys.stderr)

def log_info(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] INFO: {message}\n")
    except:
        pass
