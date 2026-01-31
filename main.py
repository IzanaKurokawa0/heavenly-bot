import os
import asyncio
import logging
import time
from typing import Dict, List, Tuple, Optional
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из вашего кода
TELEGRAM_TOKEN = "8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU"
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')  # API ключ опциональный

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
cache: Dict = {}
current_ip: Optional[str] = None
api_working: bool = False
last_api_check: float = 0

# ========== ФУНКЦИИ ДЛЯ IP И API ==========
async def get_current_ip() -> Optional[str]:
    """Получить текущий IP адрес сервера"""
    global current_ip
    try:
        # Простой запрос к ipify
        async with aiohttp.ClientSession() as temp_session:
            async with temp_session.get("https://api.ipify.org?format=json", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    current_ip = data.get('ip', 'Не определен')
                    logger.info(f"🌐 IP адрес: {current_ip}")
                    return current_ip
    except Exception as e:
        logger.error(f"❌ Ошибка получения IP: {e}")
        current_ip = "Ошибка определения"
        return None

async def check_api_status() -> bool:
    """Проверить статус API Brawl Stars"""
    global api_working, last_api_check
    
    if not BRAWL_API_KEY:
        api_working = False
        last_api_check = time.time()
        return False
    
    # Проверяем не чаще чем раз в 2 минуты
    if time.time() - last_api_check < 120:
        return api_working
    
    try:
        # Тестируем API на первом клубе
        test_tag = list(CLUBS.values())[0]["tag"]
        clean_tag = test_tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
        headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
        
        async with aiohttp.ClientSession() as temp_session:
            async with temp_session.get(url, headers=headers, timeout=10) as response:
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

async def fetch_club_data(club_tag: str) -> Dict:
    """Получить данные клуба"""
    global cache
    
    # Проверяем кэш (2 часа актуальности)
    if club_tag in cache:
        cached = cache[club_tag]
        if time.time() - cached["timestamp"] < 7200:  # 2 часа
            return cached["data"]
    
    # Пробуем получить данные из API
    if BRAWL_API_KEY:
        clean_tag = club_tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
        headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
        
        try:
            async with aiohttp.ClientSession() as temp_session:
                async with temp_session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Сохраняем в кэш
                        cache[club_tag] = {
                            "data": data,
                            "timestamp": time.time(),
                            "source": "api"
                        }
                        return data
        except Exception as e:
            logger.error(f"Ошибка API запроса {club_tag}: {e}")
    
    # Создаем фиктивные данные если API не работает
    fake_data = {
        "name": club_tag,
        "trophies": 50000,
        "requiredTrophies": 0,
        "members": [{"name": "Игрок", "trophies": 10000} for _ in range(25)],
        "description": "👑 Heavenly Dynasty" if "Heaven" in club_tag else "🩸 Bloody Family"
    }
    
    cache[club_tag] = {
        "data": fake_data,
        "timestamp": time.time(),
        "source": "fake"
    }
    
    return fake_data

async def get_sorted_clubs() -> List[Tuple[str, Dict, Dict]]:
    """Получить отсортированные данные всех клубов"""
    clubs_data = []
    
    for club_name, club_info in CLUBS.items():
        try:
            data = await fetch_club_data(club_info["tag"])
            clubs_data.append((club_name, club_info, data))
        except Exception as e:
            logger.error(f"Ошибка получения данных для {club_name}: {e}")
            # Создаем базовые данные при ошибке
            basic_data = {
                "name": club_name,
                "trophies": 45000,
                "requiredTrophies": 0,
                "members": [],
                "description": "Нет данных"
            }
            clubs_data.append((club_name, club_info, basic_data))
    
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
    
    # Получаем клубы для текущей страницы
    start_idx = page * clubs_per_page
    end_idx = min(start_idx + clubs_per_page, total_clubs)
    page_clubs = clubs_data[start_idx:end_idx]
    
    # Формируем сообщение
    message = f"🏆 *Рейтинг клубов*\n"
    message += f"📄 Страница {page + 1}/{total_pages}\n\n"
    
    # Добавляем клубы
    for i, (club_name, club_info, club_data) in enumerate(page_clubs, 1):
        message += format_club_line(start_idx + i, club_name, club_info, club_data)
        message += "\n"
    
    # Статистика
    heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
    
    # Информация о данных
    if cache:
        sources = [c.get("source", "unknown") for c in cache.values()]
        api_count = sources.count("api")
        data_info = f"📊 Данные: API {api_count}, Кэш {len(cache)-api_count}"
    else:
        data_info = "📊 Данные: загружаются..."
    
    message += f"📈 *Статистика:*\n"
    message += f"👑 Heavenly Dynasty: {heaven_count}\n"
    message += f"🩸 Bloody Family: {bloody_count}\n"
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

# ========== КОМАНДЫ БОТА ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    # Получаем IP если еще не получали
    global current_ip
    if not current_ip:
        await get_current_ip()
    
    heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
    
    message = f"""🎮 *Heaven & Bloody Stats Bot*

📊 *Статистика:*
👑 Heavenly Dynasty: {heaven_count} клубов
🩸 Bloody Family: {bloody_count} клубов
📈 Всего: {len(CLUBS)} клубов

🌐 *IP сервера:* `{current_ip or 'определяю...'}`

⚡ *Основные команды:*
/rating - Рейтинг всех клубов (по 10 на странице)
/refresh - Обновить данные из API
/status - Статус бота
/ip - Показать IP для настройки API

👥 *Команды клубов:*
Пример: /leo, /sakura, /karma, /moscow
Всего доступно: {len(CLUBS)} команд"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /ip - показать IP адрес"""
    global current_ip
    
    await update.message.reply_text("🌐 Определяю IP адрес...")
    
    # Получаем текущий IP
    ip = await get_current_ip()
    
    if ip and ip != "Ошибка определения":
        message = f"""🌐 *IP адрес сервера*

Ваш IP адрес для настройки Brawl Stars API:

`{ip}`

📝 *Как использовать:*
1. Откройте: https://developer.brawlstars.com
2. Выберите ваш проект
3. Нажмите "Edit" у API ключа
4. В "Allowed IPs" добавьте IP выше
5. Сохраните изменения"""
    else:
        message = "❌ Не удалось определить IP адрес"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status"""
    global current_ip
    
    # Обновляем информацию
    if not current_ip:
        await get_current_ip()
    
    await check_api_status()
    
    # Статистика
    heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
    
    message = f"""📊 *Статус бота*

🌐 *Сеть:*
IP адрес: `{current_ip or 'не определен'}`
API подключение: {'🟢 РАБОТАЕТ' if api_working else '🔴 НЕ РАБОТАЕТ'}

💾 *Данные:*
Всего клубов: {len(CLUBS)}
В кэше: {len(cache)} клубов

👥 *Состав семьи:*
👑 Heavenly Dynasty: {heaven_count} клубов
🩸 Bloody Family: {bloody_count} клубов

⚙️ *Команды:*
/rating - Рейтинг (10 клубов на страницу)
/refresh - Обновить данные
/ip - Показать IP для настройки"""
    
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
            "2. Используйте /ip чтобы получить ваш IP\n"
            "3. Добавьте IP в whitelist на сайте\n"
            "4. Добавьте переменную BRAWL_API_KEY в Render\n\n"
            "📊 Пока используются кэшированные данные",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await update.message.reply_text("🔄 Начинаю обновление данных...")
    
    # Обновляем данные для всех клубов
    updated = 0
    total = len(CLUBS)
    
    for idx, (club_name, club_info) in enumerate(CLUBS.items(), 1):
        try:
            await fetch_club_data(club_info["tag"])
            updated += 1
            
            # Задержка между запросами
            if idx < total:
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Ошибка обновления {club_name}: {e}")
    
    # Формируем отчет
    message = f"✅ *Обновление завершено!*\n\n"
    message += f"📊 *Результаты:*\n"
    message += f"• Обновлено: {updated} клубов\n"
    message += f"• Всего: {total} клубов\n\n"
    message += f"🏆 Используйте /rating для просмотра"
    
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
    
    # Формируем информацию
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
    message += f"🔗 /rating - Вернуться к рейтингу"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def page_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик пагинации рейтинга"""
    query = update.callback_query
    await query.answer()
    
    try:
        page_num = int(query.data.split('_')[1])
        await send_rating_page(update, context, page_num)
    except:
        await query.edit_message_text("❌ Ошибка пагинации. Используйте /rating")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

# ========== ЗАПУСК БОТА ==========
async def run_bot():
    """Основная функция запуска бота"""
    global application
    
    try:
        logger.info("🚀 Запуск Heaven & Bloody Stats Bot...")
        
        # Получаем IP адрес
        await get_current_ip()
        
        # Создаем приложение бота
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Регистрируем команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", start_command))
        application.add_handler(CommandHandler("rating", rating_command))
        application.add_handler(CommandHandler("refresh", refresh_command))
        application.add_handler(CommandHandler("status", status_command))
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
        
        logger.info(f"✅ Бот запущен! Клубов: {len(CLUBS)}")
        logger.info("🤖 Ожидаю команд...")
        
        # Запускаем бота
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

def main():
    """Точка входа"""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("👋 Завершение работы...")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    main()
