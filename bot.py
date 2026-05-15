import os
import logging
import threading
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask

# 1. Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONSTANTS & LINKS ---
BITAI_REGISTER = "https://app.bitai.com.sg/h5/#/pages/sign/sign?invite=888"
BITAI_DOWNLOAD = "https://fir.bitai.app/app.html"
WHATSAPP = "http://wa.me/6589691668"
BINANCE_REGISTER = "https://accounts.binance.com/en/register?ref=1154159582"
BINANCE_DOWNLOAD = "https://www.binance.com/en/download"
FAQ_LINK = "https://bitai.app/faq"
EMAIL_LINK = "mailto:info@bitai.app"

# 2. Step Configuration (Text, Video File IDs, and Keyboards)
STEPS = {
    "entry": {
        "video": "BAACAgQAAxkBAAIKLGoGYLkJgYymARdPzkg87KJqeqG8AAKnHwACygk4UBoeU5Ja1_HpOwQ",
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
        "video": "BAACAgQAAxkBAAIKLmoGYMf1BQVW9s08DTn-U_xztKMHAAKoHwACygk4UPpsB-FjQEYMOwQ",
        "text": (
            "<b>Step 1/6: Prepare Your Binance Account</b>\n\n"
            "To start using BitAI, you need a Binance account with KYC verification completed.\n\n"
            "Already have a verified Binance account?\n"
            "You may skip this video and continue to BitAI License Activation."
        ),
        "keyboard": [
            [InlineKeyboardButton("Create a FREE Binance account", url=BINANCE_REGISTER)],
            [InlineKeyboardButton("Download Binance (iOS & Android)", url=BINANCE_DOWNLOAD)],
            [InlineKeyboardButton("⏭ Skip to License Activation", callback_data="step_2")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_2": {
        "video": "BAACAgQAAxkBAAIKFGoGTMxEzleiVggAAcb9525_glk4DQACox8AAsoJOFAEqGixfbqjmzsE",
        "text": (
            "<b>Step 2/6: BitAI License Activation</b>\n\n"
            "To unlock BitAI’s full auto AI trading, activate your BitAI License inside your BitAI app.\n"
            "Once activated, you can proceed to activate & enable your Binance Futures."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to Activate Futures", callback_data="step_3")],
            [InlineKeyboardButton("Register my FREE BitAI account", url=BITAI_REGISTER)],
            [InlineKeyboardButton("Download BitAI (iOS & Android)", url=BITAI_DOWNLOAD)],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_3": {
        "video": "BAACAgQAAxkBAAIKMGoGYOWofd754p7DTPVOejOh-qceAAKpHwACygk4UHAbyMX5Tf9qOwQ",
        "text": (
            "<b>Step 3/6: Activate & Enable Binance Futures</b>\n\n"
            "Before BitAI can execute, you need to activate Binance Futures inside your Binance account.\n"
            "Once Futures is enabled, you can continue to the next step and create your Binance API connection."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to setting API Keys", callback_data="step_4")],
            [InlineKeyboardButton("⬅️ Back to previous step", callback_data="step_2")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_4": {
        "video": "BAACAgQAAxkBAAIKMmoGYSlkjDXaU2VkQv3G1-xtNsByAAKqHwACygk4UJHqVCnCna8NOwQ",
        "text": (
            "<b>Step 4/6: Set Up Your API Keys</b>\n\n"
            "Next, create your Binance API Keys and connect them to your BitAI account.\n\n"
            "This allows BitAI to analyze real-time market data and execute based on your selected risk profile.\n\n"
            "Make sure your API Keys are kept private and only connected inside the official BitAI platform."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to Transferring USDT", callback_data="step_5")],
            [InlineKeyboardButton("⬅️ Back to previous step", callback_data="step_3")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_5": {
        "video": "BAACAgQAAxkBAAIKNGoGYgABYtPjguv3nIzNhiFg6P7LAAOrHwACygk4ULwezjQNLPt8OwQ",
        "text": (
            "<b>Step 5/6: Transfer USDT to Binance Futures</b>\n\n"
            "Before BitAI can execute, make sure your USDT is transferred into your own Binance Futures Wallet.\n\n"
            "This will be the capital used for BitAI’s AI-driven execution based on your selected risk profile.\n\n"
            "Once completed, continue to Select Risk Profile."
        ),
        "keyboard": [
            [InlineKeyboardButton("⏭ Skip to Select Risk Profile", callback_data="step_6")],
            [InlineKeyboardButton("⬅️ Back to previous step", callback_data="step_4")],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
        ]
    },
    "step_6": {
        "video": "BAACAgQAAxkBAAIKNmoGYjJ1yi-RVkuaMROZ2Fw4fZaoAAKsHwACygk4UFjX3qv0bHZwOwQ",
        "text": (
            "<b>Step 6/6: Select Your Risk Profile</b>\n\n"
            "Choose your preferred BitAI Risk Profile based on your capital, goals, and risk appetite.\n\n"
            "BitAI will execute according to the risk level you select.\n\n"
            "Once done, BitAI will start to analyze real time market data and execute your trades 24/7 automatically!"
        ),
        "keyboard": [
            [InlineKeyboardButton("⬅️ Back to previous step", callback_data="step_5")],
            [InlineKeyboardButton("❓ Frequently Answered Questions", url=FAQ_LINK)],
            [InlineKeyboardButton("📧 Email support: info@bitai.app", url=EMAIL_LINK)],
            [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)],
            [InlineKeyboardButton("❌ Exit Conversation", callback_data="exit")]
        ]
    }
}

# 3. Endless Reminder Task
async def reminder_loop(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Background task to remind users every 6 hours endlessly."""
    try:
        while True:
            # Wait 6 hours (21600 seconds)
            await asyncio.sleep(21600)
            
            # Send the endless reminder message
            reminder_text = (
                "🔔 <b>BitAI System Reminder</b>\n\n"
                "Ensure your automated trading is fully set up and running smoothly. "
                "Don't miss out on 24/7 emotion-free execution!\n\n"
                "Click below to review the setup steps or contact our support team."
            )
            reminder_keyboard = [
                [InlineKeyboardButton("🚀 View Setup Steps", callback_data="step_1")],
                [InlineKeyboardButton("💬 Contact support", url=WHATSAPP)]
            ]
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=reminder_text,
                reply_markup=InlineKeyboardMarkup(reminder_keyboard),
                parse_mode="HTML"
            )
    except asyncio.CancelledError:
        pass # Task was cancelled properly
    except Exception as e:
        logging.error(f"Reminder loop error for {chat_id}: {e}")

# 4. Helper to send messages
async def send_step_message(chat_id: int, step_key: str, context: ContextTypes.DEFAULT_TYPE):
    step_data = STEPS[step_key]
    reply_markup = InlineKeyboardMarkup(step_data["keyboard"])
    
    try:
        await context.bot.send_video(
            chat_id=chat_id,
            video=step_data["video"],
            caption=step_data["text"],
            reply_markup=reply_markup,
            parse_mode="HTML",
            supports_streaming=True
        )
    except Exception as e:
        logging.error(f"Error sending video for {step_key}: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"<b>Notice:</b> Video loading... Please wait.\n\n{step_data['text']}",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# 5. Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Initialize chat data dictionary if not exists
    if chat_id not in context.application.chat_data:
        context.application.chat_data[chat_id] = {}

    # Start the endless 6-hour reminder loop ONLY if it hasn't been started already for this user
    if not context.application.chat_data[chat_id].get("reminder_active", False):
        context.application.chat_data[chat_id]["reminder_active"] = True
        asyncio.create_task(reminder_loop(chat_id, context))

    await send_step_message(chat_id, "entry", context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    
    if query.data == "exit":
        await query.message.delete()
        await context.bot.send_message(chat_id=chat_id, text="Onboarding closed. Type /start to begin again.")
        return

    if query.data in STEPS:
        try:
            await query.message.delete()
        except:
            pass
        await send_step_message(chat_id, query.data, context)

# 6. Flask Health Check
flask_app = Flask(__name__)
@flask_app.route('/')
def health(): return "Bot is running with Endless Reminders & File IDs"

# 7. Runner
async def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

def main():
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))), daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
