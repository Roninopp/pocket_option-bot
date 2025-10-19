import requests
import time
import threading
from logs import logger

class TelegramHandler:
    def __init__(self):
        logger.info("Telegram Handler initialized", "TELEGRAM")
        self.bot_token = "7914882777:AAGv_940utBNry2JXfwbzhtZWxtyK1qMO24"
        self.chat_id = "-1002903475551"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        self.is_polling = False
    
    # ✅ ADD THIS MISSING METHOD
    def send_message(self, text, chat_id=None):
        """Send simple message to Telegram"""
        try:
            if chat_id is None:
                chat_id = self.chat_id
                
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending message: {e}", "TELEGRAM")
            return False
    
    def send_prediction(self, prediction):
        """Send prediction to Telegram"""
        try:
            message = self._format_prediction_message(prediction)
            return self.send_message(message)
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}", "TELEGRAM", exc_info=True)
            return False
    
    def _format_prediction_message(self, prediction):
        """Format prediction message for Telegram"""
        try:
            symbol = prediction.get('symbol', 'EURUSD')
            direction = prediction.get('direction', 'NEUTRAL')
            timeframe = prediction.get('timeframe', '5min')
            pattern_type = prediction.get('pattern_type', 'Unknown Pattern')
            confidence = prediction.get('confidence', 0)
            
            if direction == 'BUY':
                direction_emoji = "🟢"
                action = "LONG"
            elif direction == 'SELL':
                direction_emoji = "🔴" 
                action = "SHORT"
            else:
                direction_emoji = "🟡"
                action = "WAIT"
            
            message = f"""
🎯 <b>TRADING SIGNAL</b>

{direction_emoji} <b>Direction:</b> {action}
📊 <b>Symbol:</b> {symbol}
⏰ <b>Timeframe:</b> {timeframe}
🔍 <b>Pattern:</b> {pattern_type}
💪 <b>Confidence:</b> {confidence}%

⚠️ <i>Use proper risk management</i>
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Error formatting message: {e}", "TELEGRAM", exc_info=True)
            return "Trading signal generated"
    
    def start_polling(self, bot_core):
        """Start polling for Telegram commands"""
        self.bot_core = bot_core
        self.is_polling = True
        logger.info("Telegram command polling started", "TELEGRAM")
    
    def stop_polling(self):
        """Stop polling for commands"""
        self.is_polling = False
        logger.info("Telegram command polling stopped", "TELEGRAM")
