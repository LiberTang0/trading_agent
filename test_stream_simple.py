#!/usr/bin/env python3
"""
Simple test script to check Alpaca streaming API compatibility
"""

import asyncio
import sys

# Your API credentials
API_KEY = 'PKG66F7DKPJEO2H1HHF3'
API_SECRET = 'P2GAROcozlav3c8EnaNhNqp26xa7DB3ELInUjTXw'

def test_imports():
    """Test different Alpaca imports."""
    print("Testing Alpaca imports...")
    
    try:
        from alpaca_trade_api.stream import Stream
        print("✅ alpaca_trade_api.stream imported successfully")
        
        # Test creating stream object
        stream = Stream(API_KEY, API_SECRET, data_feed='sip')
        print("✅ Stream object created successfully")
        
        # Check available attributes
        print(f"Stream object attributes: {dir(stream)}")
        
        return "alpaca_trade_api"
        
    except Exception as e:
        print(f"❌ alpaca_trade_api error: {e}")
    
    try:
        from alpaca.data.stream import StockDataStream
        print("✅ alpaca.data.stream imported successfully")
        return "alpaca-py"
        
    except Exception as e:
        print(f"❌ alpaca-py error: {e}")
    
    return None

async def test_alpaca_trade_api():
    """Test the older alpaca-trade-api."""
    print("\nTesting alpaca-trade-api...")
    
    try:
        from alpaca_trade_api.stream import Stream
        
        stream = Stream(API_KEY, API_SECRET, data_feed='sip')
        
        # Define handlers
        async def on_connect():
            print("✅ Connected!")
            try:
                await stream.subscribe_trades('SPY')
                print("✅ Subscribed to SPY")
            except Exception as e:
                print(f"❌ Subscribe error: {e}")
        
        async def on_trade(trade):
            print(f"📊 Trade: {trade.symbol} @ ${trade.price}")
        
        # Set handlers
        stream.on_connect = on_connect
        stream.on_trade = on_trade
        
        print("Starting stream...")
        await stream.run()
        
    except Exception as e:
        print(f"❌ Stream error: {e}")

async def test_alpaca_py():
    """Test the newer alpaca-py."""
    print("\nTesting alpaca-py...")
    
    try:
        from alpaca.data.stream import StockDataStream
        from alpaca.trading.client import TradingClient
        
        # Create trading client
        trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
        
        # Create data stream
        data_stream = StockDataStream(API_KEY, API_SECRET)
        
        async def on_trade(trade):
            print(f"📊 Trade: {trade.symbol} @ ${trade.price}")
        
        data_stream.subscribe_trades(on_trade, "SPY")
        
        print("Starting stream...")
        await data_stream.run()
        
    except Exception as e:
        print(f"❌ Stream error: {e}")

def main():
    """Main function."""
    print("=" * 60)
    print("ALPACA STREAMING API COMPATIBILITY TEST")
    print("=" * 60)
    
    # Test imports
    api_type = test_imports()
    
    if api_type == "alpaca_trade_api":
        try:
            asyncio.run(asyncio.wait_for(test_alpaca_trade_api(), timeout=15))
        except asyncio.TimeoutError:
            print("⏰ Test completed")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    elif api_type == "alpaca-py":
        try:
            asyncio.run(asyncio.wait_for(test_alpaca_py(), timeout=15))
        except asyncio.TimeoutError:
            print("⏰ Test completed")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    else:
        print("❌ No compatible Alpaca API found")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 