import os
import asyncio
from flask import Flask
import threading

print("=" * 60)
print("🤖 HEAVENLY BOT - NO UPDATER IMPORT")
print("=" * 60)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAFA4ZcJMuzOkv3PFWB88Wxe1Pal31WEquA')

async def bot_main():
    print("🤖 ЗАПУСК БОТА...")
    
    # ✅ Импортируем ТОЛЬКО нужное
    from telegram.ext import Application, CommandHandler
    from telegram import Update
    from telegram.ext import ContextTypes
    
    print("✅ Application imported (NO Updater!)")
    
    # ✅ ТОЛЬКО Application!
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    print("✅ Application создан")
    
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ БОТ РАБОТАЕТ! /rating")
    
    async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🏆 Топ клубов:\n1. Heaven Karma\n2. Bloody Legion")
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rating", rating))
    
    print("✅ Команды добавлены")
    print("✅ Бот готов к работе")
    
    await app.initialize()
    await app.start()
    print("✅ Бот запущен")
    await app.run_polling()

# Flask
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🤖 Heavenly Bot - Работает!"

# Запуск
if __name__ == '__main__':
    # Без лишних импортов
    def run_bot():
        try:
            asyncio.run(bot_main())
        except Exception as e:
            print(f"❌ Ошибка бота: {e}")
            import traceback
            traceback.print_exc()
    
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    
    port = int(os.getenv('PORT', 10000))
    print(f"🌐 Flask на порту {port}")
    flask_app.run(host='0.0.0.0', port=port, debug=False)
