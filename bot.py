import json
import os
from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
import requests
import schedule
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ---------------------------- НАСТРОЙКИ ----------------------------
BOT_TOKEN = "8637784218:AAF6NQt-HMIOaxJnh42ISkuMkqdJgFGy6P0"
BS_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImZhZmM3OWI4LTU0YWUtNDhlZi05MjdkLWRkMDliZGU3MDNiZSIsImlhdCI6MTc3NjM0OTM2NSwic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyMiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiNDUuNzkuMjE4Ljc5Il0sInR5cGUiOiJjbGllbnQifV19.0fN60l8E86kBGEGhpdwAf1CzWaSUX-ty_1mpFgVUkV-BvKb-t_5J9wZjlTzwFEGRwvXfOW5lW6dWZY9-bRc_dw"
BS_API_URL = "https://bsproxy.royaleapi.dev/v1/clubs/%23"

ALLOWED_UPDATERS = {"@IzanaKurokawa0", "@Sakvoiz"}
DATA_DIR = "data"

os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------- КЛУБЫ ----------------------------
CLUBS = {
    "Heaven Temple": {"tag": "#80LPG8V8L", "rep": "DonAyu7", "emoji": "🛕"},
    "Heaven Sakura": {"tag": "#2Q082VC08", "rep": "@IzanaKurokawa0", "emoji": "🌸"},
    "Heaven Ulqion": {"tag": "#2QL982PJ9", "rep": "whyazazel", "emoji": "🌌"},
    "Heaven Hell": {"tag": "#C0QQ8RV0", "rep": "@IzanaKurokawa0", "emoji": "🔥"},
    "Heaven KE": {"tag": "#2Q2QVYGU8", "rep": "Aktoadmin", "emoji": "🔑"},
    "Heaven Kingdom": {"tag": "#2C2YLRCCU", "rep": "@Sakvoiz", "emoji": "👑"},
    "Heaven Dream": {"tag": "#2LQ2UV0LJ", "rep": "FellStorm", "emoji": "💭"},
    "Heaven Vinland": {"tag": "#2VJRV89JG", "rep": "ecclipsa", "emoji": "⚔️"},
    "Heaven Reverse": {"tag": "#JGYRPPPY", "rep": "faweer3", "emoji": "↩️"},
    "Heaven Tomatoes": {"tag": "#2LC9JVQLJ", "rep": "HiderBro", "emoji": "🍅"},
    "Bloody Cards": {"tag": "#2JQURGVRG", "rep": "@Sakvoiz", "emoji": "🎴"},
    "Heaven Inters": {"tag": "#2CCGJ9009", "rep": "Qq_Neit", "emoji": "🔄"},
    "Heaven Hunt": {"tag": "#822PC0JQU", "rep": "Pableniso", "emoji": "🎯"},
    "Heaven Envoy": {"tag": "#JYR0YRR2", "rep": "@probs201", "emoji": "📩"},
    "Heaven Cucumber": {"tag": "#JG9U8U82", "rep": "Work_Weezz", "emoji": "🥒"},
    "Heaven Fortress": {"tag": "#C0JJC0L2", "rep": "mopsikkmii", "emoji": "🏰"},
    "Bloody Justice": {"tag": "#2VCU8J9CV", "rep": "@interscopeplay", "emoji": "⚖️"},
    "Bloody Valley": {"tag": "#2VUURGQLR", "rep": "Happyhausha", "emoji": "🏞️"},
    "Bloody Requiem": {"tag": "#2Y89QRGQU", "rep": "l0ckyYn", "emoji": "🎵"},
    "Heaven Curse": {"tag": "#2LGRGCL9U", "rep": "@ItsDanielTT", "emoji": "👻"},
    "Heaven Moscow": {"tag": "#JG2GPJ9Q", "rep": "DIMALENS21", "emoji": "🏢"},
    "Heaven Infinity": {"tag": "#2VCLRRYCV", "rep": "itsFaon4ik", "emoji": "♾️"},
    "Bloody Legion": {"tag": "#2YPYJC88J", "rep": "@ItsDanielTT", "emoji": "⚔️"},
    "Heaven Leo": {"tag": "#2C29U8Q8P", "rep": "ligavi55", "emoji": "🦁"},
    "Heaven Winter": {"tag": "#2LCUY0Q8G", "rep": "OBEP_gg", "emoji": "❄️"},
    "Heaven Thunder": {"tag": "#2CLQ2RPL8", "rep": "reidum", "emoji": "⚡"},
    "Heaven Dominion": {"tag": "#80LQRCR0J", "rep": "@Evillkass", "emoji": "🏆"},
    "Heaven Yoritake": {"tag": "#80QC8R2PV", "rep": "plugoholic", "emoji": "🎎"},
    "Heaven Yoritake 2": {"tag": "#820VPOCGU", "rep": "qtgone", "emoji": "👘"}
}

