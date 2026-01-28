import os
import sys
import json
import asyncio
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ========== ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК ==========
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    """Глобальный обработчик исключений для Render"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print("=" * 60)
    print("❌ КРИТИЧЕСКАЯ ОШИБКА:")
    print("=" * 60)
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("=" * 60)

sys.excepthook = handle_exception

# ========== НАСТРОЙКА ==========
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyMiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE2MSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Проверяем ключи
print("=" * 60)
print("🔑 ПРОВЕРКА КЛЮЧЕЙ:")
print(f"Telegram Token: {'✅ Установлен' if TELEGRAM_TOKEN else '❌ Отсутствует'}")
print(f"Brawl Stars API Key: {'✅ Установлен' if BRAWL_API_KEY else '❌ Отсутствует'}")
print(f"Cloudflare Proxy: {BRAWL_API_PROXY}")
print("=" * 60)

# Файл данных
DATA_FILE = 'clubs_data.json'
CLUBS_PER_PAGE = 10

# ========== ФУНКЦИИ ДЛЯ ДАННЫХ ==========
def load_data():
    """Загружает данные из файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            logger.info("📂 Файл данных не найден, создаю начальные данные")
            return {'last_update': None, 'clubs': get_default_clubs()}
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки данных: {e}")
        return {'last_update': None, 'clubs': get_default_clubs()}

