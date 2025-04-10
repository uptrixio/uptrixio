import os
import secrets
import time
from werkzeug.utils import secure_filename
from flask import current_app
import telegram
from telegram.constants import ParseMode
import asyncio

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
        return False
    if not chat_id or chat_id == 'YOUR_CHAT_ID_HERE':
        return False

    try:
        bot = telegram.Bot(token=token)
        message = f"Your login code for uptrix\\.io: `{otp_code}`\nThe code is valid for 5 minutes\\."

        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2)

        return True
    except telegram.error.TelegramError as e:
        return False
    except Exception as e:
        return False