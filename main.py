import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode
import aiohttp
import asyncio
import json

# ============== КОНФИГУРАЦИЯ ==============
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtkZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyIiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE1OjQ0MyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

CLUBS_PER_PAGE = 10
CLUBS_DATA = [
    {"name": "Heaven Karma", "tag": "#JYGVQR89"},
    {"name": "Heaven Moscow", "tag": "#JG2GPJ9Q"},
    {"name": "Heaven Fortress", "tag": "#C0JJC0L2"},
    {"name": "Heaven Hell", "tag": "#C0QQ8RV0"},
    {"name": "Heaven KE", "tag": "#2Q2QVYGU8"},
    {"name": "Heaven Leo", "tag": "#2C29U8Q8P"},
    {"name": "Heaven Cucumber", "tag": "#JG9U8U82"},
    {"name": "Heaven Temple", "tag": "#80LPG8V8L"},
    {"name": "Heaven Kingdom", "tag": "#2C2YLRCCU"},
    {"name": "Heaven Dream", "tag": "#2LQ2UV0LJ"},
    {"name": "Heaven Winter", "tag": "#2LCUY0Q8G"},
    {"name": "Heaven Envoy", "tag": "#JYR0YRR2"},
    {"name": "Heaven Dominion", "tag": "#80LQRCR0J"},
    {"name": "Heaven Sakura", "tag": "#2Q082VC08"},
    {"name": "Heaven Vinland", "tag": "#2VJRV89JG"},
    {"name": "Heaven Infinity", "tag": "#2VCLRRYCV"},
    {"name": "Heaven Reverse", "tag": "#JGYRPPPY"},
    {"name": "Heaven Tomatoes", "tag": "#2LC9JVQLJ"},
    {"name": "Heaven Thunder", "tag": "#2CLQ2RPL8"},
    {"name": "Heaven Curse", "tag": "#2LGRGCL9U"},
    {"name": "Bloody Legion", "tag": "#2YPYJC88J"},
    {"name": "Bloody Justice", "tag": "#2VCU8J9CV"},
    {"name": "Bloody Valley", "tag": "#2VUURGQLR"},
    {"name": "Bloody Requiem", "tag": "#2Y89QRGQU"},
    {"name": "Bloody Cards", "tag": "#2JQURGVRG"}
]

# ============== НАСТРОЙКА ЛОГИРОВАНИЯ ==============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== МОДЕЛИ ДАННЫХ ==============
@dataclass
class ClubInfo:
    tag: str
    name: str
    description: str = ""
    trophies: int = 0
    required_trophies: int = 0
    members_count: int = 0
    type: str = ""

# ============== API КЛИЕНТ ==============
class BrawlAPI:
    def __init__(self, api_key: str, proxy_url: str):
        self.api_key = api_key
        self.proxy_url = proxy_url
        self.session = None
    
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_club_info(self, club_tag: str) -> Optional[ClubInfo]:
        """Получить информацию о клубе через прокси"""
        try:
            session = await self.get_session()
            url = f"{self.proxy_url}/clubs/{club_tag.replace('#', '%23')}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return ClubInfo(
                        tag=data.get("tag", ""),
                        name=data.get("name", ""),
                        description=data.get("description", ""),
                        trophies=data.get("trophies", 0),
                        required_trophies=data.get("requiredTrophies", 0),
                        members_count=len(data.get("members", [])),
                        type=data.get("type", "")
                    )
                else:
                    logger.error(f"API Error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching club info: {e}")
            return None

# ============== ОБРАБОТЧИКИ КОМАНД ==============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """🎮 <b>Добро пожаловать в Heaven & Bloody Family!</b> 🎮

📜 <b>Основные ссылки:</b>
▶️ ПРАВИЛА: https://t.me/c/2565122949/1/674535
▶️ ЧЁРНЫЙ СПИСОК: https://t.me/+8ISCeRkWfz40YzZi
▶️ АЛЬЯНСЫ: https://t.me/+BOHHdvr04D5kZmRi
▶️ ЛЕГЕНДЫ: https://t.me/+t-dkJTsbwr1hN2Vi

Доступные команды:
/start - Начальное сообщение
/info - Информация о боте
/clubs - Рейтинг клубов
/[club_name] - Информация о конкретном клубе

Пример: /Sakura /Leo /Karma"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /info"""
    info_text = """🤖 <b>Информация о боте:</b>

<b>Версия:</b> v2.1.0
<b>Разработчик:</b> Heaven Family
<b>Функционал:</b>
• Показ рейтинга клубов
• Детальная информация о клубах
• Автоматическое обновление данных
• Поддержка прокси-сервера

Используйте /clubs для просмотра рейтинга"""
    
    await update.message.reply_text(info_text, parse_mode=ParseMode.HTML)

