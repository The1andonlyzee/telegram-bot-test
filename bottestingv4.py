import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    CallbackContext,)
import pymysql

# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)

load_dotenv()
TELEGRAM_TOKEN  = os.getenv("BOT_TOKEN")
MYSQL_HOST      = os.getenv("MYSQL_HOST")
MYSQL_USER      = os.getenv("MYSQL_USER")
MYSQL_PASS      = os.getenv("MYSQL_PASS")
MYSQL_DB        = os.getenv("MYSQL_DB")


SELECT_LOCATION = 1
NAVIGATE = 2
user_location = {}

def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        db=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_location_data(location_name):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM odptable WHERE LocationName = %s"
            cursor.execute(sql, (location_name,))
            result = cursor.fetchall()
            return result
    finally:
        conn.close()

def get_all_locations():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT LocationName FROM odptable"
            cursor.execute(sql)     
            results = cursor.fetchall()
            return [row["LocationName"] for row in results]
    finally:
        conn.close()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print('-'*10 + "start is called" + '-'*10 ) # debugging
    await update.message.reply_text("Selamat datang, silahkan set lokasi ODP menggunakan /cekodp.")

# Helper function to show location selection
async def show_location_selection(update: Update, is_callback=False) -> int:
    print('-'*10 + "show_location_selection called" + '-'*10 ) # debugging
    locations = get_all_locations()
    
    if not locations:
        message = "❌ Tidak ada lokasi tersedia."
        if is_callback:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in set(locations)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "Silakan pilih lokasi ODP:"

    if is_callback:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    print('-'*10 + "show_location_selection finished, returning SELECT_LOCATION" + '-'*10 ) # debugging
    return SELECT_LOCATION


# /cekodp -> fetch locations from DB -> inline keyboard
async def cekodp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print('-'*10 + "cekodp is called" + '-'*10 ) # debugging
    return await show_location_selection(update, is_callback=False)

# Inline keyboard callback
async def location_selected(update: Update, context: CallbackContext) -> int:
    
    print('-'*10 + 'location_selected called'+ '-'*10)
    
    query = update.callback_query
    user_id = query.from_user.id
    selected_location = query.data
    location_data = get_location_data(selected_location)

    if location_data:
        user_location[user_id] = location_data
#        print(f'{user_id} : {user_location}') # debugging
        messages = ""
        for entry in location_data:
            messages += (
                    f"🔌 ODC Code: {entry['ODCCode']}\n"
                    f"📡 ODP Code: {entry['ODPCode']}\n"
                    f"🔟 Total Port: {entry['ODPTotalPort']}\n"
                    f"🟢 Port Tersedia: {entry['ODPAvailablePort']}\n\n"
                )
        print(f'final messages : {messages}')
        # Create navigation keyboard
        keyboard = [
            [InlineKeyboardButton("🔄 Pilih Lokasi Lain", callback_data="back_to_locations")],
            [InlineKeyboardButton("❌ Selesai", callback_data="finish")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.answer()
        await query.edit_message_text("Lokasi berhasil diset.")
        await query.message.reply_text(
            f"📍 Lokasi: {selected_location}\n\n{messages}", 
            reply_markup=reply_markup
        )
        return NAVIGATE
    else:
        await query.message.reply_text("❌ Lokasi tidak ditemukan di database.")

    print('-'*10 +'location_selected finished'+ '-'*10 ) # debugging
    return ConversationHandler.END

async def handle_navigation(update: Update, context: CallbackContext) -> int:
    print('-'*10 + 'handle_navigation called'+ '-'*10)
    
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_locations":
        # Go back to location selection using the helper function
        return await show_location_selection(update, is_callback=True)
        
    elif query.data == "finish":
        # End conversation
        await query.edit_message_text("✅ Terima kasih!")
        return await cancel(update, context)
    
    return ConversationHandler.END

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print('-'*10 + '/cancel called'+ '-'*10) # debugging
    
    # Handle both regular messages and callback queries
    if update.callback_query:
        # This was called from a button press, send a new message
        await update.callback_query.message.reply_text("Proses dibatalkan. Gunakan /cancel kapan saja untuk membatalkan operasi.")
    else:
        # This was called from a command
        await update.message.reply_text("Proses dibatalkan. Gunakan /cancel kapan saja untuk membatalkan operasi.")
    
    return ConversationHandler.END

# Init app
if __name__ == '__main__':
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    print('-'*10 + "using bottestingv4.py"+'-'*10) # debugging

    # Conversation handler for cekodp
    location_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cekodp", cekodp)],
        states={
            SELECT_LOCATION: [CallbackQueryHandler(location_selected)],
            NAVIGATE: [CallbackQueryHandler(handle_navigation)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(location_conv_handler)
    application.add_handler(CommandHandler("cancel", cancel))

    print('-'*10 +"Polling started..."+'-'*10 ) # debugging
    application.run_polling()
