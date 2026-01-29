import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request
import threading
import time

print("=" * 60)
print("🤖 HEAVENLY DYNASTY BOT - DEPLOY READY")
print("=" * 60)

# Проверяем токены
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY')

if not TELEGRAM_TOKEN:
    print("⚠️  TELEGRAM_TOKEN не установлен в переменных окружения")
    print("   Бот будет работать в режиме только веб-сервера")
else:
    print("✅ TELEGRAM_TOKEN: Установлен")

if not BRAWL_API_KEY:
    print("⚠️  BRAWL_API_KEY не установлен")
else:
    print("✅ BRAWL_API_KEY: Установлен")

# Flask app
app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Простые маршруты для проверки
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Heavenly Dynasty Bot</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .running { background: #d4edda; color: #155724; }
            .warning { background: #fff3cd; color: #856404; }
        </style>
    </head>
    <body>
        <h1>🤖 Heavenly Dynasty Bot</h1>
        <div class="status running">
            ✅ <strong>Status:</strong> Running
        </div>
        <p>Version: 3.0 (Deploy Ready)</p>
        <p><strong>Endpoints:</strong></p>
        <ul>
            <li><a href="/health">/health</a> - Health check</li>
            <li><a href="/status">/status</a> - Bot status</li>
            <li><a href="/test">/test</a> - Test endpoint</li>
        </ul>
        <p><em>Telegram bot runs in background</em></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200

@app.route('/status')
def status():
    return {
        "service": "Heavenly Dynasty Bot",
        "status": "running",
        "telegram_token_set": bool(TELEGRAM_TOKEN),
        "brawl_api_key_set": bool(BRAWL_API_KEY),
        "timestamp": datetime.now().isoformat()
    }, 200

@app.route('/test')
def test():
    return {"message": "Test successful!", "timestamp": datetime.now().isoformat()}, 200

# Простая функция для имитации работы (без асинхронности)
def run_simple_bot():
    """Упрощённая версия бота для деплоя"""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не установлен, Telegram бот не запускается")
        return
    
    print("🤖 Attempting to start Telegram bot...")
    
    # Импортируем здесь, чтобы не падать при отсутствии библиотеки
    try:
        import asyncio
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        from telegram.constants import ParseMode
        
        async def simple_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "🤖 Heavenly Dynasty Bot is running!\n"
                "✅ Service deployed successfully\n"
                f"👋 Hello, {update.effective_user.first_name}!",
                parse_mode=ParseMode.HTML
            )
        
        async def main():
            # Создаём приложение
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # Добавляем команду
            application.add_handler(CommandHandler("start", simple_start))
            
            print("✅ Telegram bot configured")
            print("📱 Send /start to your bot in Telegram")
            
            # Запускаем polling
            await application.run_polling(allowed_updates=Update.ALL_TYPES)
        
        # Запускаем бота
        asyncio.run(main())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install python-telegram-bot[job-queue]==20.7")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()

# Функция запуска бота в отдельном потоке
def start_bot_in_thread():
    """Запускает бота в отдельном потоке"""
    print("🧵 Starting bot in separate thread...")
    bot_thread = threading.Thread(target=run_simple_bot, daemon=True)
    bot_thread.start()
    time.sleep(2)  # Даём время на инициализацию
    if bot_thread.is_alive():
        print("✅ Bot thread started successfully")
    else:
        print("⚠️  Bot thread may have failed")

# Основная функция запуска
def main():
    """Основная функция инициализации"""
    print("🚀 Initializing services...")
    
    # Запускаем бота в отдельном потоке (если есть токен)
    if TELEGRAM_TOKEN:
        start_bot_in_thread()
    else:
        print("⚠️  Skipping bot startup (no TELEGRAM_TOKEN)")
    
    # Получаем порт из переменных окружения
    port = int(os.getenv('PORT', 10000))
    
    print(f"🌐 Starting Flask web server on port {port}")
    print("=" * 60)
    print(f"📊 Health check: https://your-app.onrender.com/health")
    print(f"📋 Status: https://your-app.onrender.com/status")
    print("=" * 60)
    
    # Запускаем Flask сервер
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False  # Важно для Render!
    )

# Точка входа
if __name__ == '__main__':
    main()
