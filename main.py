import os
import asyncio
import logging
import json
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from aiohttp import web

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из вашего кода
TELEGRAM_TOKEN = "8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU"
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')  # API ключ опциональный
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

# ========== ФИКСИРОВАННЫЕ ДАННЫЕ (на крайний случай) ==========
FALLBACK_DATA = {
    "#2C29U8Q8P": {"trophies": 52800, "members": [{} for _ in range(28)], "requiredTrophies": 5000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Leo"},
    "#JG9U8U82": {"trophies": 51000, "members": [{} for _ in range(26)], "requiredTrophies": 4500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Cucumber"},
    "#80LPG8V8L": {"trophies": 50500, "members": [{} for _ in range(27)], "requiredTrophies": 4000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Temple"},
    "#2C2YLRCCU": {"trophies": 50200, "members": [{} for _ in range(25)], "requiredTrophies": 3500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Kingdom"},
    "#2LQ2UV0LJ": {"trophies": 49800, "members": [{} for _ in range(24)], "requiredTrophies": 3000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Dream"},
    "#C8CG8GQJ": {"trophies": 49500, "members": [{} for _ in range(23)], "requiredTrophies": 2500, "description": "👑 Heavenly Dynasty main club", "name": "Heaven Dynasty"},
    "#2LCUY0Q8G": {"trophies": 49200, "members": [{} for _ in range(22)], "requiredTrophies": 2000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Winter"},
    "#JYR0YRR2": {"trophies": 48900, "members": [{} for _ in range(21)], "requiredTrophies": 1500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Envoy"},
    "#80LQRCR0J": {"trophies": 48600, "members": [{} for _ in range(20)], "requiredTrophies": 1000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Dominion"},
    "#2Q082VC08": {"trophies": 48300, "members": [{} for _ in range(19)], "requiredTrophies": 500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Sakura"},
    "#2VJRV89JG": {"trophies": 48000, "members": [{} for _ in range(18)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Vinland"},
    "#2VCLRRYCV": {"trophies": 47700, "members": [{} for _ in range(17)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Infinity"},
    "#JGYRPPPY": {"trophies": 47400, "members": [{} for _ in range(16)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Reverse"},
    "#2LC9JVQLJ": {"trophies": 47100, "members": [{} for _ in range(15)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Tomatoes"},
    "#2CLQ2RPL8": {"trophies": 46800, "members": [{} for _ in range(14)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Thunder"},
    "#2LGRGCL9U": {"trophies": 46500, "members": [{} for _ in range(13)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Curse"},
    "#JYGVQR89": {"trophies": 46200, "members": [{} for _ in range(12)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Karma"},
    "#JG2GPJ9Q": {"trophies": 45900, "members": [{} for _ in range(11)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Moscow"},
    "#C0JJC0L2": {"trophies": 45600, "members": [{} for _ in range(10)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Fortress"},
    "#C0QQ8RV0": {"trophies": 45300, "members": [{} for _ in range(9)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Hell"},
    "#2Q2QVYGU8": {"trophies": 45000, "members": [{} for _ in range(8)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven KE"},
    "#2YPYJC88J": {"trophies": 48500, "members": [{} for _ in range(26)], "requiredTrophies": 4000, "description": "🩸 Bloody Family branch", "name": "Bloody Legion"},
    "#2VCU8J9CV": {"trophies": 48000, "members": [{} for _ in range(25)], "requiredTrophies": 3500, "description": "🩸 Bloody Family branch", "name": "Bloody Justice"},
    "#2VUURGQLR": {"trophies": 47500, "members": [{} for _ in range(24)], "requiredTrophies": 3000, "description": "🩸 Bloody Family branch", "name": "Bloody Valley"},
    "#2Y89QRGQU": {"trophies": 47000, "members": [{} for _ in range(23)], "requiredTrophies": 2500, "description": "🩸 Bloody Family branch", "name": "Bloody Requiem"},
    "#2JQURGVRG": {"trophies": 46500, "members": [{} for _ in range(22)], "requiredTrophies": 2000, "description": "🩸 Bloody Family branch", "name": "Bloody Cards"},
}

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
session: Optional[aiohttp.ClientSession] = None
application: Optional[Application] = None
web_app: Optional[web.Application] = None
runner: Optional[web.AppRunner] = None
cache: Dict = {}
current_ip: Optional[str] = None
api_working: bool = False
last_api_check: float = 0

# ========== ФУНКЦИИ ДЛЯ IP И API ==========
async def get_current_ip() -> Optional[str]:
    """Получить текущий IP адрес сервера"""
    global current_ip
    try:
        async with aiohttp.ClientSession() as temp_session:
            # Пробуем несколько сервисов для надежности
            ip_services = [
                "https://api.ipify.org?format=json",
                "https://api64.ipify.org?format=json",
                "https://ipinfo.io/json"
            ]
            
            for service in ip_services:
                try:
                    async with temp_session.get(service, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            if service == "https://ipinfo.io/json":
                                current_ip = data.get('ip', 'Не определен')
                            else:
                                current_ip = data.get('ip', 'Не определен')
                            
                            if current_ip and current_ip != 'Не определен':
                                logger.info(f"🌐 IP адрес получен: {current_ip}")
                                return current_ip
                except Exception as e:
                    logger.debug(f"Ошибка получения IP с {service}: {e}")
                    continue
            
            # Если все сервисы не сработали
            current_ip = "Не удалось определить"
            logger.warning("⚠️ Не удалось определить IP адрес")
            return None
            
    except Exception as e:
        logger.error(f"❌ Ошибка при получении IP: {e}")
        current_ip = "Ошибка определения"
        return None

async def check_api_status() -> bool:
    """Проверить статус API Brawl Stars"""
    global api_working, last_api_check, session
    
    if not BRAWL_API_KEY:
        api_working = False
        last_api_check = time.time()
        logger.info("⚠️ API ключ не установлен")
        return False
    
    # Проверяем не чаще чем раз в 2 минуты
    if time.time() - last_api_check < 120:
        return api_working
    
    # Тестируем API на первом клубе
    test_tag = list(CLUBS.values())[0]["tag"]
    clean_tag = test_tag.replace('#', '')
    url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
    
    try:
        if session is None or session.closed:
            session = aiohttp.ClientSession()
        
        async with session.get(url, headers=headers, timeout=10) as response:
            api_working = response.status == 200
            last_api_check = time.time()
            
            if api_working:
                logger.info("✅ API Brawl Stars работает")
            else:
                logger.warning(f"❌ API не работает, статус: {response.status}")
            
            return api_working
    except Exception as e:
        logger.error(f"❌ Ошибка проверки API: {e}")
        api_working = False
        last_api_check = time.time()
        return False

async def fetch_club_data(club_tag: str, force_refresh: bool = False) -> Dict:
    """Получить данные клуба с приоритетом: API → Кэш → Fallback"""
    global cache, api_working
    
    # Если force_refresh=False и есть свежий кэш (< 1 часа), используем его
    if not force_refresh and club_tag in cache:
        cached = cache[club_tag]
        if time.time() - cached["timestamp"] < 3600:  # 1 час
            logger.debug(f"Использую кэш для {club_tag}")
            return cached["data"]
    
    # Пробуем получить данные из API (если ключ есть и API работает)
    if BRAWL_API_KEY and (api_working or await check_api_status()):
        clean_tag = club_tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
        headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
        
        try:
            if session is None or session.closed:
                session = aiohttp.ClientSession()
            
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    # Сохраняем в кэш
                    cache[club_tag] = {
                        "data": data,
                        "timestamp": time.time(),
                        "source": "api"
                    }
                    logger.info(f"✅ Данные обновлены из API для {club_tag}")
                    return data
        except Exception as e:
            logger.error(f"Ошибка API запроса {club_tag}: {e}")
            # При ошибке API помечаем его как неработающий
            api_working = False
    
    # Используем fallback данные
    if club_tag in FALLBACK_DATA:
        logger.info(f"Использую fallback данные для {club_tag}")
        fallback_data = FALLBACK_DATA[club_tag]
        
        # Сохраняем в кэш как fallback
        cache[club_tag] = {
            "data": fallback_data,
            "timestamp": time.time(),
            "source": "fallback"
        }
        return fallback_data
    
    # Если ничего не нашли, возвращаем пустые данные
    empty_data = {
        "name": "Unknown Club",
        "trophies": 45000,
        "requiredTrophies": 0,
        "members": [],
        "description": "Нет данных"
    }
    cache[club_tag] = {
        "data": empty_data,
        "timestamp": time.time(),
        "source": "empty"
    }
    return empty_data

async def get_sorted_clubs() -> List[Tuple[str, Dict, Dict]]:
    """Получить отсортированные данные всех клубов"""
    clubs_data = []
    
    for club_name, club_info in CLUBS.items():
        try:
            data = await fetch_club_data(club_info["tag"])
            clubs_data.append((club_name, club_info, data))
        except Exception as e:
            logger.error(f"Ошибка получения данных для {club_name}: {e}")
            # Используем fallback при ошибке
            if club_info["tag"] in FALLBACK_DATA:
                data = FALLBACK_DATA[club_info["tag"]]
                clubs_data.append((club_name, club_info, data))
    
    # Сортировка по трофеям (по убыванию)
    clubs_data.sort(key=lambda x: x[2].get('trophies', 0), reverse=True)
    
    return clubs_data

# ========== ПАГИНАЦИЯ РЕЙТИНГА ==========
def format_club_line(idx: int, club_name: str, club_info: Dict, club_data: Dict) -> str:
    """Форматирование строки клуба для рейтинга"""
    emoji = "👑" if club_name.startswith("Heaven") else "🩸"
    rep = club_info.get('rep', '—')
    trophies = club_data.get('trophies', 0)
    members = club_data.get('members', [])
    member_count = len(members)
    
    # Короткое имя для команды
    short_name = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
    
    # Формат: позиция. эмодзи название | представитель | кубки/участники | команда
    line = f"{idx}. {emoji} *{club_name}*\n"
    line += f"   👤 {rep}\n"
    line += f"   🏆 {trophies:,} | 👥 {member_count}/30\n"
    line += f"   📖 /{short_name}\n"
    
    return line

def get_pagination_keyboard(current_page: int, total_pages: int) -> Optional[InlineKeyboardMarkup]:
    """Клавиатура для пагинации"""
    buttons = []
    
    if current_page > 0:
        buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{current_page-1}"))
    
    # Индикатор страницы
    buttons.append(InlineKeyboardButton(f"{current_page+1}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"page_{current_page+1}"))
    
    if buttons:
        return InlineKeyboardMarkup([buttons])
    return None

async def send_rating_page(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Отправить страницу рейтинга"""
    clubs_per_page = 10
    
    # Получаем отсортированные данные
    clubs_data = await get_sorted_clubs()
    
    if not clubs_data:
        error_msg = "❌ Не удалось загрузить данные клубов"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)
        return
    
    # Рассчитываем пагинацию
    total_clubs = len(clubs_data)
    total_pages = (total_clubs + clubs_per_page - 1) // clubs_per_page
    
    # Проверяем валидность страницы
    if page >= total_pages:
        page = 0
    if page < 0:
        page = total_pages - 1
    
    # Получаем клубы для текущей страницы
    start_idx = page * clubs_per_page
    end_idx = min(start_idx + clubs_per_page, total_clubs)
    page_clubs = clubs_data[start_idx:end_idx]
    
    # Формируем заголовок
    message = f"🏆 *Рейтинг клубов*\n"
    message += f"📄 Страница {page + 1}/{total_pages}\n"
    message += f"📍 Позиции {start_idx + 1}-{end_idx} из {total_clubs}\n\n"
    
    # Добавляем клубы
    for i, (club_name, club_info, club_data) in enumerate(page_clubs, 1):
        message += format_club_line(start_idx + i, club_name, club_info, club_data)
        message += "\n"  # Разделитель между клубами
    
    # Статистика
    heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
    
    # Информация о данных
    if cache:
        # Анализ источников данных
        sources = [c.get("source", "unknown") for c in cache.values()]
        api_count = sources.count("api")
        fallback_count = sources.count("fallback")
        cache_count = sources.count("cache")
        
        # Время последнего обновления
        if api_count > 0:
            api_times = [c["timestamp"] for c in cache.values() if c.get("source") == "api"]
            if api_times:
                last_api_time = max(api_times)
                time_diff = int(time.time() - last_api_time)
                if time_diff < 60:
                    data_info = f"🕐 API: {time_diff} сек назад"
                elif time_diff < 3600:
                    data_info = f"🕐 API: {time_diff//60} мин назад"
                else:
                    data_info = f"🕐 API: {time_diff//3600} ч назад"
            else:
                data_info = "📊 Данные: из кэша"
        else:
            data_info = "📊 Данные: резервные"
    else:
        data_info = "📊 Данные: загружаются..."
    
    message += f"📊 *Статистика:*\n"
    message += f"👑 Heavenly Dynasty: {heaven_count} клубов\n"
    message += f"🩸 Bloody Family: {bloody_count} клубов\n"
    message += f"🎯 Всего: {total_clubs} клубов\n"
    message += f"{data_info}\n"
    message += f"🔄 /refresh - обновить данные"
    
    # Клавиатура пагинации
    reply_markup = get_pagination_keyboard(page, total_pages)
    
    # Отправляем или обновляем сообщение
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        await update.callback_query.answer()
    else:
        await update.message.reply_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

# ========== ВЕБ-СЕРВЕР ==========
async def health_handler(request):
    """Обработчик health check"""
    return web.json_response({
        "status": "ok",
        "service": "Heaven & Bloody Bot",
        "timestamp": datetime.now().isoformat(),
        "clubs_count": len(CLUBS),
        "cache_size": len(cache),
        "api_working": api_working,
        "server_ip": current_ip
    })

async def start_web_server():
    """Запустить веб-сервер"""
    global web_app, runner
    
    web_app = web.Application()
    web_app.router.add_get('/', health_handler)
    web_app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    logger.info(f"✅ Веб-сервер запущен на порту {PORT}")

# ========== КОМАНДЫ БОТА ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    # Получаем IP если еще не получали
    global current_ip
    if not current_ip:
        await get_current_ip()
    
    # Проверяем статус API
    await check_api_status()
    
    heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
    
    # Анализ кэша
    if cache:
        sources = [c.get("source", "unknown") for c in cache.values()]
        api_count = sources.count("api")
        fallback_count = sources.count("fallback")
        data_source = f"API: {api_count}, Резерв: {fallback_count}"
    else:
        data_source = "загружаются..."
    
    message = f"""🎮 *Heaven & Bloody Stats Bot*

📊 *Статистика:*
👑 Heavenly Dynasty: {heaven_count} клубов
🩸 Bloody Family: {bloody_count} клубов
📈 Всего: {len(CLUBS)} клубов
💾 Данные: {data_source}

🌐 *IP сервера:* `{current_ip or 'определяю...'}`

📡 *Статус API:* {'🟢 работает' if api_working else '🔴 не работает'}

⚡ *Основные команды:*
/rating - Рейтинг всех клубов (по 10 на странице)
/refresh - Обновить данные из API
/status - Детальный статус бота
/ip - Показать IP для настройки API
/setup - Инструкция по настройке

👥 *Команды клубов:*
Пример: /leo, /sakura, /karma, /moscow
Всего доступно: {len(CLUBS)} команд

📖 *Формат рейтинга:*
Название | представитель | кубки/участники | команда для деталей"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /ip - показать IP адрес"""
    global current_ip
    
    await update.message.reply_text("🌐 Определяю IP адрес...")
    
    # Получаем текущий IP
    ip = await get_current_ip()
    
    if ip and ip not in ["Не удалось определить", "Ошибка определения"]:
        message = f"""🌐 *IP адрес сервера*

Ваш IP адрес для настройки Brawl Stars API:

`{ip}`

📝 *Как использовать:*
1. Откройте: https://developer.brawlstars.com
2. Выберите ваш проект
3. Нажмите "Edit" у API ключа
4. В "Allowed IPs" добавьте IP выше
5. Сохраните изменения
6. Подождите 1-2 минуты

🔧 *После настройки:*
/refresh - обновить данные из API
/status - проверить статус API

⚠️ *Примечание:* IP может меняться при перезапуске сервера"""
    else:
        message = "❌ Не удалось определить IP адрес\nПопробуйте позже или проверьте подключение к интернету"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - детальный статус"""
    global current_ip
    
    # Обновляем информацию
    if not current_ip:
        await get_current_ip()
    
    await check_api_status()
    
    # Анализ кэша
    cache_stats = {"api": 0, "fallback": 0, "cache": 0, "unknown": 0}
    cache_times = []
    
    for cached in cache.values():
        source = cached.get("source", "unknown")
        cache_stats[source] = cache_stats.get(source, 0) + 1
        cache_times.append(cached["timestamp"])
    
    # Время данных
    if cache_times:
        oldest = min(cache_times)
        newest = max(cache_times)
        
        old_diff = int(time.time() - oldest)
        new_diff = int(time.time() - newest)
        
        if old_diff < 60:
            oldest_str = f"{old_diff} сек"
        elif old_diff < 3600:
            oldest_str = f"{old_diff//60} мин"
        else:
            oldest_str = f"{old_diff//3600} ч"
            
        if new_diff < 60:
            newest_str = f"{new_diff} сек"
        elif new_diff < 3600:
            newest_str = f"{new_diff//60} мин"
        else:
            newest_str = f"{new_diff//3600} ч"
    else:
        oldest_str = "нет данных"
        newest_str = "нет данных"
    
    # Источник данных
    if cache_stats['api'] > 0:
        data_source = f"🟢 API ({cache_stats['api']} клубов)"
    elif cache_stats['fallback'] > 0:
        data_source = f"🟡 Резерв ({cache_stats['fallback']} клубов)"
    else:
        data_source = "🔴 Нет данных"
    
    message = f"""📊 *Детальный статус бота*

🌐 *Сеть:*
IP адрес: `{current_ip or 'не определен'}`
Веб-сервер: 🟢 работает на порту {PORT}
API подключение: {'🟢 РАБОТАЕТ' if api_working else '🔴 НЕ РАБОТАЕТ'}

💾 *Данные:*
Всего клубов: {len(CLUBS)}
В кэше: {len(cache)} клубов
Источник: {data_source}
Данные API: {cache_stats['api']} клубов
Резервные: {cache_stats['fallback']} клубов
Возраст данных:
  • Самые старые: {oldest_str} назад
  • Самые свежие: {newest_str} назад

👥 *Состав семьи:*
👑 Heavenly Dynasty: {len([n for n in CLUBS if n.startswith('Heaven')])} клубов
🩸 Bloody Family: {len([n for n in CLUBS if n.startswith('Bloody')])} клубов

⚙️ *Команды:*
/rating - Рейтинг (10 клубов на страницу)
/refresh - Обновить данные из API
/ip - Показать IP для настройки
/setup - Инструкция"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /setup - инструкция по настройке"""
    global current_ip
    
    # Убедимся что IP есть
    if not current_ip:
        await get_current_ip()
    
    message = f"""🔧 *ИНСТРУКЦИЯ ПО НАСТРОЙКЕ API*

Для работы с реальными данными Brawl Stars:

1️⃣ *Получить API ключ:*
• Откройте: https://developer.brawlstars.com
• Создайте новый проект
• Скопируйте API ключ

2️⃣ *Добавить IP в whitelist:*
Ваш IP адрес: `{current_ip or 'определяю...'}`
• На Brawl Stars Developer Portal
• Выберите ваш проект
• Нажмите "Edit" у API ключа
• В "Allowed IPs" добавьте IP выше
• Сохраните изменения
• Подождите 1-2 минуты

3️⃣ *Добавить ключ в переменные окружения:*
• В Render: Settings → Environment
• Добавьте переменную: `BRAWL_API_KEY`
• Вставьте ваш ключ
• Сохраните (Save Changes)

4️⃣ *Проверить работу:*
• Подождите 1-2 минуты
• Используйте: /refresh
• Затем: /rating

📊 *Пока настраиваете:*
• Бот использует резервные данные
• Все функции работают
• После настройки данные станут актуальными

⚠️ *Примечание:*
• API имеет ограничения по запросам
• IP может меняться при перезапуске
• Используйте /ip для получения текущего IP"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /rating"""
    # Показываем сообщение о загрузке
    loading_msg = await update.message.reply_text("⏳ Загружаю рейтинг...")
    
    # Отправляем первую страницу
    await send_rating_page(update, context, 0)
    
    # Удаляем сообщение о загрузке
    try:
        await loading_msg.delete()
    except:
        pass

async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /refresh - обновить данные из API"""
    if not BRAWL_API_KEY:
        await update.message.reply_text(
            "❌ API ключ не установлен\n\n"
            "Для настройки:\n"
            "1. Получите ключ на https://developer.brawlstars.com\n"
            "2. Используйте /setup для инструкции\n"
            "3. Добавьте переменную BRAWL_API_KEY\n\n"
            "📊 Пока используются резервные данные",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("🔄 Начинаю обновление данных из API...")
    
    # Проверяем API
    if not await check_api_status():
        await update.message.reply_text(
            "❌ API не доступен\n\n"
            "Возможные причины:\n"
            "• API ключ неверный\n"
            "• IP не добавлен в whitelist\n"
            "• Ограничения API\n\n"
            "Используйте:\n"
            "/ip - получить IP\n"
            "/setup - инструкция\n\n"
            "📊 Используются кэшированные данные",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Обновляем данные для всех клубов с задержкой
    updated = 0
    failed = 0
    total = len(CLUBS)
    
    progress_msg = await update.message.reply_text(f"🔄 0/{total}...")
    
    for idx, (club_name, club_info) in enumerate(CLUBS.items(), 1):
        try:
            # Обновляем прогресс каждые 5 клубов
            if idx % 5 == 0 or idx == total:
                try:
                    await progress_msg.edit_text(f"🔄 {idx}/{total}...")
                except:
                    pass
            
            # Задержка чтобы не превысить лимиты API
            await asyncio.sleep(0.3)
            
            data = await fetch_club_data(club_info["tag"], force_refresh=True)
            if data:
                updated += 1
            else:
                failed += 1
                
        except Exception as e:
            logger.error(f"Ошибка обновления {club_name}: {e}")
            failed += 1
    
    # Удаляем сообщение о прогрессе
    try:
        await progress_msg.delete()
    except:
        pass
    
    # Формируем отчет
    message = f"✅ *Обновление завершено!*\n\n"
    message += f"📊 *Результаты:*\n"
    message += f"• Успешно: {updated} клубов\n"
    message += f"• Ошибок: {failed} клубов\n"
    message += f"• Всего: {total} клубов\n\n"
    
    if updated > 0:
        message += f"🏆 Используйте /rating для просмотра актуального рейтинга"
    else:
        message += f"⚠️ Данные не обновлены. Используются кэшированные значения."
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def club_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд клубов (/leo, /sakura и т.д.)"""
    command = update.message.text[1:].lower()
    
    # Ищем клуб
    found_club = None
    found_info = None
    
    for club_name, club_info in CLUBS.items():
        short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
        if command == short:
            found_club = club_name
            found_info = club_info
            break
    
    if not found_club:
        await update.message.reply_text(f"❌ Клуб /{command} не найден")
        return
    
    # Получаем данные
    await update.message.reply_text(f"⏳ Загружаю данные для {found_club}...")
    data = await fetch_club_data(found_info["tag"])
    
    # Формируем детальную информацию
    emoji = "👑" if found_club.startswith("Heaven") else "🩸"
    rep = found_info.get("rep", "—")
    trophies = data.get('trophies', 0)
    required = data.get('requiredTrophies', 0)
    members = data.get('members', [])
    member_count = len(members)
    description = data.get('description', 'Нет описания')
    
    message = f"{emoji} *{found_club}*\n\n"
    message += f"*📋 Основная информация:*\n"
    message += f"Представитель: {rep}\n"
    message += f"Тег клуба: {found_info['tag']}\n\n"
    
    message += f"*📊 Статистика:*\n"
    message += f"🏆 Общие кубки: {trophies:,}\n"
    message += f"👥 Участников: {member_count}/30\n"
    message += f"🎯 Требуется для входа: {required:,}\n\n"
    
    message += f"*📝 Описание:*\n{description}\n\n"
    
    # Топ-3 игрока
    if members:
        # Сортируем по кубкам
        sorted_members = sorted(members, key=lambda x: x.get('trophies', 0), reverse=True)[:3]
        
        message += f"*🏅 Топ-3 игрока:*\n"
        for i, member in enumerate(sorted_members, 1):
            name = member.get('name', 'Unknown')
            member_trophies = member.get('trophies', 0)
            role = member.get('role', 'member')
            
            # Эмодзи роли
            role_emoji = {
                'president': '👑',
                'vicePresident': '⭐',
                'senior': '🌟',
                'member': '👤'
            }.get(role, '👤')
            
            message += f"{i}. {role_emoji} {name} - 🏆 {member_trophies:,}\n"
    
    message += f"\n🔗 /rating - Вернуться к рейтингу"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def page_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик пагинации рейтинга"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Извлекаем номер страницы из callback_data
        if query.data == "current_page":
            return  # Игнорируем нажатие на индикатор страницы
        
        page_num = int(query.data.split('_')[1])
        await send_rating_page(update, context, page_num)
    except (IndexError, ValueError) as e:
        logger.error(f"Ошибка обработки пагинации: {e}")
        await query.edit_message_text("❌ Ошибка пагинации. Используйте /rating")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка\n"
                "Попробуйте позже или проверьте команду",
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass

# ========== ЗАПУСК И ОЧИСТКА ==========
async def cleanup():
    """Очистка ресурсов"""
    global session, runner
    
    logger.info("🛑 Очистка ресурсов...")
    
    if session and not session.closed:
        await session.close()
        logger.info("✅ HTTP сессия закрыта")
    
    if runner:
        await runner.cleanup()
        logger.info("✅ Веб-сервер остановлен")

async def run_bot():
    """Основная функция запуска бота"""
    global application, session, current_ip
    
    try:
        # 1. Логируем запуск
        logger.info("🚀 Запуск Heaven & Bloody Stats Bot...")
        logger.info(f"🤖 Токен: {TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-5:]}")
        logger.info(f"🔑 API ключ: {'установлен' if BRAWL_API_KEY else 'не установлен'}")
        
        # 2. Получаем IP адрес при запуске
        logger.info("🌐 Получаю IP адрес сервера...")
        current_ip = await get_current_ip()
        logger.info(f"🌐 IP: {current_ip}")
        
        # 3. Создаем сессию
        session = aiohttp.ClientSession()
        
        # 4. Запускаем веб-сервер
        await start_web_server()
        
        # 5. Создаем приложение бота
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # 6. Регистрируем команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", start_command))
        application.add_handler(CommandHandler("rating", rating_command))
        application.add_handler(CommandHandler("refresh", refresh_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("setup", setup_command))
        application.add_handler(CommandHandler("ip", ip_command))
        
        # Регистрируем команды клубов
        for club_name in CLUBS.keys():
            short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
            application.add_handler(CommandHandler(short, club_info_command))
        
        # Обработчик пагинации
        application.add_handler(CallbackQueryHandler(
            page_callback_handler, 
            pattern=r"^page_\d+$"
        ))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        # 7. Проверяем API при запуске
        await check_api_status()
        
        # 8. Предзагрузка данных
        logger.info("🔄 Предзагрузка данных...")
        preload_count = min(3, len(CLUBS))
        for i, (club_name, club_info) in enumerate(list(CLUBS.items())[:preload_count]):
            try:
                await fetch_club_data(club_info["tag"])
                logger.debug(f"Предзагружен {club_name}")
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"Ошибка предзагрузки {club_name}: {e}")
        
        # 9. Статистика запуска
        logger.info(f"✅ Бот запущен!")
        logger.info(f"📊 Клубов в базе: {len(CLUBS)}")
        logger.info(f"💾 В кэше: {len(cache)} клубов")
        logger.info(f"📡 API: {'работает' if api_working else 'не работает'}")
        logger.info("🤖 Ожидаю команд...")
        
        # 10. Запускаем бота
        await application.run_polling()
        
    except asyncio.CancelledError:
        logger.info("⏹️  Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
    finally:
        await cleanup()

def main():
    """Точка входа"""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("👋 Завершение работы...")

if __name__ == "__main__":
    main()
