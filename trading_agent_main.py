
import time
import sys
import logging
import signal
import os
from datetime import datetime, timedelta
from alpaca_trade_api.rest import REST
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib
import asyncio
import threading
import warnings

# Ignore specific FutureWarnings from pandas
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

# Import functions and global variables from the core file
from trading_agent_core import start_stream_thread, trading_strategy_from_stream, historical_data_buffer, latest_data

# Configure logging for 24/7 operation
def setup_logging():
    """Setup comprehensive logging for 24/7 operation."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/trading_agent_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

# Global variables for graceful shutdown
running = True
logger = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    running = False

# Replace with your actual API key and secret key
API_KEY = 'PKG66F7DKPJEO2H1HHF3'
API_SECRET = 'P2GAROcozlav3c8EnaNhNqp26xa7DB3ELInUjTXw'
BASE_URL = 'https://paper-api.alpaca.markets'  # Or 'https://api.alpaca.markets' for live trading

# Instantiate the REST client
api = REST(API_KEY, API_SECRET, BASE_URL)

def load_model_and_scaler():
    """Load the trained model and scaler with error handling."""
    try:
        model = joblib.load('random_forest_model.joblib')
        scaler = joblib.load('scaler.joblib')
        logger.info("Model and scaler loaded successfully.")
        return model, scaler
    except FileNotFoundError:
        logger.error("Error: Model or scaler file not found. Please ensure 'random_forest_model.joblib' and 'scaler.joblib' exist in the same directory.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading model or scaler: {e}")
        sys.exit(1)

def reconstruct_feature_columns():
    """Reconstruct feature columns for model alignment."""
    try:
        tickers = ['EURUSD', 'GBPUSD', 'JPY', 'GC=F', 'CL=F', 'SPY', 'DIA']
        original_cols_tuples = [(col_type, ticker) for col_type in ['Open', 'High', 'Low', 'Close', 'Volume'] for ticker in tickers]

        # Create feature names based on the tickers and feature engineering logic
        feature_suffixes = ['_Return', '_SMA_5', '_SMA_20', '_Lag_1', '_Lag_3', '_Lag_5']
        feature_cols_tuples = []
        for ticker in tickers:
             for suffix in feature_suffixes:
                  feature_cols_tuples.append((f"('Close', '{ticker}')", suffix))

        # Convert tuple columns to strings for consistency and combine
        all_cols_str = [str(col) for col in original_cols_tuples] + [f"{col[0]}{col[1]}" for col in feature_cols_tuples]

        # Remove the target variable ('Close', 'EURUSD') and get unique columns
        X_columns = pd.Index([col for col in all_cols_str if col != "('Close', 'EURUSD')"]).unique()

        logger.info("Reconstructed X_columns for feature alignment.")
        logger.info(f"Expected Feature Columns ({len(X_columns)}): {list(X_columns)}")
        return X_columns

    except Exception as e:
        logger.error(f"Error reconstructing X_columns: {e}")
        logger.error("Please ensure X.columns is saved during training and loaded here for robust feature alignment.")
        return pd.Index([])

def check_market_hours():
    """Check if the market is currently open."""
    try:
        clock = api.get_clock()
        return clock.is_open
    except Exception as e:
        logger.warning(f"Could not check market hours: {e}")
        return True  # Assume market is open if we can't check

def execute_trading_agent_loop(api, model, scaler, X_columns, initial_capital=10000, threshold=0.001, interval_seconds=60, stop_loss_pct=0.005, take_profit_pct=0.01):
    """
    Runs the trading agent logic in a continuous loop with enhanced error handling for 24/7 operation.
    """
    global running
    
    logger.info("Starting trading agent loop...")
    
    # Track performance metrics
    iteration_count = 0
    last_successful_iteration = datetime.now()
    consecutive_errors = 0
    max_consecutive_errors = 5

    # Start the data stream in a separate thread
    stream_thread = start_stream_thread(API_KEY, API_SECRET)
    logger.info("Data stream started in a separate thread.")

    # Give the stream some time to connect and buffer data
    logger.info("Waiting for data stream to buffer initial data...")
    time.sleep(30)
    logger.info("Finished waiting for data stream.")

    while running:
        iteration_start = datetime.now()
        iteration_count += 1
        
        try:
            logger.info(f"Executing trading agent iteration #{iteration_count}...")
            
            # Check if market is open (optional - you can remove this for 24/7 forex trading)
            if not check_market_hours():
                logger.info("Market is closed. Waiting for next iteration...")
                time.sleep(interval_seconds)
                continue

            # Generate trading signal using the data buffer
            signal, current_price, predicted_price = trading_strategy_from_stream(model, scaler, X_columns)

            if signal == "hold" and current_price == 0 and predicted_price == 0:
                logger.warning("Not enough data in buffer to generate features or EURUSD price not available. Holding position.")
                time.sleep(interval_seconds)
                continue

            logger.info(f"Signal: {signal}, Current Price: {current_price:.5f}, Predicted Price: {predicted_price:.5f}")

            # Get account information
            try:
                account = api.get_account()
                equity = float(account.equity)
                cash = float(account.cash)
                logger.info(f"Account Equity: ${equity:.2f}, Available Cash: ${cash:.2f}")
            except Exception as e:
                logger.error(f"Error fetching account information: {e}")
                equity = initial_capital
                cash = initial_capital

            # Get current position
            try:
                position = api.get_position('EURUSD')
                current_position_qty = float(position.qty)
                logger.info(f"Current EURUSD Position: {current_position_qty}")
            except Exception as e:
                current_position_qty = 0
                logger.info("No current EURUSD position.")

            # Execute trades based on signal and position
            if signal == "buy" and current_position_qty == 0:
                # Calculate the number of shares to buy based on a percentage of equity
                order_value = equity * 0.10
                order_size = order_value / current_price if current_price > 0 else 0
                order_size = int(order_size)

                if order_size > 0:
                    # Calculate stop-loss and take-profit prices
                    stop_loss_price = round(current_price * (1 - stop_loss_pct), 5)
                    take_profit_price = round(current_price * (1 + take_profit_pct), 5)

                    logger.info(f"Calculated Stop-Loss Price: {stop_loss_price:.5f}, Take-Profit Price: {take_profit_price:.5f}")
                    logger.info(f"Calculated Order Size (based on 10% equity): {order_size} shares")

                    try:
                        # Cancel any open orders before placing a new one
                        api.cancel_all_orders()
                        logger.info("Cancelled all open orders.")
                    except Exception as e:
                        logger.error(f"Error cancelling orders: {e}")

                    try:
                        api.submit_order(
                            symbol='EURUSD',
                            qty=order_size,
                            side='buy',
                            type='market',
                            time_in_force='day',
                            stop_loss={'stop_price': stop_loss_price},
                            take_profit={'limit_price': take_profit_price}
                        )
                        logger.info("Submitted BUY order with Stop-Loss and Take-Profit.")
                    except Exception as e:
                        logger.error(f"Error submitting BUY order with SL/TP: {e}")
                else:
                    logger.warning("Calculated order size is not positive. Not placing a buy order.")

            elif signal == "sell" and current_position_qty > 0:
                try:
                    # Cancel any open orders before selling
                    api.cancel_all_orders()
                    logger.info("Cancelled all open orders.")
                except Exception as e:
                    logger.error(f"Error cancelling orders before sell: {e}")

                try:
                    api.submit_order(
                        symbol='EURUSD',
                        qty=current_position_qty,
                        side='sell',
                        type='market',
                        time_in_force='ioc'
                    )
                    logger.info(f"Submitted SELL order for {current_position_qty:.2f} shares of EURUSD at market price.")
                except Exception as e:
                    logger.error(f"Error submitting SELL order: {e}")

            elif signal == "hold":
                logger.info("Holding current position.")

            # Reset error counter on successful iteration
            consecutive_errors = 0
            last_successful_iteration = datetime.now()

        except Exception as e:
            consecutive_errors += 1
            logger.error(f"An unexpected error occurred during trading agent execution: {e}")
            
            # If too many consecutive errors, consider restarting
            if consecutive_errors >= max_consecutive_errors:
                logger.critical(f"Too many consecutive errors ({consecutive_errors}). Consider restarting the agent.")
                # You could implement automatic restart logic here
                
            # Check if we've been running too long without success
            if datetime.now() - last_successful_iteration > timedelta(hours=2):
                logger.warning("No successful iterations in the last 2 hours. Checking system health...")

        # Calculate sleep time to maintain consistent intervals
        iteration_duration = (datetime.now() - iteration_start).total_seconds()
        sleep_time = max(0, interval_seconds - iteration_duration)
        
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            logger.warning(f"Iteration took longer than interval ({iteration_duration:.2f}s > {interval_seconds}s)")

def main():
    """Main function to run the trading agent with proper setup and error handling."""
    global logger, running
    
    # Setup logging
    logger = setup_logging()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=== Trading Agent Starting ===")
    logger.info(f"API Key: {API_KEY[:8]}...")
    logger.info(f"Base URL: {BASE_URL}")
    
    try:
        # Load model and scaler
        model, scaler = load_model_and_scaler()
        
        # Reconstruct feature columns
        X_columns = reconstruct_feature_columns()
        
        # Run the trading agent loop
        execute_trading_agent_loop(
            api, model, scaler, X_columns, 
            interval_seconds=60, 
            stop_loss_pct=0.005, 
            take_profit_pct=0.01
        )
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise
    finally:
        logger.info("=== Trading Agent Shutdown Complete ===")

if __name__ == "__main__":
    main()
