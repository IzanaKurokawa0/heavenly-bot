import os
import asyncio
import signal
import logging
from typing import Dict, List, Tuple, Optional
import aiohttp
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from aiohttp import web
import time
from datetime import datetime

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')
PORT = int(os.getenv('PORT', '8080'))

if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU':
    logger.warning("⚠️  TELEGRAM_TOKEN не установлен или используется тестовый токен")

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

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
session: Optional[aiohttp.ClientSession] = None
application: Optional[Application] = None
web_app: Optional[web.Application] = None
runner: Optional[web.AppRunner] = None

cache: Dict = {}
current_ip: Optional[str] = None
last_api_check: Optional[float] = None
api_working: bool = False

# ========== ФУНКЦИИ ДЛЯ IP И API ==========
async def get_current_ip():
    """Получить текущий IP адрес"""
    global current_ip
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("https://api.ipify.org?format=json", timeout=5) as r:
                if r.status == 200:
                    data = await r.json()
                    current_ip = data.get('ip', 'Не определен')
                    logger.info(f"🌐 IP определен: {current_ip}")
                    return current_ip
    except Exception as e:
        logger.error(f"❌ Ошибка получения IP: {e}")
        current_ip = "Не определен"
        return None

async def check_api_status():
    """Проверить статус API"""
    global last_api_check, api_working, session
    
    if not BRAWL_API_KEY:
        api_working = False
        last_api_check = time.time()
        return False
    
    # Берем первый клуб для теста
    test_tag = list(CLUBS.values())[0]["tag"]
    clean_tag = test_tag.replace('#', '')
    url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
    
    try:
        if session is None or session.closed:
            session = aiohttp.ClientSession()
        
        async with session.get(url, headers=headers, timeout=10) as r:
            api_working = r.status == 200
            last_api_check = time.time()
            
            if api_working:
                logger.info("✅ API работает")
            else:
                logger.warning(f"❌ API не работает: {r.status}")
            
            return api_working
    except Exception as e:
        logger.error(f"❌ Ошибка проверки API: {e}")
        api_working = False
        last_api_check = time.time()
        return False

async def fetch_club_data(club_tag: str, force: bool = False) -> Optional[Dict]:
    """Получить данные клуба"""
    global session, cache, api_working
    
    # Проверяем кэш (5 минут)
    if not force and club_tag in cache:
        cached = cache[club_tag]
        if time.time() - cached["timestamp"] < 300:  # 5 минут
            return cached["data"]
    
    # Если API не работает, используем кэш
    if not api_working and club_tag in cache:
        return cache[club_tag]["data"]
    
    # Если нет API ключа, используем кэш
    if not BRAWL_API_KEY:
        return cache[club_tag]["data"] if club_tag in cache else None
    
    # Запрос к API
    clean_tag = club_tag.replace('#', '')
    url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
    
    try:
        if session is None or session.closed:
            session = aiohttp.ClientSession()
        
        async with session.get(url, headers=headers, timeout=15) as r:
            if r.status == 200:
                data = await r.json()
                # Сохраняем в кэш
                cache[club_tag] = {
                    "data": data,
                    "timestamp": time.time(),
                    "source": "api"
                }
                return data
            else:
                # Если ошибка API, используем кэш
                if club_tag in cache:
                    cache[club_tag]["source"] = "cache_error"
                    return cache[club_tag]["data"]
                return None
    except Exception as e:
        logger.error(f"Ошибка запроса {club_tag}: {e}")
        if club_tag in cache:
            cache[club_tag]["source"] = "cache_error"
            return cache[club_tag]["data"]
        return None

async def get_all_clubs() -> List[Tuple[str, Dict, Dict]]:
    """Получить данные всех клубов"""
    clubs_data = []
    
    for club_name, club_info in CLUBS.items():
        tag = club_info["tag"]
        data = await fetch_club_data(tag)
        
        if data:
            clubs_data.append((club_name, club_info, data))
    
    # Сортировка по трофеям
    clubs_data.sort(key=lambda x: x[2].get('trophies', 0), reverse=True)
    return clubs_data

