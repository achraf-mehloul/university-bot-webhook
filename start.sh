#!/bin/bash

echo "🚀 Starting University Bot on Render..."

pip install -r requirements.txt

export PORT=${PORT:-10000}
export HOST=0.0.0.0

if [ -n "$RENDER_EXTERNAL_URL" ]; then
    export WEBHOOK_URL=$RENDER_EXTERNAL_URL
    echo "🌐 Webhook URL: $WEBHOOK_URL"
fi

exec gunicorn bot.main:app \
    --workers=1 \
    --threads=4 \
    --bind=$HOST:$PORT \
    --timeout=120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
