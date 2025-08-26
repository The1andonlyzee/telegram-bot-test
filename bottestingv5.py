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

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    try:
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            db=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10  # 10 second timeout
        )
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def get_location_data(location_name):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM odptable WHERE LocationName = %s"
            cursor.execute(sql, (location_name,))
            result = cursor.fetchall()
            logger.info(f"Retrieved {len(result)} records for location: {location_name}")
            return result
    except pymysql.Error as e:
        logger.error(f"MySQL error in get_location_data: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_location_data: {e}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection in get_location_data: {e}")

def get_all_locations():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT DISTINCT LocationName FROM odptable ORDER BY LocationName"
            cursor.execute(sql)     
            results = cursor.fetchall()
            locations = [row["LocationName"] for row in results if row["LocationName"]]
            logger.info(f"Retrieved {len(locations)} unique locations")
            return locations
    except pymysql.Error as e:
        logger.error(f"MySQL error in get_all_locations: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_all_locations: {e}")
        return []
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection in get_all_locations: {e}")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'\n' +'=-'*12 + "start is called" + '=-'*12 ) # debugging
    await update.message.reply_text("Selamat datang, silahkan set lokasi ODP menggunakan /cekodp.")

# Helper function to show location selection
async def show_location_selection(update: Update, is_callback=False) -> int:
    print(f'\n' +'=-'*12 + "show_location_selection called" + '=-'*12 ) # debugging
    
    try:
        locations = get_all_locations()
        
        if not locations:
            error_message = "❌ Tidak ada lokasi tersedia atau terjadi masalah dengan database."
            logger.warning("No locations available or database error")
            
            if is_callback:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
            return ConversationHandler.END

        keyboard = [[InlineKeyboardButton(loc, callback_data=loc)] for loc in set(locations)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "Silakan pilih lokasi ODP:"

        if is_callback:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
        
        logger.info(f"Location selection displayed with {len(locations)} options")
        print(f'\n' +'=-'*12 + "show_location_selection finished, returning SELECT_LOCATION" + '=-'*12 ) # debugging
        return SELECT_LOCATION
        
    except Exception as e:
        logger.error(f"Error in show_location_selection: {e}")
        error_message = "❌ Terjadi kesalahan sistem. Silakan coba lagi nanti."
        
        try:
            if is_callback:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
        except Exception as reply_error:
            logger.error(f"Failed to send error message: {reply_error}")
        
        return ConversationHandler.END

# /cekodp -> fetch locations from DB -> inline keyboard
async def cekodp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'\n' +'=-'*12 + "cekodp is called" + '=-'*12 ) # debugging
    return await show_location_selection(update, is_callback=False)

