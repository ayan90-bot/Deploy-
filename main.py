import os
import time
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Environment variables (set in Render dashboard)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

premium_keys = {}   # {key: expire_timestamp}
premium_users = {}  # {user_id: expire_timestamp}

# ---------------- Telegram Bot Handlers ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome!\n"
        "🔑 Use your premium key to activate premium features: /key <key>"
    )

async def genk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /genk <days>")
        return

    days = int(context.args[0])
    key = f"PREMIUM-{int(time.time())}"
    expire = int(time.time()) + days * 86400
    premium_keys[key] = expire
    await update.message.reply_text(
        f"✅ Premium key generated:\n`{key}`\nValid for {days} day(s)",
        parse_mode="Markdown"
    )

async def key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /key <key>")
        return

    key_val = context.args[0]
    if key_val in premium_keys:
        expire = premium_keys.pop(key_val)
        premium_users[update.effective_user.id] = expire
        await update.message.reply_text(
            f"🎉 Premium activated!\nValid until: {time.ctime(expire)}"
        )
    else:
        await update.message.reply_text("❌ Invalid or expired key.")

async def checkpremium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in premium_users and premium_users[uid] > time.time():
        await update.message.reply_text(
            f"✅ You are premium until: {time.ctime(premium_users[uid])}"
        )
    else:
        await update.message.reply_text("❌ You are not premium.")

# ---------------- Flask Health Server ----------------
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot is running!", 200

# ---------------- Run Telegram Bot in Separate Thread ----------------
def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genk", genk))
    app.add_handler(CommandHandler("key", key))
    app.add_handler(CommandHandler("checkpremium", checkpremium))

    app.run_polling()

if __name__ == "__main__":
    # Start bot in thread
    threading.Thread(target=run_bot).start()

    # Run Flask server for Render health check
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
