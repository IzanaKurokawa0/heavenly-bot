#!/usr/bin/env python3
"""
Скрипт для проверки IP адреса Render и статуса Brawl Stars API
Запуск: python check_ip.py
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime
import sys

# Конфигурация
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')
TEST_CLUB_TAG = "#JYGVQR89"  # Heaven Karma для теста
API_URL = "https://api.brawlstars.com/v1"

async def get_external_ip():
    """Получить внешний IP адрес"""
    services = [
        "https://api.ipify.org?format=json",
        "https://icanhazip.com",
        "https://checkip.amazonaws.com",
        "https://ifconfig.me/ip"
    ]
    
    print("🌐 Получение внешнего IP адреса...")
    
    async with aiohttp.ClientSession() as session:
        for service in services:
            try:
                async with session.get(service, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Парсим JSON если это JSON
                        if 'json' in service:
                            data = json.loads(content)
                            ip = data.get('ip', content.strip())
                        else:
                            ip = content.strip()
                        
                        print(f"✅ IP адрес: {ip}")
                        print(f"   Источник: {service}")
                        
                        # Дополнительная информация о IP
                        await get_ip_info(ip, session)
                        return ip
                        
            except Exception as e:
                print(f"   ❌ {service}: {e}")
                continue
    
    print("❌ Не удалось получить IP адрес")
    return None

async def get_ip_info(ip: str, session: aiohttp.ClientSession):
    """Получить информацию об IP адресе"""
    try:
        url = f"http://ip-api.com/json/{ip}"
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('status') == 'success':
                    print(f"📍 Локация: {data.get('city', 'N/A')}, {data.get('country', 'N/A')}")
                    print(f"   Провайдер: {data.get('isp', 'N/A')}")
                    print(f"   Организация: {data.get('org', 'N/A')}")
    except Exception as e:
        print(f"   ℹ️  Детали IP: не доступны ({e})")

async def test_brawl_api():
    """Тест подключения к Brawl Stars API"""
    if not BRAWL_API_KEY:
        print("\n🔑 API ключ не установлен (переменная BRAWL_API_KEY)")
        print("   Получите ключ: https://developer.brawlstars.com")
        return False
    
    print(f"\n🔍 Тест Brawl Stars API...")
    print(f"   Ключ: {BRAWL_API_KEY[:20]}...")
    
    clean_tag = TEST_CLUB_TAG.replace('#', '')
    url = f"{API_URL}/clubs/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"   URL: {url}")
            print(f"   Запрос...")
            
            async with session.get(url, headers=headers, timeout=10) as response:
                print(f"   📊 Статус: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Успешно!")
                    print(f"   🏆 Клуб: {data.get('name', 'N/A')}")
                    print(f"   🎯 Трофеи: {data.get('trophies', 0):,}")
                    print(f"   👥 Участников: {len(data.get('members', []))}")
                    return True
                    
                elif response.status == 403:
                    error = await response.text()
                    print(f"   ❌ Ошибка 403: Доступ запрещен")
                    print(f"   📄 Ответ: {error[:200]}...")
                    print(f"   ⚠️  Возможные причины:")
                    print(f"      • Неверный API ключ")
                    print(f"      • Ключ истек")
                    print(f"      • IP адрес не разрешен в настройках ключа")
                    return False
                    
                elif response.status == 429:
                    print(f"   ⚠️  Ошибка 429: Слишком много запросов")
                    print(f"   💡 Подождите и повторите")
                    return False
                    
                else:
                    error = await response.text()
                    print(f"   ❌ Ошибка {response.status}")
                    print(f"   📄 Ответ: {error[:200]}...")
                    return False
                    
    except aiohttp.ClientConnectorError:
        print(f"   ❌ Не удалось подключиться к API")
        return False
    except asyncio.TimeoutError:
        print(f"   ⏱️  Таймаут запроса")
        return False
    except Exception as e:
        print(f"   ❌ Неизвестная ошибка: {e}")
        return False

async def test_proxy_if_exists():
    """Тест прокси-сервера если он настроен"""
    proxy_url = os.getenv('BRAWL_API_PROXY', '')
    if not proxy_url:
        return
    
    print(f"\n🔗 Тест прокси-сервера...")
    print(f"   URL: {proxy_url}")
    
    clean_tag = TEST_CLUB_TAG.replace('#', '')
    url = f"{proxy_url}/clubs/%23{clean_tag}/"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                print(f"   📊 Статус: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Прокси работает!")
                    print(f"   🏆 Клуб: {data.get('name', 'N/A')}")
                else:
                    error = await response.text()
                    print(f"   ❌ Ошибка прокси: {response.status}")
                    print(f"   📄 Ответ: {error[:200]}...")
                    
    except Exception as e:
        print(f"   ❌ Ошибка прокси: {e}")

async def check_render_environment():
    """Проверка переменных окружения Render"""
    print("\n🏗️  Проверка окружения Render...")
    
    env_vars = [
        ('TELEGRAM_TOKEN', 'Токен Telegram бота'),
        ('BRAWL_API_KEY', 'Ключ Brawl Stars API'),
        ('BRAWL_API_PROXY', 'Прокси-сервер (опционально)'),
        ('PORT', 'Порт для веб-сервера'),
    ]
    
    for var_name, description in env_vars:
        value = os.getenv(var_name, '')
        if value:
            status = "✅ установлена"
            if var_name in ['TELEGRAM_TOKEN', 'BRAWL_API_KEY']:
                # Скрываем часть значения для безопасности
                display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else value
                print(f"   {var_name}: {status} ({display_value})")
            else:
                print(f"   {var_name}: {status} ({value})")
        else:
            status = "❌ не установлена"
            print(f"   {var_name}: {status}")

async def generate_ipwhitelist_instructions(ip: str):
    """Генерация инструкций для добавления IP в белый список"""
    if not ip:
        return
    
    print("\n📝 Инструкция по добавлению IP в Brawl Stars API:")
    print("=" * 50)
    print(f"1. Перейдите на: https://developer.brawlstars.com")
    print(f"2. Выберите ваш проект")
    print(f"3. Нажмите 'Edit' у нужного ключа API")
    print(f"4. В разделе 'Allowed IPs' добавьте:")
    print(f"   {ip}")
    print(f"5. Нажмите 'Save'")
    print(f"6. Подождите 1-2 минуты")
    print(f"7. Перезапустите бота командой /refresh")
    print("=" * 50)

async def main():
    """Основная функция"""
    print("=" * 60)
    print("🔧 Диагностика IP адреса и Brawl Stars API")
    print("=" * 60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверяем окружение
    await check_render_environment()
    
    # Получаем IP
    ip = await get_external_ip()
    
    # Тестируем API
    api_works = await test_brawl_api()
    
    # Тестируем прокси если есть
    await test_proxy_if_exists()
    
    # Вывод результатов
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ:")
    print("=" * 60)
    
    if ip:
        print(f"🌐 Внешний IP: {ip}")
    
    if api_works:
        print(f"✅ Brawl Stars API: РАБОТАЕТ")
        print(f"   Можно использовать текущий IP и API ключ")
    else:
        print(f"❌ Brawl Stars API: НЕ РАБОТАЕТ")
        if ip:
            print(f"   Вероятно, IP {ip} не добавлен в белый список")
            await generate_ipwhitelist_instructions(ip)
    
    print("\n💡 Рекомендации:")
    if not api_works:
        print("1. Добавьте IP выше в белый список на developer.brawlstars.com")
        print("2. Подождите 1-2 минуты")
        print("3. Перезапустите бота")
    else:
        print("1. Все работает! Бот должен работать корректно")
        print("2. Если IP изменится, повторите процедуру")
    
    print("\n⚡ Команды для бота:")
    print("   /refresh - обновить данные после смены API ключа")
    print("   /status - проверить статус бота")
    
    print("=" * 60)

if __name__ == "__main__":
    # Проверяем Python версию
    print(f"🐍 Python {sys.version}")
    
    # Запускаем асинхронную функцию
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
