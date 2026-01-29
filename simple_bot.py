import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler

TOKEN = '8529987392:AALJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU'

async def main():
    print("🤖 Тестирую самого простого бота...")
    
    # Тест 1: Проверка токена
    try:
        bot = Bot(token=TOKEN)
        me = await bot.get_me()
        print(f"✅ Токен рабочий! Бот: @{me.username}")
    except Exception as e:
        print(f"❌ Ошибка токена: {e}")
        return
    
    # Тест 2: Простейший бот
    app = Application.builder().token(TOKEN).build()
    
    async def start(update, context):
        await update.message.reply_text("✅ Я живой!")
        print(f"📨 Получил /start от {update.effective_user.username}")
    
    app.add_handler(CommandHandler("start", start))
    
    print("✅ Бот настроен, запускаю...")
    print("📱 Напиши /start в Telegram")
    
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
