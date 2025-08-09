import os
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Environment variables se values lo (Render me set karoge)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Memory storage (Render restart hone pe reset ho jayega)
premium_keys = {}   # {key: expire_timestamp}
premium_users = {}  # {user_id: expire_timestamp}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome!\n"
        "🔑 Use your premium key to activate premium features.\n"
        "Format: /key <your-key>"
    )


async def genk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin check
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    # Check args
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
        await update.message.reply_text("Usage: /key <your-key>")
        return

    key_value = context.args[0]

    if key_value in premium_keys:
        expire = premium_keys.pop(key_value)
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


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genk", genk))
    app.add_handler(CommandHandler("key", key))
    app.add_handler(CommandHandler("checkpremium", checkpremium))

    app.run_polling()


if __name__ == "__main__":
    main()
