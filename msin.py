import os
import asyncio
import signal
import tracemalloc
from typing import Dict, List, Tuple, Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import logging
from aiohttp import web

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Включаем tracemalloc для отслеживания памяти
tracemalloc.start()

# Токены и настройки из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')
BRAWL_API_PROXY = os.getenv('BRAWL_API_PROXY', 'https://heavenly-brawl-proxy.workers.dev')
PORT = int(os.getenv('PORT', '8080'))  # Порт для health check сервера

# Проверка обязательных переменных окружения
if not BRAWL_API_KEY:
    logger.warning("⚠️  BRAWL_API_KEY не установлен в переменных окружения.")
    BRAWL_API_KEY = ''

if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU':
    logger.warning("⚠️  TELEGRAM_TOKEN не установлен или используется тестовый токен")

# Данные клубов
CLUBS = {
    "Heaven Karma": "#JYGVQR89",
    "Heaven Moscow": "#JG2GPJ9Q",
    "Heaven Fortress": "#C0JJC0L2",
    "Heaven Hell": "#C0QQ8RV0",
    "Heaven KE": "#2Q2QVYGU8",
    "Heaven Leo": "#2C29U8Q8P",
    "Heaven Cucumber": "#JG9U8U82",
    "Heaven Temple": "#80LPG8V8L",
    "Heaven Kingdom": "#2C2YLRCCU",
    "Heaven Dream": "#2LQ2UV0LJ",
    "Heaven Winter": "#2LCUY0Q8G",
    "Heaven Envoy": "#JYR0YRR2",
    "Heaven Dominion": "#80LQRCR0J",
    "Heaven Sakura": "#2Q082VC08",
    "Heaven Vinland": "#2VJRV89JG",
    "Heaven Infinity": "#2VCLRRYCV",
    "Heaven Reverse": "#JGYRPPPY",
    "Heaven Tomatoes": "#2LC9JVQLJ",
    "Heaven Thunder": "#2CLQ2RPL8",
    "Heaven Curse": "#2LGRGCL9U",
    "Bloody Legion": "#2YPYJC88J",
    "Bloody Justice": "#2VCU8J9CV",
    "Bloody Valley": "#2VUURGQLR",
    "Bloody Requiem": "#2Y89QRGQU",
    "Bloody Cards": "#2JQURGVRG"
}

# Глобальные переменные
session: Optional[aiohttp.ClientSession] = None
application: Optional[Application] = None
web_app: Optional[web.Application] = None
runner: Optional[web.AppRunner] = None

# Health Check сервер
async def health_check(request):
    """Endpoint для health check от Render"""
    return web.json_response({
        "status": "ok",
        "service": "Heaven & Bloody Stats Bot",
        "telegram_bot": "running" if application and application.running else "not_running",
        "timestamp": asyncio.get_event_loop().time()
    })

async def start_web_server():
    """Запуск веб-сервера для health check"""
    global web_app, runner
    
    web_app = web.Application()
    web_app.router.add_get('/', health_check)
    web_app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    logger.info(f"🌐 Health check сервер запущен на порту {PORT}")
    logger.info(f"📡 Endpoints: http://0.0.0.0:{PORT}/ и http://0.0.0.0:{PORT}/health")

async def stop_web_server():
    """Остановка веб-сервера"""
    global runner, web_app
    
    if runner:
        await runner.cleanup()
        runner = None
        web_app = None
        logger.info("🌐 Health check сервер остановлен")

async def get_club_data(club_tag: str) -> Optional[Dict]:
    """Получение данных клуба через API"""
    global session
    
    if not BRAWL_API_KEY:
        logger.error("❌ BRAWL_API_KEY не настроен корректно")
        return None
    
    if session is None or session.closed:
        timeout = aiohttp.ClientTimeout(total=30)
        session = aiohttp.ClientSession(timeout=timeout)
    
    try:
        # Убираем # из тега для URL
        clean_tag = club_tag.replace('#', '')
        url = f"{BRAWL_API_PROXY}/clubs/%23{clean_tag}/"
        headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
        
        logger.debug(f"Запрос данных для клуба: {club_tag}")
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                logger.debug(f"Успешно получены данные для {club_tag}")
                return data
            elif response.status == 403:
                logger.error(f"❌ Доступ запрещен для {club_tag}. Проверьте BRAWL_API_KEY.")
                return None
            elif response.status == 404:
                logger.warning(f"⚠️  Клуб {club_tag} не найден")
                return None
            else:
                logger.error(f"❌ Ошибка API для {club_tag}: {response.status}")
                return None
                
    except aiohttp.ClientError as e:
        logger.error(f"❌ Ошибка сети при запросе {club_tag}: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка при запросе {club_tag}: {e}")
        return None

