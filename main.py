import os
import asyncio
import tracemalloc
from typing import Dict, List, Tuple
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Включаем tracemalloc для отслеживания памяти
tracemalloc.start()

# Токены и настройки
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU')

# API ключ Brawl Stars
BRAWL_API_KEY = os.getenv('BRAWL_API_KEY', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjA2N2YwYTJkLWZhNzgtNDMxMy1iMTYyLTk4ZTEwZWYyNjJkZSIsImlhdCI6MTc2OTc4NzQ5Nywic3ViIjoiZGV2ZWxvcGVyLzIyODI2ZDRhLTdmNjMtNzI1NC00ZTVjLTg5NDg4YzM4ZGYyMiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiNzQuMjIwLjQ5LjI1MyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.PafSMrgWOEjwfQ3nFrKLXUk3AL3ape4er_VWwfOqmTt8O2F78klujR-WD0pHOtnbUOR-73Y1JuAfqqg74BmdfQ')

BRAWL_API_PROXY = "https://heavenly-brawl-proxy.workers.dev"

# Данные клубов
CLUBS = {
    "Heaven Karma": "#JYGVQR89",
    "Heaven Moscow": "#JG2GPJ9Q",
    "Heaven Fortress": "#C0JJC0L2",
    "Heaven Hell": "#C0QQ8RV0",
    "Heaven KE": "#2Q2QVYGU8",
    "Heaven Leo": "#2C29U8Q8P",
    "Heaven Cucumber": "#JG9U8U82",
    "Heaven Temple": "#80LPG8V8L",
    "Heaven Kingdom": "#2C2YLRCCU",
    "Heaven Dream": "#2LQ2UV0LJ",
    "Heaven Winter": "#2LCUY0Q8G",
    "Heaven Envoy": "#JYR0YRR2",
    "Heaven Dominion": "#80LQRCR0J",
    "Heaven Sakura": "#2Q082VC08",
    "Heaven Vinland": "#2VJRV89JG",
    "Heaven Infinity": "#2VCLRRYCV",
    "Heaven Reverse": "#JGYRPPPY",
    "Heaven Tomatoes": "#2LC9JVQLJ",
    "Heaven Thunder": "#2CLQ2RPL8",
    "Heaven Curse": "#2LGRGCL9U",
    "Bloody Legion": "#2YPYJC88J",
    "Bloody Justice": "#2VCU8J9CV",
    "Bloody Valley": "#2VUURGQLR",
    "Bloody Requiem": "#2Y89QRGQU",
    "Bloody Cards": "#2JQURGVRG"
}

# Сессия для HTTP запросов
session = None

async def get_club_data(club_tag: str) -> Dict:
    """Получение данных клуба через API"""
    global session
    if session is None:
        session = aiohttp.ClientSession()
    
    try:
        # Убираем # из тега для URL
        clean_tag = club_tag.replace('#', '')
        url = f"{BRAWL_API_PROXY}/clubs/%23{clean_tag}/"
        headers = {"Authorization": f"Bearer {BRAWL_API_KEY}"}
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Ошибка API для {club_tag}: {response.status}")
                return None
    except Exception as e:
        print(f"Ошибка при запросе {club_tag}: {e}")
        return None

async def get_all_clubs_data() -> List[Tuple[str, str, Dict]]:
    """Получение данных всех клубов"""
    tasks = []
    for name, tag in CLUBS.items():
        tasks.append(get_club_data(tag))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    clubs_data = []
    for (name, tag), data in zip(CLUBS.items(), results):
        if data and not isinstance(data, Exception):
            clubs_data.append((name, tag, data))
        else:
            print(f"Не удалось получить данные для {name}: {data}")
    
    # Сортировка по количеству трофеев (от большего к меньшему)
    clubs_data.sort(key=lambda x: x[2].get('trophies', 0), reverse=True)
    return clubs_data

def generate_pagination_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Генерация клавиатуры для пагинации"""
    buttons = []
    
    if page > 0:
        buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page-1}"))
    
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"page_{page+1}"))
    
    return InlineKeyboardMarkup([buttons]) if buttons else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_text = """🎮 *Добро пожаловать в Heaven & Bloody Stats Bot!*
    
📊 Я предоставляю статистику клубов Heaven и Bloody.
    
*📋 Основные команды:*
/rating - Рейтинг всех клубов
/help - Помощь и информация

*🔗 Полезные ссылки:*
▶️ ПРАВИЛА: https://t.me/c/2565122949/1/674535
▶️ ЧЁРНЫЙ СПИСОК: https://t.me/+8ISCeRkWfz40YzZi
▶️ АЛЬЯНСЫ: https://t.me/+BOHHdvr04D5kZmRi
▶️ ЛЕГЕНДЫ: https://t.me/+t-dkJTsbwr1hN2Vi

_Для подробной информации о клубе используйте команды вида /Sakura, /Leo и т.д._"""
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /info"""
    info_text = """*📖 Информация о боте*
    
Этот бот предоставляет актуальную статистику клубов Heaven и Bloody из Brawl Stars.
    
*📊 Доступные функции:*
• Рейтинг всех клубов
• Подробная информация о каждом клубе
• Автоматическое обновление данных
    
*⚡ Команды:*
/start - Начальное приветствие
/rating - Полный рейтинг клубов
/info - Эта информация
/help - Помощь
/[ИмяКлуба] - Подробности о клубе
    
_Пример: /Sakura, /Leo, /Karma_"""
    
    await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)

