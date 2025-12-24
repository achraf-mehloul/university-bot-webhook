import os
from dotenv import load_dotenv

load_dotenv()

# Required
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Render specific
IS_RENDER = os.getenv('RENDER', False)
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', '')
RENDER_SERVICE_NAME = os.getenv('RENDER_SERVICE_NAME', 'university-bot')

# Webhook configuration
if IS_RENDER and RENDER_EXTERNAL_URL:
    WEBHOOK_URL = RENDER_EXTERNAL_URL.rstrip('/')
else:
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()

# Server configuration
PORT = int(os.getenv("PORT", 10000))  # Render uses port 10000
HOST = os.getenv("HOST", "0.0.0.0")
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("RENDER_GENERAL_SECRET_KEY", "default-secret-key"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Log configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validate required variables
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is required in environment variables!")

print(f"✅ Config loaded: Render={IS_RENDER}, Webhook={WEBHOOK_URL}, Port={PORT}")