import os
import asyncio
import logging
from typing import Dict, List, Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from aiohttp import web
import time

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')
PORT = int(os.getenv('PORT', '8080'))

# ========== ДАННЫЕ КЛУБОВ ==========
CLUBS = {
    # Heavenly Dynasty (Основная ветка)
    "Heaven Leo": {"tag": "#2C29U8Q8P", "rep": "@ligavi55"},
    "Heaven Cucumber": {"tag": "#JG9U8U82", "rep": "@Work_Weezz"},
    "Heaven Temple": {"tag": "#80LPG8V8L", "rep": "@DonAyu7"},
    "Heaven Kingdom": {"tag": "#2C2YLRCCU", "rep": "@Sakvoiz"},
    "Heaven Dream": {"tag": "#2LQ2UV0LJ", "rep": "@FellStorm"},
    "Heaven Dynasty": {"tag": "#C8CG8GQJ", "rep": "@ItsDanielTT, @QNoMercyQ"},
    "Heaven Winter": {"tag": "#2LCUY0Q8G", "rep": "@OBEP_gg"},
    "Heaven Envoy": {"tag": "#JYR0YRR2", "rep": "@probs201, @neroxf133"},
    "Heaven Dominion": {"tag": "#80LQRCR0J", "rep": "@KMT_Dream"},
    "Heaven Sakura": {"tag": "#2Q082VC08", "rep": "@IzanaKurokawa0"},
    "Heaven Vinland": {"tag": "#2VJRV89JG", "rep": "@ecclipsa"},
    "Heaven Infinity": {"tag": "#2VCLRRYCV", "rep": "@itsFaon4ik"},
    "Heaven Reverse": {"tag": "#JGYRPPPY", "rep": "@faweer3"},
    "Heaven Tomatoes": {"tag": "#2LC9JVQLJ", "rep": "@HiderBro"},
    "Heaven Thunder": {"tag": "#2CLQ2RPL8", "rep": "@morphinnn1"},
    "Heaven Curse": {"tag": "#2LGRGCL9U", "rep": "@princexgod"},
    "Heaven Karma": {"tag": "#JYGVQR89", "rep": "@Sakvoiz"},
    "Heaven Moscow": {"tag": "#JG2GPJ9Q", "rep": "@DIMALENS21"},
    "Heaven Fortress": {"tag": "#C0JJC0L2", "rep": "@mopsikkmii"},
    "Heaven Hell": {"tag": "#C0QQ8RV0", "rep": "@IzanaKurokawa0"},
    "Heaven KE": {"tag": "#2Q2QVYGU8", "rep": "@Aktoadmin"},
    
    # Bloody Family (Ветка)
    "Bloody Legion": {"tag": "#2YPYJC88J", "rep": "@dijaweed"},
    "Bloody Justice": {"tag": "#2VCU8J9CV", "rep": "@interscopeplay"},
    "Bloody Valley": {"tag": "#2VUURGQLR", "rep": "@Happyhausha"},
    "Bloody Requiem": {"tag": "#2Y89QRGQU", "rep": "@l0ckyYn"},
    "Bloody Cards": {"tag": "#2JQURGVRG", "rep": "@Sakvoiz"},
}

# ========== ПРОСТОЙ КЭШ ==========
cache = {}

# ========== ВЕБ-СЕРВЕР ДЛЯ HEALTH CHECK ==========
async def health_handler(request):
    """Обработчик health check"""
    return web.Response(text="OK")

async def start_web_server():
    """Запустить веб-сервер (упрощенный)"""
    app = web.Application()
    app.router.add_get('/', health_handler)
    app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    logger.info(f"✅ Веб-сервер запущен на порту {PORT}")
    return runner

# ========== КОМАНДЫ ТЕЛЕГРАМ БОТА ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    message = """🎮 *Heaven & Bloody Stats Bot*

📊 *Статистика:*
Клубов: 26 (👑 21 | 🩸 5)

