#!/usr/bin/env python3
"""Script to setup webhook after deployment"""
import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def setup_webhook():
    bot_token = os.getenv("BOT_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL")
    secret_key = os.getenv("SECRET_KEY")
    
    if not all([bot_token, webhook_url]):
        print("❌ Missing required environment variables")
        return
    
    bot = Bot(token=bot_token)
    full_url = f"{webhook_url}/webhook"
    
    try:
        result = await bot.set_webhook(
            url=full_url,
            secret_token=secret_key,
            max_connections=40,
            drop_pending_updates=True
        )
        if result:
            print(f"✅ Webhook set successfully: {full_url}")
        else:
            print("❌ Failed to set webhook")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(setup_webhook())
