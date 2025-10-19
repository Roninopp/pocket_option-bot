import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from logs import logger

class PatternDetector:
    def __init__(self):
        logger.info("Pattern Detector initialized", "PATTERN_DETECTOR")
    
    def detect_patterns(self, df, timeframe):
        """Detect all patterns in the dataframe"""
        try:
            patterns = []
            
            if len(df) < 3:
                return patterns
            
            # Detect Engulfing Pattern
            engulfing = self._detect_engulfing(df)
            if engulfing:
                patterns.append(engulfing)
                logger.log_pattern_detection(
                    engulfing['type'], 
                    df['symbol'].iloc[-1] if 'symbol' in df.columns else 'EURUSD',
                    timeframe, 
                    engulfing.get('confidence', 0)
                )
            
            # Detect Pin Bar Pattern
            pin_bar = self._detect_pin_bar(df)
            if pin_bar:
                patterns.append(pin_bar)
                logger.log_pattern_detection(
                    pin_bar['type'], 
                    df['symbol'].iloc[-1] if 'symbol' in df.columns else 'EURUSD',
                    timeframe, 
                    pin_bar.get('confidence', 0)
                )
            
            # Detect Market Structure
            structure = self._analyze_market_structure(df)
            if structure:
                patterns.append(structure)
            
            logger.debug(f"Detected {len(patterns)} patterns for {timeframe}", "PATTERN_DETECTOR")
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}", "PATTERN_DETECTOR", exc_info=True)
            return []
    
    def _detect_engulfing(self, df):
        """Detect bullish/bearish engulfing patterns"""
        try:
            if len(df) < 2:
                return None
            
            current_candle = df.iloc[-1]
            previous_candle = df.iloc[-2]
            
            # Bullish Engulfing
            if (current_candle['close'] > current_candle['open'] and  # Current is bullish
                previous_candle['close'] < previous_candle['open'] and  # Previous is bearish
                current_candle['open'] < previous_candle['close'] and   # Current opens below previous close
                current_candle['close'] > previous_candle['open']):     # Current closes above previous open
                
                return {
                    'type': 'BULLISH_ENGULFING',
                    'direction': 'BUY',
                    'confidence': 75,
                    'timestamp': datetime.now()
                }
            
            # Bearish Engulfing
            elif (current_candle['close'] < current_candle['open'] and  # Current is bearish
                  previous_candle['close'] > previous_candle['open'] and  # Previous is bullish
                  current_candle['open'] > previous_candle['close'] and   # Current opens above previous close
                  current_candle['close'] < previous_candle['open']):     # Current closes below previous open
                
                return {
                    'type': 'BEARISH_ENGULFING',
                    'direction': 'SELL',
                    'confidence': 75,
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in engulfing detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _detect_pin_bar(self, df):
        """Detect pin bar patterns"""
        try:
            if len(df) < 1:
                return None
            
            current_candle = df.iloc[-1]
            candle_range = current_candle['high'] - current_candle['low']
            
            if candle_range == 0:
                return None
            
            # Calculate body and wick sizes
            body_size = abs(current_candle['close'] - current_candle['open'])
            upper_wick = current_candle['high'] - max(current_candle['open'], current_candle['close'])
            lower_wick = min(current_candle['open'], current_candle['close']) - current_candle['low']
            
            # Pin bar conditions (small body, long wick on one side)
            if (body_size / candle_range < 0.3 and  # Small body
                (upper_wick / candle_range > 0.6 or lower_wick / candle_range > 0.6)):  # Long wick
                
                direction = 'SELL' if upper_wick > lower_wick else 'BUY'
                pattern_type = 'BEARISH_PINBAR' if upper_wick > lower_wick else 'BULLISH_PINBAR'
                
                return {
                    'type': pattern_type,
                    'direction': direction,
                    'confidence': 80,
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in pin bar detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _analyze_market_structure(self, df):
        """Analyze market structure for sweeps and key levels"""
        try:
            if len(df) < 10:
                return None
            
            # Simple trend analysis
            recent_high = df['high'].tail(5).max()
            recent_low = df['low'].tail(5).min()
            current_price = df['close'].iloc[-1]
            
            # Determine trend
            if current_price > df['close'].iloc[-5]:
                trend = "UPTREND"
            elif current_price < df['close'].iloc[-5]:
                trend = "DOWNTREND"
            else:
                trend = "SIDEWAYS"
            
            # Check for sweep of liquidity
            sweep_detected = self._detect_liquidity_sweep(df)
            
            structure = {
                'type': 'MARKET_STRUCTURE',
                'trend': trend,
                'support': recent_low,
                'resistance': recent_high,
                'sweep_detected': sweep_detected,
                'timestamp': datetime.now()
            }
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _detect_liquidity_sweep(self, df):
        """Detect liquidity sweeps (simplified version)"""
        try:
            if len(df) < 3:
                return False
            
            current_high = df['high'].iloc[-1]
            previous_high = df['high'].iloc[-2]
            current_low = df['low'].iloc[-1]
            previous_low = df['low'].iloc[-2]
            
            # Simple sweep detection (price takes out previous high/low then reverses)
            if (current_high > previous_high and df['close'].iloc[-1] < df['open'].iloc[-1]):
                return True  # Bearish sweep
            
            if (current_low < previous_low and df['close'].iloc[-1] > df['open'].iloc[-1]):
                return True  # Bullish sweep
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting sweep: {e}", "PATTERN_DETECTOR", exc_info=True)

            return False
