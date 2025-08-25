
#!/usr/bin/env python3
import os
import signal
import psutil

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

if __name__ == "__main__":
    stop_all_bot_instances()
    print("All bot instances stopped")
