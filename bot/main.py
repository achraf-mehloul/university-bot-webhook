from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update
from flask import Flask, request, jsonify
import logging
import os
import asyncio
from bot import config, handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot_app = None

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "University Bot",
        "webhook": f"{config.WEBHOOK_URL}/webhook" if config.WEBHOOK_URL else "Not set"
    }), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string, bot_app.bot)
        asyncio.run_coroutine_threadsafe(
            bot_app.process_update(update),
            bot_app._get_running_loop()
        )
        return 'ok', 200
    return 'Bad Request', 400

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    if not config.WEBHOOK_URL:
        return jsonify({"error": "WEBHOOK_URL not set"}), 400
    
    async def set_webhook_async():
        try:
            result = await bot_app.bot.set_webhook(
                url=f"{config.WEBHOOK_URL}/webhook",
                secret_token=config.SECRET_KEY,
                max_connections=40,
                drop_pending_updates=True
            )
            return result
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(set_webhook_async())
    
    if success:
        return jsonify({"status": "success", "url": f"{config.WEBHOOK_URL}/webhook"}), 200
    else:
        return jsonify({"status": "error"}), 500

def setup_bot():
    global bot_app
    
    try:
        bot_app = Application.builder() \
            .token(config.BOT_TOKEN) \
            .connect_timeout(30.0) \
            .read_timeout(30.0) \
            .build()
        
        bot_app.add_handler(CommandHandler("start", handlers.start))
        bot_app.add_handler(CommandHandler("help", handlers.help_command))
        bot_app.add_handler(CallbackQueryHandler(handlers.handle_callback))
        
        logger.info("🤖 Bot application built successfully")
        
        if config.WEBHOOK_URL:
            logger.info(f"🌐 Using webhook: {config.WEBHOOK_URL}")
            
            async def initialize_webhook():
                await bot_app.initialize()
                await bot_app.start()
                
                await bot_app.bot.set_webhook(
                    url=f"{config.WEBHOOK_URL}/webhook",
                    secret_token=config.SECRET_KEY,
                    max_connections=40,
                    drop_pending_updates=True
                )
                logger.info("✅ Webhook set successfully")
                
                await asyncio.Event().wait()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(initialize_webhook())
        else:
            logger.info("🔍 No webhook URL, using polling")
            bot_app.run_polling(drop_pending_updates=True)
            
    except Exception as e:
        logger.error(f"❌ Bot setup failed: {e}")
        raise

def start_app():
    logger.info(f"🚀 Starting on port {config.PORT}")
    
    import threading
    bot_thread = threading.Thread(target=setup_bot, daemon=True)
    bot_thread.start()
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG, use_reloader=False)

if __name__ == '__main__':
    start_app()
