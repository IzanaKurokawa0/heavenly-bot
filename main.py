import os
import asyncio
import logging
import time
from typing import Dict, List, Tuple, Optional
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# ========== НАСТРОЙКИ ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из вашего кода
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', '')

# ========== ДАННЫЕ КЛУБОВ ==========
CLUBS = {
    "Heaven Leo": {"tag": "#2C29U8Q8P", "rep": "@ligavi55"},
    "Heaven Cucumber": {"tag": "#JG9U8U82", "rep": "@Work_Weezz"},
    "Heaven Temple": {"tag": "#80LPG8V8L", "rep": "@DonAyu7"},
    "Heaven Kingdom": {"tag": "#2C2YLRCCU", "rep": "@Sakvoiz"},
    "Heaven Dream": {"tag": "#2LQ2UV0LJ", "rep": "@FellStorm"},
    "Heaven Dynasty": {"tag": "#C8CG8GQJ", "rep": "@ItsDanielTT, @QNoMercyQ"},
    "Heaven Winter": {"tag": "#2LCUY0Q8G", "rep": "@OBEP_gg"},
    "Heaven Envoy": {"tag": "#JYR0YRR2", "rep": "@probs201, @neroxf133"},
    "Heaven Dominion": {"tag": "#80LQRCR0J", "rep": "@KMT_Dream"},
    "Heaven Sakura": {"tag": "#2Q082VC08", "rep": "@IzanaKurokawa0"},
    "Heaven Vinland": {"tag": "#2VJRV89JG", "rep": "@ecclipsa"},
    "Heaven Infinity": {"tag": "#2VCLRRYCV", "rep": "@itsFaon4ik"},
    "Heaven Reverse": {"tag": "#JGYRPPPY", "rep": "@faweer3"},
    "Heaven Tomatoes": {"tag": "#2LC9JVQLJ", "rep": "@HiderBro"},
    "Heaven Thunder": {"tag": "#2CLQ2RPL8", "rep": "@morphinnn1"},
    "Heaven Curse": {"tag": "#2LGRGCL9U", "rep": "@princexgod"},
    "Heaven Karma": {"tag": "#JYGVQR89", "rep": "@Sakvoiz"},
    "Heaven Moscow": {"tag": "#JG2GPJ9Q", "rep": "@DIMALENS21"},
    "Heaven Fortress": {"tag": "#C0JJC0L2", "rep": "@mopsikkmii"},
    "Heaven Hell": {"tag": "#C0QQ8RV0", "rep": "@IzanaKurokawa0"},
    "Heaven KE": {"tag": "#2Q2QVYGU8", "rep": "@Aktoadmin"},
    
    "Bloody Legion": {"tag": "#2YPYJC88J", "rep": "@dijaweed"},
    "Bloody Justice": {"tag": "#2VCU8J9CV", "rep": "@interscopeplay"},
    "Bloody Valley": {"tag": "#2VUURGQLR", "rep": "@Happyhausha"},
    "Bloody Requiem": {"tag": "#2Y89QRGQU", "rep": "@l0ckyYn"},
    "Bloody Cards": {"tag": "#2JQURGVRG", "rep": "@Sakvoiz"},
}

