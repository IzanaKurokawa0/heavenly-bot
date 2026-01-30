import os
import asyncio
import signal
import logging
from typing import Dict, List, Tuple, Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from aiohttp import web
import time
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токены и настройки
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')
PORT = int(os.getenv('PORT', '8080'))

if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU':
    logger.warning("⚠️  TELEGRAM_TOKEN не установлен или используется тестовый токен")

# Данные клубов с представителями
CLUBS = {
    # Heavenly Dynasty
    "Heaven Leo": {
        "tag": "#2C29U8Q8P",
        "representative": "@ligavi55"
    },
    "Heaven Cucumber": {
        "tag": "#JG9U8U82", 
        "representative": "@Work_Weezz"
    },
    "Heaven Temple": {
        "tag": "#80LPG8V8L",
        "representative": "@DonAyu7"
    },
    "Heaven Kingdom": {
        "tag": "#2C2YLRCCU",
        "representative": "@Sakvoiz"
    },
    "Heaven Dream": {
        "tag": "#2LQ2UV0LJ",
        "representative": "@FellStorm"
    },
    "Heaven Dynasty": {
        "tag": "#C8CG8GQJ",
        "representative": "@ItsDanielTT, @QNoMercyQ"
    },
    "Heaven Winter": {
        "tag": "#2LCUY0Q8G",
        "representative": "@OBEP_gg"
    },
    "Heaven Envoy": {
        "tag": "#JYR0YRR2",
        "representative": "@probs201, @neroxf133"
    },
    "Heaven Dominion": {
        "tag": "#80LQRCR0J",
        "representative": "@KMT_Dream"
    },
    "Heaven Sakura": {
        "tag": "#2Q082VC08",
        "representative": "@IzanaKurokawa0"
    },
    "Heaven Vinland": {
        "tag": "#2VJRV89JG",
        "representative": "@ecclipsa"
    },
    "Heaven Infinity": {
        "tag": "#2VCLRRYCV",
        "representative": "@itsFaon4ik"
    },
    "Heaven Reverse": {
        "tag": "#JGYRPPPY",
        "representative": "@faweer3"
    },
    "Heaven Tomatoes": {
        "tag": "#2LC9JVQLJ",
        "representative": "@HiderBro"
    },
    "Heaven Thunder": {
        "tag": "#2CLQ2RPL8",
        "representative": "@morphinnn1"
    },
    "Heaven Curse": {
        "tag": "#2LGRGCL9U",
        "representative": "@princexgod"
    },
    "Heaven Karma": {
        "tag": "#JYGVQR89",
        "representative": "@Sakvoiz"
    },
    "Heaven Moscow": {
        "tag": "#JG2GPJ9Q",
        "representative": "@DIMALENS21"
    },
    "Heaven Fortress": {
        "tag": "#C0JJC0L2",
        "representative": "@mopsikkmii"
    },
    "Heaven Hell": {
        "tag": "#C0QQ8RV0",
        "representative": "@IzanaKurokawa0"
    },
    "Heaven KE": {
        "tag": "#2Q2QVYGU8",
        "representative": "@Aktoadmin"
    },
    
    # Bloody Family
    "Bloody Legion": {
        "tag": "#2YPYJC88J",
        "representative": "@dijaweed"
    },
    "Bloody Justice": {
        "tag": "#2VCU8J9CV",
        "representative": "@interscopeplay"
    },
    "Bloody Valley": {
        "tag": "#2VUURGQLR",
        "representative": "@Happyhausha"
    },
    "Bloody Requiem": {
        "tag": "#2Y89QRGQU",
        "representative": "@l0ckyYn"
    },
    "Bloody Cards": {
        "tag": "#2JQURGVRG",
        "representative": "@Sakvoiz"
    }
}

# Глобальные переменные
session = None
application = None
web_app = None
runner = None

# Кэш данных
club_cache = {}
last_api_success = None
last_api_error = None

