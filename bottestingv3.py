import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackContext, CallbackQueryHandler, filters, ConversationHandler


# logging.basicConfig(
    # format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")


# Store the location status (in memory, you can extend this to a database or file)
user_location = {}

# simulasi doang, nnti pake dummy db dah
def get_locations_from_db():
    return ["titik a", "titik b", "titik c"]

# this for real nnti 
# import pymysql

# def get_db_connection():
#     return pymysql.connect(
#         host="localhost",
#         user="your_user",
#         password="your_password",
#         db="your_db_name",
#         cursorclass=pymysql.cursors.DictCursor
#     )

# def get_location_data(location_name):
#     conn = get_db_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = "SELECT * FROM odp_data WHERE location = %s"
#             cursor.execute(sql, (location_name,))
#             result = cursor.fetchone()
#             return result
#     finally:
#         conn.close()

# States for the conversation handler
SELECT_LOCATION = 1  # State where the user selects the location

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_message = (
        "testingbotv3.py is running\n"
        "Hello! I am your friendly bot here to assist you.\n\n"
        "I can help you with the following commands:\n\n"
        "/setlokasi - Set your location. Click the button to set your location if not already done.\n"
        "/cekodp - Check your location status and verify your location.\n\n"
        "Feel free to use any of the above commands. Let me know if you need assistance!"
    )
    await update.message.reply_text(intro_message)

async def printuserdict(update : Update, context: ContextTypes.DEFAULT_TYPE) -> None :
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    await update.message.reply_text('check cmd for debugging info')
    print(user_location)
    print(update.message.from_user.name + ": " + user_location[user_id])


async def setlokasi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets the user's location to the selected location."""
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    print(">> setlokasi is called")
    # If location is selected through callback
    if context.user_data.get('selected_location'):
        location = context.user_data['selected_location']
        print(f'set to : {location}')
    else:
        print("set to default location")
        location = "default location"  # Default if no location selected

    user_location[user_id] = location  # Store the location
    await update.message.reply_text(f"Location set to: {location}") if update.message else update.callback_query.message.reply_text(f"Location set to: {location}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the callback query for inline buttons."""
    query = update.callback_query
    await query.answer()

    if query.data == "1":  # If the user pressed "Set Lokasi"
        await query.edit_message_text(text="You pressed the button! Now I will collect your location.")
        # Call the setlokasi function after the button press
        await setlokasi(update, context)

# cek lokasi dan pilih lokasi
async def ceklokasi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompts the user to select a location from a list of available locations."""
    locations = get_locations_from_db()  # masih contoh

    # inline keyboard
    keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in locations]
    reply_markup = InlineKeyboardMarkup(keyboard)

    print(">> ceklokasi called")

    await update.message.reply_text("Please select your location:", reply_markup=reply_markup)
    return SELECT_LOCATION

async def location_selected(update: Update, context: CallbackContext) -> int:
    """Handles the location selection by the user."""
    user_id = update.callback_query.from_user.id
    selected_location = update.callback_query.data  #ambil data dari ceklokasi 
    # get_location_data(selected_location)

    print(">> location_selected called")
    # simpan datanya di context
    context.user_data['selected_location'] = selected_location
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(f"Your location has been set to: {selected_location}")

    print(">> calling setlokasi")
    # set lokasi untuk sekarang masih di dict, nntilah pindahin ke db
    await setlokasi(update, context)
    print(">> setlokasi calling finished")
    return ConversationHandler.END  

async def cekodp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """This function checks if the user has set their location, and if not, prompts them to set it."""
    user_id = update.message.from_user.id

    await update.message.reply_text("Checking odp...") # debugging 

    if user_id not in user_location:
        return await ceklokasi(update, context)
    else:
        await update.message.reply_text(f"Location is already set to: {user_location[user_id]}")

   
    await update.message.reply_text("Checking odp finished.") # debugging
    return ConversationHandler.END

async def echo(update: Update, context: CallbackContext) -> None:
    """Echoes back the user's message."""
    await update.message.reply_text(update.message.text)

if __name__ == '__main__':
    print("Starting bottestingv3.py ...") # debugging

    # template dri githubnya 
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # handler utk select lokasi
    location_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cekodp", cekodp)],  # Trigger /cekodp
        states={
            SELECT_LOCATION: [
                CallbackQueryHandler(location_selected),  
            ],
        },
        fallbacks=[],  
    )

    # commands handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlokasi", setlokasi))  # Allow direct command for setting location
    application.add_handler(CommandHandler("printuserdict", printuserdict))  # Allow direct command for setting location
    

    # convo handler
    application.add_handler(location_conv_handler)

    # button handler
    application.add_handler(CallbackQueryHandler(button))

    # ini template utk echo not needed ji sebenarnya
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Polling started...") # utk debugging

    application.run_polling()
