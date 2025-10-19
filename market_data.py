import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from logs import logger

class MarketData:
    def __init__(self):
        logger.info("Market Data initialized", "MARKET_DATA")
        self.symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    
    def get_realistic_data(self, symbol, timeframe, candles=50):
        """Generate more realistic market data with actual trends"""
        try:
            base_prices = {
                'EURUSD': 1.0850,
                'GBPUSD': 1.2650,
                'USDJPY': 148.50,
                'XAUUSD': 1980.0
            }
            
            base_price = base_prices.get(symbol, 1.0850)
            data = []
            
            # Add realistic trends
            trend_direction = random.choice([-1, 1])
            trend_strength = random.uniform(0.001, 0.005)
            
            for i in range(candles):
                # Realistic price movement with trend
                trend_effect = trend_direction * trend_strength * i
                open_price = base_price + trend_effect
                
                volatility = 0.002 if 'XAU' not in symbol else 5.0
                
                # Realistic candle generation
                high = open_price + abs(random.gauss(0, volatility)) * 1.5
                low = open_price - abs(random.gauss(0, volatility)) * 1.5
                close = random.uniform(low, high)
                
                # Ensure proper high/low
                high = max(open_price, close, high)
                low = min(open_price, close, low)
                
                candle_data = {
                    'timestamp': datetime.now() - timedelta(minutes=5*(candles-i)),
                    'open': round(open_price, 5),
                    'high': round(high, 5),
                    'low': round(low, 5),
                    'close': round(close, 5),
                    'volume': random.randint(1000, 10000),
                    'symbol': symbol
                }
                
                data.append(candle_data)
                base_price = close
            
            df = pd.DataFrame(data)
            return df
            
        except Exception as e:
            logger.error(f"Error generating data: {e}", "MARKET_DATA", exc_info=True)
            return pd.DataFrame()
    
    def get_sample_data(self, symbol, timeframe, candles=50):
        """Use realistic data instead of random"""
        return self.get_realistic_data(symbol, timeframe, candles)
