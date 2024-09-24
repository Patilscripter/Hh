import os
import json
import logging
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Replace with your bot owner's user ID and your bot token
bot_owner_id = 1912413450 # Replace with your Telegram user ID
premium_accounts = []
used_accounts = []
user_data = {}

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Function to check channel membership
async def check_membership(user_id, channel_username, application: Application):
    try:
        member = await application.bot.get_chat_member(channel_username, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def enforce_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    channel_username = '@GokuMethod'
    
    if not await check_membership(user_id, channel_username, context.application):
        await update.message.reply_text("You must be a member of the channel @GokuMethod to use this command. Please join the channel.")
        return False
    return True

# Command to load a single premium account from a specified file
async def load(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != bot_owner_id:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    if context.args:
        filename = context.args[0]
        filepath = f'accounts/{filename}'

        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                accounts = file.readlines()
                for account in accounts:
                    premium_accounts.append(account.strip())
            await update.message.reply_text(f"Loaded {len(accounts)} accounts from {filename}.")
        else:
            await update.message.reply_text("File not found.")

# Command to load multiple premium accounts from all text files in the directory
async def mload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != bot_owner_id:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    directory = 'accounts'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Clear old accounts
    old_count = len(premium_accounts)
    premium_accounts.clear()  # Remove all existing accounts
    total_loaded = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                accounts = file.readlines()
                total_loaded += len(accounts)
                for account in accounts:
                    premium_accounts.append(account.strip())

    await update.message.reply_text(f"Cleared {old_count} old accounts. Loaded {total_loaded} new accounts from all files.")

# Command to get a premium account
async def acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_membership(update, context):
        return

    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'invites': 0, 'claimed_accounts': [], 'last_login': datetime.now(), 'claims_today': 0}
    
    user_info = user_data[user_id]
    
    if user_info['coins'] >= 20:
        if premium_accounts:
            account = premium_accounts.pop(0)
            used_accounts.append(account)
            user_info['coins'] -= 20
            user_info['claimed_accounts'].append(account)
            user_info['claims_today'] += 1
            await update.message.reply_text(f"Here is your premium account: {account}")
        else:
            await update.message.reply_text("Sorry, no premium accounts are available right now.")
    else:
        await update.message.reply_text(f"You need at least 20 coins to use this command. You currently have {user_info['coins']} coins.")

# Command to simulate inviting users
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_membership(update, context):
        return

    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'invites': 0, 'claimed_accounts': [], 'last_login': datetime.now(), 'claims_today': 0}

    user_data[user_id]['invites'] += 1
    invites = user_data[user_id]['invites']

    if invites % 5 == 0:
        user_data[user_id]['coins'] += 20
        await update.message.reply_text(f"You have invited {invites} users! You earned 20 coins. Total coins: {user_data[user_id]['coins']}.")
    else:
        await update.message.reply_text(f"You have invited {invites} users. Keep going!")

# Command for daily rewards
async def daily_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_membership(update, context):
        return

    user_id = update.effective_user.id
    today = date.today()

    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'invites': 0, 'claimed_accounts': [], 'last_login': datetime.now(), 'claims_today': 0}

    if user_data[user_id]['last_login'].date() < today:
        user_data[user_id]['coins'] += 10
        user_data[user_id]['last_login'] = datetime.now()
        await update.message.reply_text("You received your daily reward of 10 coins!")

# Command to view account history
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_membership(update, context):
        return

    user_id = update.effective_user.id
    if user_id in user_data:
        claimed_accounts = user_data[user_id]['claimed_accounts']
        await update.message.reply_text(f"You have claimed the following accounts: {', '.join(claimed_accounts) if claimed_accounts else 'None'}")
    else:
        await update.message.reply_text("You have not claimed any accounts yet.")

# Shop command with inline keyboard
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await enforce_membership(update, context):
        return

    user
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'coins': 0, 'invites': 0, 'claimed_accounts': [], 'last_login': datetime.now(), 'claims_today': 0}
    
    keyboard = [
        [InlineKeyboardButton("Extra Account (50 coins)", callback_data='extra_acc')],
        [InlineKeyboardButton("Bonus 10 Coins (30 coins)", callback_data='bonus_10_coins')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to the shop! What would you like to buy?", reply_markup=reply_markup)

# Handle shop button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in user_data:
        if query.data == 'extra_acc':
            if user_data[user_id]['coins'] >= 50:
                user_data[user_id]['coins'] -= 50
                # Logic for granting an extra account goes here
                await query.edit_message_text(text="You have purchased an Extra Account!")
            else:
                await query.answer("Not enough coins!")
        
        elif query.data == 'bonus_10_coins':
            if user_data[user_id]['coins'] >= 30:
                user_data[user_id]['coins'] -= 30
                user_data[user_id]['coins'] += 10
                await query.edit_message_text(text="You have received 10 bonus coins!")
            else:
                await query.answer("Not enough coins!")

# Admin command for statistics
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == bot_owner_id:
        total_accounts = len(premium_accounts) + len(used_accounts)
        total_users = len(user_data)
        await update.message.reply_text(f"Total Accounts: {total_accounts}\nTotal Users: {total_users}")

# Support command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please describe your issue, and we will get back to you.")

# Feedback command
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_feedback = ' '.join(context.args)
    # Store or process the feedback as needed
    await update.message.reply_text("Thank you for your feedback!")

# Backup and restore functionality
def backup_data():
    with open('backup.json', 'w') as f:
        json.dump(user_data, f)

def restore_data():
    global user_data
    try:
        with open('backup.json', 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

# Seasonal event command
async def seasonal_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_date = datetime.now()
    if current_date.month == 12:  # Example: December promotion
        for user_id in user_data:
            user_data[user_id]['coins'] += 50  # Give all users 50 coins for the event
        await update.message.reply_text("🎉 Holiday Promotion! All users have received 50 coins! 🎉")
    else:
        await update.message.reply_text("No seasonal events currently.")

# Custom error handling
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

# Main function to run the bot
async def main():
    # Create the Application object with your bot token
    application = Application.builder().token('8008090212:AAEoBUvD4EMMMnRmIqlf5h2LqtQF0Xz9-TM').build()

    # Command handlers
    application.add_handler(CommandHandler('load', load))
    application.add_handler(CommandHandler('mload', mload))
    application.add_handler(CommandHandler('acc', acc))
    application.add_handler(CommandHandler('invite', invite))
    application.add_handler(CommandHandler('daily_reward', daily_reward))
    application.add_handler(CommandHandler('history', history))
    application.add_handler(CommandHandler('shop', shop))
    application.add_handler(CommandHandler('admin_stats', admin_stats))
    application.add_handler(CommandHandler('support', support))
    application.add_handler(CommandHandler('feedback', feedback))
    application.add_handler(CommandHandler('seasonal_event', seasonal_event))

    # Callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button))
    
    # Error handler
    application.add_error_handler(error_handler)

    # Restore user data on startup
    restore_data()

    # Start the bot
    await application.start()
    await application.updater.start_polling()

    # Block until the bot is stopped
    await application.idle()

    # Backup user data on shutdown
    backup_data()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())