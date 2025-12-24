import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "7194132273:AAFFf4Q9J4YJFKPm0poQ1DEjKn4WJYSNgec")

IS_RENDER = os.getenv('RENDER', False)
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', '')

if IS_RENDER and RENDER_EXTERNAL_URL:
    WEBHOOK_URL = RENDER_EXTERNAL_URL.rstrip('/')
else:
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()

PORT = int(os.getenv("PORT", 10000))
HOST = os.getenv("HOST", "0.0.0.0")
SECRET_KEY = os.getenv("SECRET_KEY", "c38579525d722b32f6c20d4dd09a744ab8bcd81061f6d58c9ff6d4fdd7dab210")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
