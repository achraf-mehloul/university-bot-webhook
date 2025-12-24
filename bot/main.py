from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update
from flask import Flask, request, jsonify
import logging
import os
import asyncio
from bot import config, handlers

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
bot_app = None

@app.route('/')
def home():
    return jsonify({
        "status": "online", 
        "service": "University Bot",
        "endpoints": ["/", "/health", "/set_webhook", "/webhook"]
    }), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "bot": "running"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string, bot_app.bot)
        
        # Process update in background
        asyncio.run_coroutine_threadsafe(
            bot_app.process_update(update),
            bot_app._get_running_loop()
        )
        return 'ok', 200
    return 'Bad Request', 400

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Manually set webhook URL"""
    if not config.WEBHOOK_URL:
        return jsonify({"error": "WEBHOOK_URL not set"}), 400
    
    webhook_url = f"{config.WEBHOOK_URL}/webhook"
    
    async def set_webhook_async():
        try:
            result = await bot_app.bot.set_webhook(
                url=webhook_url,
                secret_token=config.SECRET_KEY,
                max_connections=40,
                drop_pending_updates=True
            )
            return result
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(set_webhook_async())
    
    if success:
        logger.info(f"✅ Webhook set successfully: {webhook_url}")
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url,
            "message": "Webhook configured successfully"
        }), 200
    else:
        logger.error("❌ Failed to set webhook")
        return jsonify({
            "status": "error",
            "message": "Failed to set webhook"
        }), 500

def setup_bot():
    """Setup and run the bot"""
    global bot_app
    
    try:
        # Build bot application with timeout settings
        bot_app = Application.builder() \
            .token(config.BOT_TOKEN) \
            .connect_timeout(30.0) \
            .read_timeout(30.0) \
            .write_timeout(30.0) \
            .pool_timeout(30.0) \
            .build()
        
        # Add handlers
        bot_app.add_handler(CommandHandler("start", handlers.start))
        bot_app.add_handler(CommandHandler("help", handlers.help_command))
        bot_app.add_handler(CallbackQueryHandler(handlers.handle_callback))
        
        logger.info("🤖 Bot application built successfully")
        
        # Check if running on Render (has RENDER environment variable)
        is_render = os.getenv('RENDER', False)
        
        if config.WEBHOOK_URL and not is_render:
            # Setup webhook for external services
            webhook_url = f"{config.WEBHOOK_URL}/webhook"
            logger.info(f"🔗 Setting up webhook: {webhook_url}")
            
            # Start webhook
            bot_app.run_webhook(
                listen=config.HOST,
                port=config.PORT,
                url_path="/webhook",
                webhook_url=webhook_url,
                secret_token=config.SECRET_KEY,
                drop_pending_updates=True
            )
        else:
            # On Render, start with webhook or polling based on WEBHOOK_URL
            if config.WEBHOOK_URL:
                logger.info(f"🚀 Starting on Render with webhook: {config.WEBHOOK_URL}")
                
                # Set webhook first, then run
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def initialize():
                    await bot_app.initialize()
                    await bot_app.start()
                    
                    # Set webhook
                    await bot_app.bot.set_webhook(
                        url=f"{config.WEBHOOK_URL}/webhook",
                        secret_token=config.SECRET_KEY,
                        max_connections=40,
                        drop_pending_updates=True
                    )
                    logger.info("✅ Webhook set on Render")
                    
                    # Keep the bot running
                    await asyncio.Event().wait()
                
                loop.run_until_complete(initialize())
            else:
                # Fallback to polling on Render if no webhook URL
                logger.info("🔍 Starting in polling mode on Render")
                bot_app.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True
                )
                
    except Exception as e:
        logger.error(f"❌ Error setting up bot: {e}")
        raise

def start_app():
    """Start the application"""
    logger.info("🚀 Starting University Bot...")
    
    # Import and start bot in a separate thread
    import threading
    
    bot_thread = threading.Thread(target=setup_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=False
    )

if __name__ == '__main__':
    start_app()