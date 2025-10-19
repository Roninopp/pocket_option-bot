import time
import threading
from datetime import datetime, timezone, timedelta
from logs import logger
from pattern_detector import PatternDetector
from market_data import MarketData
from telegram_handler import TelegramHandler

class TradingBotCore:
    def __init__(self):
        logger.info("Initializing Trading Bot Core", "BOT_CORE")
        
        self.timeframes = ['5min', '15min']
        self.symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
        self.is_running = False
        self.analysis_interval = 60
        self.last_signal_time = {}
        
        self.tz = timezone(timedelta(hours=7))
        
        self.pattern_detector = PatternDetector()
        self.market_data = MarketData()
        self.telegram_handler = TelegramHandler()
        
        logger.info("Trading Bot Core initialized successfully", "BOT_CORE")
    
    def get_utc7_time(self):
        return datetime.now(self.tz)
    
    def start_bot(self):
        try:
            logger.info("Starting Trading Bot...", "BOT_CORE")
            
            if not self.telegram_handler.test_connection():
                logger.warning("Telegram connection test failed", "BOT_CORE")
            
            self.is_running = True
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            logger.info("Trading Bot started successfully", "BOT_CORE")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}", "BOT_CORE", exc_info=True)
            return False
    
    def stop_bot(self):
        logger.info("Stopping Trading Bot...", "BOT_CORE")
        self.is_running = False
    
    def _analysis_loop(self):
        while self.is_running:
            try:
                logger.debug("Starting analysis cycle", "ANALYSIS_LOOP")
                
                for symbol in self.symbols:
                    for timeframe in self.timeframes:
                        self._analyze_symbol(symbol, timeframe)
                
                logger.debug(f"Analysis completed. Waiting {self.analysis_interval}s", "ANALYSIS_LOOP")
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Analysis loop error: {e}", "ANALYSIS_LOOP", exc_info=True)
                time.sleep(self.analysis_interval)
    
    def _analyze_symbol(self, symbol, timeframe):
        try:
            signal_key = f"{symbol}_{timeframe}"
            current_time = time.time()
            if signal_key in self.last_signal_time:
                if current_time - self.last_signal_time[signal_key] < 300:
                    return
            
            logger.debug(f"Analyzing {symbol} on {timeframe}", "SYMBOL_ANALYSIS")
            
            df = self.market_data.get_sample_data(symbol, timeframe)
            
            if df.empty:
                logger.warning(f"No data for {symbol}", "SYMBOL_ANALYSIS")
                return
            
            patterns = self.pattern_detector.detect_patterns(df, timeframe)
            
            valid_patterns = []
            market_structure = None
            
            for pattern in patterns:
                if pattern['type'] in ['BULLISH_ENGULFING', 'BEARISH_ENGULFING', 'BULLISH_PINBAR', 'BEARISH_PINBAR']:
                    if pattern.get('confidence', 0) >= 70:
                        valid_patterns.append(pattern)
                
                if pattern['type'] == 'MARKET_STRUCTURE':
                    market_structure = pattern
            
            if valid_patterns and market_structure:
                for pattern in valid_patterns:
                    if self._is_trade_valid(pattern, market_structure):
                        prediction = self._generate_prediction(pattern, symbol, timeframe, market_structure)
                        if prediction:
                            if self.telegram_handler.send_prediction(prediction):
                                self.last_signal_time[signal_key] = current_time
                                time.sleep(2)
                                break
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", "SYMBOL_ANALYSIS", exc_info=True)
    
    def _is_trade_valid(self, pattern, market_structure):
        try:
            trend = market_structure.get('trend', 'SIDEWAYS')
            direction = pattern.get('direction', '')
            
            if trend == 'UPTREND' and direction == 'SELL':
                return False
            elif trend == 'DOWNTREND' and direction == 'BUY':
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating trade: {e}", "VALIDATION")
            return True
    
    def _generate_prediction(self, pattern, symbol, timeframe, market_structure):
        try:
            prediction = {
                'symbol': symbol,
                'direction': pattern['direction'],
                'timeframe': timeframe,
                'pattern_type': pattern['type'],
                'confidence': pattern.get('confidence', 0),
                'market_structure': market_structure,
                'timestamp': self.get_utc7_time(),
                'reason': self._get_prediction_reason(pattern, market_structure)
            }
            
            logger.log_prediction(symbol, pattern['direction'], timeframe, prediction['reason'])
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}", "PREDICTION", exc_info=True)
            return None
    
    def _get_prediction_reason(self, pattern, market_structure):
        reason = f"{pattern['type']} pattern detected"
        
        if market_structure:
            reason += f" in {market_structure['trend']} market"
            if market_structure.get('sweep_detected'):
                reason += " with liquidity sweep"
        
        reason += ". High confidence signal with trend confirmation."
        return reason

trading_bot = TradingBotCore()

def main():
    try:
        logger.info("=== TRADING BOT STARTING ===", "MAIN")
        
        if trading_bot.start_bot():
            logger.info("Bot is running. Press Ctrl+C to stop.", "MAIN")
            
            try:
                while trading_bot.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received Ctrl+C", "MAIN")
                
        trading_bot.stop_bot()
        logger.info("=== TRADING BOT STOPPED ===", "MAIN")
        
    except Exception as e:
        logger.error(f"Main error: {e}", "MAIN", exc_info=True)

if __name__ == "__main__":
    main()
