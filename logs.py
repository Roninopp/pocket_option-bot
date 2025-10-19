import logging
import os
from datetime import datetime
import traceback
import sys

class Logger:
    def __init__(self, name="TradingBot", log_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        log_filename = f"logs/trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message, module_name=""):
        if module_name:
            message = f"[{module_name}] {message}"
        self.logger.debug(message)
    
    def info(self, message, module_name=""):
        if module_name:
            message = f"[{module_name}] {message}"
        self.logger.info(message)
    
    def warning(self, message, module_name=""):
        if module_name:
            message = f"[{module_name}] {message}"
        self.logger.warning(message)
    
    def error(self, message, module_name="", exc_info=False):
        if module_name:
            message = f"[{module_name}] {message}"
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, module_name=""):
        if module_name:
            message = f"[{module_name}] {message}"
        self.logger.critical(message)
    
    def exception(self, message, module_name=""):
        if module_name:
            message = f"[{module_name}] {message}"
        self.logger.exception(message)
    
    def log_pattern_detection(self, pattern_type, symbol, timeframe, confidence):
        message = f"Pattern Detected - {pattern_type} | Symbol: {symbol} | TF: {timeframe} | Confidence: {confidence}%"
        self.info(message, "PATTERN")
    
    def log_prediction(self, symbol, direction, timeframe, reason):
        message = f"PREDICTION - {symbol} | Direction: {direction} | TF: {timeframe} | Reason: {reason}"
        self.info(message, "PREDICTION")
    
    def log_api_error(self, api_name, error, function_name=""):
        message = f"API Error in {function_name} - {api_name}: {error}"
        self.error(message, "API")

logger = Logger()

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception