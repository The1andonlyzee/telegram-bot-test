import os
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


load_dotenv()
TELEGRAM_TOKEN  = os.getenv("BOT_TOKEN")
MYSQL_HOST      = os.getenv("MYSQL_HOST")
MYSQL_USER      = os.getenv("MYSQL_USER")
MYSQL_PASS      = os.getenv("MYSQL_PASS")
MYSQL_DB        = os.getenv("MYSQL_DB")


SELECT_LOCATION = 1
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
    print("start is called") # debugging
    await update.message.reply_text("Selamat datang, silahkan set lokasi ODP menggunakan /cekodp.")

# /cekodp -> fetch locations from DB -> inline keyboard
async def cekodp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("cekodp is called") # debugging
    locations = get_all_locations()
    
    if not locations:
        await update.message.reply_text("❌ Tidak ada lokasi tersedia.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in set(locations)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Silakan pilih lokasi ODP:", reply_markup=reply_markup)
    print("cekodp is finished, returning SELECT_LOCATION") # debuging
    return SELECT_LOCATION

# Inline keyboard callback
async def location_selected(update: Update, context: CallbackContext) -> int:
    
    print('location_selected called')
    
    query = update.callback_query
    user_id = query.from_user.id
    selected_location = query.data
    location_data = get_location_data(selected_location)

    if location_data:
        user_location[user_id] = location_data
        print(f'{user_id} : {user_location}') # debugging
        messages = ""
        for entry in location_data:
            messages += (
                    f"🔌 ODC Code: {entry['ODCCode']}\n"
                    f"📡 ODP Code: {entry['ODPCode']}\n"
                    f"🔟 Total Port: {entry['ODPTotalPort']}\n"
                    f"🟢 Port Tersedia: {entry['ODPAvailablePort']}\n\n"
                )
        print(f'final messages : {messages}')
        await query.answer()
        await query.edit_message_text("Lokasi berhasil diset.")
        await query.message.reply_text(f"📍 Lokasi: {selected_location}\n\n{messages}")
    else:
        await query.message.reply_text("❌ Lokasi tidak ditemukan di database.")

    print('location_selected finished') # debugging
    return ConversationHandler.END

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print('/cancel called') # debugging
    await update.message.reply_text("Proses dibatalkan.")
    return ConversationHandler.END

# Init app
if __name__ == '__main__':
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    print("using bottestingv4.py") # debugging

    # Conversation handler for cekodp
    location_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("cekodp", cekodp)],
        states={SELECT_LOCATION: [CallbackQueryHandler(location_selected)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(location_conv_handler)
    application.add_handler(CommandHandler("cancel", cancel))

    print("Polling started...") # debugging
    application.run_polling()
