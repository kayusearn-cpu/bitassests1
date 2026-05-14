import os
import logging
import threading
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from flask import Flask

# 1. Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- LINKS & CONSTANTS ---
BASE_GH_URL = "https://raw.githubusercontent.com/kayusearn-cpu/bitassests/main/"
BITAI_REGISTER = "https://app.bitai.com.sg/h5/#/pages/sign/sign?invite=888"
BITAI_DOWNLOAD = "https://fir.bitai.app/app.html"
WHATSAPP = "http://wa.me/6589691668"
BINANCE_REGISTER = "https://accounts.binance.com/en/register?ref=1154159582"
BINANCE_DOWNLOAD = "https://www.binance.com/en/download"
FAQ_LINK = "https://bitai.app/faq"
EMAIL_LINK = "mailto:info@bitai.app"

# --- VIDEO IDS & FALLBACKS ---
# When you get the other IDs, paste them inside the quotes below.
VIDEOS = {
    "entry": "BAACAgQAAxkBAAIKFGoGTMxEzleiVggAAcb9525_glk4DQACox8AAsoJOFAEqGixfbqjmzsE", 
    "step_1": f"{BASE_GH_URL}1.%20Setting%20up%20Binance%20Account.mp4",
    "step_2": "https://raw.githubusercontent.com/kayusearn-cpu/bitassests1/main/2.%20License%20activation%20(1).mp4",
    "step_3": f"{BASE_GH_URL}3.%20Activating%20Enabling%20Futures.mp4",
    "step_4": f"{BASE_GH_URL}4.%20Creating%20API%20Keys.mp4",
    "step_5": f"{BASE_GH_URL}5.%20Transferring%20USDT%20to%20futures.mp4",
    "step_6": f"{BASE_GH_URL}6.%20Select%20Risk%20Profile.mp4"
}

# 2. Content Dictionary
STEPS = {
    "entry": {
        "text": (
            "🚀 <b>Welcome to BitAI by Affinity AI</b>\n\n"
            "Most crypto traders don’t lose because they lack knowledge. "
            "They lose because manual trading is emotional, bot settings are messy, and execution comes too late.\n\n"
            "It’s time to upgrade to BitAI - built to analyze real-time market data and execute your trades automatically, 24/7."
        ),
        "keyboard": [
            [InlineKeyboardButton("Register my FREE BitAI account", url=BITAI_REGISTER)],
            [InlineKeyboardButton("Download BitAI (iOS & Android)", url=BITAI_DOWNLOAD)],
            [InlineKeyboardButton("🎥 BitAI Setup Video", callback_data="step_1")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_1": {
        "text": (
            "<b>Step 1/6: Prepare Your Binance Account</b>\n\n"
            "To start using BitAI, you need a Binance account with KYC verification completed.\n\n"
            "Already have a verified Binance account? You may skip this video."
        ),
        "keyboard": [
            [InlineKeyboardButton("Create a FREE Binance account", url=BINANCE_REGISTER)],
            [InlineKeyboardButton("Download Binance (iOS & Android)", url=BINANCE_DOWNLOAD)],
            [InlineKeyboardButton("⏭ Skip to License Activation", callback_data="step_2")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_2": {
        "text": (
            "<b>Step 2/6: BitAI License Activation</b>\n\n"
            "To unlock BitAI’s full auto AI trading, activate your BitAI License inside your BitAI app."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to Activating Futures", callback_data="step_3")],
            [InlineKeyboardButton("Register my FREE BitAI account", url=BITAI_REGISTER)],
            [InlineKeyboardButton("Download BitAI (iOS & Android)", url=BITAI_DOWNLOAD)],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_3": {
        "text": (
            "<b>Step 3/6: Activate & Enable Binance Futures</b>\n\n"
            "Before BitAI can execute, you need to activate Binance Futures inside your Binance account."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to setting API Keys", callback_data="step_4")],
            [InlineKeyboardButton("⬅️ Back", callback_data="step_2")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_4": {
        "text": (
            "<b>Step 4/6: Set Up Your API Keys</b>\n\n"
            "Next, create your Binance API Keys and connect them to your BitAI account."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to Transferring USDT", callback_data="step_5")],
            [InlineKeyboardButton("⬅️ Back", callback_data="step_3")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_5": {
        "text": (
            "<b>Step 5/6: Transfer USDT to Binance Futures</b>\n\n"
            "Make sure your USDT is transferred into your own Binance Futures Wallet."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to Select Risk Profile", callback_data="step_6")],
            [InlineKeyboardButton("⬅️ Back", callback_data="step_4")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_6": {
        "text": (
            "<b>Step 6/6: Select Your Risk Profile</b>\n\n"
            "Choose your preferred BitAI Risk Profile based on your capital and goals."
        ),
        "keyboard": [
            [InlineKeyboardButton("⬅️ Back", callback_data="step_5")],
            [InlineKeyboardButton("❓ FAQ", url=FAQ_LINK)],
            [InlineKeyboardButton("📧 Email support", url=EMAIL_LINK)],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)],
            [InlineKeyboardButton("❌ Exit Conversation", callback_data="exit")]
        ]
    }
}

# 3. Helper to send messages
async def send_step_message(chat_id: int, step_key: str, context: ContextTypes.DEFAULT_TYPE):
    step_data = STEPS.get(step_key)
    if not step_data: return
    
    reply_markup = InlineKeyboardMarkup(step_data["keyboard"])
    video_source = VIDEOS.get(step_key)
    
    try:
        await context.bot.send_video(
            chat_id=chat_id,
            video=video_source,
            caption=step_data["text"],
            reply_markup=reply_markup,
            parse_mode="HTML",
            supports_streaming=True
        )
    except Exception as e:
        logging.error(f"Video failed for {step_key}: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"[Video Unavailable]\n\n{step_data['text']}",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# 4. Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_step_message(update.effective_chat.id, "entry", context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "exit":
        await query.message.delete()
        await context.bot.send_message(chat_id=query.message.chat_id, text="Setup closed. Type /start to begin again.")
        return
    if query.data in STEPS:
        try: await query.message.delete()
        except: pass
        await send_step_message(query.message.chat_id, query.data, context)

async def get_video_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_id = update.message.video.file_id
    await update.message.reply_text(f"Your File ID:\n\n`{video_id}`", parse_mode="Markdown")

# 5. Flask
flask_app = Flask(__name__)
@flask_app.route('/')
def health(): return "OK"

# 6. Run
async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.VIDEO, get_video_id))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

def main():
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try: loop.run_until_complete(run_bot())
    except KeyboardInterrupt: pass

if __name__ == '__main__':
    main()
