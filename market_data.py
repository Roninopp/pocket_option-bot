import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from logs import logger

class MarketData:
    def __init__(self):
        logger.info("Market Data initialized", "MARKET_DATA")
        self.symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    
    def get_sample_data(self, symbol, timeframe, candles=50):
        """Generate realistic sample market data"""
        try:
            logger.debug(f"Generating sample data for {symbol} {timeframe}", "MARKET_DATA")
            
            # Base price for different symbols
            base_prices = {
                'EURUSD': 1.0850,
                'GBPUSD': 1.2650,
                'USDJPY': 148.50,
                'XAUUSD': 1980.0
            }
            
            base_price = base_prices.get(symbol, 1.0850)
            data = []
            
            for i in range(candles):
                # Realistic price movement
                open_price = base_price
                volatility = 0.002 if 'XAU' not in symbol else 5.0  # Higher volatility for Gold
                
                high = open_price + abs(random.gauss(0, volatility))
                low = open_price - abs(random.gauss(0, volatility))
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
                base_price = close  # Next candle opens at previous close
            
            df = pd.DataFrame(data)
            logger.debug(f"Generated {len(df)} candles for {symbol}", "MARKET_DATA")
            return df
            
        except Exception as e:
            logger.error(f"Error generating sample data: {e}", "MARKET_DATA", exc_info=True)
            return pd.DataFrame()
    
    def add_manual_pattern(self, df, pattern_type):
        """Manually add specific patterns for testing"""
        try:
            if len(df) < 2:
                return df
            
            if pattern_type == "BULLISH_ENGULFING":
                # Create bullish engulfing pattern
                df.at[df.index[-2], 'open'] = 1.0860
                df.at[df.index[-2], 'high'] = 1.0865
                df.at[df.index[-2], 'low'] = 1.0840
                df.at[df.index[-2], 'close'] = 1.0845  # Bearish candle
                
                df.at[df.index[-1], 'open'] = 1.0840
                df.at[df.index[-1], 'high'] = 1.0870
                df.at[df.index[-1], 'low'] = 1.0835
                df.at[df.index[-1], 'close'] = 1.0865  # Bullish candle that engulfs previous
            
            elif pattern_type == "BEARISH_ENGULFING":
                # Create bearish engulfing pattern
                df.at[df.index[-2], 'open'] = 1.0840
                df.at[df.index[-2], 'high'] = 1.0850
                df.at[df.index[-2], 'low'] = 1.0830
                df.at[df.index[-2], 'close'] = 1.0845  # Bullish candle
                
                df.at[df.index[-1], 'open'] = 1.0850
                df.at[df.index[-1], 'high'] = 1.0855
                df.at[df.index[-1], 'low'] = 1.0825
                df.at[df.index[-1], 'close'] = 1.0830  # Bearish candle that engulfs previous
            
            logger.debug(f"Manual {pattern_type} pattern added", "MARKET_DATA")
            return df
            
        except Exception as e:
            logger.error(f"Error adding manual pattern: {e}", "MARKET_DATA", exc_info=True)
            return df