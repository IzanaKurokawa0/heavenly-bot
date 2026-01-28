import os
import json
import asyncio
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ========== КОНФИГУРАЦИЯ ==========
TELEGRAM_TOKEN = "8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU"
BRAWL_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyMiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE2MSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA"
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Файлы
DATA_FILE = 'clubs_data.json'
CLUBS_PER_PAGE = 10

# ========== УТИЛИТЫ ==========
def load_data():
    """Загружает данные из файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'last_update': None, 'clubs': get_default_clubs()}
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return {'last_update': None, 'clubs': get_default_clubs()}

def save_data(data):
    """Сохраняет данные в файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Данные сохранены")
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

def get_default_clubs():
    """Возвращает список клубов по умолчанию"""
    return [
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

def format_num(n):
    """Форматирует числа с разделителями"""
    return f'{int(n):,}'.replace(',', '.')

def get_sorted_clubs():
    """Возвращает отсортированные клубы"""
    data = load_data()
    return sorted(data['clubs'], key=lambda x: x['trophies'], reverse=True)

def get_club_by_id(club_id):
    """Находит клуб по ID"""
    data = load_data()
    for club in data['clubs']:
        if club['id'] == club_id:
            return club
    return None

# ========== API ОБНОВЛЕНИЕ ==========
async def update_clubs_data():
    """Обновляет данные через Cloudflare Proxy"""
    logger.info("Обновление данных...")
    data = load_data()
    updated = 0
    
    if not BRAWL_API_KEY:
        logger.error("API ключ не установлен!")
        return 0
    
    for i, club in enumerate(data['clubs']):
        try:
            clean_tag = club['tag'].strip('#').replace('#', '')
            url = f'{BRAWL_API_PROXY}/v1/clubs/%23{clean_tag}'
            headers = {
                'Authorization': f'Bearer {BRAWL_API_KEY}',
                'Accept': 'application/json',
                'User-Agent': 'HeavenlyBot/1.0'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                club_data = response.json()
                old = data['clubs'][i]['trophies']
                new = club_data.get('trophies', old)
                data['clubs'][i]['trophies'] = new
                data['clubs'][i]['members'] = len(club_data.get('memberList', []))
                updated += 1
                logger.info(f"{club['name']}: {old} → {new}")
            else:
                logger.warning(f"{club['name']}: Ошибка {response.status_code}")
            
            await asyncio.sleep(0.3)
            
        except Exception as e:
            logger.error(f"{club['name']}: {e}")
    
    data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)
    logger.info(f"Обновлено {updated} клубов")
    return updated

# ========== КОМАНДЫ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    data = load_data()
    heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
    bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
    total = sum(c['trophies'] for c in data['clubs'])
    
    text = f"""
<b>🏆 HEAVENLY DYNASTY BOT 🏆</b>

Привет, {update.effective_user.first_name}!

📊 <b>Статистика:</b>
• Клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Трофеев: <b>{format_num(total)}</b>
• Обновлено: <b>{data['last_update'] or 'Нет'}</b>

📋 <b>Команды:</b>
/rating - Рейтинг клубов
/search - Поиск клуба
/update - Обновить данные
/help - Помощь
/status - Статус
    """
    
    keyboard = [
        [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0")],
        [InlineKeyboardButton("🔍 Поиск", callback_data="search"),
         InlineKeyboardButton("🔄 Обновить", callback_data="update")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help"),
         InlineKeyboardButton("📊 Статус", callback_data="status")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE, page=0):
    """Команда /rating"""
    clubs = get_sorted_clubs()
    total = len(clubs)
    pages = (total + CLUBS_PER_PAGE - 1) // CLUBS_PER_PAGE
    page = max(0, min(page, pages - 1))
    
    start = page * CLUBS_PER_PAGE
    end = min(start + CLUBS_PER_PAGE, total)
    page_clubs = clubs[start:end]
    
    text = f"<b>🏆 РЕЙТИНГ КЛУБОВ (стр. {page+1}/{pages})</b>\n\n"
    
    for idx, club in enumerate(page_clubs):
        rank = start + idx + 1
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
        emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
        
        text += f"{medal} {emoji} <b>{club['name']}</b>\n"
        text += f"   🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n"
        text += f"   📍 /club_{club['id']}\n"
        if idx < len(page_clubs) - 1:
            text += "────\n"
    
    data = load_data()
    if data['last_update']:
        text += f"\n📅 Обновлено: {data['last_update']}"
    
    # Кнопки навигации
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("◀️", callback_data=f"rating_{page-1}"))
    buttons.append(InlineKeyboardButton(f"{page+1}/{pages}", callback_data="page_info"))
    if page < pages - 1:
        buttons.append(InlineKeyboardButton("▶️", callback_data=f"rating_{page+1}"))
    
    keyboard = [buttons] if buttons else []
    keyboard.append([
        InlineKeyboardButton("🔍 Поиск", callback_data="search"),
        InlineKeyboardButton("🔄 Обновить", callback_data="update")
    ])
    keyboard.append([InlineKeyboardButton("🏠 Главная", callback_data="home")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)

async def show_club(update: Update, context: ContextTypes.DEFAULT_TYPE, club_id: int):
    """Показывает информацию о клубе"""
    club = get_club_by_id(club_id)
    if not club:
        await (update.callback_query or update.message).reply_text("❌ Клуб не найден", parse_mode='HTML')
        return
    
    clubs = get_sorted_clubs()
    rank = next((i+1 for i, c in enumerate(clubs) if c['id'] == club_id), None)
    
    emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    
    text = f"""
{emoji} <b>{club['name']}</b> {medal}

📊 <b>Статистика:</b>
• Трофеи: <b>{format_num(club['trophies'])}</b> 🏆
• Участники: <b>{club['members']}/30</b> 👥
• Тег: <code>{club['tag']}</code>
• Семья: <b>{club['family']}</b>
• Позиция: <b>{rank} из {len(clubs)}</b>
    """
    
    data = load_data()
    if data['last_update']:
        text += f"\n📅 <b>Обновлено:</b> {data['last_update']}"
    
    keyboard = [
        [InlineKeyboardButton("📈 Весь рейтинг", callback_data="rating_0")],
        [
            InlineKeyboardButton("◀️ Пред.", callback_data=f"club_{max(0, club_id-1)}"),
            InlineKeyboardButton("След. ▶️", callback_data=f"club_{min(24, club_id+1)}")
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

async def club_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /club_X"""
    try:
        club_id = int(update.message.text.split('_')[1])
        await show_club(update, context, club_id)
    except:
        await update.message.reply_text("❌ Используйте /club_0 ... /club_24")

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /update"""
    msg = update.callback_query.message if update.callback_query else await update.message.reply_text("🔄 Обновление...")
    
    if update.callback_query:
        await update.callback_query.edit_message_text("🔄 <b>Обновляю данные...</b>\n\nОжидайте ~20 секунд", parse_mode='HTML')
    else:
        msg = await update.message.reply_text("🔄 <b>Обновляю данные...</b>\n\nОжидайте ~20 секунд", parse_mode='HTML')
    
    try:
        updated = await update_clubs_data()
        data = load_data()
        
        if updated > 0:
            text = f"""
✅ <b>ДАННЫЕ ОБНОВЛЕНЫ!</b>

📊 <b>Результат:</b>
• Обновлено: <b>{updated}/25</b> клубов
• Время: <b>{data['last_update']}</b>

🎯 <b>Используйте /rating</b>
            """
        else:
            text = f"""
⚠️ <b>ОБНОВЛЕНИЕ НЕ УДАЛОСЬ</b>

💡 Проверьте:
• IP 104.21.92.161 в белом списке
• API ключ активен

📅 <b>Текущее время:</b> {data['last_update']}
            """
        
        keyboard = [
            [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0")],
            [InlineKeyboardButton("🏠 Главная", callback_data="home")]
        ]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='HTML', 
                                                         reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await msg.edit_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        error = f"❌ <b>ОШИБКА:</b>\n\n{str(e)[:100]}"
        if update.callback_query:
            await update.callback_query.edit_message_text(error, parse_mode='HTML')
        else:
            await msg.edit_text(error, parse_mode='HTML')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search"""
    await update.message.reply_text("🔍 <b>Поиск клуба</b>\n\nВведите название:", parse_mode='HTML')

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик поиска"""
    query = update.message.text.lower().strip()
    if len(query) < 2:
        await update.message.reply_text("❌ Минимум 2 символа")
        return
    
    clubs = [c for c in load_data()['clubs'] if query in c['name'].lower()]
    
    if not clubs:
        await update.message.reply_text(f"🔍 По '{query}' ничего не найдено")
        return
    
    text = f"🔍 <b>Результаты по '{query}':</b>\n\n"
    clubs.sort(key=lambda x: x['trophies'], reverse=True)
    
    for club in clubs[:10]:
        emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
        text += f"{emoji} <b>{club['name']}</b>\n"
        text += f"🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n"
        text += f"📍 /club_{club['id']}\n────\n"
    
    if len(clubs) > 10:
        text += f"\n⚠️ Показано 10 из {len(clubs)}"
    
    keyboard = [
        [InlineKeyboardButton("📈 Весь рейтинг", callback_data="rating_0")],
        [InlineKeyboardButton("🏠 Главная", callback_data="home")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    text = """
<b>📚 ПОМОЩЬ ПО КОМАНДАМ</b>

🏠 <b>Основные:</b>
/start - Главное меню
/help - Эта справка
/status - Статус бота

📊 <b>Просмотр:</b>
/rating - Рейтинг всех клубов
/search - Поиск клуба
/club_0 ... /club_24 - Информация о клубе

🔄 <b>Обновление:</b>
/update - Обновить данные через API

🌐 <b>Техническое:</b>
• Cloudflare Proxy
• Работает 24/7 на Render
• API обновление через прокси
    """
    
    keyboard = [
        [InlineKeyboardButton("🏠 Главная", callback_data="home")],
        [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status"""
    data = load_data()
    
    text = f"""
<b>📊 СТАТУС БОТА</b>

🏆 <b>Статистика:</b>
• Клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')}</b>
• Bloody: <b>{sum(1 for c in data['clubs'] if c['family'] == 'Bloody')}</b>
• Обновлено: <b>{data['last_update'] or 'Нет'}</b>

🌐 <b>Техническое:</b>
• Прокси: <b>Cloudflare ✅</b>
• API ключ: <b>{'✅ Активен' if BRAWL_API_KEY else '❌ Нет'}</b>
• Хостинг: <b>Render.com</b>
• IP белый список: <b>104.21.92.161</b>

💡 <b>Для работы /update:</b>
1. IP выше должен быть в developer.brawlstars.com
2. API ключ должен быть активен
    """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Обновить", callback_data="update")],
        [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0"),
         InlineKeyboardButton("🏠 Главная", callback_data="home")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# ========== ОБРАБОТЧИК КНОПОК ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline-кнопок"""
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
        await query.answer(f"Страница", show_alert=False)

# ========== ОСНОВНОЙ ЗАПУСК ==========
def main():
    """Запуск бота"""
    print("=" * 60)
    print("🤖 HEAVENLY DYNASTY BOT - ЗАПУСК")
    print("=" * 60)
    
    # Проверка файла данных
    if not os.path.exists(DATA_FILE):
        print("📂 Создаю файл данных...")
        save_data({'last_update': None, 'clubs': get_default_clubs()})
        print("✅ Файл создан")
    
    print(f"🔑 API ключ: {'✅' if BRAWL_API_KEY else '❌'}")
    print(f"🤖 Токен Telegram: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"🌐 Прокси: {BRAWL_API_PROXY}")
    print("=" * 60)
    
    try:
        # Создаём приложение
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики команд
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("rating", lambda u, c: rating(u, c, 0)))
        app.add_handler(CommandHandler("update", update_command))
        app.add_handler(CommandHandler("search", search_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("status", status_command))
        
        # Добавляем обработчики для каждого клуба
        for i in range(25):
            app.add_handler(CommandHandler(f"club_{i}", 
                lambda u, c, club_id=i: show_club(u, c, club_id)))
        
        # Обработчики текста и кнопок
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Все обработчики добавлены")
        print("✅ Бот запускается...")
        print("=" * 60)
        print("📱 Открой Telegram и напиши /start")
        print("=" * 60)
        
        # Запускаем бота
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        print("🔄 Перезапуск через 10 секунд...")
        import time
        time.sleep(10)
        main()

if __name__ == '__main__':
    main()
