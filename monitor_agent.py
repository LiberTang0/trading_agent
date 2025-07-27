#!/usr/bin/env python3
"""
Trading Agent Monitor
This script monitors the status and performance of the trading agent.
"""

import os
import psutil
import time
import json
from datetime import datetime, timedelta
import glob

def find_agent_process():
    """Find the trading agent process if it's running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'trading_agent_main.py' in ' '.join(cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def get_latest_log_file():
    """Get the most recent log file."""
    log_files = glob.glob('logs/trading_agent_*.log')
    if not log_files:
        return None
    return max(log_files, key=os.path.getctime)

def get_agent_status():
    """Get the current status of the trading agent."""
    process = find_agent_process()
    
    if process:
        try:
            # Get process info
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            create_time = datetime.fromtimestamp(process.create_time())
            uptime = datetime.now() - create_time
            
            return {
                'status': 'running',
                'pid': process.pid,
                'cpu_percent': cpu_percent,
                'memory_mb': memory_info.rss / 1024 / 1024,
                'uptime': str(uptime).split('.')[0],  # Remove microseconds
                'start_time': create_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {'status': 'error', 'message': 'Cannot access process information'}
    else:
        return {'status': 'stopped'}

def get_recent_logs(lines=20):
    """Get recent log entries."""
    log_file = get_latest_log_file()
    if not log_file:
        return []
    
    try:
        with open(log_file, 'r') as f:
            lines_list = f.readlines()
            return lines_list[-lines:] if len(lines_list) > lines else lines_list
    except Exception as e:
        return [f"Error reading log file: {e}"]

def get_account_info():
    """Get basic account information (if API is available)."""
    try:
        from alpaca_trade_api.rest import REST
        
        # You'll need to import your API credentials here
        API_KEY = 'PKG66F7DKPJEO2H1HHF3'
        API_SECRET = 'P2GAROcozlav3c8EnaNhNqp26xa7DB3ELInUjTXw'
        BASE_URL = 'https://paper-api.alpaca.markets'
        
        api = REST(API_KEY, API_SECRET, BASE_URL)
        account = api.get_account()
        
        return {
            'equity': float(account.equity),
            'cash': float(account.cash),
            'buying_power': float(account.buying_power),
            'account_status': account.status
        }
    except Exception as e:
        return {'error': str(e)}

def print_status():
    """Print the current status of the trading agent."""
    print("=" * 60)
    print("TRADING AGENT MONITOR")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Agent Status
    status = get_agent_status()
    print("AGENT STATUS:")
    print("-" * 20)
    if status['status'] == 'running':
        print(f"✅ Status: {status['status'].upper()}")
        print(f"   PID: {status['pid']}")
        print(f"   CPU: {status['cpu_percent']:.1f}%")
        print(f"   Memory: {status['memory_mb']:.1f} MB")
        print(f"   Uptime: {status['uptime']}")
        print(f"   Started: {status['start_time']}")
    elif status['status'] == 'stopped':
        print("❌ Status: STOPPED")
        print("   The trading agent is not currently running.")
    else:
        print(f"⚠️  Status: {status['status'].upper()}")
        print(f"   Error: {status.get('message', 'Unknown error')}")
    
    print()
    
    # Account Information
    print("ACCOUNT INFORMATION:")
    print("-" * 20)
    account_info = get_account_info()
    if 'error' not in account_info:
        print(f"💰 Equity: ${account_info['equity']:,.2f}")
        print(f"💵 Cash: ${account_info['cash']:,.2f}")
        print(f"💳 Buying Power: ${account_info['buying_power']:,.2f}")
        print(f"📊 Status: {account_info['account_status']}")
    else:
        print(f"❌ Error: {account_info['error']}")
    
    print()
    
    # Recent Logs
    print("RECENT LOGS:")
    print("-" * 20)
    logs = get_recent_logs(10)
    if logs:
        for log in logs:
            print(log.rstrip())
    else:
        print("No log files found.")
    
    print()
    print("=" * 60)

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Trading Agent')
    parser.add_argument('--watch', action='store_true', help='Watch mode - continuously monitor')
    parser.add_argument('--interval', type=int, default=30, help='Update interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    if args.watch:
        print("Starting monitor in watch mode. Press Ctrl+C to stop.")
        try:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
                print_status()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitor stopped.")
    else:
        print_status()

if __name__ == "__main__":
    main() 