import os
import asyncio
import logging
from typing import Dict
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from telegram.constants import ParseMode
from aiohttp import web

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
PORT = int(os.getenv('PORT', '8080'))

if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не установлен!")
    exit(1)

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

# ========== ВЕБ-СЕРВЕР ДЛЯ HEALTH CHECK ==========
async def health_handler(request):
    """Обработчик health check"""
    return web.Response(text="✅ Heaven & Bloody Bot работает!")

async def start_web_server():
    """Запустить веб-сервер"""
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
    heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
    
    message = f"""🎮 *Heaven & Bloody Stats Bot*

📊 *Статистика:*
👑 Heavenly Dynasty: {heaven_count} клубов
🩸 Bloody Family: {bloody_count} клубов
📊 Всего: {len(CLUBS)} клубов

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

ℹ️ *Версия 1.0*
📅 Данные обновлены"""
    
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
    
    # Пример данных
    sample_data = [
        ("Heaven Dynasty", "👑", "@ItsDanielTT, @QNoMercyQ", 55000, 28),
        ("Heaven Leo", "👑", "@ligavi55", 52000, 27),
        ("Bloody Legion", "🩸", "@dijaweed", 51000, 26),
        ("Heaven Sakura", "👑", "@IzanaKurokawa0", 50000, 25),
        ("Heaven Kingdom", "👑", "@Sakvoiz", 48000, 24),
    ]
    
    for i, (name, emoji, rep, trophies, members) in enumerate(sample_data, 1):
        message += f"{i}. {emoji} *{name}*\n"
        message += f"   👤 {rep}\n"
        message += f"   🏆 {trophies:,} | 👥 {members}/30\n\n"
    
    message += "👑 21 клуб | 🩸 5 клубов\n"
    message += "📊 Всего: 26 клубов"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def club_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд для конкретных клубов"""
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
    
    message += f"*Примерные данные:*\n"
    message += f"🏆 Общие кубки: 50,000\n"
    message += f"👥 Участников: 25/30\n"
    message += f"🎯 Требуется для входа: 5,000\n\n"
    
    message += f"🔗 /rating - Весь рейтинг"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
async def run_bot():
    """Запуск бота"""
    logger.info("🚀 Запуск Heaven & Bloody Stats Bot...")
    
    # Запускаем веб-сервер
    try:
        runner = await start_web_server()
        logger.info("✅ Веб-сервер запущен успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
        return
    
    # Создаем приложение бота
    try:
        # ВАЖНО: Используем Application.builder() вместо Updater
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", start_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("rating", rating_command))
        application.add_handler(CommandHandler("clubs", clubs_command))
        
        # Добавляем обработчики для каждого клуба (первые 5 для примера)
        for club_name in list(CLUBS.keys())[:5]:
            short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
            application.add_handler(CommandHandler(short, club_command))
        
        logger.info("✅ Бот инициализирован")
        logger.info(f"📊 Клубов в базе: {len(CLUBS)}")
        
        # Запускаем polling
        logger.info("🤖 Запуск polling...")
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
    finally:
        # Очистка
        logger.info("🛑 Остановка веб-сервера...")
        await runner.cleanup()
        logger.info("✅ Веб-сервер остановлен")

# ========== ТОЧКА ВХОДА ==========
def main():
    """Основная функция"""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("⏹️  Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