async def get_all_clubs_data() -> List[Tuple[str, str, Dict]]:
    """Получение данных всех клубов"""
    tasks = []
    for name, tag in CLUBS.items():
        tasks.append(get_club_data(tag))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    clubs_data = []
    successful = 0
    failed = 0
    
    for (name, tag), data in zip(CLUBS.items(), results):
        if data and not isinstance(data, Exception):
            clubs_data.append((name, tag, data))
            successful += 1
        else:
            logger.warning(f"Не удалось получить данные для {name}: {data}")
            failed += 1
    
    logger.info(f"✅ Получены данные: {successful} успешно, ❌ {failed} с ошибками")
    
    # Сортировка по количеству трофеев (от большего к меньшему)
    clubs_data.sort(key=lambda x: x[2].get('trophies', 0), reverse=True)
    return clubs_data

def generate_pagination_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Генерация клавиатуры для пагинации"""
    buttons = []
    
    if page > 0:
        buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page-1}"))
    
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"page_{page+1}"))
    
    return InlineKeyboardMarkup([buttons]) if buttons else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_text = """🎮 *Добро пожаловать в Heaven & Bloody Stats Bot!*
    
📊 Я предоставляю статистику клубов Heaven и Bloody.
    
*📋 Основные команды:*
/rating - Рейтинг всех клубов
/help - Помощь и информация
/test_api - Проверка API подключения
/status - Статус бота

*🔗 Полезные ссылки:*
▶️ ПРАВИЛА: https://t.me/c/2565122949/1/674535
▶️ ЧЁРНЫЙ СПИСОК: https://t.me/+8ISCeRkWfz40YzZi
▶️ АЛЬЯНСЫ: https://t.me/+BOHHdvr04D5kZmRi
▶️ ЛЕГЕНДЫ: https://t.me/+t-dkJTsbwr1hN2Vi

_Для подробной информации о клубе используйте команды вида /Sakura, /Leo и т.д._"""
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /info"""
    info_text = """*📖 Информация о боте*
    
Этот бот предоставляет актуальную статистику клубов Heaven и Bloody из Brawl Stars.
    
*📊 Доступные функции:*
• Рейтинг всех клубов
• Подробная информация о каждом клубе
• Автоматическое обновление данных
• Проверка статуса API

*⚡ Команды:*
/start - Начальное приветствие
/rating - Полный рейтинг клубов
/info - Эта информация
/help - Помощь
/test_api - Проверка подключения к API
/status - Статус работы бота
/[ИмяКлуба] - Подробности о клубе
    
_Пример: /Sakura, /Leo, /Karma_"""
    
    await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает статус бота"""
    try:
        import psutil
        
        # Получаем информацию о системе
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Информация о боте
        status_text = "📊 *Статус бота*\n\n"
        
        # Статус Telegram бота
        if application and application.running:
            status_text += "🤖 *Telegram Bot:* 🟢 Работает\n"
        else:
            status_text += "🤖 *Telegram Bot:* 🔴 Остановлен\n"
        
        # Статус веб-сервера
        if web_app:
            status_text += "🌐 *Web Server:* 🟢 Работает\n"
            status_text += f"   • Порт: {PORT}\n"
        else:
            status_text += "🌐 *Web Server:* 🔴 Остановлен\n"
        
        # Статус API
        if BRAWL_API_KEY:
            status_text += f"🔑 *API Key:* {'🟢 JWT токен' if BRAWL_API_KEY.startswith('eyJ') else '🟡 Пользовательский ключ'}\n"
        else:
            status_text += "🔑 *API Key:* 🔴 Не установлен\n"
        
        status_text += f"📁 *Клубов в базе:* {len(CLUBS)}\n\n"
        
        # Системная информация
        status_text += "*💻 Системная информация:*\n"
        status_text += f"• CPU: {cpu_percent}%\n"
        status_text += f"• Память: {memory.percent}%\n"
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Ошибка в status: {e}")
        await update.message.reply_text("❌ Ошибка при получении статуса")

async def test_api(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверка подключения к API"""
    try:
        await update.message.reply_text("🔍 Проверяю подключение к API...")
        
        # Проверяем первый клуб в списке
        test_club_tag = list(CLUBS.values())[0]
        data = await get_club_data(test_club_tag)
        
        if data:
            club_name = list(CLUBS.keys())[0]
            trophies = data.get('trophies', 0)
            message = f"✅ *API подключение работает!*\n\n"
            message += f"*Тестовый клуб:* {club_name}\n"
            message += f"*Трофеи:* {trophies:,}\n"
            message += f"*Статус:* 🟢 Онлайн"
            
            # Проверка ключа API
            if BRAWL_API_KEY.startswith('eyJ'):
                message += f"\n*Тип ключа:* 🔑 JWT токен"
            else:
                message += f"\n*Тип ключа:* 🔑 Пользовательский"
                
        else:
            message = "❌ *Не удалось подключиться к API*\n\n"
            message += "*Возможные причины:*\n"
            message += "1. Неверный API ключ\n"
            message += "2. Проблемы с прокси-сервером\n"
            message += "3. Ограничение скорости запросов\n\n"
            message += "*Решение:*\n"
            message += "• Проверьте BRAWL_API_KEY в настройках Render\n"
            message += "• Убедитесь, что ключ активен и не истек\n"
            message += "• Проверьте прокси-сервер"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Ошибка в test_api: {e}")
        await update.message.reply_text(f"❌ Ошибка при проверке API: {str(e)}")

