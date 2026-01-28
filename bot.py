import os
import json
import asyncio
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токены из переменных окружения Railway
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY')

# Проверяем токены
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не установлен в Railway Variables!")
    logger.error("Добавь TELEGRAM_TOKEN в настройки Railway")
    exit(1)

DATA_FILE = 'clubs_data.json'
CLUBS_PER_PAGE = 10

# ========== ФУНКЦИИ ДЛЯ ДАННЫХ ==========
def load_data():
    """Загружает данные из файла"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            logger.warning("Файл данных поврежден, создаю новые данные")
            return {'last_update': None, 'clubs': get_default_clubs()}
    else:
        logger.info("Файл данных не найден, создаю начальные данные")
        return {'last_update': None, 'clubs': get_default_clubs()}

def save_data(data):
    """Сохраняет данные в файл"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
    """Обновляет данные через API Brawl Stars"""
    logger.info("🔄 Начинаю обновление данных через API Brawl Stars...")
    data = load_data()
    updated = 0
    
    if not BRAWL_API_KEY:
        logger.error("❌ BRAWL_API_KEY не установлен! Не могу обновить данные.")
        return 0
    
    for i, club in enumerate(data['clubs']):
        try:
            clean_tag = club['tag'].strip('#').replace('#', '')
            url = f'https://api.brawlstars.com/v1/clubs/%23{clean_tag}'
            headers = {'Authorization': f'Bearer {BRAWL_API_KEY}', 'Accept': 'application/json'}
            
            logger.info(f"Запрос данных для {club['name']}...")
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
                logger.error(f"❌ {club['name']}: Ошибка доступа к API (403). Проверь BRAWL_API_KEY")
            elif response.status_code == 404:
                logger.warning(f"⚠️ {club['name']}: Клуб не найден (404). Возможно изменился тег?")
            else:
                logger.warning(f"⚠️ {club['name']}: Ошибка API {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ {club['name']}: Таймаут запроса (больше 15 секунд)")
        except Exception as e:
            logger.error(f"❌ {club['name']}: Ошибка: {str(e)}")
    
    data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)
    
    logger.info(f"✅ Обновление завершено! Обновлено {updated}/{len(data['clubs'])} клубов")
    return updated

