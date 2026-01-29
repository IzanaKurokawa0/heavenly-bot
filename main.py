import os
import sys

print("=" * 60)
print("🐛 DEBUG INFO")
print("=" * 60)

# 1. Версия Python
print(f"Python: {sys.version}")

# 2. Токен
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
print(f"Token exists: {'✅' if TELEGRAM_TOKEN else '❌'}")

# 3. Проверяем установленные пакеты
print("\n📦 Checking packages...")
try:
    import telegram
    print(f"python-telegram-bot: {telegram.__version__}")
    
    # Проверяем что есть Application
    from telegram.ext import Application
    print("✅ Application imported")
    
    # Проверяем что НЕТ Updater
    try:
        from telegram.ext import Updater
        print("❌ UPSTILL EXISTS!")
    except ImportError:
        print("✅ Updater NOT in this version")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 60)
