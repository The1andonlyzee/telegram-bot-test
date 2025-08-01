import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    CallbackContext,
)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# Conversation state
SELECT_LOCATION = 1

# Memory storage for user location
user_location = {}

##### Dummy function to simulate database locations
# def get_locations_from_db():
    
#     print('get_location_from_db called')

#     return ["titik a", "titik b", "titik c"]

##### this for real nnti 
import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="rozzee",
        password="rozzee",
        db="testrozzee",
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

# Entry point: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("start is called")
    await update.message.reply_text("Selamat datang, silahkan set lokasi ODP menggunakan /cekodp.")

# /cekodp -> fetch locations from DB -> inline keyboard
async def cekodp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("cekodp is called")
    # locations = get_locations_from_db()
    locations = get_all_locations()
    
    if not locations:
        await update.message.reply_text("❌ Tidak ada lokasi tersedia.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in set(locations)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Silakan pilih lokasi ODP:", reply_markup=reply_markup)
    print("cekodp is finished, returning SELECT_LOCATION")
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
        print(f'{user_id} : {user_location}')
        messages = ""
        for entry in location_data:
            messages += (
                    # f"📍 Lokasi: {entry['LocationName']}\n"
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


    # await query.answer()
    # await query.edit_message_text(f"Lokasi Anda telah diset ke: {selected_location}")

    # user_location[user_id] = selected_location

    # Output template
    output_message = f"✅ Lokasi berhasil disimpan!\n\n📍 Lokasi: {selected_location}\nTerima kasih telah melakukan set lokasi."
    await query.message.reply_text(output_message)
    
    print('location_selected finished')
    return ConversationHandler.END

# /cancel to exit conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print('/cancel called')
    await update.message.reply_text("Proses dibatalkan.")
    return ConversationHandler.END

# Init app
if __name__ == '__main__':
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    print("using bottestingv4.py")

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

    print("Polling started...")
    application.run_polling()
