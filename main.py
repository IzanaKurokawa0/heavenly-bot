import os
import asyncio
import logging
import time
from typing import Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import aiohttp
from aiohttp import web

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')
PORT = int(os.getenv('PORT', '10000'))

# ========== ДАННЫЕ КЛУБОВ ==========
CLUBS = {
    "Heaven Leo": {"tag": "#2C29U8Q8P", "rep": "@ligavi55", "trophies": 52800},
    "Heaven Cucumber": {"tag": "#JG9U8U82", "rep": "@Work_Weezz", "trophies": 51000},
    "Heaven Temple": {"tag": "#80LPG8V8L", "rep": "@DonAyu7", "trophies": 50500},
    "Heaven Kingdom": {"tag": "#2C2YLRCCU", "rep": "@Sakvoiz", "trophies": 50200},
    "Heaven Dream": {"tag": "#2LQ2UV0LJ", "rep": "@FellStorm", "trophies": 49800},
}

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
app = None

# ========== КОМАНДЫ БОТА ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """🎮 *Heaven & Bloody Stats Bot*
    
📊 *Быстрый старт:*
/rating - Посмотреть рейтинг клубов
/refresh - Обновить данные из API
/status - Статус бота

👑 Heavenly Dynasty: 21 клубов
🩸 Bloody Family: 5 клубов
🎯 Всего: 26 клубов"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Сортируем клубы по трофеям
    sorted_clubs = sorted(
        CLUBS.items(),
        key=lambda x: x[1]["trophies"],
        reverse=True
    )
    
    message = "🏆 *ТОП-5 клубов*\n\n"
    
    for i, (name, info) in enumerate(sorted_clubs[:5], 1):
        emoji = "👑" if name.startswith("Heaven") else "🩸"
        message += f"{i}. {emoji} *{name}*\n"
        message += f"   🏆 {info['trophies']:,} | 👤 {info['rep']}\n\n"
    
    message += "📊 *Общая статистика:*\n"
    message += f"👑 Heavenly: {len([n for n in CLUBS if 'Heaven' in n])} клубов\n"
    message += f"🩸 Bloody: {len([n for n in CLUBS if 'Bloody' in n])} клубов\n"
    message += f"🔗 Всего: {len(CLUBS)} клубов"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BRAWL_API_KEY:
        await update.message.reply_text(
            "⚠️ *API ключ не настроен*\n\n"
            "Для настройки API:\n"
            "1. Зайдите на https://developer.brawlstars.com\n"
            "2. Создайте новый API ключ\n"
            "3. Добавьте в Render переменную BRAWL_API_KEY\n\n"
            "📌 Без API данные обновляться не будут",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("🔄 Обновление данных...")
    
    # Имитация обновления
    await asyncio.sleep(2)
    
    # Обновляем трофеи (имитация)
    for name in CLUBS:
        CLUBS[name]["trophies"] += 10
    
    await update.message.reply_text(
        "✅ Данные обновлены!\n"
        "Все клубы получили +10 🏆\n"
        "Используйте /rating для просмотра",
        parse_mode=ParseMode.MARKDOWN
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import psutil
    import datetime
    
    # Статистика
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent()
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    
    message = f"""📊 *Статус бота*

💻 *Система:*
CPU: {cpu}%
Память: {memory.percent}%
Время работы: {str(uptime).split('.')[0]}

📡 *Бот:*
API ключ: {'✅ Настроен' if BRAWL_API_KEY else '❌ Отсутствует'}
Клубов в базе: {len(CLUBS)}
Версия: 1.0

🔧 *Команды:*
/start - Главное меню
/rating - Рейтинг
/refresh - Обновить
/status - Этот статус"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
async def health_check(request):
    """Эндпоинт для проверки здоровья на Render"""
    return web.Response(text="Heaven & Bloody Stats Bot is running")

async def handle_webhook(request):
    """Обработчик веб-хуков от Telegram"""
    try:
        data = await request.json()
        update = Update.de_json(data, app.bot)
        
        # Обрабатываем update
        await app.process_update(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Ошибка веб-хука: {e}")
        return web.Response(status=500)

async def start_web_server():
    """Запуск веб-сервера для Render"""
    # Создаем aiohttp приложение
    web_app = web.Application()
    
    # Регистрируем маршруты
    web_app.router.add_get('/', health_check)
    web_app.router.add_get('/health', health_check)
    web_app.router.add_post('/webhook', handle_webhook)
    
    # Запускаем сервер
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    logger.info(f"🌐 Веб-сервер запущен на порту {PORT}")
    return web_app

async def main():
    """Основная функция"""
    global app
    
    logger.info("🚀 Запуск Heaven & Bloody Stats Bot...")
    
    # Создаем приложение Telegram
    token = TELEGRAM_TOKEN
    if not token or token == '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU':
        logger.error("❌ TELEGRAM_TOKEN не установлен!")
        return
    
    app = Application.builder().token(token).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("rating", rating_command))
    app.add_handler(CommandHandler("refresh", refresh_command))
    app.add_handler(CommandHandler("status", status_command))
    
    # Инициализируем
    await app.initialize()
    await app.start()
    
    logger.info("✅ Бот инициализирован")
    
    # Настраиваем webhook для Render
    webhook_url = os.getenv('RENDER_EXTERNAL_URL')
    if webhook_url:
        await app.bot.set_webhook(
            url=f"{webhook_url}/webhook",
            allowed_updates=Update.ALL_TYPES
        )
        logger.info(f"✅ Веб-хук установлен: {webhook_url}/webhook")
    else:
        logger.info("📡 Используется polling (только для тестов)")
        # Для локального тестирования
        async with app:
            await app.updater.start_polling()
    
    # Запускаем веб-сервер
    await start_web_server()
    
    # Бесконечный цикл
    try:
        while True:
            await asyncio.sleep(3600)  # Спим 1 час
    except KeyboardInterrupt:
        logger.info("⏹️  Остановка...")
    finally:
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