ALIASES = {
    "temple": "Heaven Temple",
    "sakura": "Heaven Sakura",
    "ulqion": "Heaven Ulqion",
    "hell": "Heaven Hell",
    "ke": "Heaven KE",
    "kingdom": "Heaven Kingdom",
    "dream": "Heaven Dream",
    "vinland": "Heaven Vinland",
    "reverse": "Heaven Reverse",
    "tomatoes": "Heaven Tomatoes",
    "cards": "Bloody Cards",
    "inters": "Heaven Inters",
    "hunt": "Heaven Hunt",
    "envoy": "Heaven Envoy",
    "cucumber": "Heaven Cucumber",
    "fortress": "Heaven Fortress",
    "justice": "Bloody Justice",
    "valley": "Bloody Valley",
    "requiem": "Bloody Requiem",
    "curse": "Heaven Curse",
    "moscow": "Heaven Moscow",
    "infinity": "Heaven Infinity",
    "legion": "Bloody Legion",
    "leo": "Heaven Leo",
    "winter": "Heaven Winter",
    "thunder": "Heaven Thunder",
    "dominion": "Heaven Dominion",
    "yoritake": "Heaven Yoritake",
    "yoritake2": "Heaven Yoritake 2"
}

# ---------------------------- УТИЛИТЫ ----------------------------
def load_history(club_name):
    filepath = os.path.join(DATA_DIR, f"{club_name}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(club_name, history):
    filepath = os.path.join(DATA_DIR, f"{club_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def fetch_club_data(tag):
    url = f"{BS_API_URL}{tag.strip('#')}"
    headers = {"Authorization": f"Bearer {BS_API_KEY}"}
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return None

def update_all_clubs():
    for name, info in CLUBS.items():
        data = fetch_club_data(info["tag"])
        if not data:
            continue
        trophies = data.get("trophies", 0)
        members = len(data.get("members", []))
        history = load_history(name)
        last = history[-1] if history else None
        if not last or last["trophies"] != trophies or last["members"] != members:
            history.append({
                "timestamp": datetime.now().isoformat(),
                "trophies": trophies,
                "members": members
            })
            save_history(name, history)

def generate_graph(history, club_name):
    if len(history) < 2:
        return None
    dates = [datetime.fromisoformat(p["timestamp"]) for p in history]
    values = [p["trophies"] for p in history]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(dates, values, color='#00FFFF', linewidth=2)
    ax.fill_between(dates, values, color='#00FFFF', alpha=0.3)
    ax.set_title(f"{club_name} – Динамика трофеев", color='white')
    ax.set_xlabel("Время", color='white')
    ax.set_ylabel("Трофеи", color='white')
    ax.tick_params(colors='white')
    fig.autofmt_xdate()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor='black', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

# ---------------------------- КОМАНДЫ ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Привет, я бот Heavenly Dynasty для аналитики данных клубов и рейтинговой системы.\n\n"
        "Доступные команды:\n"
        "/start – приветствие и список команд\n"
        "/top – рейтинг клубов по трофеям (пагинация)\n"
        "/list – все короткие команды для клубов\n"
        "/update – принудительное обновление (только для админов)\n\n"
        "Короткие команды клубов (примеры):\n"
        "/leo, /sakura, /temple, /kingdom, /cards, /envoy..."
    )
    await update.message.reply_text(help_text)

async def update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username
    if f"@{user}" not in ALLOWED_UPDATERS:
        await update.message.reply_text("⛔ Недостаточно прав.")
        return
    await update.message.reply_text("🔄 Запущено принудительное обновление...")
    update_all_clubs()
    await update.message.reply_text("✅ Обновление завершено.")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    club_stats = []
    for name in CLUBS:
        hist = load_history(name)
        if hist:
            last = hist[-1]
            club_stats.append((name, last["trophies"], last["members"]))
    club_stats.sort(key=lambda x: x[1], reverse=True)

    page = 0
    per_page = 10
    total_pages = (len(club_stats) - 1) // per_page + 1

    def format_page(p):
        start = p * per_page
        end = start + per_page
        lines = [f"🏆 Топ клубов (страница {p+1}/{total_pages}):\n"]
        for i, (name, trophies, members) in enumerate(club_stats[start:end], start+1):
            emoji = CLUBS[name]["emoji"]
            lines.append(f"{i}. {emoji} {name}: 🏆 {trophies:,} | 👥 {members}/30")
        return "\n".join(lines)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("←", callback_data=f"top_{page-1}_{page}"),
            InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="none"),
            InlineKeyboardButton("→", callback_data=f"top_{page+1}_{page}")
        ]
    ])

    await update.message.reply_text(format_page(page), reply_markup=keyboard)

