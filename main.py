import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask
import threading
import time

print("=" * 60)
print("🤖 HEAVENLY DYNASTY BOT v3.0")
print("=" * 60)

# Токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyIiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE2MSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

print(f"Telegram Token: {'✅ Установлен' if TELEGRAM_TOKEN else '❌ Нет'}")
print(f"Brawl API Key: {'✅ Установлен' if BRAWL_API_KEY else '❌ Нет'}")
print(f"Cloudflare Proxy: {BRAWL_API_PROXY}")
print("=" * 60)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    try:
        return f'{int(n):,}'.replace(',', '.')
    except:
        return str(n)

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
def update_clubs_data():
    """Обновляет данные через Cloudflare Proxy"""
    logger.info("🔄 Начинаю обновление данных...")
    
    data = load_data()
    updated = 0
    
    if not BRAWL_API_KEY:
        logger.error("❌ BRAWL_API_KEY не установлен!")
        return 0
    
    for i, club in enumerate(data['clubs']):
        try:
            clean_tag = club['tag'].strip('#').replace('#', '')
            
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
            elif response.status_code == 404:
                logger.warning(f"⚠️ {club['name']}: Клуб не найден")
            else:
                logger.warning(f"⚠️ {club['name']}: Ошибка {response.status_code}")
                
            time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"❌ {club['name']}: {str(e)}")
    
    data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)
    
    logger.info(f"✅ Обновлено {updated}/{len(data['clubs'])} клубов")
    return updated

# ========== ТЕЛЕГРАМ БОТ ==========
def run_bot():
    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен!")
        return
    
    print("🤖 Запускаю Telegram бота...")
    
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
        from telegram.constants import ParseMode
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # ========== КОМАНДЫ ==========
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            data = load_data()
            heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
            bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
            total_trophies = sum(c['trophies'] for c in data['clubs'])
            
            text = f"""<b>🏆 HEAVENLY DYNASTY BOT v3.0</b>

Привет, {update.effective_user.first_name}!

📊 <b>СТАТИСТИКА:</b>
• Всего клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Трофеев: <b>{format_num(total_trophies)}</b>
• Обновлено: <b>{data['last_update'] or 'Ещё не было'}</b>

📋 <b>КОМАНДЫ:</b>
/rating - Рейтинг клубов
/update - Обновить данные
/help - Помощь
/status - Статус"""
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
            sorted_clubs = get_sorted_clubs()
            text = "<b>🏆 ТОП-10 КЛУБОВ:</b>\n\n"
            
            for i, club in enumerate(sorted_clubs[:10], 1):
                emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
                text += f"{i}. {emoji} <b>{club['name']}</b>\n"
                text += f"   🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n\n"
            
            data = load_data()
            if data['last_update']:
                text += f"📅 Обновлено: {data['last_update']}"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            msg = await update.message.reply_text("🔄 <b>Обновляю данные...</b>", parse_mode=ParseMode.HTML)
            updated = update_clubs_data()
            data = load_data()
            
            if updated > 0:
                text = f"✅ <b>Обновлено {updated} клубов</b>\n📅 {data['last_update']}"
            else:
                text = "⚠️ <b>Не удалось обновить</b>"
            
            await msg.edit_text(text, parse_mode=ParseMode.HTML)
        
        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            text = """<b>📚 КОМАНДЫ:</b>
/start - Главное меню
/rating - Рейтинг клубов
/update - Обновить данные
/status - Статус бота
/help - Эта справка"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            data = load_data()
            text = f"""<b>📊 СТАТУС БОТА:</b>

🏆 Клубов: <b>{len(data['clubs'])}</b>
🔄 Обновлено: <b>{data['last_update'] or 'Никогда'}</b>
🌐 Прокси: <b>Cloudflare ✅</b>
⚡ Хостинг: <b>Render.com</b>

✅ <b>Бот работает!</b>"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("rating", rating))
        application.add_handler(CommandHandler("update", update_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        
        print("✅ Бот настроен!")
        print("📱 Открой Telegram и напиши /start")
        print("=" * 60)
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()

# ========== ВЕБ-СЕРВЕР ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Heavenly Dynasty Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.getenv('PORT', 10000))
    print(f"🌐 Веб-сервер на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🚀 Запуск приложения...")
    
    # Веб-сервер
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    time.sleep(3)
    
    # Бот
    run_bot()
