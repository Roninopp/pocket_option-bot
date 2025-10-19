# config.py
import os

class Config:
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = "7914882777:AAGv_940utBNry2JXfwbzhtZWxtyK1qMO24"
    TELEGRAM_CHAT_ID = "-1002903475551"
    
    # Pocket Option Configuration
    POCKET_OPTION_EMAIL = os.getenv('POCKET_OPTION_EMAIL', '')
    POCKET_OPTION_PASSWORD = os.getenv('POCKET_OPTION_PASSWORD', '')
    
    # Trading Configuration
    SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    TIMEFRAMES = ['5min', '15min']
    ANALYSIS_INTERVAL = 300  # 5 minutes
    
    # Risk Management
    MIN_CONFIDENCE = 70
    COOLDOWN_PERIOD = 3600  # 1 hour between similar signals
