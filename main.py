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

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAFA4ZcJMuzOkv3PFWB88Wxe1Pal31WEquA')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjRmZGNlZDcxLWY1NjMtNDlkZS1iNzA3LTZkYTYyMjdiNWRkNiIsImlhdCI6MTc2OTYxMzU1NCwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyIiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTA0LjIxLjkyLjE2MSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.yMAS5RPWkTRtf6WpyaG7PDxdaqaVVb9PxOUCMuVMP87vJlARjS-RReEUNebQnwuY7AbfmlvXbWnuJxLREhkrqA')
BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

print(f"Telegram Token: {'✅ Установлен' if TELEGRAM_TOKEN else '❌ Нет'}")
print(f"Brawl API Key: {'✅ Установлен' if BRAWL_API_KEY else '❌ Нет'}")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DATA_FILE = 'clubs_data.json'

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return {'last_update': None, 'clubs': get_default_clubs()}
    except Exception as e:
        logger.error(f"Ошибка загрузки: {e}")
        return {'last_update': None, 'clubs': get_default_clubs()}

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

def get_default_clubs():
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
    try:
        return f'{int(n):,}'.replace(',', '.')
    except:
        return str(n)

def get_sorted_clubs():
    data = load_data()
    return sorted(data['clubs'], key=lambda x: x['trophies'], reverse=True)

def get_club_command_name(club_name):
    return club_name.lower().replace(' ', '_')

def update_clubs_data():
    logger.info("🔄 Обновление данных...")
    data = load_data()
    updated = 0
    
    for i, club in enumerate(data['clubs']):
        try:
            clean_tag = club['tag'].strip('#').replace('#', '')
            url = f'{BRAWL_API_PROXY}/v1/clubs/%23{clean_tag}'
            headers = {
                'Authorization': f'Bearer {BRAWL_API_KEY}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                club_data = response.json()
                data['clubs'][i]['trophies'] = club_data.get('trophies', club['trophies'])
                data['clubs'][i]['members'] = len(club_data.get('memberList', []))
                updated += 1
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"❌ {club['name']}: {e}")
    
    data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)
    return updated

async def start_bot():
    print("🤖 Запускаю Telegram бота...")
    
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        from telegram.constants import ParseMode
        
        # ✅ Application вместо Updater
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        data = load_data()
        club_commands = {}
        for club in data['clubs']:
            command_name = get_club_command_name(club['name'])
            club_commands[command_name] = club
        
        async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

⚡ <b>Примеры:</b>
<code>/heaven_karma</code> - Heaven Karma
<code>/bloody_legion</code> - Bloody Legion"""
            
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        async def club_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                command_text = update.message.text[1:]
                
                if command_text not in club_commands:
                    await update.message.reply_text(f"❌ Клуб не найден: <code>/{command_text}</code>", parse_mode=ParseMode.HTML)
                    return
                
                club = club_commands[command_text]
                sorted_clubs = get_sorted_clubs()
                rank = next((i+1 for i, c in enumerate(sorted_clubs) if c['id'] == club['id']), None)
                
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
                
                await update.message.reply_text(text, parse_mode=ParseMode.HTML)
                
            except Exception as e:
                await update.message.reply_text("❌ Ошибка", parse_mode=ParseMode.HTML)
        
        async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            msg = await update.message.reply_text("🔄 <b>Обновляю...</b>", parse_mode=ParseMode.HTML)
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
/help - Справка
/status - Статус
/rating - Рейтинг клубов
/update - Обновить данные

<code>/heaven_karma</code> - Детали клуба
<code>/heaven_moscow</code> - Детали клуба"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            data = load_data()
            text = f"""<b>📊 СТАТУС БОТА:</b>

🏆 Клубов: <b>{len(data['clubs'])}</b>
🔄 Обновлено: <b>{data['last_update'] or 'Никогда'}</b>
🌐 Прокси: <b>Cloudflare ✅</b>

✅ <b>Бот работает!</b>"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("rating", rating_command))
        application.add_handler(CommandHandler("update", update_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        
        for command_name in club_commands.keys():
            application.add_handler(CommandHandler(command_name, club_command))
        
        print("✅ Telegram bot configured")
        print("📱 Отправьте /start боту @Club_stats_bot")
        
        await application.initialize()
        await application.start()
        await application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

app = Flask(__name__)

@app.route('/')
def home():
    data = load_data()
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>🤖 Heavenly Dynasty Bot</title></head>
    <body>
        <h1>🤖 Heavenly Dynasty Bot</h1>
        <p>✅ <strong>Status:</strong> Running</p>
        <p><strong>Статистика:</strong></p>
        <ul>
            <li>Клубов: {len(data['clubs'])}</li>
            <li>Обновлено: {data['last_update'] or 'Никогда'}</li>
        </ul>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200

@app.route('/stats')
def stats():
    data = load_data()
    return {
        "clubs": len(data['clubs']),
        "last_update": data['last_update'],
        "heavenly": sum(1 for c in data['clubs'] if c['family'] == 'Heavenly'),
        "bloody": sum(1 for c in data['clubs'] if c['family'] == 'Bloody'),
        "total_trophies": sum(c['trophies'] for c in data['clubs'])
    }, 200

@app.route('/update', methods=['POST'])
def manual_update():
    updated = update_clubs_data()
    return {"updated": updated, "timestamp": datetime.now().isoformat()}, 200

def start_services():
    print("🚀 Starting services...")
    
    def run_bot_in_thread():
        asyncio.run(start_bot())
    
    bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
    bot_thread.start()
    time.sleep(2)
    
    if bot_thread.is_alive():
        print("✅ Bot thread started")
    else:
        print("⚠️ Bot thread may have failed")
    
    print("🌐 Flask web server ready")

start_services()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    print(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
