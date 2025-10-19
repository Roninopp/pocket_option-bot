# market_data.py (UPDATED)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from logs import logger
from pocket_option_api import PocketOptionAPI

class MarketData:
    def __init__(self):
        logger.info("Market Data initialized", "MARKET_DATA")
        self.symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
        self.pocket_api = PocketOptionAPI()
        self.use_real_data = False
        
    def initialize_real_data(self, email, password):
        """Initialize real Pocket Option API connection"""
        try:
            success = self.pocket_api.connect(email, password)
            if success:
                self.use_real_data = True
                logger.info("Real market data enabled", "MARKET_DATA")
                return True
            else:
                logger.warning("Failed to connect to Pocket Option, using sample data", "MARKET_DATA")
                return False
        except Exception as e:
            logger.error(f"Error initializing real data: {e}", "MARKET_DATA", exc_info=True)
            return False
    
    def get_real_data(self, symbol, timeframe, candles=50):
        """Get real market data from Pocket Option API"""
        try:
            if not self.use_real_data:
                return self.get_sample_data(symbol, timeframe, candles)
                
            df = self.pocket_api.get_candles(symbol, timeframe, candles)
            if df is not None and not df.empty:
                df['symbol'] = symbol
                return df
            else:
                logger.warning(f"No real data for {symbol}, falling back to sample", "MARKET_DATA")
                return self.get_sample_data(symbol, timeframe, candles)
                
        except Exception as e:
            logger.error(f"Error getting real data: {e}", "MARKET_DATA", exc_info=True)
            return self.get_sample_data(symbol, timeframe, candles)
    
    def get_sample_data(self, symbol, timeframe, candles=50):
        """Generate sample data as fallback"""
        try:
            base_prices = {
                'EURUSD': 1.0850,
                'GBPUSD': 1.2650,
                'USDJPY': 148.50,
                'XAUUSD': 1980.0
            }
            
            base_price = base_prices.get(symbol, 1.0850)
            data = []
            
            trend_direction = np.random.choice([-1, 1])
            trend_strength = np.random.uniform(0.001, 0.005)
            
            for i in range(candles):
                trend_effect = trend_direction * trend_strength * i
                open_price = base_price + trend_effect
                
                volatility = 0.002 if 'XAU' not in symbol else 5.0
                
                high = open_price + abs(np.random.normal(0, volatility)) * 1.5
                low = open_price - abs(np.random.normal(0, volatility)) * 1.5
                close = np.random.uniform(low, high)
                
                high = max(open_price, close, high)
                low = min(open_price, close, low)
                
                candle_data = {
                    'timestamp': datetime.now() - timedelta(minutes=5*(candles-i)),
                    'open': round(open_price, 5),
                    'high': round(high, 5),
                    'low': round(low, 5),
                    'close': round(close, 5),
                    'volume': np.random.randint(1000, 10000),
                    'symbol': symbol
                }
                
                data.append(candle_data)
                base_price = close
            
            df = pd.DataFrame(data)
            logger.info(f"Generated sample data for {symbol} ({len(df)} candles)", "MARKET_DATA")
            return df
            
        except Exception as e:
            logger.error(f"Error generating sample data: {e}", "MARKET_DATA", exc_info=True)
            return pd.DataFrame()