async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> None:
    """Отображение рейтинга клубов"""
    try:
        await update.message.reply_text("⏳ Получаю данные клубов...")
        
        clubs_data = await get_all_clubs_data()
        
        if not clubs_data:
            await update.message.reply_text("❌ Не удалось получить данные клубов. Попробуйте позже.")
            return
        
        # Пагинация: 10 клубов на страницу
        clubs_per_page = 10
        total_pages = (len(clubs_data) + clubs_per_page - 1) // clubs_per_page
        
        if page >= total_pages:
            page = 0
        
        start_idx = page * clubs_per_page
        end_idx = min(start_idx + clubs_per_page, len(clubs_data))
        
        # Формирование сообщения
        message_text = f"🏆 *Рейтинг клубов* (Страница {page + 1}/{total_pages})\n\n"
        
        for i, (name, tag, data) in enumerate(clubs_data[start_idx:end_idx], start=1):
            position = start_idx + i
            trophies = data.get('trophies', 0)
            members = data.get('members', [])
            member_count = len(members) if members else 0
            
            # Извлекаем короткое имя для команды
            short_name = name.split()[-1] if ' ' in name else name
            command_name = short_name.lower()
            
            message_text += f"{position}) *{name}*\n"
            message_text += f"   🏆 {trophies:,}/{member_count}\n"
            message_text += f"   ℹ️ Подробнее: /{command_name}\n\n"
        
        # Статус API
        if BRAWL_API_KEY.startswith('eyJ'):
            api_status = "🟢 (JWT токен)"
        else:
            api_status = "🟡 (пользовательский)"
        
        message_text += f"*Статус API:* {api_status}\n"
        message_text += f"*Обновлено:* {len(clubs_data)}/{len(CLUBS)} клубов"
        
        # Отправка сообщения
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=generate_pagination_keyboard(page, total_pages)
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(
                text=message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=generate_pagination_keyboard(page, total_pages)
            )
    except Exception as e:
        logger.error(f"Ошибка в rating: {e}")
        await update.message.reply_text("❌ Ошибка при получении рейтинга")

