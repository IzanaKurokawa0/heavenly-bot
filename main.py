import os
import json
import logging
import requests
import asyncio
from datetime import datetime
from flask import Flask
import threading
import time

print("=" * 60)
print("🤖 HEAVENLY DYNASTY BOT v3.0")
print("=" * 60)

# Токены
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

# Проверка токенов
if not TELEGRAM_TOKEN:
    print("❌ ВНИМАНИЕ: TELEGRAM_TOKEN не установлен!")
    print("   Установите переменную окружения TELEGRAM_TOKEN")
    # Не выходим, так как веб-сервер должен работать

if not BRAWL_API_KEY:
    print("⚠️  ВНИМАНИЕ: BRAWL_API_KEY не установлен!")
    print("   Обновление данных будет недоступно")

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

def get_club_command_name(club_name):
    """Преобразует имя клуба в название команды"""
    return club_name.lower().replace(' ', '_')

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
async def run_bot():
    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен! Бот не запущен.")
        return
    
    print("🤖 Запускаю Telegram бота...")
    
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        from telegram.constants import ParseMode
        
        # Создаем приложение - ТОЛЬКО TApplication, НЕ Updater!
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Словарь для быстрого поиска клуба по названию команды
        data = load_data()
        club_commands = {}
        for club in data['clubs']:
            command_name = get_club_command_name(club['name'])
            club_commands[command_name] = club
        
        # Команда /start
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
/status - Статус

⚡ <b>Примеры команд клубов:</b>
<code>/heaven_karma</code> - Heaven Karma
<code>/heaven_moscow</code> - Heaven Moscow
<code>/bloody_legion</code> - Bloody Legion
<code>/bloody_cards</code> - Bloody Cards"""
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        # Команда /rating
        async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
            sorted_clubs = get_sorted_clubs()
            text = "<b>🏆 ТОП-10 КЛУБОВ:</b>\n\n"
            
            for i, club in enumerate(sorted_clubs[:10], 1):
                emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
                command_name = get_club_command_name(club['name'])
                
                text += f"{i}. {emoji} <b>{club['name']}</b>\n"
                text += f"   🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n"
                text += f"   📍 <code>/{command_name}</code>\n\n"
            
            text += "📋 <b>Популярные клубы:</b>\n"
            text += "<code>/heaven_karma</code> <code>/heaven_moscow</code>\n"
            text += "<code>/bloody_legion</code> <code>/bloody_justice</code>\n\n"
            
            data = load_data()
            if data['last_update']:
                text += f"📅 Обновлено: {data['last_update']}"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        # Общая функция для команд клубов
        async def club_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                # Получаем название команды (/heaven_karma -> "heaven_karma")
                command_text = update.message.text[1:]  # Убираем "/"
                
                if command_text not in club_commands:
                    await update.message.reply_text(
                        f"❌ Клуб не найден: <code>/{command_text}</code>\n"
                        f"📊 Используй <code>/rating</code> для списка клубов",
                        parse_mode=ParseMode.HTML
                    )
                    return
                
                club = club_commands[command_text]
                
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
                
                # Навигация по клубам
                nav_text = "\n\n🔄 <b>Другие клубы:</b>\n"
                
                # Соседние клубы по рейтингу
                if rank > 1:
                    prev_club = sorted_clubs[rank-2]
                    prev_command = get_club_command_name(prev_club['name'])
                    nav_text += f"◀️ Выше: <code>/{prev_command}</code>\n"
                
                if rank < len(sorted_clubs):
                    next_club = sorted_clubs[rank]
                    next_command = get_club_command_name(next_club['name'])
                    nav_text += f"▶️ Ниже: <code>/{next_command}</code>\n"
                
                nav_text += f"📊 Весь рейтинг: <code>/rating</code>"
                text += nav_text
                
                await update.message.reply_text(text, parse_mode=ParseMode.HTML)
                
            except Exception as e:
                logger.error(f"Ошибка в club_command: {e}")
                await update.message.reply_text(
                    "❌ Ошибка при обработке команды\n"
                    "📊 Используй <code>/rating</code> для списка клубов",
                    parse_mode=ParseMode.HTML
                )
        
        # Команда /update
        async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            msg = await update.message.reply_text("🔄 <b>Обновляю данные...</b>", parse_mode=ParseMode.HTML)
            updated = update_clubs_data()
            data = load_data()
            
            if updated > 0:
                text = f"✅ <b>Обновлено {updated} клубов</b>\n📅 {data['last_update']}"
            else:
                text = "⚠️ <b>Не удалось обновить</b>"
            
            await msg.edit_text(text, parse_mode=ParseMode.HTML)
        
        # Команда /help
        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            text = """<b>📚 КОМАНДЫ:</b>

🏠 <b>Основные:</b>
<code>/start</code> - Главное меню
<code>/help</code> - Эта справка
<code>/status</code> - Статус бота

📊 <b>Просмотр:</b>
<code>/rating</code> - Рейтинг клубов
<code>/название_клуба</code> - Детали клуба

🔄 <b>Обновление:</b>
<code>/update</code> - Обновить данные

🎯 <b>Примеры команд клубов:</b>
<code>/heaven_karma</code>
<code>/heaven_moscow</code>
<code>/bloody_legion</code>
<code>/bloody_justice</code>

📱 <b>Как использовать:</b>
1. <code>/rating</code> - смотри топ клубов
2. <code>/heaven_karma</code> - детали клуба
3. <code>/update</code> - обнови данные"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        # Команда /status
        async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            data = load_data()
            text = f"""<b>📊 СТАТУС БОТА:</b>

🏆 Клубов: <b>{len(data['clubs'])}</b>
🔄 Обновлено: <b>{data['last_update'] or 'Никогда'}</b>
🌐 Прокси: <b>Cloudflare ✅</b>
⚡ Хостинг: <b>Render.com</b>

✅ <b>Бот работает!</b>"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        # Добавляем основные обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("rating", rating))
        application.add_handler(CommandHandler("update", update_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        
        # Добавляем обработчики для всех клубов
        for command_name in club_commands.keys():
            application.add_handler(CommandHandler(command_name, club_command))
        
        print("✅ Бот настроен!")
        print("📱 Открой Telegram и напиши /start")
        print("=" * 60)
        
        # Запускаем бота - ТОЛЬКО application.run_polling()
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что установлены нужные библиотеки:")
        print("pip install python-telegram-bot[job-queue]==20.7 requests flask")
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

@app.route('/update', methods=['POST'])
def manual_update():
    """Ручное обновление данных через веб-запрос"""
    updated = update_clubs_data()
    return f"Updated {updated} clubs", 200

def run_web():
    port = int(os.getenv('PORT', 10000))
    print(f"🌐 Веб-сервер на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== ЗАПУСК ==========
def main():
    print("🚀 Запуск приложения...")
    
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    time.sleep(2)
    
    # Запускаем бота в основном потоке
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == '__main__':
    main()