def save_data(data):
    """Сохраняет данные в файл"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Данные сохранены в {DATA_FILE}")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения данных: {e}")

def get_default_clubs():
    """Возвращает список клубов по умолчанию"""
    clubs = [
        {'id': 0, 'name': 'Heaven Karma', 'tag': '#JYGVQR89', 'trophies': 55000, 'members': 30, 'family': 'Heavenly'},
        {'id': 1, 'name': 'Heaven Moscow', 'tag': '#JG2GPJ9Q', 'trophies': 54800, 'members': 29, 'family': 'Heavenly'},
        {'id': 2, 'name': 'Heaven Fortress', 'tag': '#C0JJC0L2', 'trophies': 52100, 'members': 28, 'family': 'Heavenly'},
        {'id': 3, 'name': 'Heaven Hell', 'tag': '#C0QQ8RV0', 'trophies': 51900, 'members': 30, 'family': 'Heavenly'},
        {'id': 4, 'name': 'Heaven KE', 'tag': '#2Q2QVYGU8', 'trophies': 51500, 'members': 27, 'family': 'Heavenly'},
        {'id': 5, 'name': 'Heaven Leo', 'tag': '#2C29U8Q8P', 'trophies': 50000, 'members': 26, 'family': 'Heavenly'},
        {'id': 6, 'name': 'Heaven Cucumber', 'tag': '#JG9U8U82', 'trophies': 49000, 'members': 28, 'family': 'Heavenly'},
        {'id': 7, 'name': 'Heaven Temple', 'tag': '#80LPG8V8L', 'trophies': 48500, 'members': 29, 'family': 'Heavenly'},
        {'id': 8, 'name': 'Heaven Kingdom', 'tag': '#2C2YLRCCU', 'trophies': 48000, 'members': 30, 'family': 'Heavenly'},
        {'id': 9, 'name': 'Heaven Dream', 'tag': '#2LQ2UV0LJ', 'trophies': 47500, 'members': 28, 'family': 'Heavenly'},
        {'id': 10, 'name': 'Heaven Winter', 'tag': '#2LCUY0Q8G', 'trophies': 47000, 'members': 27, 'family': 'Heavenly'},
        {'id': 11, 'name': 'Heaven Envoy', 'tag': '#JYR0YRR2', 'trophies': 46500, 'members': 29, 'family': 'Heavenly'},
        {'id': 12, 'name': 'Heaven Dominion', 'tag': '#80LQRCR0J', 'trophies': 46000, 'members': 28, 'family': 'Heavenly'},
        {'id': 13, 'name': 'Heaven Sakura', 'tag': '#2Q082VC08', 'trophies': 45500, 'members': 30, 'family': 'Heavenly'},
        {'id': 14, 'name': 'Heaven Vinland', 'tag': '#2VJRV89JG', 'trophies': 45000, 'members': 29, 'family': 'Heavenly'},
        {'id': 15, 'name': 'Heaven Infinity', 'tag': '#2VCLRRYCV', 'trophies': 44500, 'members': 28, 'family': 'Heavenly'},
        {'id': 16, 'name': 'Heaven Reverse', 'tag': '#JGYRPPPY', 'trophies': 44000, 'members': 27, 'family': 'Heavenly'},
        {'id': 17, 'name': 'Heaven Tomatoes', 'tag': '#2LC9JVQLJ', 'trophies': 43500, 'members': 26, 'family': 'Heavenly'},
        {'id': 18, 'name': 'Heaven Thunder', 'tag': '#2CLQ2RPL8', 'trophies': 43000, 'members': 28, 'family': 'Heavenly'},
        {'id': 19, 'name': 'Heaven Curse', 'tag': '#2LGRGCL9U', 'trophies': 42500, 'members': 29, 'family': 'Heavenly'},
        {'id': 20, 'name': 'Bloody Legion', 'tag': '#2YPYJC88J', 'trophies': 2300000, 'members': 30, 'family': 'Bloody'},
        {'id': 21, 'name': 'Bloody Justice', 'tag': '#2VCU8J9CV', 'trophies': 1905000, 'members': 30, 'family': 'Bloody'},
        {'id': 22, 'name': 'Bloody Valley', 'tag': '#2VUURGQLR', 'trophies': 1890000, 'members': 29, 'family': 'Bloody'},
        {'id': 23, 'name': 'Bloody Requiem', 'tag': '#2Y89QRGQU', 'trophies': 1667972, 'members': 28, 'family': 'Bloody'},
        {'id': 24, 'name': 'Bloody Cards', 'tag': '#2JQURGVRG', 'trophies': 866127, 'members': 27, 'family': 'Bloody'}
    ]
    return clubs

def format_num(n):
    """Форматирует числа с разделителями"""
    return f'{int(n):,}'.replace(',', '.')

def get_sorted_clubs():
    """Возвращает отсортированные клубы по трофеям"""
    data = load_data()
    return sorted(data['clubs'], key=lambda x: x['trophies'], reverse=True)

def get_club_by_id(club_id):
    """Находит клуб по ID"""
    data = load_data()
    for club in data['clubs']:
        if club['id'] == club_id:
            return club
    return None

# ========== ОБНОВЛЕНИЕ ДАННЫХ ==========
async def update_clubs_data():
    """Обновляет данные через Cloudflare Proxy"""
    logger.info("🔄 Начинаю обновление данных через Cloudflare Proxy...")
    
    data = load_data()
    updated = 0
    
    if not BRAWL_API_KEY:
        logger.error("❌ BRAWL_API_KEY не установлен!")
        return 0
    
    for i, club in enumerate(data['clubs']):
        try:
            clean_tag = club['tag'].strip('#').replace('#', '')
            
            # Используем Cloudflare Worker прокси
            url = f'{BRAWL_API_PROXY}/v1/clubs/%23{clean_tag}'
            
            headers = {
                'Authorization': f'Bearer {BRAWL_API_KEY}',
                'Accept': 'application/json',
                'User-Agent': 'HeavenlyDynastyBot/1.0'
            }
            
            logger.info(f"📡 Запрос для {club['name']}...")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                club_data = response.json()
                old_trophies = data['clubs'][i]['trophies']
                new_trophies = club_data.get('trophies', old_trophies)
                data['clubs'][i]['trophies'] = new_trophies
                data['clubs'][i]['members'] = len(club_data.get('memberList', []))
                updated += 1
                logger.info(f"✅ {club['name']}: {old_trophies} → {new_trophies} трофеев")
            elif response.status_code == 403:
                logger.error(f"❌ {club['name']}: Ошибка 403")
                logger.info(f"💡 IP {response.url} не в белом списке")
            elif response.status_code == 404:
                logger.warning(f"⚠️ {club['name']}: Клуб не найден")
            else:
                logger.warning(f"⚠️ {club['name']}: Ошибка {response.status_code}")
                
            await asyncio.sleep(0.5)
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ {club['name']}: Таймаут")
        except Exception as e:
            logger.error(f"❌ {club['name']}: {str(e)}")
    
    data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)
    
    logger.info(f"✅ Обновлено {updated}/{len(data['clubs'])} клубов")
    return updated

# ========== КОМАНДЫ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    data = load_data()
    
    heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
    bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
    total_trophies = sum(c['trophies'] for c in data['clubs'])
    
    text = f"""
