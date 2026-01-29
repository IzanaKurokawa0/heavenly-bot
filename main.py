import os
import json
import logging
import requests
import asyncio
from datetime import datetime
from flask import Flask
import threading
import time

print("=" * 60)
print("🤖 HEAVENLY DYNASTY BOT v3.0")
print("=" * 60)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAFA4ZcJMuzOkv3PFWB88Wxe1Pal31WEquA')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyIiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE2MSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

print(f"Telegram Token: {'✅ Установлен' if TELEGRAM_TOKEN else '❌ Нет'}")
print(f"Brawl API Key: {'✅ Установлен' if BRAWL_API_KEY else '❌ Нет'}")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DATA_FILE = 'clubs_data.json'

# ... (все ваши функции: load_data, save_data, get_default_clubs, format_num и т.д.)

async def start_bot():
    """Запускает Telegram бота (версия 20.7+)"""
    print("🤖 Инициализирую Telegram бота...")
    
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        from telegram.constants import ParseMode
        
        # ✅ ВАЖНО: Application вместо Updater
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # ... (все ваши async функции: start_command, rating_command и т.д.)
        
        # ✅ Добавляем обработчики
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("rating", rating_command))
        application.add_handler(CommandHandler("update", update_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        
        # ... (добавление команд клубов)
        
        print("✅ Telegram bot configured")
        
        # ✅ Запускаем правильно для v20.7
        await application.initialize()
        await application.start()
        await application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()

# ... (Flask роуты: /, /health, /stats, /update)

def start_services():
    print("🚀 Starting services...")
    
    def run_bot_in_thread():
        asyncio.run(start_bot())
    
    bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
    bot_thread.start()
    time.sleep(2)
    
    if bot_thread.is_alive():
        print("✅ Bot thread started")
    else:
        print("⚠️ Bot thread may have failed")
    
    print("🌐 Flask web server ready")

start_services()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    print(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
