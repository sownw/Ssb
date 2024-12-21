from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# Bot token
TOKEN = "7342723416:AAEPV7QPSVD11dmLDRYj0KGudhUzhuoHPfA"
CHANNEL_USERNAME = "@PhantomCheatzone"  # Default channel username
ADMINS = [123456789]  # Replace with your Telegram ID(s) for admin access
blocked_users = set()
super_admin = 2060007339  # Replace with your Telegram ID (Owner of the bot)

# Track user referrals
user_referrals = {}

# Start command
def start(update, context):
    user = update.message.from_user
    if user.id in blocked_users:
        update.message.reply_text("🚫 You are blocked from using this bot.")
        return

    welcome_message = (
        f"Hi {user.first_name}!\n\n"
        "🌟 **Join our channel** to get exclusive rewards!\n\n"
        f"👉 [Join our Channel](https://t.me/{CHANNEL_USERNAME})\n\n"
        "📢 Share this bot with 5 friends to earn your free gift!"
    )
    keyboard = [[
        InlineKeyboardButton("✅ I Joined the Channel", callback_data="joined"),
        InlineKeyboardButton("🔗 Share Bot", url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Admin-only commands
def admin(update, context):
    user = update.message.from_user
    if user.id not in ADMINS:
        update.message.reply_text("❌ You are not authorized to use admin commands.")
        return

    keyboard = [
        [InlineKeyboardButton("👤 Block User", callback_data="block_user"),
         InlineKeyboardButton("🔓 Unblock User", callback_data="unblock_user")],
        [InlineKeyboardButton("✍️ Change Channel", callback_data="change_channel"),
         InlineKeyboardButton("🛠 Manage Admins", callback_data="manage_admins")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("⚙️ Admin Panel", reply_markup=reply_markup)

# Block user function
def block_user(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("👤 Send the user ID to block:")

    def block_user_id(update, context):
        try:
            user_id = int(update.message.text)
            blocked_users.add(user_id)
            update.message.reply_text(f"🚫 User {user_id} has been blocked.")
        except ValueError:
            update.message.reply_text("❌ Invalid User ID.")
    
    context.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, block_user_id), group=1)

# Unblock user function
def unblock_user(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("🔓 Send the user ID to unblock:")

    def unblock_user_id(update, context):
        try:
            user_id = int(update.message.text)
            if user_id in blocked_users:
                blocked_users.remove(user_id)
                update.message.reply_text(f"✅ User {user_id} has been unblocked.")
            else:
                update.message.reply_text("❌ User is not in the blocked list.")
        except ValueError:
            update.message.reply_text("❌ Invalid User ID.")

    context.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, unblock_user_id), group=2)

# Change channel dynamically
def change_channel(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("✍️ Send the new channel username (e.g., @NewChannel):")

    def update_channel(update, context):
        global CHANNEL_USERNAME
        CHANNEL_USERNAME = update.message.text.strip()
        update.message.reply_text(f"✅ Channel updated to {CHANNEL_USERNAME}.")
    
    context.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, update_channel), group=3)

# Manage admins dynamically
def manage_admins(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("✍️ Send the user ID to add/remove as admin:")

    def update_admins(update, context):
        try:
            user_id = int(update.message.text)
            if user_id in ADMINS:
                ADMINS.remove(user_id)
                update.message.reply_text(f"❌ User {user_id} removed from admin list.")
            else:
                ADMINS.append(user_id)
                update.message.reply_text(f"✅ User {user_id} added as admin.")
        except ValueError:
            update.message.reply_text("❌ Invalid User ID.")

    context.dispatcher.add_handler(MessageHandler(Filters.text & Filters.private, update_admins), group=4)

# Check if user is admin
def is_admin(user_id):
    return user_id in ADMINS or user_id == super_admin

# Callback handler
def callback_handler(update, context):
    query = update.callback_query
    user = query.from_user

    if query.data == "block_user" and is_admin(user.id):
        block_user(update, context)
    elif query.data == "unblock_user" and is_admin(user.id):
        unblock_user(update, context)
    elif query.data == "change_channel" and is_admin(user.id):
        change_channel(update, context)
    elif query.data == "manage_admins" and is_admin(user.id):
        manage_admins(update, context)
    else:
        query.answer("❌ You are not authorized to perform this action.", show_alert=True)

# Main function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin))

    # Callback handler
    dp.add_handler(CallbackQueryHandler(callback_handler))

    # Start bot
    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
    