# ========== КОМАНДЫ БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    data = load_data()
    
    # Считаем статистику
    heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
    bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
    total_trophies = sum(c['trophies'] for c in data['clubs'])
    
    text = f"""
<b>🏆 HEAVENLY DYNASTY BOT 🏆</b>
<i>Работает на Railway 24/7 🚂</i>

Привет, {update.effective_user.first_name}!

📊 <b>СТАТИСТИКА:</b>
• Всего клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Всего трофеев: <b>{format_num(total_trophies)}</b>
• Обновлено: <b>{data['last_update'] or 'Ещё не было'}</b>

📋 <b>ОСНОВНЫЕ КОМАНДЫ:</b>
/rating - Рейтинг всех клубов (постранично)
/search - Поиск клуба по названию
/update - Обновить данные через API
/help - Помощь по командам

🔍 <b>КОМАНДЫ ДЛЯ КАЖДОГО КЛУБА:</b>
/club_0 - Heaven Karma
/club_1 - Heaven Moscow
...
/club_24 - Bloody Cards

<i>Используй /rating чтобы увидеть все команды!</i>
    """
    
    keyboard = [
        [InlineKeyboardButton("📈 Рейтинг (страница 1)", callback_data="rating_0")],
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
    
    # Корректируем номер страницы
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1
    
    start_idx = page * CLUBS_PER_PAGE
    end_idx = min(start_idx + CLUBS_PER_PAGE, total_clubs)
    page_clubs = sorted_clubs[start_idx:end_idx]
    
    text = f"<b>🏆 РЕЙТИНГ КЛУБОВ (страница {page + 1}/{total_pages})</b>\n\n"
    
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
    else:
        text += f"\n📅 Данные ещё не обновлялись. Используй /update"
    
    # Создаем клавиатуру для навигации
    keyboard_buttons = []
    
    # Кнопки навигации по страницам
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"rating_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data=f"page_info"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"rating_{page+1}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    # Быстрые кнопки для первых страниц
    quick_pages = []
    for p in range(min(3, total_pages)):
        if p != page:
            quick_pages.append(InlineKeyboardButton(f"Стр. {p+1}", callback_data=f"rating_{p}"))
    
    if quick_pages:
        keyboard_buttons.append(quick_pages)
    
    # Дополнительные кнопки
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
        text = "❌ <b>Клуб не найден</b>\n\nИспользуйте /rating чтобы увидеть список всех клубов."
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

📊 <b>Детальная статистика:</b>
• Трофеи: <b>{format_num(club['trophies'])}</b> 🏆
• Участники: <b>{club['members']}/30</b> 👥
• Тег клуба: <code>{club['tag']}</code>
• Семья: <b>{club['family']}</b>
• ID клуба: <code>{club['id']}</code>

📈 <b>Позиция в рейтинге:</b> {rank} из {len(sorted_clubs)}

💡 <b>Быстрые команды:</b>
/rating - Весь рейтинг
/update - Обновить все данные
    """
    
    data = load_data()
    if data['last_update']:
        text += f"\n📅 <b>Обновлено:</b> {data['last_update']}"
    else:
        text += f"\n📅 <b>Данные не обновлялись.</b> Используй /update"
    
    # Кнопки навигации
    keyboard = [
        [InlineKeyboardButton("📈 Весь рейтинг", callback_data="rating_0")],
        [
            InlineKeyboardButton("◀️ Пред. клуб", callback_data=f"club_{max(0, club_id-1)}"),
            InlineKeyboardButton("След. клуб ▶️", callback_data=f"club_{min(len(data['clubs'])-1, club_id+1)}")
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
        # Извлекаем ID из команды /club_0, /club_1 и т.д.
        club_id = int(command.split('_')[1])
        await show_club(update, context, club_id)
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ <b>Неверная команда</b>\n\n"
            "Используйте команды вида:\n"
            "<code>/club_0</code> - Heaven Karma\n"
            "<code>/club_1</code> - Heaven Moscow\n"
            "...\n"
            "<code>/club_24</code> - Bloody Cards\n\n"
            "Полный список: /rating",
            parse_mode='HTML'
        )

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /update - обновление данных"""
    if update.callback_query:
        msg = update.callback_query.message
        await update.callback_query.edit_message_text("🔄 <b>Обновляю данные через API Brawl Stars...</b>\n\nЭто может занять до 30 секунд.", parse_mode='HTML')
    else:
        msg = await update.message.reply_text("🔄 <b>Обновляю данные через API Brawl Stars...</b>\n\nЭто может занять до 30 секунд.", parse_mode='HTML')
    
    try:
        if not BRAWL_API_KEY:
            error_text = "❌ <b>ОШИБКА: BRAWL_API_KEY не настроен</b>\n\nДобавь BRAWL_API_KEY в Variables на Railway!"
            if update.callback_query:
                await update.callback_query.edit_message_text(error_text, parse_mode='HTML')
            else:
                await msg.edit_text(error_text, parse_mode='HTML')
            return
        
        updated = await update_clubs_data()
        data = load_data()
        
        text = f"""
✅ <b>ДАННЫЕ УСПЕШНО ОБНОВЛЕНЫ!</b>

📊 <b>Результат:</b>
• Обновлено клубов: <b>{updated}/{len(data['clubs'])}</b>
• Время обновления: <b>{data['last_update']}</b>

🎯 <b>Что обновилось:</b>
• Трофеи каждого клуба
• Количество участников
• Время последнего обновления

<b>Используйте /rating для просмотра актуального рейтинга!</b>
        """
        
        keyboard = [
            [InlineKeyboardButton("📈 Смотреть рейтинг", callback_data="rating_0")],
            [InlineKeyboardButton("🏠 Главная", callback_data="home")]
        ]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await msg.edit_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        logger.error(f"Ошибка при обновлении: {str(e)}")
        error_text = f"❌ <b>ОШИБКА ПРИ ОБНОВЛЕНИИ</b>\n\n{str(e)[:200]}"
        if update.callback_query:
            await update.callback_query.edit_message_text(error_text, parse_mode='HTML')
        else:
            await msg.edit_text(error_text, parse_mode='HTML')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /search - поиск клуба"""
    await update.message.reply_text(
        "🔍 <b>Поиск клуба</b>\n\n"
        "Введите название клуба для поиска (можно часть названия):\n\n"
        "<i>Примеры:</i>\n"
        "<code>Karma</code> - найдет Heaven Karma\n"
        "<code>Blood</code> - найдет все Bloody клубы\n"
        "<code>Moscow</code> - найдет Heaven Moscow",
        parse_mode='HTML'
    )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстового поиска"""
    query = update.message.text.strip().lower()
    
    if not query or len(query) < 2:
        await update.message.reply_text("❌ Введите хотя бы 2 символа для поиска.")
        return
    
    data = load_data()
    results = []
    
    for club in data['clubs']:
        if query in club['name'].lower():
            results.append(club)
    
    if not results:
        await update.message.reply_text(f"🔍 По запросу '<i>{query}</i>' ничего не найдено.\n\nПопробуйте другой запрос или посмотрите /rating", parse_mode='HTML')
        return
    
    text = f"🔍 <b>Результаты поиска по '{query}'</b>\n\n"
    
    # Сортируем результаты по трофеям
    results_sorted = sorted(results, key=lambda x: x['trophies'], reverse=True)
    
    for i, club in enumerate(results_sorted[:10]):  # Ограничиваем 10 результатами
        emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
        text += f"{emoji} <b>{club['name']}</b>\n"
        text += f"🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n"
        text += f"📍 Детали: /club_{club['id']}\n"
        
        if i < len(results_sorted[:10]) - 1:
            text += "────\n"
    
    if len(results) > 10:
        text += f"\n⚠️ Показано 10 из {len(results)} найденных клубов"
    
    keyboard = [
        [InlineKeyboardButton("📈 Весь рейтинг", callback_data="rating_0")],
        [InlineKeyboardButton("🏠 Главная", callback_data="home")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - помощь"""
    text = """
<b>📚 ПОМОЩЬ ПО КОМАНДАМ</b>

🏠 <b>Основные команды:</b>
<code>/start</code> - Главное меню
<code>/help</code> - Эта справка
<code>/status</code> - Статус бота

📊 <b>Просмотр данных:</b>
<code>/rating</code> - Рейтинг всех клубов (по 10 на странице)
<code>/search</code> - Поиск клуба по названию
<code>/club_0</code> ... <code>/club_24</code> - Детали по каждому клубу

🔄 <b>Обновление данных:</b>
<code>/update</code> - Обновить данные через API Brawl Stars
(Нужен BRAWL_API_KEY в настройках Railway)

🔍 <b>Примеры использования:</b>
1. Посмотреть рейтинг: <code>/rating</code>
2. Найти клуб: <code>/search</code> → ввести "Karma"
3. Детали клуба: <code>/club_0</code>
4. Обновить данные: <code>/update</code>

🚂 <b>Техническая информация:</b>
• Бот работает на Railway 24/7
• Данные хранятся в файле clubs_data.json
• Обновление через официальное API Brawl Stars
    """
    
    keyboard = [
        [InlineKeyboardButton("🏠 Главная", callback_data="home")],
        [InlineKeyboardButton("📈 Рейтинг", callback_data="rating_0"),
         InlineKeyboardButton("🔄 Обновить", callback_data="update")]
    ]
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - статус бота"""
    data = load_data()
    sorted_clubs = get_sorted_clubs()
    
    # Считаем статистику
    heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
    bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
    total_trophies = sum(c['trophies'] for c in data['clubs'])
    
    # Топ-3 клуба
    top3 = sorted_clubs[:3] if len(sorted_clubs) >= 3 else sorted_clubs
    
    text = f"""
<b>📊 СТАТУС БОТА</b>

🏆 <b>Общая статистика:</b>
• Всего клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Всего трофеев: <b>{format_num(total_trophies)}</b>
• Последнее обновление: <b>{data['last_update'] or 'Ещё не было'}</b>

🥇 <b>Топ-3 клуба:</b>
"""
    
    for i, club in enumerate(top3, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        text += f"{medal} {club['name']} - {format_num(club['trophies'])} 🏆\n"
    
    text += f"""
⚙️ <b>Техническая информация:</b>
• Хостинг: <b>Railway 🚂</b>
• Статус: <b>Активен ✅</b>
• Режим работы: <b>24/7</b>
• Telegram API: <b>{'✅ Подключен' if TELEGRAM_TOKEN else '❌ Не настроен'}</b>
• Brawl Stars API: <b>{'✅ Настроен' if BRAWL_API_KEY else '❌ Не настроен'}</b>

💡 <b>Рекомендации:</b>
"""
    
    if not data['last_update']:
        text += "• Используйте <code>/update</code> для первого обновления данных\n"
    if not BRAWL_API_KEY:
        text += "• Добавьте BRAWL_API_KEY в Variables Railway для обновления данных\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Обновить данные", callback_data="update")],
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
            await query.edit_message_text("❌ Ошибка при загрузке клуба")
    elif data == 'page_info':
        await query.answer("Текущая страница", show_alert=False)

# ========== СОЗДАНИЕ ОБРАБОТЧИКОВ КОМАНД КЛУБОВ ==========
def create_club_command_handlers(application):
    """Создает обработчики для всех команд /club_0 ... /club_24"""
    data = load_data()
    
    for club in data['clubs']:
        # Создаем динамическую функцию для каждого клуба
        async def club_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, club_id=club['id']):
            await show_club(update, context, club_id)
        
        # Добавляем обработчик команды
        application.add_handler(CommandHandler(f"club_{club['id']}", club_handler))

# ========== ЗАПУСК БОТА ==========
async def main():
    """Основная функция запуска бота"""
    print("=" * 60)
    print("🤖 HEAVENLY DYNASTY TELEGRAM BOT")
    print("🚂 Запускается на Railway...")
    print("=" * 60)
    
    # Проверяем токен
    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен!")
        print("✅ РЕШЕНИЕ: Добавь в Railway Variables:")
        print("   TELEGRAM_TOKEN = 8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU")
        print("=" * 60)
        return
    
    print(f"✅ Токен Telegram: {TELEGRAM_TOKEN[:10]}...")
    print(f"✅ Ключ API: {'Установлен' if BRAWL_API_KEY else 'Не установлен'}")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем основные обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rating", lambda u, c: rating(u, c, 0)))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("update", update_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Добавляем обработчики для всех клубов
    create_club_command_handlers(application)
    
    # Добавляем обработчик текстовых сообщений (для поиска)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    
    # Добавляем обработчик inline-кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Все обработчики команд добавлены")
    print("✅ Бот готов к работе!")
    print("=" * 60)
    print("📱 Открой Telegram и отправь боту /start")
    print("=" * 60)
    
    # Запускаем бота
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Запускаем асинхронную main функцию
    asyncio.run(main())
