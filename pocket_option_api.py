# pocket_option_api.py
import requests
import json
import time
import websocket
import threading
from datetime import datetime
from logs import logger

class PocketOptionAPI:
    def __init__(self):
        self.base_url = "https://pocketoption.com/api"
        self.ws_url = "wss://pocketoption.com/websocket"
        self.session = requests.Session()
        self.is_connected = False
        self.ws = None
        self.assets = {}
        
    def connect(self, email, password):
        """Connect to Pocket Option API"""
        try:
            # Login to get session
            login_data = {
                'email': email,
                'password': password
            }
            
            response = self.session.post(f"{self.base_url}/login", json=login_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.is_connected = True
                    logger.info("Successfully connected to Pocket Option API", "POCKET_OPTION")
                    self._get_assets()
                    return True
                else:
                    logger.error(f"Login failed: {result.get('message', 'Unknown error')}", "POCKET_OPTION")
                    return False
            else:
                logger.error(f"Login request failed: {response.status_code}", "POCKET_OPTION")
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {e}", "POCKET_OPTION", exc_info=True)
            return False
    
    def _get_assets(self):
        """Get available trading assets"""
        try:
            response = self.session.get(f"{self.base_url}/assets")
            if response.status_code == 200:
                self.assets = response.json()
                logger.info(f"Loaded {len(self.assets)} assets", "POCKET_OPTION")
            else:
                logger.error(f"Failed to get assets: {response.status_code}", "POCKET_OPTION")
        except Exception as e:
            logger.error(f"Error getting assets: {e}", "POCKET_OPTION")
    
    def get_candles(self, symbol, timeframe, count=100):
        """Get real candle data from Pocket Option"""
        try:
            # Map timeframe to Pocket Option format
            tf_map = {
                '1min': 60,
                '5min': 300,
                '15min': 900,
                '1hour': 3600
            }
            
            timeframe_sec = tf_map.get(timeframe, 300)  # Default to 5min
            
            params = {
                'asset': symbol,
                'timeframe': timeframe_sec,
                'count': count
            }
            
            response = self.session.get(f"{self.base_url}/candles", params=params)
            if response.status_code == 200:
                candles = response.json()
                
                # Convert to pandas DataFrame
                import pandas as pd
                df_data = []
                for candle in candles:
                    df_data.append({
                        'timestamp': datetime.fromtimestamp(candle['time']),
                        'open': candle['open'],
                        'high': candle['high'],
                        'low': candle['low'],
                        'close': candle['close'],
                        'volume': candle.get('volume', 0)
                    })
                
                df = pd.DataFrame(df_data)
                logger.info(f"Retrieved {len(df)} real candles for {symbol} {timeframe}", "POCKET_OPTION")
                return df
            else:
                logger.error(f"Failed to get candles: {response.status_code}", "POCKET_OPTION")
                return None
                
        except Exception as e:
            logger.error(f"Error getting candles: {e}", "POCKET_OPTION", exc_info=True)
            return None
    
    def get_current_price(self, symbol):
        """Get current price for symbol"""
        try:
            response = self.session.get(f"{self.base_url}/quote", params={'asset': symbol})
            if response.status_code == 200:
                return response.json().get('price')
            return None
        except Exception as e:
            logger.error(f"Error getting price: {e}", "POCKET_OPTION")
            return None
