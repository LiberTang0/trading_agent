
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import asyncio
from alpaca_trade_api.stream import Stream
import warnings # Import warnings

# Ignore specific FutureWarnings from pandas
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")


# Define the list of tickers to subscribe to
forex_tickers = ['EURUSD'] # Alpaca uses just the pair symbol for forex
stock_tickers = ['SPY', 'DIA'] # Using SPY and DIA as proxies for ^GSPC and ^DJI as Alpaca doesn't directly support index futures/spot

# Dictionary to store the latest data for each ticker
latest_data = {ticker: {'close': None, 'timestamp': None} for ticker in forex_tickers + stock_tickers}
historical_data_buffer = {ticker: pd.DataFrame(columns=['Close']) for ticker in forex_tickers + stock_tickers} # Initialize buffer


async def update_data_buffer(symbol, price, timestamp):
    """Updates the historical data buffer with the latest price."""
    # Append new data as a new row with timestamp as index
    # Ensure timestamp is in datetime format
    timestamp_dt = pd.to_datetime(timestamp)
    new_row = pd.DataFrame({'Close': price}, index=[timestamp_dt])
    historical_data_buffer[symbol] = pd.concat([historical_data_buffer[symbol], new_row])
    # Keep only the most recent data required for feature engineering (e.g., last 60 days)
    historical_data_buffer[symbol] = historical_data_buffer[symbol].last('60D')


async def trade_updates_handler(trade):
    """Handles incoming trade updates."""
    symbol = trade.symbol
    price = trade.price
    timestamp = trade.timestamp
    if symbol in [t.replace('USD', '') for t in forex_tickers]: # Handle forex symbols
         symbol = symbol + 'USD'
    latest_data[symbol]['close'] = price
    latest_data[symbol]['timestamp'] = timestamp
    await update_data_buffer(symbol, price, timestamp)


async def bar_updates_handler(bar):
    """Handles incoming bar updates."""
    symbol = bar.symbol
    close_price = bar.close
    timestamp = bar.timestamp
    if symbol in [t.replace('USD', '') for t in forex_tickers]: # Handle forex symbols
         symbol = symbol + 'USD'
    latest_data[symbol]['close'] = close_price
    latest_data[symbol]['timestamp'] = timestamp
    await update_data_buffer(symbol, close_price, timestamp)


async def start_stream(api_key, api_secret):
    """Starts the WebSocket data stream."""
    # Create a single stream for both forex and stocks
    # The newer Alpaca API supports both forex and stocks in one stream
    stream = Stream(api_key, api_secret, data_feed='sip')

    # Define event handlers
    async def on_connected():
        print("Connected to Alpaca stream")
        # Subscribe to trade and bar updates for all tickers
        # For forex, we need to use the base currency (without USD)
        forex_symbols = [t.replace('USD', '') for t in forex_tickers]
        all_symbols = forex_symbols + stock_tickers
        
        try:
            await stream.subscribe_trades(*all_symbols)
            await stream.subscribe_bars(*all_symbols)
            print(f"Subscribed to trades and bars for: {all_symbols}")
        except Exception as e:
            print(f"Error subscribing to symbols: {e}")

    async def handle_trade(trade):
        await trade_updates_handler(trade)

    async def handle_bar(bar):
        await bar_updates_handler(bar)

    async def handle_error(error):
        print(f"Stream error: {error}")

    async def handle_disconnected():
        print("Stream disconnected")

    # Register event handlers
    stream.on_connect = on_connected
    stream.on_trade = handle_trade
    stream.on_bar = handle_bar
    stream.on_error = handle_error
    stream.on_disconnect = handle_disconnected

    # Run the stream
    await stream.run()

def start_stream_thread(api_key, api_secret):
    """Start the stream in a separate thread with its own event loop."""
    def stream_worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(start_stream(api_key, api_secret))
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            loop.close()
    
    # Start the stream in a separate thread
    import threading
    thread = threading.Thread(target=stream_worker, daemon=True)
    thread.start()
    return thread


