""" ini masih setlokasi() nya dan misah dari ceklokasi() """
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackContext, CallbackQueryHandler, filters

# Load environment variables from .env file
load_dotenv()

# Fetch the bot token from environment variables
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# Store the location status (in memory, you can extend this to a database or file)
user_location = {}

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create the introductory message with links to /setlokasi and /cekodp
    intro_message = (
        "Hello! I am your friendly bot here to assist you.\n\n"
        "I can help you with the following commands:\n\n"
        "/setlokasi - Set your location. Click the button to set your location if not already done.\n"
        "/cekodp - Check your location status and verify your location.\n\n"
        "Feel free to use any of the above commands. Let me know if you need assistance!"
    )
    await update.message.reply_text(intro_message)

async def setlokasi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt the user to provide their location and store it."""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    # Simulate setting a location
    user_location[user_id] = "Some Location"  # Placeholder logic
    if update.message:
        print("this is from message")
        await update.message.reply_text(f"Location set to: {user_location[user_id]}")
    else:
        print('this is form callback_query')
        await update.callback_query.message.reply_text(f"Location set to: {user_location[user_id]}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the callback query for inline buttons."""
    query = update.callback_query
    await query.answer()

    if query.data == "1":  # If the user pressed "Set Lokasi"
        await query.edit_message_text(text="You pressed the button! Now I will collect your location.")
        await setlokasi(update, context)

async def cekodp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """This function checks if the user has set their location, and if not, prompts them to set it."""
    user_id = update.message.from_user.id

    # Start the checking process
    await update.message.reply_text("Checking odp...")

    # If location is not set, prompt the user to set it using the inline keyboard
    if user_id not in user_location:
        keyboard = [
            [InlineKeyboardButton("Set Lokasi", callback_data="1")]  # Button to trigger location setting
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please set your location first.", reply_markup=reply_markup)
    else:
        # If location is already set, output a success message
        await update.message.reply_text("Location is already set.")

    # Finish the checking process
    await update.message.reply_text("Checking odp finished.")

async def echo(update: Update, context: CallbackContext) -> None:
    """Echoes back the user's message."""
    await update.message.reply_text(update.message.text)

if __name__ == '__main__':
    print("Starting bot...")

    # Create the application with the bot token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlokasi", setlokasi))  # Allow direct command for setting location
    application.add_handler(CommandHandler("cekodp", cekodp))

    # Add handler for button callback (this listens for inline button presses)
    application.add_handler(CallbackQueryHandler(button))

    # Add handler for messages (echoing messages)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Polling started...")

    # Start the bot (polling)
    application.run_polling()