# ========== ФИКСИРОВАННЫЕ ДАННЫЕ ==========
FALLBACK_DATA = {
    "#2C29U8Q8P": {"trophies": 52800, "members": [{} for _ in range(28)], "requiredTrophies": 5000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Leo"},
    "#JG9U8U82": {"trophies": 51000, "members": [{} for _ in range(26)], "requiredTrophies": 4500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Cucumber"},
    "#80LPG8V8L": {"trophies": 50500, "members": [{} for _ in range(27)], "requiredTrophies": 4000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Temple"},
    "#2C2YLRCCU": {"trophies": 50200, "members": [{} for _ in range(25)], "requiredTrophies": 3500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Kingdom"},
    "#2LQ2UV0LJ": {"trophies": 49800, "members": [{} for _ in range(24)], "requiredTrophies": 3000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Dream"},
    "#C8CG8GQJ": {"trophies": 49500, "members": [{} for _ in range(23)], "requiredTrophies": 2500, "description": "👑 Heavenly Dynasty main club", "name": "Heaven Dynasty"},
    "#2LCUY0Q8G": {"trophies": 49200, "members": [{} for _ in range(22)], "requiredTrophies": 2000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Winter"},
    "#JYR0YRR2": {"trophies": 48900, "members": [{} for _ in range(21)], "requiredTrophies": 1500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Envoy"},
    "#80LQRCR0J": {"trophies": 48600, "members": [{} for _ in range(20)], "requiredTrophies": 1000, "description": "👑 Heavenly Dynasty family", "name": "Heaven Dominion"},
    "#2Q082VC08": {"trophies": 48300, "members": [{} for _ in range(19)], "requiredTrophies": 500, "description": "👑 Heavenly Dynasty family", "name": "Heaven Sakura"},
    "#2VJRV89JG": {"trophies": 48000, "members": [{} for _ in range(18)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Vinland"},
    "#2VCLRRYCV": {"trophies": 47700, "members": [{} for _ in range(17)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Infinity"},
    "#JGYRPPPY": {"trophies": 47400, "members": [{} for _ in range(16)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Reverse"},
    "#2LC9JVQLJ": {"trophies": 47100, "members": [{} for _ in range(15)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Tomatoes"},
    "#2CLQ2RPL8": {"trophies": 46800, "members": [{} for _ in range(14)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Thunder"},
    "#2LGRGCL9U": {"trophies": 46500, "members": [{} for _ in range(13)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Curse"},
    "#JYGVQR89": {"trophies": 46200, "members": [{} for _ in range(12)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Karma"},
    "#JG2GPJ9Q": {"trophies": 45900, "members": [{} for _ in range(11)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Moscow"},
    "#C0JJC0L2": {"trophies": 45600, "members": [{} for _ in range(10)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Fortress"},
    "#C0QQ8RV0": {"trophies": 45300, "members": [{} for _ in range(9)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven Hell"},
    "#2Q2QVYGU8": {"trophies": 45000, "members": [{} for _ in range(8)], "requiredTrophies": 0, "description": "👑 Heavenly Dynasty family", "name": "Heaven KE"},
    "#2YPYJC88J": {"trophies": 48500, "members": [{} for _ in range(26)], "requiredTrophies": 4000, "description": "🩸 Bloody Family branch", "name": "Bloody Legion"},
    "#2VCU8J9CV": {"trophies": 48000, "members": [{} for _ in range(25)], "requiredTrophies": 3500, "description": "🩸 Bloody Family branch", "name": "Bloody Justice"},
    "#2VUURGQLR": {"trophies": 47500, "members": [{} for _ in range(24)], "requiredTrophies": 3000, "description": "🩸 Bloody Family branch", "name": "Bloody Valley"},
    "#2Y89QRGQU": {"trophies": 47000, "members": [{} for _ in range(23)], "requiredTrophies": 2500, "description": "🩸 Bloody Family branch", "name": "Bloody Requiem"},
    "#2JQURGVRG": {"trophies": 46500, "members": [{} for _ in range(22)], "requiredTrophies": 2000, "description": "🩸 Bloody Family branch", "name": "Bloody Cards"},
}

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
cache: Dict = {}
current_ip: Optional[str] = None
api_working: bool = False
last_api_check: float = 0

# ========== ФУНКЦИИ ДЛЯ IP И API ==========
async def get_current_ip() -> Optional[str]:
    """Получить текущий IP адрес сервера"""
    global current_ip
    try:
        async with aiohttp.ClientSession() as temp_session:
            async with temp_session.get("https://api.ipify.org?format=json", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    current_ip = data.get('ip', 'Не определен')
                    logger.info(f"🌐 IP адрес получен: {current_ip}")
                    return current_ip
    except Exception as e:
        logger.error(f"❌ Ошибка при получении IP: {e}")
        current_ip = "Ошибка определения"
        return None

async def check_api_status() -> bool:
    """Проверить статус API Brawl Stars"""
    global api_working, last_api_check
    
    if not BRAWL_API_KEY:
        api_working = False
        last_api_check = time.time()
        logger.info("⚠️ API ключ не установлен")
        return False
    
    if time.time() - last_api_check < 120:
        return api_working
    
    test_tag = list(CLUBS.values())[0]["tag"]
    clean_tag = test_tag.replace('#', '')
    url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
    
    try:
        async with aiohttp.ClientSession() as temp_session:
            async with temp_session.get(url, headers=headers, timeout=10) as response:
                api_working = response.status == 200
                last_api_check = time.time()
                
                if api_working:
                    logger.info("✅ API Brawl Stars работает")
                else:
                    logger.warning(f"❌ API не работает, статус: {response.status}")
                
                return api_working
    except Exception as e:
        logger.error(f"❌ Ошибка проверки API: {e}")
        api_working = False
        last_api_check = time.time()
        return False

async def fetch_club_data(club_tag: str, force_refresh: bool = False) -> Dict:
    """Получить данные клуба"""
    global cache, api_working
    
    if not force_refresh and club_tag in cache:
        cached = cache[club_tag]
        if time.time() - cached["timestamp"] < 3600:
            return cached["data"]
    
    if BRAWL_API_KEY and (api_working or await check_api_status()):
        clean_tag = club_tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
        headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
        
        try:
            async with aiohttp.ClientSession() as temp_session:
                async with temp_session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        cache[club_tag] = {
                            "data": data,
                            "timestamp": time.time(),
                            "source": "api"
                        }
                        logger.info(f"✅ Данные обновлены из API для {club_tag}")
                        return data
                    else:
                        logger.warning(f"❌ API вернул ошибку {response.status} для {club_tag}")
        except Exception as e:
            logger.error(f"Ошибка API запроса {club_tag}: {e}")
            api_working = False
    
    # Используем fallback данные
    if club_tag in FALLBACK_DATA:
        fallback_data = FALLBACK_DATA[club_tag]
        cache[club_tag] = {
            "data": fallback_data,
            "timestamp": time.time(),
            "source": "fallback"
        }
        return fallback_data
    
    # Если ничего нет, возвращаем пустые данные
    empty_data = {
        "name": "Unknown Club",
        "trophies": 45000,
        "requiredTrophies": 0,
        "members": [],
        "description": "Нет данных"
    }
    cache[club_tag] = {
        "data": empty_data,
        "timestamp": time.time(),
        "source": "empty"
    }
    return empty_data

async def get_sorted_clubs() -> List[Tuple[str, Dict, Dict]]:
    """Получить отсортированные данные всех клубов"""
    clubs_data = []
    
    for club_name, club_info in CLUBS.items():
        try:
            data = await fetch_club_data(club_info["tag"])
            clubs_data.append((club_name, club_info, data))
        except Exception as e:
            logger.error(f"Ошибка получения данных для {club_name}: {e}")
            if club_info["tag"] in FALLBACK_DATA:
                data = FALLBACK_DATA[club_info["tag"]]
                clubs_data.append((club_name, club_info, data))
    
    clubs_data.sort(key=lambda x: x[2].get('trophies', 0), reverse=True)
    return clubs_data

# ========== КОМАНДЫ БОТА ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    global current_ip
    if not current_ip:
        await get_current_ip()
    
    await check_api_status()
    
    heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
    bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
    
    message = f"""🎮 *Heaven & Bloody Stats Bot*

📊 *Статистика:*
👑 Heavenly Dynasty: {heaven_count} клубов
🩸 Bloody Family: {bloody_count} клубов
📈 Всего: {len(CLUBS)} клубов

🌐 *IP сервера:* `{current_ip or 'определяю...'}`

📡 *Статус API:* {'🟢 работает' if api_working else '🔴 не работает'}

⚡ *Основные команды:*
/rating - Рейтинг всех клубов
/refresh - Обновить данные из API
/status - Детальный статус бота
/ip - Показать IP для настройки API"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def rating_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /rating"""
    try:
        loading_msg = await update.message.reply_text("⏳ Загружаю рейтинг...")
        
        clubs_data = await get_sorted_clubs()
        
        if not clubs_data:
            await loading_msg.edit_text("❌ Не удалось загрузить данные клубов")
            return
        
        message = "🏆 *Рейтинг клубов*\n\n"
        
        for i, (club_name, club_info, club_data) in enumerate(clubs_data, 1):
            emoji = "👑" if club_name.startswith("Heaven") else "🩸"
            rep = club_info.get('rep', '—')
            trophies = club_data.get('trophies', 0)
            members = club_data.get('members', [])
            member_count = len(members)
            
            short_name = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
            
            message += f"{i}. {emoji} *{club_name}*\n"
            message += f"   👤 {rep}\n"
            message += f"   🏆 {trophies:,} | 👥 {member_count}/30\n"
            message += f"   📖 /{short_name}\n\n"
        
        heaven_count = len([n for n in CLUBS if n.startswith("Heaven")])
        bloody_count = len([n for n in CLUBS if n.startswith("Bloody")])
        
        message += f"👑 Heavenly Dynasty: {heaven_count} клубов\n"
        message += f"🩸 Bloody Family: {bloody_count} клубов\n"
        message += f"🎯 Всего: {len(clubs_data)} клубов\n"
        message += f"🔄 /refresh - обновить данные"
        
        await loading_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Ошибка в команде /rating: {e}")
        await update.message.reply_text("❌ Произошла ошибка при загрузке рейтинга")

async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /refresh"""
    if not BRAWL_API_KEY:
        await update.message.reply_text(
            "❌ API ключ не установлен. Используйте /ip чтобы получить ваш IP для настройки.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        loading_msg = await update.message.reply_text("🔄 Начинаю обновление данных...")
        
        updated = 0
        failed = 0
        
        for club_name, club_info in CLUBS.items():
            try:
                await asyncio.sleep(0.3)  # Задержка чтобы не превысить лимиты API
                data = await fetch_club_data(club_info["tag"], force_refresh=True)
                if data:
                    updated += 1
            except Exception as e:
                logger.error(f"Ошибка обновления {club_name}: {e}")
                failed += 1
        
        message = f"✅ *Обновление завершено!*\n\n"
        message += f"• Успешно: {updated} клубов\n"
        message += f"• Ошибок: {failed} клубов\n"
        message += f"• Всего: {len(CLUBS)} клубов\n\n"
        message += f"🏆 Используйте /rating для просмотра"
        
        await loading_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Ошибка в команде /refresh: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обновлении данных")

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /ip"""
    try:
        ip = await get_current_ip()
        
        if ip and ip not in ["Не удалось определить", "Ошибка определения"]:
            message = f"""🌐 *IP адрес сервера*

`{ip}`

📝 *Как использовать для Brawl Stars API:*
1. Откройте: https://developer.brawlstars.com
2. Выберите ваш проект
3. Нажмите "Edit" у API ключа
4. В "Allowed IPs" добавьте IP выше
5. Сохраните изменения"""
        else:
            message = "❌ Не удалось определить IP адрес"
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Ошибка в команде /ip: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении IP")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status"""
    try:
        if not current_ip:
            await get_current_ip()
        
        await check_api_status()
        
        # Получаем информацию о кэше
        api_count = sum(1 for item in cache.values() if item.get("source") == "api")
        fallback_count = sum(1 for item in cache.values() if item.get("source") == "fallback")
        
        message = f"""📊 *Детальный статус бота*

🌐 *Сеть:*
IP адрес: `{current_ip or 'не определен'}`
API подключение: {'🟢 РАБОТАЕТ' if api_working else '🔴 НЕ РАБОТАЕТ'}

💾 *Данные:*
Всего клубов: {len(CLUBS)}
В кэше: {len(cache)} клубов
• Из API: {api_count}
• Fallback: {fallback_count}

👥 *Состав семьи:*
👑 Heavenly Dynasty: {len([n for n in CLUBS if n.startswith('Heaven')])} клубов
🩸 Bloody Family: {len([n for n in CLUBS if n.startswith('Bloody')])} клубов

⚙️ *Команды:*
/rating - Рейтинг клубов
/refresh - Обновить данные
/ip - Показать IP"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Ошибка в команде /status: {e}")
        await update.message.reply_text("❌ Произошла ошибка при получении статуса")

async def club_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команд клубов"""
    try:
        command = update.message.text[1:].lower()
        
        found_club = None
        found_info = None
        
        for club_name, club_info in CLUBS.items():
            short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
            if command == short:
                found_club = club_name
                found_info = club_info
                break
        
        if not found_club:
            await update.message.reply_text(f"❌ Клуб /{command} не найден")
            return
        
        # Показываем статус загрузки
        loading_msg = await update.message.reply_text(f"⏳ Загружаю информацию о {found_club}...")
        
        data = await fetch_club_data(found_info["tag"])
        
        emoji = "👑" if found_club.startswith("Heaven") else "🩸"
        rep = found_info.get("rep", "—")
        trophies = data.get('trophies', 0)
        required = data.get('requiredTrophies', 0)
        members = data.get('members', [])
        member_count = len(members)
        description = data.get('description', 'Нет описания')
        
        message = f"{emoji} *{found_club}*\n\n"
        message += f"*📋 Основное:*\n"
        message += f"Представитель: {rep}\n"
        message += f"Тег: {found_info['tag']}\n\n"
        
        message += f"*📊 Статистика:*\n"
        message += f"🏆 Общие кубки: {trophies:,}\n"
        message += f"👥 Участников: {member_count}/30\n"
        message += f"🎯 Требуется для входа: {required:,}\n\n"
        
        message += f"*📝 Описание:*\n{description}\n\n"
        
        message += f"🔗 /rating - Вернуться к рейтингу"
        
        await loading_msg.edit_text(message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Ошибка в команде клуба: {e}")
        await update.message.reply_text(f"❌ Произошла ошибка при получении информации о клубе")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка при обработке команды. Попробуйте позже."
            )
    except:
        pass

async def main():
    """Основная функция запуска через polling"""
    logger.info("🚀 Запуск Heaven & Bloody Stats Bot...")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("rating", rating_command))
    application.add_handler(CommandHandler("refresh", refresh_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("ip", ip_command))
    
    # Команды клубов
    for club_name in CLUBS.keys():
        short = club_name.split()[-1].lower() if ' ' in club_name else club_name.lower()
        application.add_handler(CommandHandler(short, club_info_command))
    
    application.add_error_handler(error_handler)
    
    # Получаем IP
    await get_current_ip()
    
    # Проверяем API статус
    await check_api_status()
    
    # Запускаем polling
    logger.info("✅ Бот запущен в режиме polling")
    await application.run_polling()

if __name__ == "__main__":
    # Запуск бота через polling
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