⚡ *Основные команды:*
/rating - Рейтинг всех клубов
/status - Статус бота
/clubs - Список всех клубов

👥 *Информация о клубе:*
Пример: /leo, /sakura, /karma"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status"""
    message = """📊 *Статус бота*

✅ Бот работает нормально
✅ Веб-сервер активен
✅ Готов к запросам

👑 Heavenly Dynasty: 21 клубов
🩸 Bloody Family: 5 клубов
📊 Всего: 26 клубов

🔄 Кэш: {} записей""".format(len(cache))
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def clubs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /clubs - список всех клубов"""
    heaven_clubs = []
    bloody_clubs = []
    
    for name, info in CLUBS.items():
        if name.startswith("Heaven"):
            heaven_clubs.append(f"👑 {name} - {info['rep']}")
        else:
            bloody_clubs.append(f"🩸 {name} - {info['rep']}")
    
    message = "📋 *Список всех клубов*\n\n"
    message += "*👑 Heavenly Dynasty:*\n" + "\n".join(heaven_clubs[:10])
    
    if len(heaven_clubs) > 10:
        message += f"\n... и еще {len(heaven_clubs)-10} клубов"
    
    message += "\n\n*🩸 Bloody Family:*\n" + "\n".join(bloody_clubs)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /rating"""
    message = "🏆 *Рейтинг клубов*\n\n"
    
    # Создаем заглушку данных для примера
    for i, (name, info) in enumerate(list(CLUBS.items())[:10], 1):
        emoji = "👑" if name.startswith("Heaven") else "🩸"
        message += f"{i}. {emoji} *{name}*\n"
        message += f"   👤 {info['rep']}\n"
        message += f"   🏆 50,000 | 👥 25/30\n\n"
    
    message += "👑 21 клуб | 🩸 5 клубов\n"
    message += "📊 Всего: 26 клубов"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def club_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд для конкретных клубов (/leo, /sakura и т.д.)"""
    command = update.message.text[1:].lower()
    
    # Ищем клуб
    found = None
    info = None
    
    for club_name, club_info in CLUBS.items():
        short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
        if command == short:
            found = club_name
            info = club_info
            break
    
    if not found:
        await update.message.reply_text(f"❌ Клуб /{command} не найден")
        return
    
    emoji = "👑" if found.startswith("Heaven") else "🩸"
    club_type = "Heavenly Dynasty" if found.startswith("Heaven") else "Bloody Family"
    
    message = f"{emoji} *{found}*\n\n"
    message += f"*Основное:*\n"
    message += f"Тип: {club_type}\n"
    message += f"Представитель: {info['rep']}\n"
    message += f"Тег: {info['tag']}\n\n"
    
    message += f"*Статистика (пример):*\n"
    message += f"🏆 Общие кубки: 50,000\n"
    message += f"👥 Участников: 25/30\n"
    message += f"🎯 Требуется для входа: 5,000\n\n"
    
    message += f"🔗 /rating - Весь рейтинг"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
async def main():
    """Основная асинхронная функция"""
    logger.info("🚀 Запуск Heaven & Bloody Stats Bot...")
    
    # Запускаем веб-сервер
    try:
        runner = await start_web_server()
    except Exception as e:
        logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
        return
    
    # Создаем приложение бота
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", start_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("rating", rating_command))
        application.add_handler(CommandHandler("clubs", clubs_command))
        
        # Добавляем обработчики для каждого клуба
        for club_name in CLUBS.keys():
            short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
            application.add_handler(CommandHandler(short, club_command))
        
        logger.info("✅ Бот инициализирован")
        logger.info(f"📊 Клубов в базе: {len(CLUBS)}")
        
        # Запускаем polling
        logger.info("🤖 Бот запущен и ожидает команд...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
    finally:
        # Очистка
        logger.info("🛑 Остановка веб-сервера...")
        await runner.cleanup()

# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