async def health_check(request):
    """Health check endpoint для Render"""
    return web.json_response({
        "status": "ok",
        "service": "Heaven & Bloody Stats Bot",
        "timestamp": time.time(),
        "cache_size": len(club_cache)
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

async def get_club_data_with_cache(club_tag: str, force_refresh: bool = False) -> Optional[Dict]:
    """Получение данных клуба с кэшированием"""
    global session, club_cache, last_api_success, last_api_error
    
    # Проверяем кэш (5 минут)
    CACHE_TIMEOUT = 300
    
    if not force_refresh and club_tag in club_cache:
        cached = club_cache[club_tag]
        if time.time() - cached["timestamp"] < CACHE_TIMEOUT:
            return cached["data"]
    
    # Если нет API ключа, используем кэш
    if not BRAWL_API_KEY:
        if club_tag in club_cache:
            return club_cache[club_tag]["data"]
        return None
    
    # Создаем сессию если нужно
    if session is None or session.closed:
        timeout = aiohttp.ClientTimeout(total=30)
        session = aiohttp.ClientSession(timeout=timeout)
    
    try:
        # Делаем запрос к API
        clean_tag = club_tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
        headers = {
            "Authorization": f"Bearer {BRAWL_API_KEY}",
            "Accept": "application/json"
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                
                # Сохраняем в кэш
                club_cache[club_tag] = {
                    "data": data,
                    "timestamp": time.time()
                }
                last_api_success = time.time()
                last_api_error = None
                
                return data
            else:
                error_text = await response.text()
                last_api_error = f"Status {response.status}"
                
                # Используем старый кэш если есть
                if club_tag in club_cache:
                    return club_cache[club_tag]["data"]
                return None
                
    except Exception as e:
        last_api_error = str(e)
        
        if club_tag in club_cache:
            return club_cache[club_tag]["data"]
        return None

async def get_all_clubs_data() -> List[Tuple[str, Dict, Dict]]:
    """Получение данных всех клубов"""
    clubs_data = []
    
    for club_name, club_info in CLUBS.items():
        tag = club_info["tag"]
        data = await get_club_data_with_cache(tag)
        
        if data:
            clubs_data.append((club_name, club_info, data))
    
    # Сортировка по трофеям
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
    welcome_text = """🎮 *Heaven & Bloody Stats Bot*

📊 *Команды:*
/rating - Рейтинг клубов
/refresh - Обновить данные
/status - Статус системы
/help - Помощь

👥 *Информация о клубе:*
/Sakura, /Leo, /Karma, /Moscow и т.д.

⚡ *Особенности:*
• Данные кэшируются на 5 минут
• При смене IP на Render используйте /refresh
• Автоматическая загрузка при запуске"""
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def refresh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Принудительное обновление данных"""
    if not BRAWL_API_KEY:
        await update.message.reply_text(
            "❌ API ключ не установлен\n"
            "Добавьте BRAWL_API_KEY в настройках Render",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("🔄 Обновляю данные...")
    
    updated = 0
    for club_info in list(CLUBS.values())[:3]:  # Обновляем 3 клуба
        await get_club_data_with_cache(club_info["tag"], force_refresh=True)
        updated += 1
        await asyncio.sleep(1)
    
    await update.message.reply_text(
        f"✅ Обновлено: {updated} клубов\n"
        f"Используйте /rating",
        parse_mode=ParseMode.MARKDOWN
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать статус системы"""
    status_text = f"""📊 *Статус системы*

🔑 API ключ: {'🟢 есть' if BRAWL_API_KEY else '🔴 нет'}
💾 В кэше: {len(club_cache)}/{len(CLUBS)} клубов

👥 *Клубов всего:* {len(CLUBS)}
👑 Heavenly: {len([name for name in CLUBS.keys() if name.startswith('Heaven')])}
🩸 Bloody: {len([name for name in CLUBS.keys() if name.startswith('Bloody')])}

⚡ *Команды:*
/rating - Рейтинг
/refresh - Обновить
/[club] - Инфо о клубе"""
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> None:
    """Отображение рейтинга клубов в КОМПАКТНОМ формате"""
    # Проверяем данные
    if not club_cache and not BRAWL_API_KEY:
        await update.message.reply_text(
            "⚠️  Нет данных\n"
            "Установите API ключ и используйте /refresh",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("⏳ Загружаю рейтинг...")
    
    clubs_data = await get_all_clubs_data()
    
    if not clubs_data:
        await update.message.reply_text(
            "❌ Нет данных\n"
            "Используйте /refresh",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Пагинация
    clubs_per_page = 10
    total_pages = (len(clubs_data) + clubs_per_page - 1) // clubs_per_page
    
    if page >= total_pages:
        page = 0
    
    start_idx = page * clubs_per_page
    end_idx = min(start_idx + clubs_per_page, len(clubs_data))
    
    # КОМПАКТНЫЙ заголовок
    message_text = f"🏆 *Рейтинг* (стр. {page + 1}/{total_pages})\n\n"
    
    # КОМПАКТНЫЙ формат клубов
    for i, (club_name, club_info, data) in enumerate(clubs_data[start_idx:end_idx], start=1):
        position = start_idx + i
        
        trophies = data.get('trophies', 0)
        members = data.get('members', [])
        member_count = len(members) if members else 0
        representative = club_info.get('representative', 'Не указан')
        
        # Эмодзи для типа клуба
        club_emoji = "👑" if club_name.startswith("Heaven") else "🩸"
        
        # Короткое имя для команды
        short_name = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
        
        # КОМПАКТНЫЙ формат (ровно как ты просил):
        # название | представитель
        # общие кубки | участники
        # команда для инфы
        message_text += f"{position}. {club_emoji} *{club_name}*\n"
        message_text += f"   👤 {representative}\n"
        message_text += f"   🏆 {trophies:,} | 👥 {member_count}/30\n"
        message_text += f"   📖 /{short_name}\n\n"
    
    # Компактная статистика внизу
    heavenly_count = len([name for name, _, _ in clubs_data if name.startswith("Heaven")])
    bloody_count = len([name for name, _, _ in clubs_data if name.startswith("Bloody")])
    
    message_text += f"👑 {heavenly_count} | 🩸 {bloody_count}\n"
    message_text += f"📊 {len(clubs_data)}/{len(CLUBS)} клубов\n"
    
    if last_api_success:
        time_diff = int(time.time() - last_api_success)
        if time_diff < 3600:
            message_text += f"🕐 {time_diff//60} мин назад"
        else:
            message_text += f"🕐 {time_diff//3600} ч назад"
    
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

async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки пагинации"""
    query = update.callback_query
    await query.answer()
    
    try:
        page = int(query.data.split('_')[1])
        await rating(update, context, page)
    except Exception as e:
        await query.edit_message_text("❌ Ошибка")

async def club_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команд вида /Sakura, /Leo и т.д."""
    club_command = update.message.text[1:].lower()
    
    # Поиск клуба
    found_club = None
    club_info_data = None
    
    for club_name, info in CLUBS.items():
        short_name = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
        if club_command == short_name.lower():
            found_club = club_name
            club_info_data = info
            break
    
    if not found_club:
        await update.message.reply_text(
            f"❌ Клуб /{club_command} не найден\n"
            f"Пример: /Sakura, /Leo, /Karma",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Получаем данные
    data = await get_club_data_with_cache(club_info_data["tag"])
    
    if not data:
        await update.message.reply_text(
            f"❌ Нет данных для {found_club}\n"
            f"Используйте /refresh",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Формируем компактную информацию
    representative = club_info_data.get('representative', 'Не указан')
    trophies = data.get('trophies', 0)
    required_trophies = data.get('requiredTrophies', 0)
    members = data.get('members', [])
    member_count = len(members) if members else 0
    description = data.get('description', 'Нет описания')
    
    # Эмодзи для типа
    club_emoji = "👑" if found_club.startswith("Heaven") else "🩸"
    club_type = "Heavenly Dynasty" if found_club.startswith("Heaven") else "Bloody Family"
    
    message_text = f"{club_emoji} *{found_club}*\n\n"
    message_text += f"*Основное:*\n"
    message_text += f"Тип: {club_type}\n"
    message_text += f"Представитель: {representative}\n\n"
    
    message_text += f"*Статистика:*\n"
    message_text += f"🏆 Кубы: {trophies:,}\n"
    message_text += f"👥 Участники: {member_count}/30\n"
    message_text += f"🎯 Требуется: {required_trophies:,}\n\n"
    
    message_text += f"*Описание:*\n{description}\n\n"
    
    # Топ-3 игрока
    if members:
        sorted_members = sorted(members, key=lambda x: x.get('trophies', 0), reverse=True)[:3]
        message_text += f"*Топ-3 игрока:*\n"
        for j, player in enumerate(sorted_members, 1):
            message_text += f"{j}. {player.get('name', 'Unknown')} - 🏆 {player.get('trophies', 0):,}\n"
    
    message_text += f"\n🔗 /rating - Весь рейтинг"
    
    await update.message.reply_text(message_text, parse_mode=ParseMode.MARKDOWN)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ Ошибка")
    except:
        pass

async def cleanup():
    """Очистка ресурсов"""
    global session, application, runner
    
    if session and not session.closed:
        await session.close()
    
    if application:
        await application.stop()
        await application.shutdown()
    
    if runner:
        await runner.cleanup()

async def run_bot():
    """Запуск бота"""
    global application
    
    try:
        # Запускаем веб-сервер
        await start_web_server()
        
        # Создаем Application (не Updater!)
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Регистрируем команды в Application
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", start))
        application.add_handler(CommandHandler("rating", rating))
        application.add_handler(CommandHandler("refresh", refresh))
        application.add_handler(CommandHandler("status", status_command))
        
        # Команды для всех клубов
        for club_name in CLUBS.keys():
            short_name = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
            application.add_handler(CommandHandler(short_name, club_info))
        
        # Пагинация
        application.add_handler(CallbackQueryHandler(page_callback, pattern=r"^page_\d+$"))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        logger.info("✅ Бот запущен!")
        logger.info(f"📊 Клубов: {len(CLUBS)}")
        
        # Автозагрузка данных при запуске
        if BRAWL_API_KEY:
            for club_info in list(CLUBS.values())[:2]:
                await get_club_data_with_cache(club_info["tag"], force_refresh=True)
                await asyncio.sleep(1)
        
        # Запускаем polling в Application
        await application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await cleanup()

def main():
    """Точка входа"""
    # Настройка сигналов
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(cleanup()))
    signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(cleanup()))
    
    # Запуск
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
