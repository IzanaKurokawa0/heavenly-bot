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
print("🤖 HEAVENLY DYNASTY BOT v3.0 - FULL DEBUG")
print("=" * 60)

# ========== НАСТРОЙКА ==========
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:aafa4zcjmuzokv3pfwb88wxe1pal31wequa')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyIiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE2MSJdLCJ0eXBlIjoidGxpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

print(f"📊 Конфигурация:")
print(f"  Telegram Token: {'✅' if TELEGRAM_TOKEN else '❌'} ({len(TELEGRAM_TOKEN)} символов)")
print(f"  Brawl API Key: {'✅' if BRAWL_API_KEY else '❌'}")
print(f"  Cloudflare Proxy: {BRAWL_API_PROXY}")

# ========== ПРОВЕРКА БИБЛИОТЕК ==========
print("\n📚 Проверка библиотек:")
try:
    import telegram
    print(f"  ✅ python-telegram-bot: {telegram.__version__}")
except ImportError as e:
    print(f"  ❌ python-telegram-bot: {e}")
    sys.exit(1)

try:
    import flask
    print(f"  ✅ Flask: {flask.__version__}")
except ImportError as e:
    print(f"  ❌ Flask: {e}")

print(f"  ✅ Python: {sys.version}")

# ========== ПРОВЕРКА ТОКЕНА TELEGRAM ==========
print("\n🔐 Проверка Telegram токена:")
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
    elif response.status_code == 401:
        print(f"  ❌ Ошибка 401: Неверный токен!")
        print(f"  💡 Проверь токен: {TELEGRAM_TOKEN[:20]}...")
        sys.exit(1)
    else:
        print(f"  ❌ Неожиданный статус: {response.text}")
except requests.exceptions.Timeout:
    print(f"  ❌ Таймаут запроса к Telegram API")
except Exception as e:
    print(f"  ❌ Ошибка проверки токена: {e}")

# ========== ПРОВЕРКА ФАЙЛОВОЙ СИСТЕМЫ ==========
print("\n📁 Проверка файловой системы:")
DATA_FILE = 'clubs_data.json'
print(f"  Файл данных: {DATA_FILE}")
print(f"  Текущая директория: {os.getcwd()}")
print(f"  Содержимое директории:")
for item in os.listdir('.'):
    print(f"    - {item}")

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_debug.log')
    ]
)
logger = logging.getLogger(__name__)

# ========== FLASK APP ==========
app = Flask(__name__)

