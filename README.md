# Trading Agent 24/7 Operation Guide

This guide explains how to run your trading agent continuously 24/7 with automatic restart capabilities and monitoring.

## 🚀 Quick Start

### Option 1: Windows Batch File (Easiest)
```bash
# Double-click or run:
start_agent.bat
```

### Option 2: PowerShell Script (Recommended for Windows)
```powershell
# Right-click and "Run with PowerShell" or run:
.\start_agent.ps1
```

### Option 3: Direct Python Execution
```bash
# Run the agent directly:
python run_agent_24_7.py

# Or run the main agent:
python trading_agent_main.py
```

## 📁 File Structure

```
trading_agent/
├── trading_agent_main.py      # Main trading agent (improved for 24/7)
├── trading_agent_core.py      # Core trading logic and data streaming
├── run_agent_24_7.py         # 24/7 runner with auto-restart
├── monitor_agent.py          # Monitoring and status checking
├── start_agent.bat           # Windows batch file
├── start_agent.ps1           # PowerShell script
├── requirements.txt          # Python dependencies
├── random_forest_model.joblib # Trained ML model
├── scaler.joblib            # Data scaler
└── logs/                    # Log files directory (created automatically)
```

## 🔧 Features for 24/7 Operation

### ✅ Enhanced Error Handling
- Graceful shutdown on Ctrl+C
- Automatic restart on crashes
- Consecutive error tracking
- Health monitoring

### ✅ Comprehensive Logging
- Timestamped log files in `logs/` directory
- Both file and console output
- Automatic log rotation

### ✅ Process Monitoring
- CPU and memory usage tracking
- Uptime monitoring
- Automatic restart after 6 hours of no output

### ✅ Risk Management
- Stop-loss and take-profit orders
- Position size limits (10% of equity)
- Market hours checking (optional)

## 📊 Monitoring Your Agent

### Check Agent Status
```bash
python monitor_agent.py
```

### Continuous Monitoring
```bash
python monitor_agent.py --watch --interval 30
```

### View Recent Logs
```bash
# Check the latest log file
tail -f logs/trading_agent_*.log
```

## ⚙️ Configuration

### Environment Variables
You can customize the behavior using environment variables:

```bash
# Set maximum restart attempts (default: 10)
set MAX_RESTARTS=20

# Set restart delay in seconds (default: 60)
set RESTART_DELAY=30

# Then run the agent
python run_agent_24_7.py
```

### Trading Parameters
Edit `trading_agent_main.py` to modify:
- `interval_seconds`: Time between trading decisions (default: 60)
- `stop_loss_pct`: Stop-loss percentage (default: 0.5%)
- `take_profit_pct`: Take-profit percentage (default: 1.0%)
- Position size: Currently 10% of equity per trade

## 🛡️ Safety Features

### Automatic Restart
- Restarts automatically if the agent crashes
- Maximum restart attempts (default: 10)
- Configurable restart delay

### Error Recovery
- Tracks consecutive errors
- Warns if too many errors occur
- Graceful handling of API failures

### Logging and Monitoring
- All activities logged with timestamps
- Process monitoring with resource usage
- Account balance tracking

## 🔍 Troubleshooting

### Common Issues

1. **Agent won't start**
   - Check if all required files exist
   - Verify Python and dependencies are installed
   - Check API credentials in the code

2. **Agent keeps restarting**
   - Check logs for error messages
   - Verify internet connection
   - Check Alpaca API status

3. **No trading activity**
   - Check if market is open (for stocks)
   - Verify data stream is working
   - Check account balance and buying power

### Log Files
- Check `logs/trading_agent_*.log` for detailed error messages
- Check `agent_runner.log` for restart information

### API Issues
- Verify your Alpaca API credentials
- Check if you're using paper trading vs live trading
- Ensure your account has sufficient funds

## 🚨 Important Notes

### Paper Trading
- The agent is configured for **paper trading** by default
- Change `BASE_URL` to `'https://api.alpaca.markets'` for live trading
- **Test thoroughly on paper trading before going live**

### Risk Warning
- This is automated trading software
- Always monitor your agent's performance
- Start with small position sizes
- Be prepared for potential losses

### System Requirements
- Python 3.7+
- Stable internet connection
- Sufficient system resources (CPU/Memory)
- Windows 10/11 (for batch/PowerShell scripts)

## 📈 Performance Monitoring

### Key Metrics to Watch
- Account equity changes
- Win/loss ratio
- Maximum drawdown
- CPU and memory usage
- API response times

### Recommended Monitoring Schedule
- Check status every 30 minutes initially
- Review logs daily
- Monitor account balance regularly
- Set up alerts for unusual activity

## 🔄 Maintenance

### Regular Tasks
- Monitor log files for errors
- Check account performance
- Update dependencies as needed
- Backup configuration and logs

### Updates
- Keep your Python packages updated
- Monitor for Alpaca API changes
- Review and adjust trading parameters

## 📞 Support

If you encounter issues:
1. Check the log files first
2. Use the monitoring script to diagnose problems
3. Verify your API credentials and account status
4. Test with paper trading before live trading

---

**Remember: Automated trading involves risk. Always start with paper trading and monitor your agent's performance closely.** 
