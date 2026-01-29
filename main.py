import os
import json
import logging
import requests
import asyncio
import sys
import threading
import time
from datetime import datetime
from flask import Flask

print("=" * 60)
print("🤖 CLUB STATS BOT v3.0 - ОБНОВЛЁННЫЙ ТОКЕН")
print("=" * 60)

# ========== НОВЫЙ ТОКЕН ==========
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAFA4ZcJMuzOkv3PFWB88Wxe1Pal31WEquA')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyIiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE2MSJdLCJ0eXBlIjoidGxpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

print(f"📊 Конфигурация:")
print(f"  Telegram Бот: @Club_stats_bot")
print(f"  Токен: ✅ ОБНОВЛЁН ({len(TELEGRAM_TOKEN)} символов)")
print(f"  Brawl API Key: {'✅' if BRAWL_API_KEY else '❌'}")

# ========== ПРОВЕРКА ТОКЕНА ==========
print("\n🔐 Проверка нового токена...")
try:
    response = requests.get(
        f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe',
        timeout=10
    )
    print(f"  📡 API статус: {response.status_code}")
    
    if response.status_code == 200:
        bot_info = response.json()['result']
        print(f"  ✅ Бот найден: @{bot_info['username']} ({bot_info['first_name']})")
        print(f"  🆔 ID: {bot_info['id']}")
        print(f"  💬 Можно писать: /start")
    elif response.status_code == 401:
        print(f"  ❌ Ошибка 401: Неверный токен!")
        sys.exit(1)
    else:
        print(f"  ❌ Неожиданный статус: {response.text}")
except Exception as e:
    print(f"  ❌ Ошибка проверки: {e}")
    sys.exit(1)

print("=" * 60)

# ========== ОСТАЛЬНОЙ КОД БЕЗ ИЗМЕНЕНИЙ ==========
# (всё остальное как в предыдущем полном коде)
# ... весь остальной код функций, Flask app и т.д.

# Flask app
app = Flask(__name__)

# Файл данных
DATA_FILE = 'clubs_data.json'

# ========== ВСЕ ФУНКЦИИ ОСТАЮТСЯ ТАКИМИ ЖЕ ==========
def load_data():
    """Загружает данные из файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return {'last_update': None, 'clubs': get_default_clubs()}
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return {'last_update': None, 'clubs': get_default_clubs()}

def save_data(data):
    """Сохраняет данные в файл"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

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

# ========== ТЕЛЕГРАМ БОТ ==========
async def run_bot_async():
    """Асинхронная функция запуска бота"""
    print("\n🤖 ЗАПУСКАЮ @Club_stats_bot...")
    
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        from telegram.constants import ParseMode
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Проверяем подключение
        bot = application.bot
        me = await bot.get_me()
        print(f"✅ Подключено к боту: @{me.username}")
        
        # Загружаем данные
        data = load_data()
        club_commands = {}
        for club in data['clubs']:
            command_name = get_club_command_name(club['name'])
            club_commands[command_name] = club
        
        # Команда /start
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            print(f"📨 Получен /start от {update.effective_user.username}")
            
            data = load_data()
            heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
            bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
            total_trophies = sum(c['trophies'] for c in data['clubs'])
            
            text = f"""<b>🏆 CLUB STATS BOT v3.0</b>

Привет, {update.effective_user.first_name}!

🤖 <b>Бот полностью обновлён!</b>
✅ Новый токен активирован
🚀 Хостинг: Render.com

📊 <b>СТАТИСТИКА:</b>
• Всего клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Трофеев: <b>{format_num(total_trophies)}</b>
• Обновлено: <b>{data['last_update'] or 'Ещё не было'}</b>

📋 <b>КОМАНДЫ:</b>
/start - Это меню
/rating - Топ клубов
/test - Тест работы
/status - Статус бота

⚡ <b>Примеры команд клубов:</b>
<code>/heaven_karma</code> - Heaven Karma
<code>/bloody_legion</code> - Bloody Legion"""
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            print(f"✅ Отправлен ответ пользователю {update.effective_user.username}")
        
        # Команда /test
        async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("✅ Тест пройден! Бот работает!")
            print(f"✅ Тест от {update.effective_user.username}")
        
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
            text += "<code>/bloody_legion</code> <code>/bloody_justice</code>"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            print(f"📊 Отправлен рейтинг пользователю {update.effective_user.username}")
        
        # Команда /status
        async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
            text = f"""<b>📊 СТАТУС БОТА:</b>

✅ <b>Бот работает!</b>
🤖 Аккаунт: @Club_stats_bot
🔑 Токен: Обновлён
🚀 Версия: 3.0
🕐 Время: {datetime.now().strftime('%H:%M:%S')}"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test))
        application.add_handler(CommandHandler("rating", rating))
        application.add_handler(CommandHandler("status", status))
        
        # Добавляем команды для клубов
        for command_name in club_commands.keys():
            application.add_handler(CommandHandler(command_name, 
                lambda update, context, cmd=command_name, club=club_commands[cmd]: 
                update.message.reply_text(
                    f"<b>{club['name']}</b>\n🏆 {format_num(club['trophies'])} трофеев\n👥 {club['members']}/30\n🏷️ {club['tag']}",
                    parse_mode=ParseMode.HTML
                )
            ))
        
        print("✅ Бот настроен и готов к работе!")
        print("📱 Напиши /start боту @Club_stats_bot")
        print("=" * 60)
        
        # Запускаем polling
        await application.run_polling()
        
    except Exception as e:
        print(f"💥 Ошибка бота: {e}")
        import traceback
        traceback.print_exc()
        raise

def run_bot():
    """Запускает бота"""
    print("🧵 Запускаю поток бота...")
    try:
        asyncio.run(run_bot_async())
    except Exception as e:
        print(f"💥 Поток упал: {e}")
        print("🔄 Перезапуск через 30 секунд...")
        time.sleep(30)
        run_bot()

# ========== ВЕБ-СЕРВЕР ==========
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Club Stats Bot</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .running { background: #d4edda; color: #155724; }
        </style>
    </head>
    <body>
        <h1>🤖 Club Stats Bot</h1>
        <div class="status running">
            ✅ <strong>Status:</strong> Running с новым токеном!
        </div>
        <p><strong>Telegram бот:</strong> @Club_stats_bot</p>
        <p><strong>Токен:</strong> Обновлён ✅</p>
        <p><a href="/health">Health Check</a> | <a href="/debug">Debug</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "@Club_stats_bot", "timestamp": datetime.now().isoformat()}, 200

@app.route('/debug')
def debug():
    threads = []
    for thread in threading.enumerate():
        threads.append(f"{thread.name} (alive={thread.is_alive()})")
    
    return {
        "bot": "@Club_stats_bot",
        "token_length": len(TELEGRAM_TOKEN),
        "threads": threads,
        "total_threads": threading.active_count()
    }, 200

# ========== ЗАПУСК ==========
def start_services():
    print("\n🚀 ЗАПУСК СЕРВИСОВ")
    print("=" * 60)
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, name="BotThread", daemon=True)
    bot_thread.start()
    time.sleep(2)
    
    print(f"✅ Поток бота запущен: {bot_thread.is_alive()}")
    print(f"📊 Всего потоков: {threading.active_count()}")
    print("=" * 60)
    print("🌐 Веб-сервер запускается...")
    print("🤖 Telegram: @Club_stats_bot")
    print("📱 Команда: /start")

# Запускаем сервисы
start_services()

# Запускаем Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
