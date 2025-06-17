
#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys
import logging
from datetime import datetime

class PermanentBotHost:
    def __init__(self):
        self.bot_script = "enhanced_bot.py"  # Using your enhanced bot
        self.python_path = "python3"
        self.process = None
        self.running = True
        self.restart_count = 0
        self.max_restarts = 1000  # Allow many restarts for continuous operation
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_host.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start_bot(self):
        """Start the bot process"""
        try:
            self.logger.info("🚀 Starting FlexBot Premium Services...")
            self.process = subprocess.Popen(
                [self.python_path, self.bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd(),
                bufsize=1,
                universal_newlines=True
            )
            self.logger.info(f"✅ Bot started with PID: {self.process.pid}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to start bot: {e}")
            return False
    
    def is_bot_running(self):
        """Check if bot process is still running"""
        if self.process is None:
            return False
        return self.process.poll() is None
    
    def stop_bot(self):
        """Stop the bot process gracefully"""
        if self.process and self.is_bot_running():
            self.logger.info("🛑 Stopping bot gracefully...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
                self.logger.info("✅ Bot stopped gracefully")
            except subprocess.TimeoutExpired:
                self.logger.warning("⚠️ Force killing bot...")
                self.process.kill()
                self.process.wait()
                self.logger.info("💀 Bot force killed")
    
    def restart_bot(self):
        """Restart the bot"""
        self.restart_count += 1
        self.logger.info(f"🔄 Restarting bot (Restart #{self.restart_count})...")
        
        if self.restart_count > self.max_restarts:
            self.logger.error("❌ Maximum restart limit reached. Stopping service.")
            self.running = False
            return False
            
        self.stop_bot()
        time.sleep(3)  # Wait before restart
        return self.start_bot()
    
    def monitor_and_log_output(self):
        """Monitor bot output and log it"""
        if self.process and self.process.stdout:
            try:
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        self.logger.info(f"BOT: {line.strip()}")
                    if not self.is_bot_running():
                        break
            except Exception as e:
                self.logger.error(f"Error reading bot output: {e}")
    
    def run_permanent_host(self):
        """Main hosting loop - runs forever"""
        self.logger.info("🌟 FlexBot Permanent Hosting Service Started")
        self.logger.info("📅 Free Trial Period - Maximum Uptime Enabled")
        self.logger.info("🔄 Auto-restart enabled with unlimited attempts")
        self.logger.info("💾 Logs saved to bot_host.log")
        
        # Start bot initially
        if not self.start_bot():
            self.logger.error("❌ Failed to start bot initially")
            return
        
        # Main hosting loop
        while self.running:
            try:
                # Check if bot is still running
                if not self.is_bot_running():
                    self.logger.warning("⚠️ Bot process died, initiating restart...")
                    
                    if not self.restart_bot():
                        self.logger.error("❌ Failed to restart, waiting 30 seconds...")
                        time.sleep(30)
                        continue
                
                # Health check every 30 seconds
                time.sleep(30)
                
                # Log status every 10 minutes
                if self.restart_count % 20 == 0:
                    uptime_msg = f"💚 Bot running healthy | Restarts: {self.restart_count} | PID: {self.process.pid if self.process else 'None'}"
                    self.logger.info(uptime_msg)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Shutdown requested by user...")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"❌ Monitor error: {e}")
                time.sleep(10)
        
        # Cleanup
        self.stop_bot()
        self.logger.info("🏁 Permanent hosting service stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"📡 Received signal {signum}, shutting down...")
        self.running = False
        self.stop_bot()
        sys.exit(0)

def main():
    """Main function to start permanent hosting"""
    print("🎯 FlexBot Permanent Hosting Service")
    print("⏰ Free Trial - Maximum Uptime Configuration")
    print("🔥 Starting in 3 seconds...")
    time.sleep(3)
    
    # Create hosting service
    host_service = PermanentBotHost()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, host_service.signal_handler)
    signal.signal(signal.SIGTERM, host_service.signal_handler)
    
    try:
        # Start permanent hosting
        host_service.run_permanent_host()
    except Exception as e:
        print(f"❌ Critical hosting error: {e}")
    finally:
        host_service.stop_bot()
        print("🔚 Hosting service terminated")

if __name__ == "__main__":
    main()