# Inline keyboard callback
async def location_selected(update: Update, context: CallbackContext) -> int:
    print(f'\n' +'=-'*12 + 'location_selected called'+ '=-'*12)
    
    try:
        query = update.callback_query
        user_id = query.from_user.id
        selected_location = query.data
        
        # Validate input
        if not selected_location or len(selected_location.strip()) == 0:
            logger.warning(f"Empty location selected by user {user_id}")
            await query.answer("❌ Lokasi tidak valid")
            return ConversationHandler.END
        
        logger.info(f"User {user_id} selected location: {selected_location}")
        
        location_data = get_location_data(selected_location)

        if location_data is None:
            logger.error(f"Database error when fetching data for location: {selected_location}")
            await query.answer("❌ Terjadi kesalahan database")
            await query.edit_message_text("❌ Terjadi kesalahan saat mengakses database. Silakan coba lagi nanti.")
            return ConversationHandler.END

        if location_data:
            user_location[user_id] = location_data
            messages = ""
            
            try:
                for entry in location_data:
                    # Safely access dictionary keys with defaults
                    odc_code = entry.get('ODCCode', 'N/A')
                    odp_code = entry.get('ODPCode', 'N/A')
                    total_port = entry.get('ODPTotalPort', 'N/A')
                    available_port = entry.get('ODPAvailablePort', 'N/A')
                    
                    messages += (
                        f"🔌 ODC Code: {odc_code}\n"
                        f"📡 ODP Code: {odp_code}\n"
                        f"🔟 Total Port: {total_port}\n"
                        f"🟢 Port Tersedia: {available_port}\n\n"
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
                
                logger.info(f"Successfully displayed data for location {selected_location} to user {user_id}")
                return NAVIGATE
                
            except KeyError as e:
                logger.error(f"Missing expected field in database result: {e}")
                await query.answer("❌ Data tidak lengkap")
                await query.edit_message_text("❌ Data lokasi tidak lengkap. Silakan hubungi administrator.")
                return ConversationHandler.END
                
        else:
            logger.warning(f"No data found for location: {selected_location}")
            await query.answer("❌ Lokasi tidak ditemukan")
            await query.edit_message_text("❌ Lokasi tidak ditemukan di database.")
            return ConversationHandler.END

    except Exception as e:
        logger.error(f"Unexpected error in location_selected: {e}")
        try:
            await query.answer("❌ Terjadi kesalahan")
            await query.edit_message_text("❌ Terjadi kesalahan sistem. Silakan coba lagi nanti.")
        except Exception as reply_error:
            logger.error(f"Failed to send error message in location_selected: {reply_error}")
        return ConversationHandler.END

    print(f'\n' +'=-'*12 +'location_selected finished'+ '=-'*12 ) # debugging

# Handle navigation buttons
async def handle_navigation(update: Update, context: CallbackContext) -> int:
    print(f'\n' +'=-'*12 + 'handle_navigation called'+ '=-'*12)
    
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        if not query.data:
            logger.warning(f"Empty callback data received from user {user_id}")
            await query.answer("❌ Data tidak valid")
            return ConversationHandler.END
        
        await query.answer()
        logger.info(f"User {user_id} selected navigation option: {query.data}")
        
        if query.data == "back_to_locations":
            # Go back to location selection using the helper function
            return await show_location_selection(update, is_callback=True)
            
        elif query.data == "finish":
            # Call the cancel function to end conversation and educate user about /cancel
            await query.edit_message_text("✅ Terima kasih!")
            return await cancel(update, context)
        else:
            logger.warning(f"Unknown navigation option: {query.data} from user {user_id}")
            await query.edit_message_text("❌ Pilihan tidak dikenal. Silakan mulai ulang dengan /cekodp")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_navigation: {e}")
        try:
            await query.answer("❌ Terjadi kesalahan")
            await query.edit_message_text("❌ Terjadi kesalahan sistem. Silakan coba lagi dengan /cekodp")
        except Exception as reply_error:
            logger.error(f"Failed to send error message in handle_navigation: {reply_error}")
        return ConversationHandler.END

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'\n' +'=-'*12 + '/cancel called'+ '=-'*12) # debugging
    
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.info(f"Cancel command executed for user {user_id}")
        
        message = "Proses dibatalkan. Gunakan /cancel kapan saja untuk membatalkan operasi."
        
        # Handle both regular messages and callback queries
        if update.callback_query:
            # This was called from a button press, send a new message
            await update.callback_query.message.reply_text(message)
        else:
            # This was called from a command
            await update.message.reply_text(message)
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in cancel function: {e}")
        try:
            # Try to send a basic error message
            if update.callback_query:
                await update.callback_query.message.reply_text("❌ Proses dibatalkan dengan kesalahan.")
            elif update.message:
                await update.message.reply_text("❌ Proses dibatalkan dengan kesalahan.")
        except Exception as reply_error:
            logger.error(f"Failed to send error message in cancel: {reply_error}")
        return ConversationHandler.END

# Init app
if __name__ == '__main__':
    try:
        # Validate environment variables
        required_env_vars = ['BOT_TOKEN', 'MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASS', 'MYSQL_DB']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            print(f"❌ Missing required environment variables: {missing_vars}")
            print("Please check your .env file")
            exit(1)
        
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        print(f'\n' +'=-'*12 + "using enhanced bot with error handling"+'=-'*12) # debugging
        logger.info("Bot application initialized successfully")

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
        
        logger.info("All handlers registered successfully")
        print(f'\n' +'=-'*12 +"Polling started..."+'=-'*12 ) # debugging
        logger.info("Bot polling started")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Critical error during bot initialization: {e}")
        print(f"❌ Critical error: {e}")
        print("Bot failed to start. Check logs for details.")
        exit(1)