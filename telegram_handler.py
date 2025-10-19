cat > telegram_handler.py << 'EOF'
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
        self.commands_running = False
        
    def send_prediction(self, prediction):
        """Send prediction to Telegram"""
        try:
            message = self._format_prediction_message(prediction)
            
            # Send message to Telegram
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Prediction sent to Telegram successfully", "TELEGRAM")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}", "TELEGRAM")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}", "TELEGRAM", exc_info=True)
            return False
    
    def send_message(self, text):
        """Send simple message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending message: {e}", "TELEGRAM")
            return False
    
    def _format_prediction_message(self, prediction):
        """Format prediction message for Telegram"""
        try:
            symbol = prediction.get('symbol', 'EURUSD')
            direction = prediction.get('direction', 'NEUTRAL')
            timeframe = prediction.get('timeframe', '5min')
            pattern_type = prediction.get('pattern_type', 'Unknown Pattern')
            confidence = prediction.get('confidence', 0)
            reason = prediction.get('reason', 'Pattern based prediction')
            
            # Format timestamp for UTC+7
            timestamp = prediction.get('timestamp')
            if hasattr(timestamp, 'strftime'):
                time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S UTC+7')
            else:
                time_str = "Unknown time"
            
            # Emojis based on direction
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
🎯 <b>TRADING SIGNAL DETECTED</b> 🎯

{direction_emoji} <b>Direction:</b> {action}
📊 <b>Symbol:</b> {symbol}
⏰ <b>Timeframe:</b> {timeframe}
🔍 <b>Pattern:</b> {pattern_type}
💪 <b>Confidence:</b> {confidence}%
📈 <b>Market Structure:</b> {prediction.get('market_structure', {}).get('trend', 'Unknown')}

📝 <b>Reason:</b>
{reason}

🕐 <b>Time:</b> {time_str}

⚠️ <i>Always use proper risk management</i>

💬 <i>Use /status for bot status</i>
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Error formatting message: {e}", "TELEGRAM", exc_info=True)
            return "Trading signal generated - check logs for details"
    
    def test_connection(self):
        """Test Telegram connection"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram connection test successful", "TELEGRAM")
                return True
            else:
                logger.error(f"Telegram connection test failed: {response.status_code}", "TELEGRAM")
                return False
                
        except Exception as e:
            logger.error(f"Telegram connection test error: {e}", "TELEGRAM", exc_info=True)
            return False

    def get_bot_commands(self):
        """Get available bot commands"""
        commands = {
            '/status': 'Get bot status and statistics',
            '/logs': 'Get recent logs (last 10 lines)',
            '/stop': 'Stop the bot',
            '/start': 'Start the bot'
        }
        return commands
EOF