# ========== ВЕБ-СЕРВЕР ДЛЯ HEALTH CHECK ==========
async def health_handler(request):
    """Обработчик health check"""
    return web.json_response({
        "status": "ok",
        "service": "Heaven & Bloody Bot",
        "ip": current_ip,
        "api_working": api_working,
        "cache_size": len(cache),
        "timestamp": time.time()
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

# ========== КОМАНДЫ ТЕЛЕГРАМ БОТА ==========
def pagination_keyboard(page: int, total_pages: int):
    """Клавиатура пагинации"""
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"page_{page+1}"))
    return InlineKeyboardMarkup([buttons]) if buttons else None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    # Определяем IP если еще не определили
    global current_ip
    if not current_ip:
        await get_current_ip()
    
    # Проверяем API
    await check_api_status()
    
    # Статистика
    total_clubs = len(CLUBS)
    heaven_clubs = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_clubs = len([n for n in CLUBS if n.startswith("Bloody")])
    
    message = f"""🎮 *Heaven & Bloody Stats Bot*

📊 *Статистика:*
Клубов: {total_clubs} (👑 {heaven_clubs} | 🩸 {bloody_clubs})
Данные: {len(cache)}/{total_clubs} в кэше
API: {'🟢 работает' if api_working else '🔴 не работает'}

🌐 *IP сервера:* `{current_ip or "определяю..."}`

⚡ *Основные команды:*
/rating - Рейтинг всех клубов
/status - Детальный статус
/refresh - Обновить данные
/setup - Инструкция по настройке

👥 *Информация о клубе:*
Пример: /Sakura, /Leo, /Karma, /Moscow"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status"""
    # Обновляем статус
    global current_ip, last_api_check, api_working
    
    if not current_ip:
        await get_current_ip()
    
    await check_api_status()
    
    # Время последней проверки
    if last_api_check:
        time_diff = int(time.time() - last_api_check)
        if time_diff < 60:
            last_check = f"{time_diff} сек назад"
        else:
            last_check = f"{time_diff//60} мин назад"
    else:
        last_check = "никогда"
    
    # Информация о кэше
    cache_info = []
    for tag, cached in cache.items():
        time_diff = int(time.time() - cached["timestamp"])
        if time_diff < 60:
            age = f"{time_diff} сек"
        else:
            age = f"{time_diff//60} мин"
        cache_info.append(f"• {age} назад")
    
    cache_summary = "\n".join(cache_info[:3]) if cache_info else "нет данных"
    if len(cache_info) > 3:
        cache_summary += f"\n• ...и еще {len(cache_info)-3}"
    
    message = f"""📊 *Детальный статус*

🌐 *Сеть:*
IP адрес: `{current_ip or "не определен"}`
API подключение: {'🟢 РАБОТАЕТ' if api_working else '🔴 НЕ РАБОТАЕТ'}
Последняя проверка: {last_check}

💾 *Данные:*
Всего клубов: {len(CLUBS)}
В кэше: {len(cache)} клубов
Актуальность кэша:
{cache_summary}

👥 *Состав:*
👑 Heavenly Dynasty: {len([n for n in CLUBS if n.startswith('Heaven')])}
🩸 Bloody Family: {len([n for n in CLUBS if n.startswith('Bloody')])}"""
    
    # Инструкция если API не работает
    if not api_working and current_ip and current_ip != "Не определен":
        message += f"""

🔧 *НАСТРОЙКА API:*

1️⃣ *Добавьте IP в Brawl Stars API:*
`{current_ip}`
Сайт: https://developer.brawlstars.com

2️⃣ *Добавьте ключ в Render:*
• Settings → Environment
• Добавить BRAWL_API_KEY
• Вставить ключ
• Сохранить (НЕ "Save & Deploy")

3️⃣ *Обновить данные:* /refresh"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /setup - инструкция"""
    global current_ip
    
    if not current_ip:
        await get_current_ip()
    
    if not current_ip or current_ip == "Не определен":
        await update.message.reply_text("❌ Не удалось определить IP адрес")
        return
    
    message = f"""🔧 *ИНСТРУКЦИЯ ПО НАСТРОЙКЕ*

📝 *Ваш IP адрес для whitelist:*
`{current_ip}`

1️⃣ *Добавить IP в Brawl Stars API:*
• Откройте: https://developer.brawlstars.com
• Выберите ваш проект
• Нажмите "Edit" у API ключа
• В "Allowed IPs" добавьте IP выше
• Нажмите "Save"
• Подождите 1-2 минуты

2️⃣ *Добавить ключ в Render (БЕЗ перезапуска!):*
• Render Dashboard → ваш сервис
• Environment → Add Environment Variable
• Name: `BRAWL_API_KEY`
• Value: ваш API ключ
• Сохранить (НЕ "Save & Deploy"!)

3️⃣ *Проверить и обновить:*
• Команда: /status
• Должно быть: "API подключение: 🟢 РАБОТАЕТ"
• Команда: /refresh

📊 *Пока настраиваете:*
• Бот работает с кэшированными данными
• /rating покажет последние сохраненные данные
• После настройки данные станут свежими"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /refresh"""
    if not BRAWL_API_KEY:
        await update.message.reply_text(
            "❌ API ключ не установлен\n"
            "Используйте /setup для инструкции",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("🔄 Обновляю данные...")
    
    # Проверяем API
    if not await check_api_status():
        await update.message.reply_text(
            f"❌ API не работает\n"
            f"IP: `{current_ip}`\n"
            f"Используйте /setup для проверки",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Обновляем данные
    updated = 0
    failed = 0
    
    for club_info in list(CLUBS.values())[:5]:  # Обновляем 5 клубов
        try:
            data = await fetch_club_data(club_info["tag"], force=True)
            if data:
                updated += 1
            else:
                failed += 1
            await asyncio.sleep(1)  # Задержка между запросами
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
            failed += 1
    
    message = f"✅ Обновление завершено!\n\n"
    message += f"📊 Результат:\n"
    message += f"• Успешно: {updated} клубов\n"
    message += f"• Ошибка: {failed} клубов\n\n"
    
    if updated > 0:
        message += f"Используйте /rating для просмотра"
    else:
        message += f"Проверьте настройки API (/setup)"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Команда /rating"""
    # Проверяем есть ли данные
    if not cache and not BRAWL_API_KEY:
        await update.message.reply_text(
            "⚠️  *Нет данных*\n\n"
            "Бот еще не загрузил данные.\n"
            "Используйте /setup для настройки API\n"
            "Или подождите автозагрузки",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("⏳ Загружаю рейтинг...")
    
    # Получаем данные
    clubs_data = await get_all_clubs()
    
    if not clubs_data:
        await update.message.reply_text(
            "❌ *Не удалось загрузить данные*\n"
            "Используйте /setup и /refresh",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Пагинация (10 клубов на страницу)
    per_page = 10
    total_pages = (len(clubs_data) + per_page - 1) // per_page
    
    if page >= total_pages:
        page = 0
    
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(clubs_data))
    
    # Формируем сообщение
    message = f"🏆 *Рейтинг клубов*\n"
    message += f"📄 Страница {page + 1}/{total_pages}\n\n"
    
    # Компактный формат
    for i, (club_name, club_info, data) in enumerate(clubs_data[start_idx:end_idx], start=1):
        pos = start_idx + i
        trophies = data.get('trophies', 0)
        members = data.get('members', [])
        member_count = len(members)
        rep = club_info.get('rep', 'Не указан')
        
        # Эмодзи для типа клуба
        emoji = "👑" if club_name.startswith("Heaven") else "🩸"
        
        # Короткое имя для команды
        short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
        
        # Формат: название | представитель | кубки/участники | команда
        message += f"{pos}. {emoji} *{club_name}*\n"
        message += f"   👤 {rep}\n"
        message += f"   🏆 {trophies:,} | 👥 {member_count}/30\n"
        message += f"   📖 /{short}\n\n"
    
    # Статистика
    heaven_count = len([n for n, _, _ in clubs_data if n.startswith("Heaven")])
    bloody_count = len([n for n, _, _ in clubs_data if n.startswith("Bloody")])
    
    # Информация о данных
    if cache:
        # Берем время самого свежего кэша
        latest_time = max([c["timestamp"] for c in cache.values()])
        time_diff = int(time.time() - latest_time)
        
        if time_diff < 60:
            data_age = f"🕐 {time_diff} сек назад"
        elif time_diff < 3600:
            data_age = f"🕐 {time_diff//60} мин назад"
        else:
            data_age = f"🕐 {time_diff//3600} ч назад"
    else:
        data_age = "🕐 нет данных"
    
    message += f"👑 {heaven_count} | 🩸 {bloody_count}\n"
    message += f"📊 {len(clubs_data)}/{len(CLUBS)} клубов\n"
    message += f"{data_age}\n"
    message += f"🔄 /refresh"
    
    # Отправляем
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=pagination_keyboard(page, total_pages)
        )
        await update.callback_query.answer()
    else:
        await update.message.reply_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=pagination_keyboard(page, total_pages)
        )

async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик пагинации"""
    query = update.callback_query
    await query.answer()
    
    try:
        page = int(query.data.split('_')[1])
        await rating_command(update, context, page)
    except:
        await query.edit_message_text("❌ Ошибка пагинации")

async def club_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для информации о клубе (/Sakura, /Leo и т.д.)"""
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
        await update.message.reply_text(
            f"❌ Клуб /{command} не найден\n"
            f"Пример: /Sakura, /Leo, /Karma",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text(f"⏳ Загружаю данные для {found}...")
    
    # Получаем данные
    data = await fetch_club_data(info["tag"])
    
    if not data:
        await update.message.reply_text(
            f"❌ Нет данных для {found}\n"
            f"Используйте /setup и /refresh",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Формируем информацию
    rep = info.get('rep', 'Не указан')
    trophies = data.get('trophies', 0)
    required = data.get('requiredTrophies', 0)
    members = data.get('members', [])
    member_count = len(members)
    description = data.get('description', 'Нет описания')
    
    emoji = "👑" if found.startswith("Heaven") else "🩸"
    club_type = "Heavenly Dynasty" if found.startswith("Heaven") else "Bloody Family"
    
    message = f"{emoji} *{found}*\n\n"
    message += f"*Основное:*\n"
    message += f"Тип: {club_type}\n"
    message += f"Представитель: {rep}\n\n"
    
    message += f"*Статистика:*\n"
    message += f"🏆 Общие кубки: {trophies:,}\n"
    message += f"👥 Участников: {member_count}/30\n"
    message += f"🎯 Требуется для входа: {required:,}\n\n"
    
    message += f"*Описание:*\n{description}\n\n"
    
    # Топ-3 игрока
    if members:
        top_players = sorted(members, key=lambda x: x.get('trophies', 0), reverse=True)[:3]
        message += f"*🏅 Топ-3 игрока:*\n"
        for i, player in enumerate(top_players, 1):
            name = player.get('name', 'Unknown')
            player_trophies = player.get('trophies', 0)
            role = player.get('role', 'member')
            
            # Эмодзи для роли
            role_emoji = {
                'president': '👑',
                'vicePresident': '⭐',
                'senior': '🌟',
                'member': '👤'
            }.get(role.lower(), '👤')
            
            message += f"{i}. {role_emoji} {name} - 🏆 {player_trophies:,}\n"
    
    message += f"\n🔗 /rating - Весь рейтинг"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка\n"
                "Попробуйте позже",
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass

# ========== ЗАПУСК И ОЧИСТКА ==========
async def cleanup():
    """Очистка ресурсов"""
    global session, application, runner
    
    logger.info("🛑 Очистка ресурсов...")
    
    if session and not session.closed:
        await session.close()
        logger.info("✅ Сессия закрыта")
    
    if application:
        await application.stop()
        await application.shutdown()
        logger.info("✅ Бот остановлен")
    
    if runner:
        await runner.cleanup()
        logger.info("✅ Веб-сервер остановлен")

async def shutdown_signal():
    """Обработчик сигналов завершения"""
    logger.info("📶 Получен сигнал завершения")
    await cleanup()

async def run_bot():
    """Запуск бота"""
    global application, current_ip
    
    try:
        # 1. Определяем IP при запуске
        logger.info("🚀 Запуск Heaven & Bloody Stats Bot...")
        await get_current_ip()
        
        # 2. Запускаем веб-сервер
        await start_web_server()
        
        # 3. Создаем Application
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # 4. Регистрируем команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", start_command))
        application.add_handler(CommandHandler("rating", rating_command))
        application.add_handler(CommandHandler("refresh", refresh_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("setup", setup_command))
        application.add_handler(CommandHandler("ip", setup_command))
        
        # Команды для клубов
        for club_name in CLUBS.keys():
            short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
            application.add_handler(CommandHandler(short, club_info_command))
        
        # Пагинация
        application.add_handler(CallbackQueryHandler(page_callback, pattern=r"^page_\d+$"))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        # 5. Логируем информацию
        logger.info("✅ Бот инициализирован!")
        logger.info(f"🌐 IP: {current_ip}")
        logger.info(f"📊 Клубов: {len(CLUBS)}")
        logger.info(f"🔑 API ключ: {'установлен' if BRAWL_API_KEY else 'не установлен'}")
        
        # 6. Проверяем API и загружаем данные если работает
        if BRAWL_API_KEY:
            logger.info("🔄 Проверка API...")
            if await check_api_status():
                logger.info("🔄 Автозагрузка данных...")
                # Загружаем данные для нескольких клубов
                for i, club_info in enumerate(list(CLUBS.values())[:3]):
                    await fetch_club_data(club_info["tag"])
                    if i < 2:
                        await asyncio.sleep(1)
                logger.info(f"✅ Загружено {min(3, len(CLUBS))} клубов")
            else:
                logger.warning("⚠️  API не работает, используем кэш")
        
        # 7. Запускаем бота
        logger.info("🤖 Бот запущен и ожидает команд...")
        
        # ИСПРАВЛЕНИЕ: используем правильный метод для запуска polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Бесконечный цикл ожидания
        while True:
            await asyncio.sleep(3600)  # Спим 1 час
        
    except KeyboardInterrupt:
        logger.info("⏹️  Остановлено пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await cleanup()

async def main():
    """Основная асинхронная функция"""
    # Регистрируем обработчики сигналов
    loop = asyncio.get_event_loop()
    
    # Обработка сигналов завершения
    stop_event = asyncio.Event()
    
    def signal_handler():
        logger.info("📶 Получен сигнал завершения")
        stop_event.set()
    
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    
    try:
        # Запускаем бота
        await run_bot()
    except asyncio.CancelledError:
        logger.info("⏹️  Задача отменена")
    finally:
        # Очистка ресурсов
        await cleanup()

if __name__ == "__main__":
    # Запускаем основную функцию
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  Приложение остановлено")
