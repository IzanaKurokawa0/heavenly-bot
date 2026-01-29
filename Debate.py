import requests
import asyncio

TOKEN = '8028581574:AAFz-mI8pRUjySICbGvy0r83gb0a1TibJt0'

print("=" * 60)
print("🔍 ТЕСТ ТОКЕНА И API")
print("=" * 60)

# Тест 1: Проверка через requests
try:
    print("1. Проверяю токен через Telegram API...")
    response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getMe', timeout=10)
    print(f"   Статус: {response.status_code}")
    print(f"   Ответ: {response.json()}")
    
    if response.status_code == 200:
        bot_info = response.json()
        print(f"   ✅ Токен рабочий!")
        print(f"   🤖 Бот: @{bot_info['result']['username']}")
        print(f"   🆔 ID: {bot_info['result']['id']}")
    else:
        print(f"   ❌ Ошибка: {response.text}")
        
except Exception as e:
    print(f"   ❌ Ошибка запроса: {e}")

# Тест 2: Проверка через библиотеку
async def test_library():
    try:
        print("\n2. Проверяю через python-telegram-bot...")
        from telegram import Bot
        bot = Bot(token=TOKEN)
        me = await bot.get_me()
        print(f"   ✅ Библиотека работает!")
        print(f"   🤖 Бот: @{me.username}")
        print(f"   📛 Имя: {me.first_name}")
        return True
    except ImportError as e:
        print(f"   ❌ Нет библиотеки: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Ошибка библиотеки: {e}")
        return False

# Запуск теста
print("\n" + "=" * 60)
try:
    success = asyncio.run(test_library())
    print(f"✅ Тест пройден!" if success else "❌ Тест не пройден")
except Exception as e:
    print(f"❌ Ошибка asyncio: {e}")

print("=" * 60)