<b>🏆 HEAVENLY DYNASTY BOT v2.0 🏆</b>

Привет, {update.effective_user.first_name}!

📊 <b>СТАТИСТИКА:</b>
• Всего клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Всего трофеев: <b>{format_num(total_trophies)}</b>
• Обновлено: <b>{data['last_update'] or 'Ещё не было'}</b>
• API: <b>Cloudflare Proxy ✅</b>

📋 <b>КОМАНДЫ:</b>
/rating - Рейтинг клубов
/search - Поиск клуба
/update - Обновить данные
/help - Помощь
/status - Статус бота

⚡ <b>Быстрые команды:</b>
/club_0 - Heaven Karma
/club_1 - Heaven Moscow
...
/club_24 - Bloody Cards
    """
    
    keyboard = [
        [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0")],
        [InlineKeyboardButton("🔍 Поиск", callback_data="search"),
         InlineKeyboardButton("🔄 Обновить", callback_data="update")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help"),
         InlineKeyboardButton("📊 Статус", callback_data="status")]
    ]
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0):
    """Команда /rating - рейтинг с пагинацией"""
    sorted_clubs = get_sorted_clubs()
    total_clubs = len(sorted_clubs)
    total_pages = (total_clubs + CLUBS_PER_PAGE - 1) // CLUBS_PER_PAGE
    
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * CLUBS_PER_PAGE
    end_idx = min(start_idx + CLUBS_PER_PAGE, total_clubs)
    page_clubs = sorted_clubs[start_idx:end_idx]
    
    text = f"<b>🏆 РЕЙТИНГ КЛУБОВ (стр. {page + 1}/{total_pages})</b>\n\n"
    
    for idx, club in enumerate(page_clubs):
        global_rank = start_idx + idx + 1
        emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
        medal = "🥇" if global_rank == 1 else "🥈" if global_rank == 2 else "🥉" if global_rank == 3 else f"{global_rank}."
        
        text += f"{medal} {emoji} <b>{club['name']}</b>\n"
        text += f"   🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n"
        text += f"   📍 Детали: /club_{club['id']}\n"
        
        if idx < len(page_clubs) - 1:
            text += "────\n"
    
    data = load_data()
    if data['last_update']:
        text += f"\n📅 Обновлено: {data['last_update']}"
    
    # Навигация
    keyboard_buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"rating_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="page_info"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"rating_{page+1}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard_buttons.append([
        InlineKeyboardButton("🔍 Поиск", callback_data="search"),
        InlineKeyboardButton("🔄 Обновить", callback_data="update")
    ])
    
    keyboard_buttons.append([
        InlineKeyboardButton("🏠 Главная", callback_data="home")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard_buttons)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_club(update: Update, context: ContextTypes.DEFAULT_TYPE, club_id: int):
    """Показывает информацию о конкретном клубе"""
    club = get_club_by_id(club_id)
    
    if not club:
        text = "❌ Клуб не найден"
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='HTML')
        else:
            await update.message.reply_text(text, parse_mode='HTML')
        return
    
    # Находим позицию в рейтинге
    sorted_clubs = get_sorted_clubs()
    rank = None
    for i, c in enumerate(sorted_clubs, 1):
        if c['id'] == club['id']:
            rank = i
            break
    
    emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    
    text = f"""
{emoji} <b>{club['name']}</b> {medal}

📊 <b>Статистика:</b>
• Трофеи: <b>{format_num(club['trophies'])}</b> 🏆
• Участники: <b>{club['members']}/30</b> 👥
• Тег: <code>{club['tag']}</code>
• Семья: <b>{club['family']}</b>

