#!/usr/bin/env python3
"""
Test Runner for Trading Agent
Run specific test categories or all tests.
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime

def run_test_category(category):
    """Run a specific test category."""
    print(f"\n{'='*60}")
    print(f"RUNNING {category.upper()} TESTS")
    print(f"{'='*60}")
    
    if category == "all":
        # Run all tests
        result = subprocess.run([sys.executable, "test_trading_agent.py"], 
                              capture_output=True, text=True)
    else:
        # Run specific test category
        result = subprocess.run([sys.executable, "-m", "unittest", 
                               f"test_trading_agent.Test{category}"], 
                              capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)
    
    return result.returncode == 0

def run_quick_tests():
    """Run quick smoke tests."""
    print(f"\n{'='*60}")
    print("QUICK SMOKE TESTS")
    print(f"{'='*60}")
    
    # Test imports
    try:
        import pandas as pd
        import numpy as np
        from trading_agent_core import historical_data_buffer, latest_data
        print("[PASS] All imports successful")
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    
    # Test basic functionality
    try:
        # Test data buffer
        assert isinstance(historical_data_buffer, dict)
        assert isinstance(latest_data, dict)
        print("[PASS] Data structures initialized correctly")
    except Exception as e:
        print(f"[FAIL] Data structure error: {e}")
        return False
    
    # Test model files exist
    required_files = ['random_forest_model.joblib', 'scaler.joblib']
    for file in required_files:
        if os.path.exists(file):
            print(f"[PASS] {file} found")
        else:
            print(f"[FAIL] {file} not found")
            return False
    
    print("[PASS] All quick tests passed!")
    return True

def run_integration_tests():
    """Run integration tests."""
    print(f"\n{'='*60}")
    print("INTEGRATION TESTS")
    print(f"{'='*60}")
    
    # Test streaming connection (without actually connecting)
    try:
        from alpaca_trade_api.stream import Stream
        print("[PASS] Alpaca Stream import successful")
    except ImportError as e:
        print(f"[FAIL] Alpaca Stream import failed: {e}")
        return False
    
    # Test API configuration
    try:
        from trading_agent_main import API_KEY, API_SECRET, BASE_URL
        assert len(API_KEY) > 0
        assert len(API_SECRET) > 0
        print("[PASS] API configuration loaded")
    except Exception as e:
        print(f"[FAIL] API configuration error: {e}")
        return False
    
    print("[PASS] All integration tests passed!")
    return True

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description='Run Trading Agent Tests')
    parser.add_argument('--category', choices=['all', 'quick', 'integration', 'data', 'strategy', 'risk'], 
                       default='quick', help='Test category to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print(f"{'='*60}")
    print("TRADING AGENT TEST RUNNER")
    print(f"{'='*60}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Category: {args.category}")
    print(f"Verbose: {args.verbose}")
    
    success = True
    
    if args.category == 'quick':
        success = run_quick_tests()
    elif args.category == 'integration':
        success = run_integration_tests()
    elif args.category == 'all':
        # Run quick tests first
        if not run_quick_tests():
            print("❌ Quick tests failed, stopping")
            return False
        
        # Run integration tests
        if not run_integration_tests():
            print("❌ Integration tests failed, stopping")
            return False
        
        # Run full test suite
        success = run_test_category('all')
    else:
        success = run_test_category(args.category)
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    if success:
        print("[PASS] All tests passed!")
        return 0
    else:
        print("[FAIL] Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 