async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки пагинации"""
    query = update.callback_query
    await query.answer()
    
    try:
        page = int(query.data.split('_')[1])
        await rating(update, context, page)
    except Exception as e:
        logger.error(f"Ошибка в page_callback: {e}")
        await query.edit_message_text("❌ Ошибка при переключении страницы")

async def club_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команд вида /Sakura, /Leo и т.д."""
    try:
        club_command = update.message.text[1:].lower()  # Убираем слэш
        
        # Поиск клуба по короткому имени
        found_club = None
        club_tag = None
        
        for name, tag in CLUBS.items():
            short_name = name.split()[-1].lower() if ' ' in name else name.lower()
            if club_command == short_name.lower():
                found_club = name
                club_tag = tag
                break
        
        if not found_club:
            await update.message.reply_text(f"❌ Клуб с командой /{club_command} не найден")
            return
        
        await update.message.reply_text(f"⏳ Получаю данные для {found_club}...")
        
        # Получение данных клуба
        data = await get_club_data(club_tag)
        
        if not data:
            await update.message.reply_text(f"❌ Не удалось получить данные для {found_club}")
            return
        
        # Формирование детальной информации
        trophies = data.get('trophies', 0)
        required_trophies = data.get('requiredTrophies', 0)
        members = data.get('members', [])
        member_count = len(members) if members else 0
        description = data.get('description', 'Нет описания')
        tag = data.get('tag', club_tag)
        
        # Топ-5 игроков по трофеям
        top_players = ""
        if members:
            sorted_members = sorted(members, key=lambda x: x.get('trophies', 0), reverse=True)[:5]
            for j, player in enumerate(sorted_members, 1):
                top_players += f"{j}. {player.get('name', 'Unknown')} - 🏆 {player.get('trophies', 0):,}\n"
        
        message_text = f"*🏰 {found_club}*\n\n"
        message_text += f"*📊 Общая статистика:*\n"
        message_text += f"🏆 Трофеи клуба: {trophies:,}\n"
        message_text += f"👥 Участников: {member_count}\n"
        message_text += f"🎯 Необходимо трофеев: {required_trophies:,}\n"
        message_text += f"🔖 Тег: {tag}\n\n"
        
        message_text += f"*📝 Описание:*\n{description}\n\n"
        
        if top_players:
            message_text += f"*👑 Топ-5 игроков:*\n{top_players}"
        
        await update.message.reply_text(message_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Ошибка в club_info: {e}")
        await update.message.reply_text("❌ Ошибка при получении информации о клубе")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    error_msg = str(context.error) if context.error else "Неизвестная ошибка"
    logger.error(f"Ошибка: {error_msg}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    except:
        pass

async def cleanup():
    """Очистка ресурсов"""
    global session, application, web_app, runner
    
    logger.info("Начало очистки ресурсов...")
    
    # Остановка веб-сервера
    if runner:
        await stop_web_server()
    
    # Закрытие сессии aiohttp
    if session and not session.closed:
        try:
            await session.close()
            logger.info("✅ Сессия aiohttp закрыта")
        except Exception as e:
            logger.error(f"Ошибка при закрытии сессии: {e}")
        session = None
    
    # Остановка Telegram бота
    if application:
        try:
            if application.running:
                await application.stop()
                await application.shutdown()
                logger.info("✅ Приложение Telegram остановлено")
        except Exception as e:
            logger.error(f"Ошибка при остановке приложения: {e}")
        application = None

async def shutdown(signum=None, frame=None):
    """Корректное завершение работы"""
    logger.info(f"Получен сигнал завершения работы")
    await cleanup()
    
    # Отображение информации о памяти
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')[:5]
    
    logger.info("\nТоп-5 использования памяти:")
    for stat in top_stats:
        logger.info(f"  {stat}")
    
    tracemalloc.stop()
    logger.info("✅ Бот завершил работу")
    os._exit(0)

async def run_bot():
    """Асинхронный запуск бота и веб-сервера"""
    global application
    
    try:
        # Запуск веб-сервера для health check
        await start_web_server()
        
        # Создание приложения Telegram
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("info", info))
        application.add_handler(CommandHandler("rating", rating))
        application.add_handler(CommandHandler("help", info))
        application.add_handler(CommandHandler("test_api", test_api))
        application.add_handler(CommandHandler("status", status))
        
        # Регистрация динамических команд для каждого клуба
        for name in CLUBS.keys():
            short_name = name.split()[-1].lower() if ' ' in name else name.lower()
            application.add_handler(CommandHandler(short_name, club_info))
        
        # Регистрация обработчика пагинации
        application.add_handler(CallbackQueryHandler(page_callback, pattern=r"^page_\d+$"))
        
        # Регистрация обработчика ошибок
        application.add_error_handler(error_handler)
        
        logger.info("✅ Бот успешно инициализирован")
        logger.info("📊 Мониторинг памяти включен через tracemalloc")
        logger.info("🤖 Бот запущен и ожидает сообщений...")
        
        # Запуск бота в режиме polling
        await application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Получен сигнал прерывания от клавиатуры")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
        logger.error(f"Тип ошибки: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    finally:
        await cleanup()

def main():
    """Основная функция запуска бота"""
    # Логирование информации о настройках
    logger.info("=" * 50)
    logger.info("🚀 Запуск Heaven & Bloody Stats Bot")
    logger.info("=" * 50)
    
    # Проверка переменных окружения
    env_vars = {
        "TELEGRAM_TOKEN": "установлен" if TELEGRAM_TOKEN and TELEGRAM_TOKEN != '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU' else "тестовый/не установлен",
        "BRAWL_API_KEY": "установлен" if BRAWL_API_KEY else "не установлен",
        "BRAWL_API_PROXY": BRAWL_API_PROXY,
        "PORT": PORT
    }
    
    for var, status in env_vars.items():
        logger.info(f"{var}: {status}")
    
    logger.info(f"Количество клубов: {len(CLUBS)}")
    logger.info("=" * 50)
    
    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(shutdown()))
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown()))
    
    # Запуск асинхронного бота
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
