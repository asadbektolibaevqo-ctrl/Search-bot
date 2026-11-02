import asyncio
import logging
import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# --- LOGIRASH SOZLAMALARI ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- KONFIGURATSIYA ---
API_ID = 37881267
API_HASH = "fd1edeb73b34fa0955df2a06f31620fd"
BOT_TOKEN = "9214605810:AAEqIRIy93JA0qk4k792iRnTp"

MAIN_ADMIN_ID = 0  # Telegram ID-ingizni kiriting
MY_CHANNEL_USERNAME = "siznin_kanaliniz"  # Kanalingiz username-i
KEYWORDS = ["Nukus", "Kungrad", "Kegeyli", "Shimbay"]

# SMM Panel API Sozlamalari
smm_config = {
    "url": "https://smm-panel-provider.com/api/v2",
    "key": "YOUR_SMM_API_KEY",
    "service_id": "123",
    "amount": 5000
}

# --- RENDER WEB SERVICE UCHUN PORT DUMMY SERVER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Bot is running")

def run_dummy_server():
    # Render avtomatik ajratadigan PORT ni oladi (standart 10000)
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info(f"Web server port {port} da ishga tushdi.")
    server.serve_forever()

# --- PYROGRAM KLIENTINI YARATISH ---
app = Client(
    "search_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- BOT HANDLERLARI VA LOGIKASI ---

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("🔍 Qidiruvni tekshirish"), KeyboardButton("📊 Status")],
            [KeyboardButton("⚙️ Sozlamalar")]
        ],
        resize_keyboard=True
    )
    await message.reply_text(
        f"Xush kelibsiz! Telegram Search Booster Bot ish faoliyatida.\n\n"
        f"Kanal: @{MY_CHANNEL_USERNAME}\n"
        f"Kalit so'zlar: {', '.join(KEYWORDS)}",
        reply_markup=keyboard
    )

@app.on_message(filters.command("ping") | filters.regex("📊 Status"))
async def ping_cmd(client: Client, message: Message):
    await message.reply_text("<b>Pong! Bot Render Web Service platformasida faol ishlamoqda.</b>")

@app.on_message(filters.regex("🔍 Qidiruvni tekshirish"))
async def check_search(client: Client, message: Message):
    await message.reply_text("Qidiruv pozitsiyalari va kalit so'zlar bo'yicha tahlil boshlandi...")

def order_smm_boost():
    try:
        payload = {
            "key": smm_config["key"],
            "action": "add",
            "service": smm_config["service_id"],
            "link": f"https://t.me/{MY_CHANNEL_USERNAME}",
            "quantity": smm_config["amount"]
        }
        response = requests.post(smm_config["url"], data=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"SMM Panel xatoligi: {e}")
        return None

# --- MAIN ISHGA TUSHIRISH (Asyncio Event Loop) ---
async def main():
    # Web Service uchun fonda kichik HTTP serverni yuritish (Render talabi)
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    async with app:
        logger.info(">>> Telegram Search Bot muvaffaqiyatli ishga tushdi va 24/7 rejimida ishlamoqda! <<<")
        await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