📈 <b>Позиция:</b> {rank} из {len(sorted_clubs)}
    """
    
    data = load_data()
    if data['last_update']:
        text += f"\n📅 <b>Обновлено:</b> {data['last_update']}"
    
    # Кнопки навигации
    keyboard = [
        [InlineKeyboardButton("📈 Весь рейтинг", callback_data="rating_0")],
        [
            InlineKeyboardButton("◀️ Пред.", callback_data=f"club_{max(0, club_id-1)}"),
            InlineKeyboardButton("След. ▶️", callback_data=f"club_{min(len(data['clubs'])-1, club_id+1)}")
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data="update"),
            InlineKeyboardButton("🏠 Главная", callback_data="home")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def club_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд вида /club_0, /club_1 и т.д."""
    command = update.message.text
    try:
        club_id = int(command.split('_')[1])
        await show_club(update, context, club_id)
    except:
        await update.message.reply_text(
            "❌ Используйте /club_0, /club_1, ... /club_24\nПолный список: /rating",
            parse_mode='HTML'
        )

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /update - обновление данных"""
    if update.callback_query:
        msg = update.callback_query.message
        await update.callback_query.edit_message_text(
            "🔄 <b>Обновляю данные через Cloudflare Proxy...</b>\n\nОжидайте ~30 секунд",
            parse_mode='HTML'
        )
    else:
        msg = await update.message.reply_text(
            "🔄 <b>Обновляю данные через Cloudflare Proxy...</b>\n\nОжидайте ~30 секунд",
            parse_mode='HTML'
        )
    
    try:
        updated = await update_clubs_data()
        data = load_data()
        
        if updated > 0:
            text = f"""
✅ <b>ДАННЫЕ ОБНОВЛЕНЫ!</b>

📊 <b>Результат:</b>
• Обновлено клубов: <b>{updated}/{len(data['clubs'])}</b>
• Время: <b>{data['last_update']}</b>
• Прокси: <b>Cloudflare ✅</b>

🎯 <b>Используйте /rating для просмотра!</b>
            """
        else:
            text = f"""
⚠️ <b>ОБНОВЛЕНИЕ НЕ УДАЛОСЬ</b>

💡 <b>Возможные причины:</b>
• API ключ неверный
• IP Cloudflare не в белом списке
• Проблемы с API Brawl Stars

