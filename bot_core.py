# bot_core.py (UPDATED)
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
        self.analysis_interval = 300  # 5 minutes between analyses to avoid spam
        self.last_signal_time = {}
        self.signals_sent = 0
        
        self.tz = timezone(timedelta(hours=7))
        
        self.pattern_detector = PatternDetector()
        self.market_data = MarketData()
        self.telegram_handler = TelegramHandler()
        
        # Analysis thread
        self.analysis_thread = None
        
        logger.info("Trading Bot Core initialized successfully", "BOT_CORE")
    
    def start(self, pocket_option_email=None, pocket_option_password=None):
        """Start the trading bot with real data"""
        try:
            if self.is_running:
                logger.warning("Bot is already running", "BOT_CORE")
                return False
            
            # Initialize real market data
            if pocket_option_email and pocket_option_password:
                real_data_initialized = self.market_data.initialize_real_data(
                    pocket_option_email, pocket_option_password
                )
                if real_data_initialized:
                    logger.info("✅ Using REAL Pocket Option market data", "BOT_CORE")
                else:
                    logger.warning("⚠️ Using SAMPLE data (Pocket Option connection failed)", "BOT_CORE")
            else:
                logger.warning("⚠️ Using SAMPLE data (no Pocket Option credentials)", "BOT_CORE")
            
            # Start Telegram command polling
            self.telegram_handler.start_polling(self)
            
            # Start analysis thread
            self.is_running = True
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            # Send startup message
            self.telegram_handler.send_message(
                "🤖 <b>Trading Bot Started</b>\n"
                f"📈 Monitoring {len(self.symbols)} symbols\n"
                f"⏰ Timeframes: {', '.join(self.timeframes)}\n"
                f"💡 Using {'REAL' if self.market_data.use_real_data else 'SAMPLE'} market data"
            )
            
            logger.info("Trading bot started successfully", "BOT_CORE")
            return True
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}", "BOT_CORE", exc_info=True)
            return False
    
    def stop(self):
        """Stop the trading bot"""
        try:
            self.is_running = False
            self.telegram_handler.stop_polling()
            
            if self.analysis_thread and self.analysis_thread.is_alive():
                self.analysis_thread.join(timeout=5)
            
            self.telegram_handler.send_message("🛑 <b>Trading Bot Stopped</b>")
            logger.info("Trading bot stopped", "BOT_CORE")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", "BOT_CORE", exc_info=True)
            return False
    
    def _analysis_loop(self):
        """Main analysis loop with real data"""
        logger.info("Analysis loop started", "BOT_CORE")
        
        while self.is_running:
            try:
                current_time = datetime.now(self.tz)
                
                # Analyze each symbol and timeframe
                for symbol in self.symbols:
                    for timeframe in self.timeframes:
                        self._analyze_symbol_timeframe(symbol, timeframe, current_time)
                
                # Wait for next analysis cycle
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}", "BOT_CORE", exc_info=True)
                time.sleep(60)  # Wait 1 minute on error
    
    def _analyze_symbol_timeframe(self, symbol, timeframe, current_time):
        """Analyze specific symbol and timeframe with real data"""
        try:
            # Get market data (real or sample)
            df = self.market_data.get_real_data(symbol, timeframe, candles=100)
            
            if df.empty:
                logger.warning(f"No data for {symbol} {timeframe}", "BOT_CORE")
                return
            
            # Detect patterns
            patterns = self.pattern_detector.detect_patterns(df, timeframe)
            
            # Process detected patterns
            for pattern in patterns:
                if self._should_send_signal(symbol, timeframe, pattern, current_time):
                    self._send_trading_signal(symbol, timeframe, pattern, df)
                    
        except Exception as e:
            logger.error(f"Error analyzing {symbol} {timeframe}: {e}", "BOT_CORE", exc_info=True)
    
    def _should_send_signal(self, symbol, timeframe, pattern, current_time):
        """Check if we should send a signal (avoid spam)"""
        key = f"{symbol}_{timeframe}_{pattern['direction']}"
        
        # Check if we recently sent a similar signal
        last_time = self.last_signal_time.get(key)
        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            if time_diff < 3600:  # 1 hour cooldown for same symbol/tf/direction
                return False
        
        # Only send high confidence signals
        if pattern.get('confidence', 0) < 70:
            return False
            
        return True
    
    def _send_trading_signal(self, symbol, timeframe, pattern, df):
        """Send trading signal to Telegram"""
        try:
            # Create prediction object
            prediction = {
                'symbol': symbol,
                'direction': pattern['direction'],
                'timeframe': timeframe,
                'pattern_type': pattern['type'],
                'confidence': pattern['confidence'],
                'timestamp': datetime.now(self.tz),
                'reason': f"Pattern: {pattern['type']} with {pattern['confidence']}% confidence",
                'market_structure': self._analyze_market_structure(df)
            }
            
            # Send to Telegram
            success = self.telegram_handler.send_prediction(prediction)
            
            if success:
                # Update tracking
                key = f"{symbol}_{timeframe}_{pattern['direction']}"
                self.last_signal_time[key] = datetime.now(self.tz)
                self.signals_sent += 1
                
                logger.log_prediction(
                    symbol, pattern['direction'], timeframe, 
                    f"{pattern['type']} ({pattern['confidence']}%)"
                )
                
        except Exception as e:
            logger.error(f"Error sending signal: {e}", "BOT_CORE", exc_info=True)
    
    def _analyze_market_structure(self, df):
        """Analyze market structure from price data"""
        try:
            if len(df) < 20:
                return {'trend': 'UNKNOWN', 'support': None, 'resistance': None}
            
            recent = df.tail(20)
            prices = recent['close'].values
            
            # Simple trend detection
            if prices[-1] > prices[0]:
                trend = "UPTREND"
            elif prices[-1] < prices[0]:
                trend = "DOWNTREND"
            else:
                trend = "SIDEWAYS"
            
            return {
                'trend': trend,
                'support': float(recent['low'].min()),
                'resistance': float(recent['high'].max())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}", "BOT_CORE")
            return {'trend': 'UNKNOWN', 'support': None, 'resistance': None}
    
    def get_bot_status(self):
        """Get bot status for commands"""
        return {
            'status': 'RUNNING' if self.is_running else 'STOPPED',
            'symbols': len(self.symbols),
            'timeframes': self.timeframes,
            'signals_sent': self.signals_sent,
            'last_analysis': datetime.now().strftime('%H:%M:%S'),
            'data_source': 'REAL' if self.market_data.use_real_data else 'SAMPLE'
                }
