import os
import asyncio
from flask import Flask
import threading

print("=" * 60)
print("🤖 HEAVENLY BOT - PTB v21.0+")
print("=" * 60)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAFA4ZcJMuzOkv3PFWB88Wxe1Pal31WEquA')

async def bot_main():
    print("🤖 ЗАПУСК БОТА v21.0...")
    
    # v21.0+ - ТОЛЬКО Application
    from telegram.ext import Application, CommandHandler
    from telegram import Update
    from telegram.ext import ContextTypes
    from telegram.constants import ParseMode
    
    print("✅ PTB v21.0+ loaded")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    print("✅ Application создан")
    
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """<b>🤖 Heavenly Dynasty Bot</b>

✅ <b>Бот работает на PTB v21.0+</b>

🏆 <b>Команды:</b>
/rating - Рейтинг клубов
/help - Помощь

<code>/heaven_karma</code> - Детали клуба"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """<b>🏆 Топ клубов:</b>

1. <b>Heaven Karma</b> - 55.000 🏆
2. <b>Bloody Legion</b> - 2.300.000 🏆
3. <b>Heaven Moscow</b> - 54.800 🏆"""
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rating", rating))
    app.add_handler(CommandHandler("help", start))
    
    print("✅ Команды добавлены")
    
    await app.initialize()
    await app.start()
    print("✅ Бот запущен и ждет сообщений...")
    await app.run_polling()

# Flask
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>🤖 Heavenly Bot v21.0</title></head>
    <body>
        <h1>🤖 Heavenly Dynasty Bot</h1>
        <p><strong>Версия:</strong> python-telegram-bot v21.0+</p>
        <p><strong>Статус:</strong> ✅ Работает</p>
        <p><strong>Telegram:</strong> @Club_stats_bot</p>
    </body>
    </html>
    """

# Запуск
if __name__ == '__main__':
    def run_bot():
        try:
            asyncio.run(bot_main())
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    print("🚀 Запускаю бота в фоне...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    port = int(os.getenv('PORT', 10000))
    print(f"🌐 Flask на порту {port}")
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