📅 <b>Текущее время:</b> {data['last_update']}
            """
        
        keyboard = [
            [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0")],
            [InlineKeyboardButton("🏠 Главная", callback_data="home")]
        ]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await msg.edit_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        error_text = f"❌ <b>ОШИБКА:</b>\n\n{str(e)[:200]}"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text, parse_mode='HTML')
        else:
            await msg.edit_text(error_text, parse_mode='HTML')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search - поиск клуба"""
    await update.message.reply_text(
        "🔍 <b>Поиск клуба</b>\n\nВведите название клуба для поиска:",
        parse_mode='HTML'
    )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстового поиска"""
    query = update.message.text.strip().lower()
    
    if not query or len(query) < 2:
        await update.message.reply_text("❌ Введите хотя бы 2 символа")
        return
    
    data = load_data()
    results = []
    
    for club in data['clubs']:
        if query in club['name'].lower():
            results.append(club)
    
    if not results:
        await update.message.reply_text(f"🔍 По запросу '{query}' ничего не найдено", parse_mode='HTML')
        return
    
    text = f"🔍 <b>Результаты по '{query}':</b>\n\n"
    
    results_sorted = sorted(results, key=lambda x: x['trophies'], reverse=True)
    
    for club in results_sorted[:10]:
        emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
        text += f"{emoji} <b>{club['name']}</b>\n"
        text += f"🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n"
        text += f"📍 /club_{club['id']}\n"
        text += "────\n"
    
    if len(results) > 10:
        text += f"\n⚠️ Показано 10 из {len(results)}"
    
    keyboard = [
        [InlineKeyboardButton("📈 Весь рейтинг", callback_data="rating_0")],
        [InlineKeyboardButton("🏠 Главная", callback_data="home")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - помощь"""
    text = """
<b>📚 ПОМОЩЬ ПО КОМАНДАМ</b>

🏠 <b>Основные:</b>
/start - Главное меню
/help - Эта справка
/status - Статус бота

📊 <b>Просмотр:</b>
/rating - Рейтинг клубов
/search - Поиск клуба
/club_0 ... /club_24 - Детали клуба

🔄 <b>Обновление:</b>
/update - Обновить данные через API

🌐 <b>Техническое:</b>
• Использует Cloudflare Proxy
• Статический IP: 104.21.92.161
• Работает 24/7
    """
    
    keyboard = [
        [InlineKeyboardButton("🏠 Главная", callback_data="home")],
        [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - статус бота"""
    data = load_data()
    
    heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
    bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
    total_trophies = sum(c['trophies'] for c in data['clubs'])
    
    text = f"""
<b>📊 СТАТУС БОТА</b>

🏆 <b>Статистика:</b>
• Всего клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Трофеев: <b>{format_num(total_trophies)}</b>
• Обновлено: <b>{data['last_update'] or 'Нет'}</b>

🌐 <b>Техническое:</b>
• Прокси: <b>Cloudflare ✅</b>
• API ключ: <b>{'✅ Установлен' if BRAWL_API_KEY else '❌ Нет'}</b>
• Хостинг: <b>Render.com</b>
• Работает: <b>24/7</b>

💡 <b>IP для белого списка:</b>
<code>104.21.92.161</code>
    """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Обновить", callback_data="update")],
        [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0"),
         InlineKeyboardButton("🏠 Главная", callback_data="home")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ========== ОБРАБОТЧИК КНОПОК ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'home':
        await start(update, context)
    elif data == 'help':
        await help_command(update, context)
    elif data == 'status':
        await status_command(update, context)
    elif data == 'search':
        await search_command(update, context)
    elif data == 'update':
        await update_command(update, context)
    elif data.startswith('rating_'):
        try:
            page = int(data.split('_')[1])
            await rating(update, context, page)
        except:
            await rating(update, context, 0)
    elif data.startswith('club_'):
        try:
            club_id = int(data.split('_')[1])
            await show_club(update, context, club_id)
        except:
            await query.edit_message_text("❌ Ошибка")
    elif data == 'page_info':
        await query.answer("Страница", show_alert=False)

# ========== СОЗДАНИЕ ОБРАБОТЧИКОВ КОМАНД КЛУБОВ ==========
def create_club_command_handlers(application):
    """Создает обработчики для всех команд /club_0 ... /club_24"""
    data = load_data()
    
    for club in data['clubs']:
        async def club_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, club_id=club['id']):
            await show_club(update, context, club_id)
        
        application.add_handler(CommandHandler(f"club_{club['id']}", club_handler))

# ========== ЗАПУСК БОТА ==========
async def main():
    """Основная функция запуска бота"""
    print("=" * 60)
    print("🤖 HEAVENLY DYNASTY BOT v2.0")
    print("🌐 Cloudflare Proxy: heavenly-brawl-proxy.workers.dev")
    print("🔑 API Key: Установлен" if BRAWL_API_KEY else "🔑 API Key: Требуется")
    print("=" * 60)
    
    # Проверка обязательных переменных
    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен!")
        print("💡 Добавьте TELEGRAM_TOKEN в переменные окружения Render")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rating", lambda u, c: rating(u, c, 0)))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("update", update_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Добавляем обработчики для всех клубов
    create_club_command_handlers(application)
    
    # Обработчики текста и кнопок
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Все обработчики добавлены")
    print("✅ Бот готов к работе!")
    print("=" * 60)
    print("📱 Открой Telegram и напиши /start")
    print("=" * 60)
    
    # Запускаем бота
    try:
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        traceback.print_exc()
        print("🔄 Перезапуск через 10 секунд...")
        await asyncio.sleep(10)
        await main()

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
from flask import Flask
import threading
import time

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🤖 Heavenly Dynasty Bot is running!"

@flask_app.route('/health')
def health():
    return "OK", 200

@flask_app.route('/test')
def test():
    return {
        "status": "running",
        "bot": "Heavenly Dynasty Bot v2.0",
        "telegram_token": "set" if TELEGRAM_TOKEN else "not set"
    }

def run_web():
    """Запускает Flask сервер в отдельном потоке"""
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Запуск веб-сервера на порту {port}")
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== ТОЧКА ВХОДА ДЛЯ RENDER ==========
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ЗАПУСК НА RENDER.COM")
    print("=" * 60)
    
    # Запускаем веб-сервер для health checks
    print("🌐 Запускаю Flask сервер...")
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    time.sleep(3)
    
    print("🤖 Запускаю Telegram бота...")
    
    # Запускаем бота
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        traceback.print_exc()
