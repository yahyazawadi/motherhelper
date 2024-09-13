from flask import Flask
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta
import pytz
import re
from collections import deque
from hijridate import Hijri, Gregorian
from typing import Final

# Initialize Flask app
app = Flask(__name__)

# Dummy route for Flask to serve
@app.route('/')
def hello_world():
    return 'Hello, World! The bot is running.'

# Your Telegram bot code below
TOKEN: Final = '6760459910:AAFUSNruwV6IFn_uZvQho-ubZJpAwXU8zig'
BOT_USERNAME: Final = '@mother_python_helper_bot'

async def start_command(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm here to help. Send me some text, and I'll process it for you.")

async def help_command(update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "You can use this bot to process text in various ways. Here's how:\n"
        "- Just send any text directly to me, and I'll do some processing on it.\n"
        "- Use /start to see the welcome message.\n"
        "- Use /help to see this message again."
    )
    await update.message.reply_text(help_text)

async def print_current_day(date: datetime) -> str:
    days_of_week = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
    return f"اليوم: {days_of_week[date.weekday()]}"

async def print_current_date(date: datetime) -> str:
    return f"الميلادي: {date.year}-{date.month}-{date.day}"

async def print_islamic_date(date: datetime) -> str:
    greg_date = Gregorian(date.year, date.month, date.day)
    hijri_date = greg_date.to_hijri()
    months = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"]
    month = months[hijri_date.month - 1]
    return f"الهجري: {hijri_date.year}-{month}-{hijri_date.day}"

def clean_arabic_strings(text):
    lines = text.split('\n')
    cleaned_lines = [line.lstrip("0123456789- ").strip() for line in lines if not line.startswith("🕋")]
    return cleaned_lines[-30:]

def rotate_strings(strings, direction):
    deque_strings = deque(strings)
    deque_strings.rotate(direction)
    return list(deque_strings)

def extract_date(text):
    date_pattern = r"الميلادي:\s*(\d{4})-(\d{1,2})-(\d{1,2})"
    match = re.search(date_pattern, text)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)
    return None

async def process_text(text: str, input_date: datetime, rotation_count: int) -> str:
    cleaned_text = clean_arabic_strings(text)
    rotated_text = rotate_strings(cleaned_text, rotation_count)
    numbered_text = [f"{idx + 1}- {line}" for idx, line in enumerate(rotated_text)]

    current_day = await print_current_day(input_date)
    current_date = await print_current_date(input_date)
    islamic_date = await print_islamic_date(input_date)

    header_and_footer = "🕋☪️🕋☪️🕋☪️🕋☪️🕋"
    return f"{header_and_footer}\n🕋ختمتي القرآن الحلبوني والفرج\n🕋{current_day}\n🕋{current_date}\n🕋{islamic_date}\n{header_and_footer}\n" + "\n".join(numbered_text)

async def handle_message(update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    input_date = extract_date(text)
    
    if not input_date:
        await update.message.reply_text("Please provide a valid date in the format 'YYYY-MM-DD'.")
        return
    
    tz = pytz.timezone('Asia/Riyadh')
    current_date = datetime.now(tz).date()
    attempts = 0

    while attempts < 10:
        next_date = input_date + timedelta(days=1 + attempts)
        processed_text = await process_text(text, next_date, rotation_count=attempts + 1)
        await update.message.reply_text(processed_text)
        
        if next_date.date() == current_date:
            break

        attempts += 1

def run_telegram_bot():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    application.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_telegram_bot()