# Placeholder for feature engineering using the buffer
# This function now relies solely on the historical_data_buffer populated by the stream
def get_features_from_buffer(X_columns):
    """Generates features from the historical data buffer."""
    # Check if there is enough data in the buffer for feature engineering
    min_lookback = 25 # Minimum data points required for features (e.g., for 20-day SMA and 5-day lag)
    # Check if all required tickers have enough data
    required_tickers_in_buffer = forex_tickers + stock_tickers
    if not historical_data_buffer or any(ticker not in historical_data_buffer or len(historical_data_buffer[ticker]) < min_lookback for ticker in required_tickers_in_buffer):
        # print("Not enough data in buffer to generate features.")
        return pd.DataFrame()

    # Combine data from all tickers in the buffer into a single DataFrame
    combined_data = pd.DataFrame()
    for ticker in required_tickers_in_buffer:
        data = historical_data_buffer.get(ticker)
        if data is not None and not data.empty:
            # Rename the 'Close' column to include the ticker for clarity
            data = data.rename(columns={'Close': ('Close', ticker)})
            if combined_data.empty:
                combined_data = data
            else:
                # Use join with an outer or inner strategy depending on how you want to handle missing timestamps
                # An outer join will keep all timestamps, potentially creating NaNs
                # An inner join will only keep timestamps present in all dataframes
                # For simplicity here, we'll use outer join and handle NaNs later if needed
                combined_data = combined_data.join(data, how='outer')

    if combined_data.empty:
        # print("Combined data from buffer is empty.")
        return pd.DataFrame()

    # Ensure data is sorted by index (timestamp)
    combined_data.sort_index(inplace=True)

    # Reapply feature engineering steps
    # Handle potential NaNs introduced by outer join or missing data points in the stream
    # For simplicity, we'll use forward fill and then drop remaining NaNs, but a more
    # robust approach might involve interpolation or more sophisticated handling.
    combined_data.fillna(method='ffill', inplace=True)
    # After forward fill, there might still be leading NaNs if the buffer didn't have
    # enough history for a ticker. Drop those rows.
    combined_data.dropna(inplace=True)

    if combined_data.empty:
        # print("Features DataFrame is empty after dropping NaNs.")
        return pd.DataFrame()


    returns_df = combined_data['Close'].pct_change()
    returns_df.columns = [f'{col}_Return' for col in returns_df.columns]
    sma_5_df = combined_data['Close'].rolling(window=5).mean()
    sma_5_df.columns = [f'{col}_SMA_5' for col in sma_5_df.columns]
    sma_20_df = combined_data['Close'].rolling(window=20).mean()
    sma_20_df.columns = [f'{col}_SMA_20' for col in sma_20_df.columns]
    lagged_1_df = combined_data['Close'].shift(1)
    lagged_1_df.columns = [f'{col}_Lag_1' for col in lagged_1_df.columns]
    lagged_3_df = combined_data['Close'].shift(3)
    lagged_3_df.columns = [f'{col}_Lag_3' for col in lagged_3_df.columns]
    lagged_5_df = combined_data['Close'].shift(5)
    lagged_5_df.columns = [f'{col}_Lag_5' for col in lagged_5_df.columns]


    features = pd.concat([combined_data, returns_df, sma_5_df, sma_20_df, lagged_1_df, lagged_3_df, lagged_5_df], axis=1)

    # Drop rows with any missing values that result from feature engineering (especially from the rolling windows and lags)
    features.dropna(inplace=True)


    if features.empty:
        # print("Features DataFrame is empty after dropping NaNs.")
        return pd.DataFrame()

    # Return only the latest row of features for prediction
    return features.iloc[[-1]]


def trading_strategy_from_stream(model, scaler, X_columns):
    """
    Generates a trading signal based on the model's predictions using buffered data.
    """
    latest_features_df = get_features_from_buffer(X_columns)

    if latest_features_df.empty:
        # print("Not enough data in buffer or features could not be generated.")
        return "hold", 0, 0

    # Use the latest row of generated features
    latest_features = latest_features_df.iloc[[-1]]
    # Ensure EURUSD is in the features, otherwise return hold
    if ('Close', 'EURUSD') not in latest_features.columns:
         print("EURUSD close price not in latest features.")
         return "hold", 0, 0

    current_price = latest_features[('Close', 'EURUSD')].iloc[0] # Assuming EURUSD is the target

    # Drop the target variable and convert columns to string for scaling
    # Need to handle potential absence of other tickers if data feed is inconsistent
    X_latest = latest_features.drop(('Close', 'EURUSD'), axis=1, errors='ignore')
    X_latest.columns = X_latest.columns.astype(str)

    # Align columns with the training data (assuming X_columns from previous steps is available)
    # This step is crucial to ensure the scaler and model receive features in the
    # same order and with the same names as during training.
    # Create a DataFrame with the same columns as X_columns, filled with 0s
    X_aligned = pd.DataFrame(0.0, index=X_latest.index, columns=X_columns)
    # Copy the values from X_latest into the aligned DataFrame
    for col in X_latest.columns:
        if col in X_aligned.columns:
            X_aligned[col] = X_latest[col]
    X_latest = X_aligned


    # Scale the features
    X_latest_scaled = scaler.transform(X_latest)

    # Predict
    predicted_price = model.predict(X_latest_scaled)[0]

    # Define the threshold for buy/sell signals
    threshold = 0.001  # 0.1%

    if predicted_price > current_price * (1 + threshold):
        return "buy", current_price, predicted_price
    elif predicted_price < current_price * (1 - threshold):
        return "sell", current_price, predicted_price
    else:
        return "hold", current_price, predicted_price

