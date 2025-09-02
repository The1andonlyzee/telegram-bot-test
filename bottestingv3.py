import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackContext, CallbackQueryHandler, filters, ConversationHandler

# Load environment variables from .env file
load_dotenv()

# Fetch the bot token from environment variables
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# Store the location status (in memory, you can extend this to a database or file)
user_location = {}

# Simulate fetching locations from the database
def get_locations_from_db():
    return ["Location 1", "Location 2", "Location 3"]

# States for the conversation handler
SELECT_LOCATION = 1  # State where the user selects the location

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_message = (
        "Hello! I am your friendly bot here to assist you.\n\n"
        "I can help you with the following commands:\n\n"
        "/setlokasi - Set your location. Click the button to set your location if not already done.\n"
        "/cekodp - Check your location status and verify your location.\n\n"
        "Feel free to use any of the above commands. Let me know if you need assistance!"
    )
    await update.message.reply_text(intro_message)

async def setlokasi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets the user's location to the selected location."""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    # If location is selected through callback
    if context.user_data.get('selected_location'):
        location = context.user_data['selected_location']
        print(f'set to : {location}')
    else:
        print("set to default location")
        location = "default location"  # Default if no location selected

    user_location[user_id] = location  # Store the location
    await update.message.reply_text(f"Location set to: {location}" if update.message else f"Location set to: {location}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the callback query for inline buttons."""
    query = update.callback_query
    await query.answer()

    if query.data == "1":  # If the user pressed "Set Lokasi"
        await query.edit_message_text(text="You pressed the button! Now I will collect your location.")
        # Call the setlokasi function after the button press
        await setlokasi(update, context)

# Function to prompt the user to select a location
async def ceklokasi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompts the user to select a location from a list of available locations."""
    locations = get_locations_from_db()  # Fetch locations from database

    # Create buttons for each location
    keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in locations]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ask the user to select a location
    await update.message.reply_text("Please select your location:", reply_markup=reply_markup)
    return SELECT_LOCATION

async def location_selected(update: Update, context: CallbackContext) -> int:
    """Handles the location selection by the user."""
    user_id = update.callback_query.from_user.id
    selected_location = update.callback_query.data  # Get the selected location

    # Store the selected location for the user in context.user_data
    context.user_data['selected_location'] = selected_location

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Your location has been set to: {selected_location}")

    # Now call setlokasi to set the actual location in the user_location dictionary
    await setlokasi(update, context)

    return ConversationHandler.END  # End the conversation

async def cekodp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """This function checks if the user has set their location, and if not, prompts them to set it."""
    user_id = update.message.from_user.id

    # Start the checking process
    await update.message.reply_text("Checking odp...")

    # If location is not set, prompt the user to select a location
    if user_id not in user_location:
        # Start the conversation for selecting a location
        return await ceklokasi(update, context)

    else:
        # If location is already set, output a success message
        await update.message.reply_text(f"Location is already set to: {user_location[user_id]}")

    # Finish the checking process
    await update.message.reply_text("Checking odp finished.")
    return ConversationHandler.END

async def echo(update: Update, context: CallbackContext) -> None:
    """Echoes back the user's message."""
    await update.message.reply_text(update.message.text)

if __name__ == '__main__':
    print("Starting bot...")

    # Create the application with the bot token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Define the conversation handler for location selection
    location_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cekodp", cekodp)],  # Trigger /cekodp
        states={
            SELECT_LOCATION: [
                CallbackQueryHandler(location_selected),  # Handle location selection
            ],
        },
        fallbacks=[],  # No fallback in this example
    )

    # Add handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlokasi", setlokasi))  # Allow direct command for setting location

    # Add the conversation handler for location selection
    application.add_handler(location_conv_handler)

    # Add handler for button callback (this listens for inline button presses)
    application.add_handler(CallbackQueryHandler(button))

    # Add handler for messages (echoing messages)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Polling started...")

    # Start the bot (polling)
    application.run_polling()
