
#!/usr/bin/env python3
import subprocess
import time
import os

def run_bot_forever():
    """Simple permanent bot runner for free trial"""
    print("🎯 FlexBot Quick Permanent Host")
    print("⚡ Free Trial - Continuous Operation")
    print("🔄 Auto-restart enabled")
    print("")
    
    bot_file = "enhanced_bot.py"
    restart_count = 0
    
    while True:
        try:
            restart_count += 1
            print(f"🚀 Starting bot (Run #{restart_count})...")
            
            # Start bot process
            process = subprocess.run([
                "python3", bot_file
            ], capture_output=True, text=True)
            
            print(f"⚠️ Bot stopped with code: {process.returncode}")
            if process.stdout:
                print(f"Output: {process.stdout[-200:]}")  # Last 200 chars
            if process.stderr:
                print(f"Error: {process.stderr[-200:]}")   # Last 200 chars
            
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("🛑 Stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot_forever()