async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> None:
    """Отображение рейтинга клубов"""
    try:
        clubs_data = await get_all_clubs_data()
        
        if not clubs_data:
            await update.message.reply_text("❌ Не удалось получить данные клубов")
            return
        
        # Пагинация: 10 клубов на страницу
        clubs_per_page = 10
        total_pages = (len(clubs_data) + clubs_per_page - 1) // clubs_per_page
        
        if page >= total_pages:
            page = 0
        
        start_idx = page * clubs_per_page
        end_idx = min(start_idx + clubs_per_page, len(clubs_data))
        
        # Формирование сообщения
        message_text = f"🏆 *Рейтинг клубов* (Страница {page + 1}/{total_pages})\n\n"
        
        for i, (name, tag, data) in enumerate(clubs_data[start_idx:end_idx], start=1):
            position = start_idx + i
            trophies = data.get('trophies', 0)
            members = data.get('members', [])
            member_count = len(members) if members else 0
            
            # Извлекаем короткое имя для команды
            short_name = name.split()[-1] if ' ' in name else name
            command_name = short_name.lower()
            
            message_text += f"{position}) *{name}*\n"
            message_text += f"   🏆 {trophies:,}/{member_count}\n"
            message_text += f"   ℹ️ Подробнее: /{command_name}\n\n"
        
        # Отправка сообщения
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=generate_pagination_keyboard(page, total_pages)
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(
                text=message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=generate_pagination_keyboard(page, total_pages)
            )
    except Exception as e:
        print(f"Ошибка в rating: {e}")
        await update.message.reply_text("❌ Ошибка при получении рейтинга")

async def page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки пагинации"""
    query = update.callback_query
    await query.answer()
    
    try:
        page = int(query.data.split('_')[1])
        await rating(update, context, page)
    except Exception as e:
        print(f"Ошибка в page_callback: {e}")
        await query.edit_message_text("❌ Ошибка при переключении страницы")

async def club_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команд вида /Sakura, /Leo и т.д."""
    try:
        club_command = update.message.text[1:].lower()  # Убираем слэш
        
        # Поиск клуба по короткому имени
        found_club = None
        club_tag = None
        
        for name, tag in CLUBS.items():
            short_name = name.split()[-1].lower() if ' ' in name else name.lower()
            if club_command == short_name.lower():
                found_club = name
                club_tag = tag
                break
        
        if not found_club:
            await update.message.reply_text(f"❌ Клуб с командой /{club_command} не найден")
            return
        
        # Получение данных клуба
        data = await get_club_data(club_tag)
        
        if not data:
            await update.message.reply_text(f"❌ Не удалось получить данные для {found_club}")
            return
        
        # Формирование детальной информации
        trophies = data.get('trophies', 0)
        required_trophies = data.get('requiredTrophies', 0)
        members = data.get('members', [])
        member_count = len(members) if members else 0
        description = data.get('description', 'Нет описания')
        tag = data.get('tag', club_tag)
        
        # Топ-5 игроков по трофеям
        top_players = ""
        if members:
            sorted_members = sorted(members, key=lambda x: x.get('trophies', 0), reverse=True)[:5]
            for j, player in enumerate(sorted_members, 1):
                top_players += f"{j}. {player.get('name', 'Unknown')} - 🏆 {player.get('trophies', 0):,}\n"
        
        message_text = f"*🏰 {found_club}*\n\n"
        message_text += f"*📊 Общая статистика:*\n"
        message_text += f"🏆 Трофеи клуба: {trophies:,}\n"
        message_text += f"👥 Участников: {member_count}\n"
        message_text += f"🎯 Необходимо трофеев: {required_trophies:,}\n"
        message_text += f"🔖 Тег: {tag}\n\n"
        
        message_text += f"*📝 Описание:*\n{description}\n\n"
        
        if top_players:
            message_text += f"*👑 Топ-5 игроков:*\n{top_players}"
        
        await update.message.reply_text(message_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"Ошибка в club_info: {e}")
        await update.message.reply_text("❌ Ошибка при получении информации о клубе")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    error_msg = str(context.error) if context.error else "Неизвестная ошибка"
    print(f"Ошибка: {error_msg}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    except:
        pass

async def cleanup() -> None:
    """Очистка ресурсов"""
    global session
    if session:
        await session.close()
        session = None

async def main() -> None:
    """Основная функция запуска бота"""
    application = None
    try:
        print("Запуск бота...")
        
        # Проверяем наличие токена
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == '8529987392:AAELJdw9sPpk4F2BiByLNPzPYoUAtwSVpuU':
            print("⚠️  Используется тестовый токен Telegram")
        
        # Создание приложения
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("info", info))
        application.add_handler(CommandHandler("rating", rating))
        application.add_handler(CommandHandler("help", info))
        
        # Регистрация динамических команд для каждого клуба
        for name in CLUBS.keys():
            short_name = name.split()[-1].lower() if ' ' in name else name.lower()
            application.add_handler(CommandHandler(short_name, club_info))
        
        # Регистрация обработчика пагинации
        application.add_handler(CallbackQueryHandler(page_callback, pattern=r"^page_\d+$"))
        
        # Регистрация обработчика ошибок
        application.add_error_handler(error_handler)
        
        # Запуск бота
        print("✅ Бот успешно запущен и ожидает сообщений...")
        print("📊 Мониторинг памяти включен через tracemalloc")
        
        await application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
        
    except asyncio.CancelledError:
        print("Получен сигнал отмены...")
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске бота: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    finally:
        print("Очистка ресурсов...")
        await cleanup()
        
        # Отображение информации о памяти
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')[:10]
        
        print("\n📈 Топ-10 использования памяти:")
        for stat in top_stats:
            print(f"{stat}")
        
        tracemalloc.stop()
        print("✅ Очистка завершена")

if __name__ == "__main__":
    asyncio.run(main())