# ========== ФУНКЦИИ ДЛЯ ДАННЫХ ==========
def load_data():
    """Загружает данные из файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            logger.info("Создаю начальные данные")
            return {'last_update': None, 'clubs': get_default_clubs()}
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return {'last_update': None, 'clubs': get_default_clubs()}

def save_data(data):
    """Сохраняет данные в файл"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Данные сохранены")
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")

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
    print("\n" + "=" * 60)
    print("🤖 ЗАПУСК TELEGRAM БОТА")
    print("=" * 60)
    
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        from telegram.constants import ParseMode
        
        print("1. Создаю приложение...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        print("2. Проверяю подключение к боту...")
        bot = application.bot
        me = await bot.get_me()
        print(f"   ✅ Подключено к боту: @{me.username}")
        
        print("3. Загружаю данные клубов...")
        data = load_data()
        club_commands = {}
        for club in data['clubs']:
            command_name = get_club_command_name(club['name'])
            club_commands[command_name] = club
        print(f"   ✅ Загружено {len(club_commands)} клубов")
        
        print("4. Настраиваю обработчики команд...")
        
        # Команда /start
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger.info(f"Получен /start от {update.effective_user.username}")
            data = load_data()
            heavenly = sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')
            bloody = sum(1 for c in data['clubs'] if c['family'] == 'Bloody')
            total_trophies = sum(c['trophies'] for c in data['clubs'])
            
            text = f"""<b>🏆 HEAVENLY DYNASTY BOT v3.0</b>

Привет, {update.effective_user.first_name}!

✅ <b>Бот полностью обновлён!</b>
🤖 Новый аккаунт: @Club_stats_bot
🚀 Хостинг: Render.com

📊 <b>СТАТИСТИКА:</b>
• Всего клубов: <b>{len(data['clubs'])}</b>
• Heavenly: <b>{heavenly}</b> | Bloody: <b>{bloody}</b>
• Трофеев: <b>{format_num(total_trophies)}</b>
• Обновлено: <b>{data['last_update'] or 'Ещё не было'}</b>

📋 <b>КОМАНДЫ:</b>
/start - Это меню
/rating - Рейтинг клубов
/test - Тестовая команда
/status - Статус бота"""
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            print(f"📨 Отправлен /start пользователю {update.effective_user.username}")
        
        # Команда /test
        async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("✅ Тест пройден! Бот работает!")
            print(f"✅ Тест от {update.effective_user.username}")
        
        # Команда /rating
        async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
            sorted_clubs = get_sorted_clubs()
            text = "<b>🏆 ТОП-5 КЛУБОВ:</b>\n\n"
            
            for i, club in enumerate(sorted_clubs[:5], 1):
                emoji = "☁️" if club['family'] == 'Heavenly' else "🔴"
                text += f"{i}. {emoji} <b>{club['name']}</b>\n"
                text += f"   🏆 {format_num(club['trophies'])} | 👥 {club['members']}/30\n\n"
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            print(f"📊 Отправлен рейтинг пользователю {update.effective_user.username}")
        
        # Команда /status
        async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
            text = f"""<b>📊 СТАТУС БОТА:</b>

✅ <b>Бот работает!</b>
🤖 Аккаунт: @Club_stats_bot
🚀 Версия: 3.0
🕐 Время: {datetime.now().strftime('%H:%M:%S')}

<i>Все системы в норме</i>"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test))
        application.add_handler(CommandHandler("rating", rating))
        application.add_handler(CommandHandler("status", status))
        
        print("5. Добавляю команды клубов...")
        # Простые команды для клубов
        for command_name, club in list(club_commands.items())[:5]:  # Только первые 5
            async def club_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, club=club):
                text = f"""<b>{club['name']}</b>
🏆 Трофеи: {format_num(club['trophies'])}
👥 Участники: {club['members']}/30
🏷️ Тег: <code>{club['tag']}</code>
👨‍👩‍👧‍👦 Семья: {club['family']}"""
                await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            
            application.add_handler(CommandHandler(command_name, club_cmd))
        
        print("✅ Все обработчики настроены!")
        print("=" * 60)
        print("📱 Бот готов! Напиши /start в Telegram")
        print("=" * 60)
        
        # Запускаем polling
        await application.run_polling()
        
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА В БОТЕ:")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")
        
        # Записываем полный traceback
        import traceback
        error_details = traceback.format_exc()
        print("\n🔍 Полный traceback:")
        print(error_details)
        
        # Сохраняем в файл
        with open('bot_crash.log', 'w') as f:
            f.write(f"Время: {datetime.now()}\n")
            f.write(f"Ошибка: {type(e).__name__}\n")
            f.write(f"Сообщение: {str(e)}\n")
            f.write("\nTraceback:\n")
            f.write(error_details)
        
        raise  # Пробрасываем ошибку дальше

def run_bot():
    """Запускает бота с обработкой ошибок"""
    print("\n🧵 ЗАПУСК ПОТОКА БОТА")
    try:
        asyncio.run(run_bot_async())
    except KeyboardInterrupt:
        print("👋 Бот остановлен по запросу пользователя")
    except Exception as e:
        print(f"💥 Поток бота упал с ошибкой: {type(e).__name__}")
        print(f"🔄 Перезапуск через 30 секунд...")
        time.sleep(30)
        print("🔄 Перезапускаю бота...")
        run_bot()  # Рекурсивный перезапуск

# ========== ВЕБ-СЕРВЕР ==========
@app.route('/')
def home():
    data = load_data()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Heavenly Dynasty Bot</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
            .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
            .running {{ background: #d4edda; color: #155724; }}
            .debug {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>🤖 Heavenly Dynasty Bot</h1>
        <div class="status running">
            ✅ <strong>Status:</strong> Running с новым ботом @HeavenlyHD_bot
        </div>
        
        <h3>📊 Статистика:</h3>
        <ul>
            <li>Клубов: {len(data['clubs'])}</li>
            <li>Heavenly: {sum(1 for c in data['clubs'] if c['family'] == 'Heavenly')}</li>
            <li>Bloody: {sum(1 for c in data['clubs'] if c['family'] == 'Bloody')}</li>
            <li>Обновлено: {data['last_update'] or 'Никогда'}</li>
        </ul>
        
        <h3>🔗 Эндпоинты:</h3>
        <ul>
            <li><a href="/health">/health</a> - Health check</li>
            <li><a href="/stats">/stats</a> - Статистика</li>
            <li><a href="/debug">/debug</a> - Отладка</li>
            <li><a href="/threads">/threads</a> - Потоки</li>
        </ul>
        
        <div class="debug">
            <h3>🐛 Отладка:</h3>
            <p><strong>Telegram бот:</strong> @HeavenlyHD_bot</p>
            <p><strong>Токен:</strong> {TELEGRAM_TOKEN[:15]}...</p>
            <p><strong>Время запуска:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "service": "Heavenly Dynasty Bot",
        "bot": "@Club_stats_bot",
        "timestamp": datetime.now().isoformat()
    }, 200

@app.route('/stats')
def stats():
    data = load_data()
    return {
        "clubs": len(data['clubs']),
        "heavenly": sum(1 for c in data['clubs'] if c['family'] == 'Heavenly'),
        "bloody": sum(1 for c in data['clubs'] if c['family'] == 'Bloody'),
        "total_trophies": sum(c['trophies'] for c in data['clubs']),
        "last_update": data['last_update']
    }, 200

@app.route('/debug')
def debug():
    """Страница отладки"""
    threads = []
    for thread in threading.enumerate():
        threads.append({
            'name': thread.name,
            'daemon': thread.daemon,
            'alive': thread.is_alive(),
            'id': thread.ident
        })
    
    return {
        'system': {
            'python_version': sys.version,
            'platform': sys.platform,
            'current_dir': os.getcwd(),
            'files': os.listdir('.')
        },
        'bot': {
            'token_length': len(TELEGRAM_TOKEN),
            'token_prefix': TELEGRAM_TOKEN[:15],
            'bot_username': 'Club_stats_bot'
        },
        'threads': {
            'count': threading.active_count(),
            'list': threads
        },
        'timestamp': datetime.now().isoformat()
    }

@app.route('/threads')
def threads_info():
    """Информация о потоках"""
    threads = []
    for i, thread in enumerate(threading.enumerate(), 1):
        threads.append(f"{i}. {thread.name} (daemon={thread.daemon}, alive={thread.is_alive()})")
    
    return "<br>".join(threads), 200, {'Content-Type': 'text/html'}

# ========== ЗАПУСК СЕРВИСОВ ==========
def start_services():
    """Запускает все сервисы"""
    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК СЕРВИСОВ")
    print("=" * 60)
    
    print("1. Запускаю Telegram бота в фоновом потоке...")
    bot_thread = threading.Thread(
        target=run_bot,
        name="TelegramBotThread",
        daemon=True
    )
    bot_thread.start()
    
    # Даём время на инициализацию
    time.sleep(3)
    
    print(f"2. Состояние потока бота:")
    print(f"   Имя: {bot_thread.name}")
    print(f"   Жив: {bot_thread.is_alive()}")
    print(f"   Daemon: {bot_thread.daemon}")
    
    print(f"3. Всего потоков: {threading.active_count()}")
    print("   Активные потоки:")
    for thread in threading.enumerate():
        print(f"   - {thread.name} (alive={thread.is_alive()})")
    
    print("4. Веб-сервер Flask готов")
    print("=" * 60)
    print("🌐 Веб-интерфейс доступен по основному URL")
    print("🤖 Telegram бот: @Club_stats_bot")
    print("📱 Напиши /start в Telegram")
    print("=" * 60)

# ========== ТОЧКА ВХОДА ==========
if __name__ == '__main__':
    # Запускаем сервисы
    start_services()
    
    # Запускаем Flask
    port = int(os.getenv('PORT', 10000))
    print(f"\n🌐 Запускаю Flask на порту {port}")
    print(f"📊 Открой: http://0.0.0.0:{port}")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )
