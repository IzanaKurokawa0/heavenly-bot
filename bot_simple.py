# bot_simple.py - минимальный рабочий бот для Render
import os
import json
import asyncio
import logging
import requests
from datetime import datetime
from flask import Flask, request
import threading
import time

# Telegram бот (старая версия 13.x)
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# ========== НАСТРОЙКА ==========
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY')

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🤖 HEAVENLY DYNASTY BOT - SIMPLE VERSION")
print("=" * 60)
print(f"Telegram Token: {'✅ Установлен' if TELEGRAM_TOKEN else '❌ Нет'}")
print(f"Brawl API Key: {'✅ Установлен' if BRAWL_API_KEY else '❌ Нет'}")

# ========== КОМАНДЫ БОТА ==========
def start(update: Update, context: CallbackContext):
    """Обработчик команды /start"""
    user = update.effective_user
    update.message.reply_text(
        f'Привет {user.first_name}! 👋\n\n'
        f'Я бот Heavenly Dynasty.\n'
        f'Используй /help для списка команд.',
        parse_mode=ParseMode.HTML
    )

def help_command(update: Update, context: CallbackContext):
    """Обработчик команды /help"""
    update.message.reply_text(
        '📚 Доступные команды:\n'
        '/start - Начать работу\n'
        '/help - Помощь\n'
        '/rating - Рейтинг клубов\n'
        '/status - Статус бота'
    )

def rating(update: Update, context: CallbackContext):
    """Обработчик команды /rating"""
    # Пример данных
    clubs = [
        {"name": "Heaven Karma", "trophies": 55000},
        {"name": "Heaven Moscow", "trophies": 54800},
        {"name": "Bloody Legion", "trophies": 2300000}
    ]
    
    text = "🏆 Рейтинг клубов:\n\n"
    for i, club in enumerate(clubs, 1):
        text += f"{i}. {club['name']} - {club['trophies']:,} 🏆\n"
    
    update.message.reply_text(text)

def status(update: Update, context: CallbackContext):
    """Обработчик команды /status"""
    update.message.reply_text(
        '📊 Статус бота:\n'
        '✅ Бот работает\n'
        '🌐 Хостинг: Render.com\n'
        '⚡ Версия: Simple 1.0'
    )

# ========== ЗАПУСК БОТА ==========
def run_bot():
    """Запускает Telegram бота"""
    if not TELEGRAM_TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен!")
        return
    
    print("🤖 Запускаю Telegram бота...")
    
    try:
        # Создаем Updater (старый стиль для версии 13.x)
        updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        
        # Получаем dispatcher
        dispatcher = updater.dispatcher
        
        # Добавляем обработчики команд
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("rating", rating))
        dispatcher.add_handler(CommandHandler("status", status))
        
        print("✅ Бот настроен и запускается...")
        
        # Запускаем бота
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()

# ========== ВЕБ-СЕРВЕР ДЛЯ RENDER ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Heavenly Dynasty Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_web():
    """Запускает Flask сервер"""
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Запуск веб-сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# ========== ГЛАВНЫЙ ЗАПУСК ==========
if __name__ == '__main__':
    print("🚀 Запуск приложения...")
    
    # Запускаем веб-сервер в отдельном потоке
    print("🌐 Запускаю веб-сервер...")
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    time.sleep(2)
    
    # Запускаем бота
    run_bot()