async def top_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    if data[0] != "top":
        return
    new_page = int(data[1])
    current_page = int(data[2])
    if new_page == current_page:
        return

    club_stats = []
    for name in CLUBS:
        hist = load_history(name)
        if hist:
            last = hist[-1]
            club_stats.append((name, last["trophies"], last["members"]))
    club_stats.sort(key=lambda x: x[1], reverse=True)

    total_pages = (len(club_stats) - 1) // 10 + 1
    if new_page < 0 or new_page >= total_pages:
        return

    def format_page(p):
        start = p * 10
        end = start + 10
        lines = [f"🏆 Топ клубов (страница {p+1}/{total_pages}):\n"]
        for i, (name, trophies, members) in enumerate(club_stats[start:end], start+1):
            emoji = CLUBS[name]["emoji"]
            lines.append(f"{i}. {emoji} {name}: 🏆 {trophies:,} | 👥 {members}/30")
        return "\n".join(lines)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("←", callback_data=f"top_{new_page-1}_{new_page}"),
            InlineKeyboardButton(f"{new_page+1}/{total_pages}", callback_data="none"),
            InlineKeyboardButton("→", callback_data=f"top_{new_page+1}_{new_page}")
        ]
    ])

    await query.edit_message_text(format_page(new_page), reply_markup=keyboard)

async def club_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.strip("/")
    club_name = ALIASES.get(cmd)
    if not club_name:
        await update.message.reply_text("❌ Клуб не найден. Используй /list для списка команд.")
        return

    info = CLUBS[club_name]
    tag = info["tag"]
    emoji = info["emoji"]
    president = info["rep"]

    data = fetch_club_data(tag)
    if data:
        trophies = data.get("trophies", 0)
        members = len(data.get("members", []))
        required = data.get("requiredTrophies", 0)
    else:
        hist = load_history(club_name)
        if hist:
            last = hist[-1]
            trophies = last["trophies"]
            members = last["members"]
            required = "?"
        else:
            await update.message.reply_text("⚠️ Нет данных о клубе.")
            return

    history = load_history(club_name)
    graph_buf = generate_graph(history, club_name)

    caption = (
        f"{emoji} {club_name} ({tag})\n"
        f"├─ 👑 Президент: {president}\n"
        f"├─ 🏆 Общие трофеи: {trophies:,}\n"
        f"├─ 👥 Участников: {members}/30\n"
        f"└─ 🚪 Порог входа: {required}"
    )

    if graph_buf:
        await update.message.reply_photo(photo=graph_buf, caption=caption)
    else:
        await update.message.reply_text(caption + "\n📉 Недостаточно данных для графика")

async def list_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmds = "\n".join([f"/{k} – {v}" for k, v in ALIASES.items()])
    await update.message.reply_text(f"📋 Доступные команды клубов:\n{cmds}")

# ---------------------------- ЗАПУСК ----------------------------
def main():
    import time
    import threading
    schedule.every().hour.do(update_all_clubs)

    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(1)
    threading.Thread(target=scheduler_loop, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("update", update_cmd))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("list", list_commands))
    app.add_handler(CallbackQueryHandler(top_callback, pattern="^top_"))
    for alias in ALIASES:
        app.add_handler(CommandHandler(alias, club_info))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
