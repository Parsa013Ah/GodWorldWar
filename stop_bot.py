
#!/usr/bin/env python3
import os
import signal
import psutil
from database import Database

def stop_all_bot_instances():
    """Stop all running bot instances"""
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any('main.py' in cmd for cmd in proc.info['cmdline']):
                if proc.info['pid'] != current_pid:
                    print(f"Stopping bot process PID: {proc.info['pid']}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def cleanup_test_data():
    """Clean up test data from database"""
    try:
        db = Database()
        db.initialize()
        result = db.clear_test_data()
        if result:
            print("✅ Test data cleaned successfully")
        else:
            print("❌ Failed to clean test data")
    except Exception as e:
        print(f"❌ Error cleaning test data: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--clean-test":
        cleanup_test_data()
    else:
        stop_all_bot_instances()
        print("All bot instances stopped")
