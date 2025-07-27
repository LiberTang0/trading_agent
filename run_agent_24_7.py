#!/usr/bin/env python3
"""
24/7 Trading Agent Runner
This script runs the trading agent continuously with automatic restart capabilities.
"""

import subprocess
import sys
import time
import signal
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_runner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TradingAgentRunner:
    def __init__(self, max_restarts=10, restart_delay=60):
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.restart_count = 0
        self.process = None
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Shutting down agent runner...")
        self.running = False
        if self.process:
            self.process.terminate()
    
    def start_agent(self):
        """Start the trading agent process."""
        try:
            logger.info("Starting trading agent...")
            self.process = subprocess.Popen(
                [sys.executable, 'trading_agent_main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            logger.info(f"Trading agent started with PID: {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start trading agent: {e}")
            return False
    
    def monitor_agent(self):
        """Monitor the trading agent process and restart if needed."""
        while self.running and self.restart_count < self.max_restarts:
            if not self.start_agent():
                logger.error("Failed to start agent. Exiting...")
                break
            
            # Monitor the process
            start_time = datetime.now()
            while self.running and self.process.poll() is None:
                # Check if process has been running for too long without output
                if datetime.now() - start_time > timedelta(hours=6):
                    logger.warning("Agent has been running for 6+ hours without output. Restarting...")
                    break
                
                time.sleep(30)  # Check every 30 seconds
            
            # Process has ended
            if self.process.poll() is not None:
                return_code = self.process.returncode
                logger.info(f"Trading agent process ended with return code: {return_code}")
                
                if return_code == 0:
                    logger.info("Agent exited normally. Restarting...")
                else:
                    logger.warning(f"Agent exited with error code {return_code}. Restarting...")
            
            self.restart_count += 1
            
            if self.restart_count >= self.max_restarts:
                logger.error(f"Maximum restart attempts ({self.max_restarts}) reached. Stopping.")
                break
            
            if self.running:
                logger.info(f"Waiting {self.restart_delay} seconds before restart {self.restart_count}/{self.max_restarts}...")
                time.sleep(self.restart_delay)
    
    def run(self):
        """Main run method."""
        logger.info("=== Trading Agent Runner Starting ===")
        logger.info(f"Max restarts: {self.max_restarts}")
        logger.info(f"Restart delay: {self.restart_delay} seconds")
        
        try:
            self.monitor_agent()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            if self.process and self.process.poll() is None:
                logger.info("Terminating trading agent process...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning("Process didn't terminate gracefully. Force killing...")
                    self.process.kill()
            
            logger.info("=== Trading Agent Runner Shutdown Complete ===")

def main():
    """Main function."""
    # You can customize these parameters
    max_restarts = int(os.environ.get('MAX_RESTARTS', '10'))
    restart_delay = int(os.environ.get('RESTART_DELAY', '60'))
    
    runner = TradingAgentRunner(max_restarts=max_restarts, restart_delay=restart_delay)
    runner.run()

if __name__ == "__main__":
    main() 