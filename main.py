# main.py
import os
import signal
import sys
from bot_core import TradingBotCore
from logs import logger

def main():
    """Main application entry point"""
    print("🤖 Trading Bot Starting...")
    
    # Create bot instance
    bot = TradingBotCore()
    
    # Get Pocket Option credentials from environment or config
    po_email = os.getenv('POCKET_OPTION_EMAIL')
    po_password = os.getenv('POCKET_OPTION_PASSWORD')
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down bot...")
        bot.stop()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the bot
        if bot.start(po_email, po_password):
            print("✅ Bot started successfully")
            print("💡 Use /start, /status, /logs in Telegram to interact")
            print("🛑 Press Ctrl+C to stop the bot")
            
            # Keep main thread alive
            while bot.is_running:
                signal.pause()
                
        else:
            print("❌ Failed to start bot")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", "MAIN", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
