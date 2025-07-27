#!/usr/bin/env python3
"""
Unit Tests for Trading Agent
Tests all major components of the trading agent system.
"""

import unittest
import pandas as pd
import numpy as np
import asyncio
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the modules we want to test
from trading_agent_core import (
    historical_data_buffer, 
    latest_data, 
    update_data_buffer, 
    trade_updates_handler, 
    bar_updates_handler,
    get_features_from_buffer,
    trading_strategy_from_stream
)

class TestDataBuffer(unittest.TestCase):
    """Test the data buffer functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Clear the buffer before each test
        for ticker in historical_data_buffer:
            historical_data_buffer[ticker] = pd.DataFrame(columns=['Close'])
        
        # Clear latest data
        for ticker in latest_data:
            latest_data[ticker] = {'close': None, 'timestamp': None}
    
    def test_update_data_buffer(self):
        """Test updating the data buffer with new data."""
        # Test data
        symbol = 'EURUSD'
        price = 1.0850
        timestamp = datetime.now()
        
        # Update buffer
        asyncio.run(update_data_buffer(symbol, price, timestamp))
        
        # Check if data was added
        self.assertFalse(historical_data_buffer[symbol].empty)
        self.assertEqual(len(historical_data_buffer[symbol]), 1)
        self.assertEqual(historical_data_buffer[symbol].iloc[0]['Close'], price)
    
    def test_buffer_size_limit(self):
        """Test that buffer maintains size limit."""
        symbol = 'EURUSD'
        base_time = datetime.now()
        
        # Add more than 60 days of data (1440 hours)
        for i in range(1500):
            timestamp = base_time + timedelta(hours=i)
            price = 1.0850 + (i * 0.0001)
            asyncio.run(update_data_buffer(symbol, price, timestamp))
        
        # Check that buffer is limited (should be around 60 days)
        self.assertLess(len(historical_data_buffer[symbol]), 1500)
    
    def test_trade_updates_handler(self):
        """Test trade updates handler."""
        # Mock trade object
        mock_trade = Mock()
        mock_trade.symbol = 'EUR'
        mock_trade.price = 1.0850
        mock_trade.timestamp = datetime.now()
        
        # Process trade
        asyncio.run(trade_updates_handler(mock_trade))
        
        # Check if data was updated
        self.assertEqual(latest_data['EURUSD']['close'], 1.0850)
        self.assertIsNotNone(latest_data['EURUSD']['timestamp'])
    
    def test_bar_updates_handler(self):
        """Test bar updates handler."""
        # Mock bar object
        mock_bar = Mock()
        mock_bar.symbol = 'SPY'
        mock_bar.close = 450.50
        mock_bar.timestamp = datetime.now()
        
        # Process bar
        asyncio.run(bar_updates_handler(mock_bar))
        
        # Check if data was updated
        self.assertEqual(latest_data['SPY']['close'], 450.50)
        self.assertIsNotNone(latest_data['SPY']['timestamp'])

class TestFeatureEngineering(unittest.TestCase):
    """Test feature engineering functionality."""
    
    def setUp(self):
        """Set up test data with historical prices."""
        # Clear and populate buffer with test data
        for ticker in historical_data_buffer:
            historical_data_buffer[ticker] = pd.DataFrame(columns=['Close'])
        
        # Add 30 days of test data
        base_time = datetime.now() - timedelta(days=30)
        for i in range(30):
            timestamp = base_time + timedelta(days=i)
            for ticker in ['EURUSD', 'SPY', 'DIA']:
                # Generate realistic price data
                if ticker == 'EURUSD':
                    price = 1.0850 + (i * 0.001) + (np.random.random() - 0.5) * 0.01
                else:
                    price = 450 + (i * 2) + (np.random.random() - 0.5) * 10
                
                new_row = pd.DataFrame({'Close': price}, index=[timestamp])
                historical_data_buffer[ticker] = pd.concat([historical_data_buffer[ticker], new_row])
    
    def test_get_features_from_buffer_sufficient_data(self):
        """Test feature generation with sufficient data."""
        # Create X_columns similar to what the model expects
        X_columns = pd.Index([
            "('Open', 'EURUSD')", "('High', 'EURUSD')", "('Low', 'EURUSD')", 
            "('Close', 'EURUSD')", "('Volume', 'EURUSD')",
            "('Open', 'SPY')", "('High', 'SPY')", "('Low', 'SPY')", 
            "('Close', 'SPY')", "('Volume', 'SPY')"
        ])
        
        features = get_features_from_buffer(X_columns)
        
        # Should return a DataFrame with features
        self.assertIsInstance(features, pd.DataFrame)
        self.assertFalse(features.empty)
    
    def test_get_features_from_buffer_insufficient_data(self):
        """Test feature generation with insufficient data."""
        # Clear buffer
        for ticker in historical_data_buffer:
            historical_data_buffer[ticker] = pd.DataFrame(columns=['Close'])
        
        X_columns = pd.Index(["('Close', 'EURUSD')"])
        features = get_features_from_buffer(X_columns)
        
        # Should return empty DataFrame
        self.assertIsInstance(features, pd.DataFrame)
        self.assertTrue(features.empty)

class TestTradingStrategy(unittest.TestCase):
    """Test trading strategy functionality."""
    
    def setUp(self):
        """Set up mock model and scaler."""
        # Create mock model
        self.mock_model = Mock()
        self.mock_model.predict.return_value = np.array([1.0860])  # Predicted price
        
        # Create mock scaler
        self.mock_scaler = Mock()
        self.mock_scaler.transform.return_value = np.array([[0.1, 0.2, 0.3]])
        
        # Populate buffer with test data
        base_time = datetime.now() - timedelta(days=30)
        for i in range(30):
            timestamp = base_time + timedelta(days=i)
            for ticker in ['EURUSD', 'SPY', 'DIA']:
                if ticker == 'EURUSD':
                    price = 1.0850 + (i * 0.001)
                else:
                    price = 450 + (i * 2)
                
                new_row = pd.DataFrame({'Close': price}, index=[timestamp])
                historical_data_buffer[ticker] = pd.concat([historical_data_buffer[ticker], new_row])
        
        # Set current price
        latest_data['EURUSD']['close'] = 1.0850
        latest_data['EURUSD']['timestamp'] = datetime.now()
    
    def test_trading_strategy_buy_signal(self):
        """Test trading strategy with buy signal."""
        # Mock model to predict higher price (buy signal)
        self.mock_model.predict.return_value = np.array([1.0900])  # 0.5% increase
        
        X_columns = pd.Index(["('Close', 'EURUSD')", "('Close', 'SPY')"])
        
        signal, current_price, predicted_price = trading_strategy_from_stream(
            self.mock_model, self.mock_scaler, X_columns
        )
        
        self.assertIn(signal, ['buy', 'sell', 'hold'])
        self.assertIsInstance(current_price, (int, float))
        self.assertIsInstance(predicted_price, (int, float))
    
    def test_trading_strategy_insufficient_data(self):
        """Test trading strategy with insufficient data."""
        # Clear buffer
        for ticker in historical_data_buffer:
            historical_data_buffer[ticker] = pd.DataFrame(columns=['Close'])
        
        X_columns = pd.Index(["('Close', 'EURUSD')"])
        
        signal, current_price, predicted_price = trading_strategy_from_stream(
            self.mock_model, self.mock_scaler, X_columns
        )
        
        # Should return hold signal with zero prices
        self.assertEqual(signal, 'hold')
        self.assertEqual(current_price, 0)
        self.assertEqual(predicted_price, 0)

class TestRiskManagement(unittest.TestCase):
    """Test risk management calculations."""
    
    def test_position_size_calculation(self):
        """Test position size calculation."""
        equity = 10000
        current_price = 1.0850
        risk_percentage = 0.10  # 10%
        
        order_value = equity * risk_percentage
        order_size = order_value / current_price
        
        self.assertEqual(order_value, 1000)
        self.assertAlmostEqual(order_size, 921.66, places=2)
    
    def test_stop_loss_calculation(self):
        """Test stop loss calculation."""
        current_price = 1.0850
        stop_loss_pct = 0.005  # 0.5%
        
        stop_loss_price = current_price * (1 - stop_loss_pct)
        
        self.assertAlmostEqual(stop_loss_price, 1.0796, places=4)
    
    def test_take_profit_calculation(self):
        """Test take profit calculation."""
        current_price = 1.0850
        take_profit_pct = 0.01  # 1%
        
        take_profit_price = current_price * (1 + take_profit_pct)
        
        self.assertAlmostEqual(take_profit_price, 1.0959, places=4)

class TestMarketHours(unittest.TestCase):
    """Test market hours checking."""
    
    @patch('trading_agent_main.api')
    def test_market_hours_open(self, mock_api):
        """Test market hours when market is open."""
        from trading_agent_main import check_market_hours
        
        # Mock clock response
        mock_clock = Mock()
        mock_clock.is_open = True
        mock_api.get_clock.return_value = mock_clock
        
        result = check_market_hours()
        self.assertTrue(result)
    
    @patch('trading_agent_main.api')
    def test_market_hours_closed(self, mock_api):
        """Test market hours when market is closed."""
        from trading_agent_main import check_market_hours
        
        # Mock clock response
        mock_clock = Mock()
        mock_clock.is_open = False
        mock_api.get_clock.return_value = mock_clock
        
        result = check_market_hours()
        self.assertFalse(result)

class TestLogging(unittest.TestCase):
    """Test logging functionality."""
    
    def test_logging_setup(self):
        """Test logging setup."""
        from trading_agent_main import setup_logging
        
        logger = setup_logging()
        
        self.assertIsNotNone(logger)
        self.assertTrue(os.path.exists('logs'))
        
        # Check if log file was created
        log_files = [f for f in os.listdir('logs') if f.startswith('trading_agent_')]
        self.assertGreater(len(log_files), 0)

class TestModelLoading(unittest.TestCase):
    """Test model and scaler loading."""
    
    @patch('joblib.load')
    def test_model_loading_success(self, mock_load):
        """Test successful model loading."""
        from trading_agent_main import load_model_and_scaler
        
        # Mock successful loading
        mock_model = Mock()
        mock_scaler = Mock()
        mock_load.side_effect = [mock_model, mock_scaler]
        
        model, scaler = load_model_and_scaler()
        
        self.assertEqual(model, mock_model)
        self.assertEqual(scaler, mock_scaler)
    
    @patch('joblib.load')
    def test_model_loading_file_not_found(self, mock_load):
        """Test model loading when files don't exist."""
        from trading_agent_main import load_model_and_scaler
        
        # Mock file not found error
        mock_load.side_effect = FileNotFoundError("File not found")
        
        with self.assertRaises(SystemExit):
            load_model_and_scaler()