def generate_clubs_page(page: int) -> tuple[str, InlineKeyboardMarkup]:
    """Генерация страницы с клубами"""
    start_idx = (page - 1) * CLUBS_PER_PAGE
    end_idx = start_idx + CLUBS_PER_PAGE
    clubs_page = CLUBS_DATA[start_idx:end_idx]
    
    text_lines = [f"📊 <b>Рейтинг клубов (Страница {page})</b>\n"]
    
    for idx, club in enumerate(clubs_page, start=start_idx + 1):
        text_lines.append(f"{idx}. {club['name']} - {club['tag']}")
    
    text_lines.append(f"\n📝 <b>Всего клубов:</b> {len(CLUBS_DATA)}")
    text_lines.append("<i>Для детальной информации используйте команду /[название]</i>")
    text_lines.append("<i>Пример: /Sakura /Leo /Karma</i>")
    
    # Создание кнопок навигации
    keyboard = []
    total_pages = (len(CLUBS_DATA) + CLUBS_PER_PAGE - 1) // CLUBS_PER_PAGE
    
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="current"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"page_{page+1}"))
        keyboard.append(nav_buttons)
    
    return "\n".join(text_lines), InlineKeyboardMarkup(keyboard) if keyboard else None

async def clubs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /clubs"""
    page = 1
    if context.args and context.args[0].isdigit():
        page = int(context.args[0])
        total_pages = (len(CLUBS_DATA) + CLUBS_PER_PAGE - 1) // CLUBS_PER_PAGE
        page = max(1, min(page, total_pages))
    
    text, reply_markup = generate_clubs_page(page)
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def club_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд вида /[club_name]"""
    command = update.message.text[1:].lower()  # Убираем / и приводим к нижнему регистру
    
    # Находим клуб по имени (игнорируя регистр и часть имени после пробела)
    club = None
    for c in CLUBS_DATA:
        club_name_lower = c['name'].lower()
        if command in club_name_lower or command == club_name_lower.split()[-1].lower():
            club = c
            break
    
    if not club:
        await update.message.reply_text(
            "❌ Клуб не найден. Используйте /clubs для просмотра всех клубов."
        )
        return
    
    # Получаем информацию из API
    brawl_api = BrawlAPI(BRAWL_API_KEY, BRAWL_API_PROXY)
    club_info = await brawl_api.get_club_info(club['tag'])
    await brawl_api.close()
    
    if club_info:
        response_text = f"""
🏆 <b>{club_info.name}</b> {club_info.tag}

📊 <b>Трофеи:</b> {club_info.trophies:,}
🎯 <b>Требуется для входа:</b> {club_info.required_trophies:,}
👥 <b>Участники:</b> {club_info.members_count}/30
📝 <b>Тип:</b> {club_info.type}
📋 <b>Описание:</b> {club_info.description if club_info.description else 'Нет описания'}

💬 <b>Команда для быстрого доступа:</b> /{club['name'].split()[-1]}
"""
    else:
        response_text = f"""
🏆 <b>{club['name']}</b> {club['tag']}

⚠️ <b>Не удалось загрузить данные из API</b>

💬 <b>Команда для быстрого доступа:</b> /{club['name'].split()[-1]}
"""
    
    await update.message.reply_text(response_text, parse_mode=ParseMode.HTML)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("page_"):
        page = int(query.data.split("_")[1])
        text, reply_markup = generate_clubs_page(page)
        
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
        )

# ============== FLASK APP ДЛЯ WEBHOOK ==============
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Heaven & Bloody Family Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint для webhook от Telegram"""
    if request.method == "POST":
        json_str = request.get_data().decode('UTF-8')
        update = Update.de_json(json.loads(json_str), bot)
        asyncio.run(process_update(update))
    return "OK"

async def process_update(update: Update):
    """Асинхронная обработка обновления"""
    await application.process_update(update)

# ============== ОСНОВНОЙ КОД ==============
def main():
    """Основная функция запуска бота"""
    global application, bot
    
    # Создаём приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    bot = application.bot
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("clubs", clubs_command))
    
    # Добавляем обработчики для команд клубов (например, /Sakura)
    for club in CLUBS_DATA:
        club_command = club['name'].split()[-1].lower()
        application.add_handler(
            CommandHandler(club_command, club_detail_command)
        )
    
    # Добавляем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Проверяем переменные окружения
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU':
        logger.warning("Используется тестовый токен Telegram")
    
    if not BRAWL_API_KEY or BRAWL_API_KEY.startswith('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMi'):
        logger.warning("Используется тестовый API ключ Brawl Stars")
    
    # Запускаем Flask и бота в разных потоках
    import threading
    
    def run_flask():
        app.run(host="0.0.0.0", port=10000, debug=False)
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Запускаем бота
    main()
