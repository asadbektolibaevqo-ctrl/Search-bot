import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# --- PYTHON 3.14+ EVENT LOOP FIX ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- BOSH LANG'ICH SOZLAMALAR ---
API_ID = 37881267
API_HASH = "fd1edeb73b34fa0955df2a06f31620fd"
BOT_TOKEN = "9214605810:AAEqIR1y93JA0qk4k792iRnTpq9ItO8quk4"

# Чтение STRING_SESSION напрямую из Render Environment Variables
STRING_SESSION = os.environ.get("STRING_SESSION")

MAIN_ADMIN_ID = 8660278027  # Telegram ID'ingiz

BOT_CONFIG = {
    "channel_username": "siznin_kanaliniz",
    "keywords": ["Nukus", "Kungrad", "Kegeyli", "Shimbay"],
    "auto_boost": True,
    "check_interval_minutes": 15,
    "smm_url": "https://smm-panel-provider.com/api/v2",  # SMM API URL
    "smm_key": "YOUR_SMM_API_KEY",  # SMM API KEY
    "smm_service_id": "123",  # SERVICE ID
    "smm_amount": 1000,  # Avto-boost standard
}

PREVIOUS_POSITIONS = {}

# --- ИНИЦИАЛИЗА КЛИЕНТОВ ---
bot = Client("search_booster_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

userbot = None
if STRING_SESSION:
    userbot = Client("search_userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# --- МЕНЮ ТЕЛЕГРАМ ---
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🔍 Qidiruvni tekshirish"), KeyboardButton("🚀 Boost qilish")],
        [KeyboardButton("⚙️ Sozlamalar"), KeyboardButton("📊 Status")],
        [KeyboardButton("👤 Login yaratish")]
    ],
    resize_keyboard=True
)

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "👋 **Telegram Search Auto-Booster Botiga xush kelibsiz!**\n\n"
        "Menyu orqali kerakli bo'limni tanlang:",
        reply_markup=main_keyboard
    )

@bot.on_message(filters.regex("🔍 Qidiruvni tekshirish"))
async def check_search_handler(client, message):
    if userbot and userbot.is_connected:
        await message.reply_text("✅ Userbot ulangan! Qidiruv mavqeyi tekshirilmoqda...")
        # Bu yerga qidiruvni tekshirish mantiqiy kodi yoziladi
    elif userbot:
        try:
            await userbot.start()
            await message.reply_text("✅ Userbot muvaffaqiyatli ishga tushdi va ulandi!")
        except Exception as e:
            await message.reply_text(f"❌ Userbotni ulashda xatolik: {e}")
    else:
        await message.reply_text("⚠️ Userbot ulanmagan! (STRING_SESSION kiriting).")

@bot.on_message(filters.regex("🚀 Boost qilish"))
async def boost_handler(client, message):
    await message.reply_text("🚀 SMM Panel orqali boost sorovi yuborilmoqda...")

@bot.on_message(filters.regex("📊 Status"))
async def status_handler(client, message):
    status_text = "✅ **Bot Holati:** Faol (24/7)\n"
    if STRING_SESSION:
        status_text += "✅ **Userbot:** Ulangan"
    else:
        status_text += "❌ **Userbot:** Ulanmagan"
    await message.reply_text(status_text)

# --- DUMMY HTTP SERVER (Render uchun Web Service Port Fix) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# --- MAIN RUNNER ---
async def main():
    # Запуск фонового веб-сервера для Render
    threading.Thread(target=run_health_check_server, daemon=True).start()

    logger.info(">>> Telegram Search Booster Bot 24/7 rejimida ishlamoqda! <<<")
    
    if userbot:
        try:
            await userbot.start()
            logger.info("Userbot session started successfully!")
        except Exception as e:
            logger.error(f"Userbot error: {e}")

    await bot.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
