 # telegram_handler.py (UPDATED)
import requests
import time
import threading
import json
from logs import logger

class TelegramHandler:
    def __init__(self):
        logger.info("Telegram Handler initialized", "TELEGRAM")
        self.bot_token = "7914882777:AAGv_940utBNry2JXfwbzhtZWxtyK1qMO24"
        self.chat_id = "-1002903475551"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        self.command_handlers = {}
        self.polling_thread = None
        self.is_polling = False
        
        # Register command handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register command handlers"""
        self.command_handlers = {
            '/start': self._handle_start,
            '/status': self._handle_status,
            '/logs': self._handle_logs,
            '/stop': self._handle_stop,
            '/help': self._handle_help
        }
    
    def start_polling(self, bot_core):
        """Start polling for Telegram commands"""
        self.bot_core = bot_core
        self.is_polling = True
        self.polling_thread = threading.Thread(target=self._poll_commands)
        self.polling_thread.daemon = True
        self.polling_thread.start()
        logger.info("Telegram command polling started", "TELEGRAM")
    
    def stop_polling(self):
        """Stop polling for commands"""
        self.is_polling = False
        logger.info("Telegram command polling stopped", "TELEGRAM")
    
    def _poll_commands(self):
        """Poll for Telegram commands"""
        while self.is_polling:
            try:
                updates = self._get_updates()
                if updates:
                    for update in updates:
                        self._process_update(update)
                
                time.sleep(2)  # Poll every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in command polling: {e}", "TELEGRAM", exc_info=True)
                time.sleep(5)
    
    def _get_updates(self):
        """Get new updates from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    updates = data['result']
                    if updates:
                        self.last_update_id = updates[-1]['update_id']
                    return updates
            return []
            
        except Exception as e:
            logger.error(f"Error getting updates: {e}", "TELEGRAM")
            return []
    
    def _process_update(self, update):
        """Process a single update"""
        try:
            if 'message' in update and 'text' in update['message']:
                message = update['message']
                chat_id = message['chat']['id']
                text = message['text'].strip()
                
                # Check if it's a command
                if text.startswith('/'):
                    self._handle_command(chat_id, text)
                    
        except Exception as e:
            logger.error(f"Error processing update: {e}", "TELEGRAM", exc_info=True)
    
    def _handle_command(self, chat_id, command):
        """Handle a command"""
        try:
            cmd_parts = command.split(' ')
            base_cmd = cmd_parts[0].lower()
            
            handler = self.command_handlers.get(base_cmd)
            if handler:
                handler(chat_id, cmd_parts)
            else:
                self.send_message(chat_id, f"❓ Unknown command: {base_cmd}\nUse /help for available commands.")
                
        except Exception as e:
            logger.error(f"Error handling command: {e}", "TELEGRAM", exc_info=True)
            self.send_message(chat_id, "❌ Error processing command")
    
    def _handle_start(self, chat_id, cmd_parts):
        """Handle /start command"""
        welcome_msg = """
🤖 <b>Trading Bot Started</b>

Available commands:
/status - Bot status and statistics
/logs - Recent logs (last 10 lines)
/stop - Stop the bot
/help - Show this help message

Bot is now monitoring markets and will send signals when patterns are detected.
        """
        self.send_message(chat_id, welcome_msg)
    
    def _handle_status(self, chat_id, cmd_parts):
        """Handle /status command"""
        try:
            status = self.bot_core.get_bot_status()
            
            status_msg = f"""
📊 <b>Bot Status</b>

🟢 Status: {status['status']}
📈 Symbols: {status['symbols']}
⏰ Timeframes: {', '.join(status['timeframes'])}
📨 Signals Sent: {status['signals_sent']}
🕐 Last Analysis: {status['last_analysis']}

💡 Using {'REAL' if self.bot_core.market_data.use_real_data else 'SAMPLE'} market data
            """
            self.send_message(chat_id, status_msg)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}", "TELEGRAM")
            self.send_message(chat_id, "❌ Error getting bot status")
    
    def _handle_logs(self, chat_id, cmd_parts):
        """Handle /logs command"""
        try:
            logs = self._get_recent_logs(10)
            log_msg = f"📋 <b>Recent Logs</b>\n\n<code>{logs}</code>"
            self.send_message(chat_id, log_msg)
            
        except Exception as e:
            logger.error(f"Error in logs command: {e}", "TELEGRAM")
            self.send_message(chat_id, "❌ Error getting logs")
    
    def _handle_stop(self, chat_id, cmd_parts):
        """Handle /stop command"""
        try:
            self.bot_core.stop()
            self.send_message(chat_id, "🛑 Bot stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}", "TELEGRAM")
            self.send_message(chat_id, "❌ Error stopping bot")
    
    def _handle_help(self, chat_id, cmd_parts):
        """Handle /help command"""
        help_msg = """
📖 <b>Available Commands</b>

/start - Start the bot and show welcome
/status - Show bot status and statistics  
/logs - Get recent logs (last 10 lines)
/stop - Stop the bot
/help - Show this help message

The bot automatically analyzes markets and sends trading signals when patterns are detected.
        """
        self.send_message(chat_id, help_msg)
    
    def _get_recent_logs(self, lines=10):
        """Get recent logs from log file"""
        try:
            import os
            from datetime import datetime
            
            log_file = f"logs/trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    return ''.join(recent_lines).strip()
            return "No logs found for today"
            
        except Exception as e:
            logger.error(f"Error reading logs: {e}", "TELEGRAM")
            return f"Error reading logs: {e}"
    
    # ... [KEEP ALL EXISTING METHODS LIKE send_prediction, send_message, etc.]
