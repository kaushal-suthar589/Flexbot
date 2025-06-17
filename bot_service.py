#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys

class BotService:
    def __init__(self):
        self.bot_script = "production_bot.py"
        self.python_path = "/home/runner/workspace/.pythonlibs/bin/python3"
        self.process = None
        self.running = True
        
    def start_bot(self):
        """Start the bot process"""
        try:
            print("Starting FlexBot service...")
            self.process = subprocess.Popen(
                [self.python_path, self.bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            print(f"Bot started with PID: {self.process.pid}")
            return True
        except Exception as e:
            print(f"Failed to start bot: {e}")
            return False
    
    def is_bot_running(self):
        """Check if bot process is still running"""
        if self.process is None:
            return False
        return self.process.poll() is None
    
    def stop_bot(self):
        """Stop the bot process"""
        if self.process and self.is_bot_running():
            print("Stopping bot...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("Force killing bot...")
                self.process.kill()
            print("Bot stopped")
    
    def restart_bot(self):
        """Restart the bot"""
        print("Restarting bot...")
        self.stop_bot()
        time.sleep(2)
        return self.start_bot()
    
    def monitor(self):
        """Monitor bot and restart if needed"""
        print("FlexBot 24/7 Service Started")
        print("Monitoring bot health...")
        
        # Start bot initially
        if not self.start_bot():
            print("Failed to start bot initially")
            return
        
        while self.running:
            try:
                if not self.is_bot_running():
                    print("Bot process died, restarting...")
                    if not self.restart_bot():
                        print("Failed to restart, waiting 30 seconds...")
                        time.sleep(30)
                        continue
                
                # Check every 30 seconds
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\nShutdown requested...")
                self.running = False
                self.stop_bot()
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(10)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False
        self.stop_bot()
        sys.exit(0)

def main():
    service = BotService()
    
    # Handle shutdown signals
    signal.signal(signal.SIGINT, service.signal_handler)
    signal.signal(signal.SIGTERM, service.signal_handler)
    
    try:
        service.monitor()
    except Exception as e:
        print(f"Service error: {e}")
    finally:
        service.stop_bot()

if __name__ == "__main__":
    main()