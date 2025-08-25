
#!/usr/bin/env python3
import subprocess
import sys
import time

def run_clean_tests():
    """Run tests with clean environment"""
    print("🛑 Stopping any running bot instances...")
    subprocess.run([sys.executable, "stop_bot.py"], capture_output=True)
    
    print("🧹 Cleaning test data...")
    subprocess.run([sys.executable, "stop_bot.py", "--clean-test"], capture_output=True)
    
    print("⏱️  Waiting for cleanup...")
    time.sleep(2)
    
    print("🚀 Running comprehensive tests...")
    result = subprocess.run([sys.executable, "test_bot.py"])
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_clean_tests()
    sys.exit(exit_code)
