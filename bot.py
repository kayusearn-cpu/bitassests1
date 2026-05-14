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
BITAI_REGISTER = "https://app.bitai.com.sg/h5/#/pages/sign/sign?invite=888"
BITAI_DOWNLOAD = "https://fir.bitai.app/app.html"
WHATSAPP = "http://wa.me/6589691668"
BINANCE_REGISTER = "https://accounts.binance.com/en/register?ref=1154159582"
BINANCE_DOWNLOAD = "https://www.binance.com/en/download"
FAQ_LINK = "https://bitai.app/faq"
EMAIL_LINK = "mailto:info@bitai.app"

# We will replace these empty strings with the IDs later
VIDEOS = {
    "entry": "", 
    "step_1": "",
    "step_2": "",
    "step_3": "",
    "step_4": "",
    "step_5": "",
    "step_6": ""
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
    # ... (Other steps text/keyboards are identical to previous version, omitted for brevity but they are handled by the helper below)
}
# Just adding basic text for the other steps so the code runs while you get IDs
for i in range(1, 7):
    STEPS[f"step_{i}"] = {"text": f"This is step {i}", "keyboard": [[InlineKeyboardButton("Next", callback_data=f"step_{i+1}")]]}


# 3. Helper to send messages
async def send_step_message(chat_id: int, step_key: str, context: ContextTypes.DEFAULT_TYPE):
    step_data = STEPS.get(step_key)
    if not step_data: return
    
    reply_markup = InlineKeyboardMarkup(step_data["keyboard"])
    video_id = VIDEOS.get(step_key)
    
    if video_id:
        try:
            await context.bot.send_video(chat_id=chat_id, video=video_id, caption=step_data["text"], reply_markup=reply_markup, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Video failed: {e}")
            await context.bot.send_message(chat_id=chat_id, text=step_data['text'], reply_markup=reply_markup, parse_mode="HTML")
    else:
         await context.bot.send_message(chat_id=chat_id, text=f"[No Video Yet]\n\n{step_data['text']}", reply_markup=reply_markup, parse_mode="HTML")

# 4. Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_step_message(update.effective_chat.id, "entry", context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data in STEPS:
        try: await query.message.delete()
        except: pass
        await send_step_message(query.message.chat_id, query.data, context)

# -------------------------------------------------------------
# THIS IS THE TEMPORARY TOOL TO GET YOUR VIDEO IDs
# -------------------------------------------------------------
async def get_video_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_id = update.message.video.file_id
    await update.message.reply_text(f"Here is your Video File ID:\n\n`{video_id}`\n\nCopy this string!", parse_mode="Markdown")
# -------------------------------------------------------------

# 5. Flask Web Server
flask_app = Flask(__name__)
@flask_app.route('/')
def health_check(): return "Active"

# 6. Bot Runner
async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Register the video ID tool
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
    finally: loop.close()

if __name__ == '__main__':
    main()
