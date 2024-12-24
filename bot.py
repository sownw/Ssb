
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
)

# Bot token from environment variables (secure)
TOKEN = os.getenv("7342723416:AAEPV7QPSVD11dmLDRYj0KGudhUzhuoHPfA")
CHANNEL_USERNAME = "@PhantomCheatzone"  # Default channel username
SUPER_ADMIN = 2060007339  # Replace with your Telegram ID (Owner of the bot)

# Initialize SQLite database
db = sqlite3.connect("bot_data.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_users (user_id INTEGER PRIMARY KEY);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY);
""")
cursor.execute("""
INSERT OR IGNORE INTO admins (user_id) VALUES (?);
""", (SUPER_ADMIN,))
db.commit()

# Helper functions
async def is_blocked(user_id):
    cursor.execute("SELECT 1 FROM blocked_users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

async def is_admin(user_id):
    cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if await is_blocked(user.id):
        await update.message.reply_text("🚫 You are blocked from using this bot.")
        return

    welcome_message = (
        f"Hi {user.first_name}!

"
        "🌟 **Join our channel** to get exclusive rewards!

"
        f"👉 [Join our Channel](https://t.me/{CHANNEL_USERNAME})

"
        "📢 Share this bot with 5 friends to earn your free gift!"
    )
    keyboard = [[
        InlineKeyboardButton("✅ I Joined the Channel", callback_data="joined"),
        InlineKeyboardButton("🔗 Share Bot", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Admin command
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_admin(user.id):
        await update.message.reply_text("❌ You are not authorized to use admin commands.")
        return

    keyboard = [
        [InlineKeyboardButton("👤 Block User", callback_data="block_user"),
         InlineKeyboardButton("🔓 Unblock User", callback_data="unblock_user")],
        [InlineKeyboardButton("✍️ Change Channel", callback_data="change_channel"),
         InlineKeyboardButton("🛠 Manage Admins", callback_data="manage_admins")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ Admin Panel", reply_markup=reply_markup)

# Block user function
async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("👤 Send the user ID to block:")

    def block_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = int(update.message.text)
            cursor.execute("INSERT OR IGNORE INTO blocked_users (user_id) VALUES (?);", (user_id,))
            db.commit()
            update.message.reply_text(f"🚫 User {user_id} has been blocked.")
        except ValueError:
            update.message.reply_text("❌ Invalid User ID.")

    context.application.add_handler(MessageHandler(filters.TEXT & filters.PRIVATE, block_user_id), group=1)

# Unblock user function
async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔓 Send the user ID to unblock:")

    def unblock_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user_id = int(update.message.text)
            cursor.execute("DELETE FROM blocked_users WHERE user_id = ?;", (user_id,))
            db.commit()
            update.message.reply_text(f"✅ User {user_id} has been unblocked.")
        except ValueError:
            update.message.reply_text("❌ Invalid User ID.")

    context.application.add_handler(MessageHandler(filters.TEXT & filters.PRIVATE, unblock_user_id), group=2)

# Change channel dynamically
async def change_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✍️ Send the new channel username (e.g., @NewChannel):")

    def update_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global CHANNEL_USERNAME
        CHANNEL_USERNAME = update.message.text.strip()
        update.message.reply_text(f"✅ Channel updated to {CHANNEL_USERNAME}.")

    context.application.add_handler(MessageHandler(filters.TEXT & filters.PRIVATE, update_channel), group=3)

# Main function
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(block_user, pattern="block_user"))
    app.add_handler(CallbackQueryHandler(unblock_user, pattern="unblock_user"))
    app.add_handler(CallbackQueryHandler(change_channel, pattern="change_channel"))

    print("Bot is running...")
    await app.start()
    await app.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
