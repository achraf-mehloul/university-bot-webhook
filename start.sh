
echo "🚀 Starting University Bot on Render..."

pip install --upgrade pip
pip install -r requirements.txt

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

mkdir -p logs

export PORT=${PORT:-10000}
export HOST=0.0.0.0

if [ -n "$RENDER_EXTERNAL_URL" ]; then
    export WEBHOOK_URL=$RENDER_EXTERNAL_URL
    echo "🌐 Webhook URL set to: $WEBHOOK_URL"
fi

echo "📡 Starting Gunicorn on port $PORT..."
exec gunicorn bot.main:app \
    --workers=1 \
    --threads=4 \
    --bind=$HOST:$PORT \
    --timeout=120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --worker-class sync