#!/usr/bin/env python3
"""
Test script to verify the Alpaca streaming functionality
"""

import asyncio
import sys
import threading
import time
from alpaca_trade_api.stream import Stream

# Your API credentials
API_KEY = ''
API_SECRET = ''

def run_stream_in_thread():
    """Run the stream in a separate thread with its own event loop."""
    def stream_worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Create stream
            stream = Stream(API_KEY, API_SECRET, data_feed='sip')
            
            # Define event handlers
            async def on_connected():
                print("✅ Successfully connected to Alpaca stream!")
                try:
                    # Test with a simple symbol
                    await stream.subscribe_trades('SPY')
                    print("✅ Successfully subscribed to SPY trades")
                    
                    # Test forex symbol
                    await stream.subscribe_trades('EUR')
                    print("✅ Successfully subscribed to EUR trades")
                    
                except Exception as e:
                    print(f"❌ Error subscribing to symbols: {e}")
            
            async def handle_trade(trade):
                print(f"📊 Received trade: {trade.symbol} @ ${trade.price}")
            
            async def handle_error(error):
                print(f"❌ Stream error: {error}")
            
            async def handle_disconnected():
                print("🔌 Stream disconnected")
            
            # Register event handlers
            stream.on_connect = on_connected
            stream.on_trade = handle_trade
            stream.on_error = handle_error
            stream.on_disconnect = handle_disconnected
            
            print("Starting stream...")
            loop.run_until_complete(stream.run())
            
        except Exception as e:
            print(f"❌ Failed to create stream: {e}")
        finally:
            loop.close()
    
    # Start the stream in a separate thread
    thread = threading.Thread(target=stream_worker, daemon=True)
    thread.start()
    return thread

def main():
    """Main function."""
    print("=" * 50)
    print("ALPACA STREAM TEST")
    print("=" * 50)
    
    try:
        # Start the stream in a thread
        stream_thread = run_stream_in_thread()
        
        # Wait for 30 seconds
        print("Waiting 30 seconds for stream data...")
        time.sleep(30)
        
        print("\n⏰ Test completed after 30 seconds")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 