class TestSignalHandling(unittest.TestCase):
    """Test signal handling."""
    
    def test_signal_handler(self):
        """Test signal handler functionality."""
        from trading_agent_main import signal_handler, running
        
        # Test that signal handler sets running to False
        original_running = running
        signal_handler(2, None)  # SIGINT
        self.assertFalse(running)

def run_performance_tests():
    """Run performance tests."""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    # Test data buffer performance
    start_time = time.time()
    
    # Add 1000 data points
    base_time = datetime.now()
    for i in range(1000):
        timestamp = base_time + timedelta(minutes=i)
        asyncio.run(update_data_buffer('EURUSD', 1.0850 + i*0.0001, timestamp))
    
    end_time = time.time()
    print(f"Data buffer performance: {end_time - start_time:.4f} seconds for 1000 updates")
    
    # Test feature generation performance
    start_time = time.time()
    X_columns = pd.Index(["('Close', 'EURUSD')", "('Close', 'SPY')"])
    for _ in range(100):
        get_features_from_buffer(X_columns)
    
    end_time = time.time()
    print(f"Feature generation performance: {end_time - start_time:.4f} seconds for 100 generations")

def main():
    """Run all tests."""
    print("="*60)
    print("TRADING AGENT UNIT TESTS")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDataBuffer,
        TestFeatureEngineering,
        TestTradingStrategy,
        TestRiskManagement,
        TestMarketHours,
        TestLogging,
        TestModelLoading,
        TestSignalHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance tests
    run_performance_tests()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n[PASS] All tests passed!")
    else:
        print("\n[FAIL] Some tests failed!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 