import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from logs import logger

class PatternDetector:
    def __init__(self):
        logger.info("Pattern Detector initialized", "PATTERN_DETECTOR")
    
    def detect_patterns(self, df, timeframe):
        """More accurate pattern detection"""
        try:
            patterns = []
            
            if len(df) < 3:
                return patterns
            
            # Only analyze recent candles for better accuracy
            recent_df = df.tail(10)
            
            # Detect Engulfing Pattern with better logic
            engulfing = self._detect_engulfing(recent_df)
            if engulfing:
                patterns.append(engulfing)
            
            # Detect Pin Bar Pattern with better logic
            pin_bar = self._detect_pin_bar(recent_df)
            if pin_bar:
                patterns.append(pin_bar)
            
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
        """More accurate engulfing detection"""
        try:
            if len(df) < 2:
                return None
            
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            current_body = abs(current['close'] - current['open'])
            previous_body = abs(previous['close'] - previous['open'])
            
            # Bullish Engulfing - More strict conditions
            if (current['close'] > current['open'] and  # Current bullish
                previous['close'] < previous['open'] and  # Previous bearish
                current['open'] < previous['close'] and   # Opens below previous close
                current['close'] > previous['open'] and   # Closes above previous open
                current_body > previous_body * 1.2):      # Body is significantly larger
                
                confidence = min(80 + int((current_body / previous_body - 1) * 100), 95)
                return {
                    'type': 'BULLISH_ENGULFING',
                    'direction': 'BUY',
                    'confidence': confidence,
                    'timestamp': datetime.now()
                }
            
            # Bearish Engulfing - More strict conditions
            elif (current['close'] < current['open'] and  # Current bearish
                  previous['close'] > previous['open'] and  # Previous bullish
                  current['open'] > previous['close'] and   # Opens above previous close
                  current['close'] < previous['open'] and   # Closes below previous open
                  current_body > previous_body * 1.2):      # Body is significantly larger
                
                confidence = min(80 + int((current_body / previous_body - 1) * 100), 95)
                return {
                    'type': 'BEARISH_ENGULFING',
                    'direction': 'SELL',
                    'confidence': confidence,
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in engulfing detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _detect_pin_bar(self, df):
        """More accurate pin bar detection"""
        try:
            if len(df) < 1:
                return None
            
            candle = df.iloc[-1]
            candle_range = candle['high'] - candle['low']
            
            if candle_range == 0:
                return None
            
            body_size = abs(candle['close'] - candle['open'])
            upper_wick = candle['high'] - max(candle['open'], candle['close'])
            lower_wick = min(candle['open'], candle['close']) - candle['low']
            
            # More strict pin bar conditions
            is_small_body = body_size / candle_range < 0.3
            has_long_upper_wick = upper_wick / candle_range > 0.6
            has_long_lower_wick = lower_wick / candle_range > 0.6
            
            if is_small_body and (has_long_upper_wick or has_long_lower_wick):
                if has_long_upper_wick and upper_wick > lower_wick * 2:
                    return {
                        'type': 'BEARISH_PINBAR',
                        'direction': 'SELL',
                        'confidence': 75,
                        'timestamp': datetime.now()
                    }
                elif has_long_lower_wick and lower_wick > upper_wick * 2:
                    return {
                        'type': 'BULLISH_PINBAR',
                        'direction': 'BUY',
                        'confidence': 75,
                        'timestamp': datetime.now()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in pin bar detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
