import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from logs import logger

class PatternDetector:
    def __init__(self):
        logger.info("Pattern Detector initialized", "PATTERN_DETECTOR")
    
    def detect_patterns(self, df, timeframe):
        """Enhanced pattern detection for real market data"""
        try:
            patterns = []
            
            if len(df) < 10:  # Increased minimum for better analysis
                logger.warning(f"Insufficient data: {len(df)} candles", "PATTERN_DETECTOR")
                return patterns
            
            # Use more candles for better context (15-20 for real analysis)
            recent_df = df.tail(20)
            
            # Detect Engulfing Pattern
            engulfing = self._detect_engulfing(recent_df)
            if engulfing:
                patterns.append(engulfing)
            
            # Detect Pin Bar Pattern
            pin_bar = self._detect_pin_bar(recent_df)
            if pin_bar:
                patterns.append(pin_bar)
            
            # Detect Double Top/Bottom
            double_pattern = self._detect_double_top_bottom(df)
            if double_pattern:
                patterns.append(double_pattern)
            
            # Detect Support/Resistance Break
            sr_break = self._detect_support_resistance_break(df)
            if sr_break:
                patterns.append(sr_break)
            
            # Enhanced Market Structure Analysis
            structure = self._analyze_market_structure(df)
            if structure:
                patterns.append(structure)
            
            logger.info(f"Detected {len(patterns)} patterns for {timeframe}", "PATTERN_DETECTOR")
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}", "PATTERN_DETECTOR", exc_info=True)
            return []
    
    def _detect_engulfing(self, df):
        """Enhanced engulfing detection with volume confirmation"""
        try:
            if len(df) < 3:
                return None
            
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            # Check if we have volume data (real API provides this)
            has_volume = 'volume' in current and 'volume' in previous
            
            current_body = abs(current['close'] - current['open'])
            previous_body = abs(previous['close'] - previous['open'])
            
            # Minimum body size requirement (avoid noise on small moves)
            min_body_requirement = (current['high'] - current['low']) * 0.001
            
            if current_body < min_body_requirement:
                return None
            
            # Bullish Engulfing with enhanced conditions
            if (current['close'] > current['open'] and  # Current bullish
                previous['close'] < previous['open'] and  # Previous bearish
                current['open'] <= previous['close'] and   # Opens at or below previous close
                current['close'] >= previous['open'] and   # Closes at or above previous open
                current_body > previous_body * 1.3):       # Body is significantly larger (30%)
                
                # Volume confirmation for real data
                volume_confirmation = 1.0
                if has_volume and previous['volume'] > 0:
                    volume_ratio = current['volume'] / previous['volume']
                    volume_confirmation = min(volume_ratio, 2.0)  # Cap at 2.0
                
                confidence = min(75 + int((current_body / previous_body - 1) * 50 * volume_confirmation), 90)
                
                return {
                    'type': 'BULLISH_ENGULFING',
                    'direction': 'BUY',
                    'confidence': confidence,
                    'timestamp': datetime.now(),
                    'volume_confirmation': volume_confirmation
                }
            
            # Bearish Engulfing with enhanced conditions
            elif (current['close'] < current['open'] and  # Current bearish
                  previous['close'] > previous['open'] and  # Previous bullish
                  current['open'] >= previous['close'] and   # Opens at or above previous close
                  current['close'] <= previous['open'] and   # Closes at or below previous open
                  current_body > previous_body * 1.3):       # Body is significantly larger (30%)
                
                # Volume confirmation for real data
                volume_confirmation = 1.0
                if has_volume and previous['volume'] > 0:
                    volume_ratio = current['volume'] / previous['volume']
                    volume_confirmation = min(volume_ratio, 2.0)
                
                confidence = min(75 + int((current_body / previous_body - 1) * 50 * volume_confirmation), 90)
                
                return {
                    'type': 'BEARISH_ENGULFING',
                    'direction': 'SELL',
                    'confidence': confidence,
                    'timestamp': datetime.now(),
                    'volume_confirmation': volume_confirmation
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in engulfing detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _detect_pin_bar(self, df):
        """Enhanced pin bar detection with location context"""
        try:
            if len(df) < 5:
                return None
            
            candle = df.iloc[-1]
            candle_range = candle['high'] - candle['low']
            
            if candle_range == 0:
                return None
            
            body_size = abs(candle['close'] - candle['open'])
            upper_wick = candle['high'] - max(candle['open'], candle['close'])
            lower_wick = min(candle['open'], candle['close']) - candle['low']
            
            # More realistic pin bar conditions
            is_small_body = body_size / candle_range < 0.4  # Slightly more flexible
            has_long_upper_wick = upper_wick / candle_range > 0.5  # Reduced threshold
            has_long_lower_wick = lower_wick / candle_range > 0.5  # Reduced threshold
            
            # Check if pin bar is at significant level
            at_support = self._is_near_support(df)
            at_resistance = self._is_near_resistance(df)
            
            if is_small_body and (has_long_upper_wick or has_long_lower_wick):
                confidence = 70  # Base confidence
                
                # Increase confidence if at key level
                if has_long_upper_wick and upper_wick > lower_wick * 1.8:  # Reduced ratio
                    if at_resistance:
                        confidence = 80
                    return {
                        'type': 'BEARISH_PINBAR',
                        'direction': 'SELL',
                        'confidence': confidence,
                        'timestamp': datetime.now(),
                        'at_key_level': at_resistance
                    }
                elif has_long_lower_wick and lower_wick > upper_wick * 1.8:  # Reduced ratio
                    if at_support:
                        confidence = 80
                    return {
                        'type': 'BULLISH_PINBAR',
                        'direction': 'BUY',
                        'confidence': confidence,
                        'timestamp': datetime.now(),
                        'at_key_level': at_support
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in pin bar detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _detect_double_top_bottom(self, df):
        """Detect double top and bottom patterns"""
        try:
            if len(df) < 20:
                return None
            
            # Use last 15 candles for pattern detection
            recent = df.tail(15)
            highs = recent['high'].values
            lows = recent['low'].values
            
            # Find potential double top (M pattern)
            if len(highs) >= 5:
                # Look for two similar highs with dip in between
                peak1 = highs[-5]
                peak2 = highs[-1]
                trough = lows[-3]
                
                peak_diff = abs(peak1 - peak2) / peak1
                decline_depth = (peak1 - trough) / peak1
                
                if (peak_diff < 0.002 and  # Peaks within 0.2%
                    decline_depth > 0.001 and  # Meaningful decline
                    peak2 < peak1):  # Second peak slightly lower (resistance)
                    
                    return {
                        'type': 'DOUBLE_TOP',
                        'direction': 'SELL',
                        'confidence': 75,
                        'timestamp': datetime.now()
                    }
            
            # Find potential double bottom (W pattern)
            if len(lows) >= 5:
                trough1 = lows[-5]
                trough2 = lows[-1]
                peak = highs[-3]
                
                trough_diff = abs(trough1 - trough2) / trough1
                rise_depth = (peak - trough1) / trough1
                
                if (trough_diff < 0.002 and  # Troughs within 0.2%
                    rise_depth > 0.001 and  # Meaningful rise
                    trough2 > trough1):  # Second trough slightly higher (support)
                    
                    return {
                        'type': 'DOUBLE_BOTTOM',
                        'direction': 'BUY',
                        'confidence': 75,
                        'timestamp': datetime.now()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in double top/bottom detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _detect_support_resistance_break(self, df):
        """Detect support and resistance breaks"""
        try:
            if len(df) < 25:
                return None
            
            # Use more data for reliable S/R levels
            historical = df.tail(25)
            current = df.iloc[-1]
            
            # Find key resistance level (recent high)
            resistance = historical['high'].max()
            # Find key support level (recent low)
            support = historical['low'].min()
            
            current_high = current['high']
            current_low = current['low']
            current_close = current['close']
            
            # Resistance break with close above
            resistance_distance = abs(current_high - resistance) / resistance
            if (current_close > resistance and 
                resistance_distance < 0.005):  # Within 0.5% of resistance
                
                return {
                    'type': 'RESISTANCE_BREAK',
                    'direction': 'BUY',
                    'confidence': 80,
                    'timestamp': datetime.now(),
                    'break_level': resistance
                }
            
            # Support break with close below
            support_distance = abs(current_low - support) / support
            if (current_close < support and 
                support_distance < 0.005):  # Within 0.5% of support
                
                return {
                    'type': 'SUPPORT_BREAK', 
                    'direction': 'SELL',
                    'confidence': 80,
                    'timestamp': datetime.now(),
                    'break_level': support
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in S/R break detection: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _analyze_market_structure(self, df):
        """Enhanced market structure analysis"""
        try:
            if len(df) < 20:
                return None
            
            recent = df.tail(20)
            prices = recent['close'].values
            
            # Calculate simple moving averages for trend
            sma_short = np.mean(prices[-5:])  # 5-period SMA
            sma_long = np.mean(prices[-10:])  # 10-period SMA
            
            # Trend determination
            if sma_short > sma_long * 1.001:  # Uptrend
                trend = "STRONG_UPTREND"
                direction = "BUY"
                confidence = 70
            elif sma_short > sma_long:  # Weak uptrend
                trend = "UPTREND" 
                direction = "BUY"
                confidence = 60
            elif sma_short < sma_long * 0.999:  # Downtrend
                trend = "STRONG_DOWNTREND"
                direction = "SELL"
                confidence = 70
            elif sma_short < sma_long:  # Weak downtrend
                trend = "DOWNTREND"
                direction = "SELL" 
                confidence = 60
            else:
                trend = "SIDEWAYS"
                direction = "NEUTRAL"
                confidence = 50
            
            return {
                'type': 'MARKET_STRUCTURE',
                'direction': direction,
                'confidence': confidence,
                'timestamp': datetime.now(),
                'trend': trend,
                'sma_short': sma_short,
                'sma_long': sma_long
            }
            
        except Exception as e:
            logger.error(f"Error in market structure analysis: {e}", "PATTERN_DETECTOR", exc_info=True)
            return None
    
    def _is_near_support(self, df, lookback=10, threshold=0.002):
        """Check if current price is near support level"""
        try:
            if len(df) < lookback + 1:
                return False
            
            historical = df.tail(lookback)
            current_low = df.iloc[-1]['low']
            support_level = historical['low'].min()
            
            return abs(current_low - support_level) / support_level <= threshold
            
        except Exception as e:
            logger.error(f"Error checking support: {e}", "PATTERN_DETECTOR")
            return False
    
    def _is_near_resistance(self, df, lookback=10, threshold=0.002):
        """Check if current price is near resistance level"""
        try:
            if len(df) < lookback + 1:
                return False
            
            historical = df.tail(lookback)
            current_high = df.iloc[-1]['high']
            resistance_level = historical['high'].max()
            
            return abs(current_high - resistance_level) / resistance_level <= threshold
            
        except Exception as e:
            logger.error(f"Error checking resistance: {e}", "PATTERN_DETECTOR")
            return False
