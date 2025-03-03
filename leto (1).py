import logging
from datetime import datetime, time
from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes
from zoneinfo import ZoneInfo

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота
TOKEN = '7799105036:AAFjUNuNKKcqTZVoYzCW9mLipv8CKZjQ1_U'

# ID канала (например, @yedinstvennyy_and_nepovtorimyy)
CHANNEL_ID = '@yedinstvennyy_and_nepovtorimyy'

# Глобальный список chat_id, куда бот будет отправлять сообщения
active_chats = set()

# Функция для расчета дней до начала лета (1 июня)
def days_until_summer():
    now = datetime.now(ZoneInfo('Asia/Yekaterinburg'))  # Используем ZoneInfo
    summer_start = datetime(now.year, 6, 1, tzinfo=ZoneInfo('Asia/Yekaterinburg'))
    if now > summer_start:
        summer_start = datetime(now.year + 1, 6, 1, tzinfo=ZoneInfo('Asia/Yekaterinburg'))
    return (summer_start - now).days

# Функция для проверки подписки на канал
async def is_user_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if await is_user_subscribed(user_id, context):
        chat_id = update.message.chat_id
        active_chats.add(chat_id)  # Добавляем chat_id в список активных чатов
        await update.message.reply_text('Привет! Я буду сообщать количество дней до начала лета каждый день в 00:00 по Екатеринбургу. Также вы можете использовать команду /days, чтобы узнать количество дней до лета в любое время.')
    else:
        await update.message.reply_text('Чтобы пользоваться этим ботом, нужно подписаться на канал https://t.me/yedinstvennyy_and_nepovtorimyy')

# Команда /days
async def days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if await is_user_subscribed(user_id, context):
        chat_id = update.message.chat_id
        active_chats.add(chat_id)  # Добавляем chat_id в список активных чатов
        days = days_until_summer()
        await update.message.reply_text(f'До начала лета осталось {days} дней!')
    else:
        await update.message.reply_text('Чтобы пользоваться этим ботом, нужно подписаться на канал https://t.me/yedinstvennyy_and_nepovtorimyy')

# Функция для отправки сообщения
async def send_days_remaining(context: ContextTypes.DEFAULT_TYPE):
    days = days_until_summer()
    for chat_id in active_chats:  # Отправляем сообщение во все активные чаты
        try:
            await context.bot.send_message(chat_id=chat_id, text=f'До начала лета осталось {days} дней!')
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в чат {chat_id}: {e}")

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик команды /days
    application.add_handler(CommandHandler("days", days))

    # Планирование ежедневного сообщения
    job_queue = application.job_queue
    job_queue.run_daily(send_days_remaining, time=time(0, 0, 0, tzinfo=ZoneInfo('Asia/Yekaterinburg')))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
