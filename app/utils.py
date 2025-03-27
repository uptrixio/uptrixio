import os
import secrets
import time
from werkzeug.utils import secure_filename
from flask import current_app
import telegram
from telegram.constants import ParseMode
import logging
import asyncio

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn

def generate_slug(title):
    return title.lower().replace(' ', '-')

def generate_otp(length=6):
    return "".join(secrets.choice("0123456789") for _ in range(length))

async def send_telegram_otp(otp_code):
    token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    chat_id = current_app.config.get('TELEGRAM_ADMIN_CHAT_ID')

    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        logger.error("Telegram Bot Token не настроен в конфигурации!")
        return False
    if not chat_id or chat_id == 'YOUR_CHAT_ID_HERE':
        logger.error("Telegram Admin Chat ID не настроен в конфигурации!")
        return False

    try:
        bot = telegram.Bot(token=token)
        message = f"Ваш код для входа на uptrix\\.io: `{otp_code}`\nКод действителен 5 минут\\."

        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)

        logger.info(f"OTP {otp_code} успешно отправлен на Chat ID {chat_id}")
        return True
    except telegram.error.TelegramError as e:
        logger.error(f"Ошибка отправки OTP в Telegram: {e}")
        if hasattr(e, 'message'):
             logger.error(f"Telegram API error message: {e.message}")
        return False
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при отправке OTP: {e}")
        return False