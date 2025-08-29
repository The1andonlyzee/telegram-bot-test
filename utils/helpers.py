import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from database.db_manager import db_manager
from utils.constants import SELECT_LOCATION

logger = logging.getLogger(__name__)

async def show_location_selection(update, is_callback=False):
    """Helper function to display location selection menu"""
    print(f'\n' +'=-'*12 + "show_location_selection called" + '=-'*12)
    
    try:
        locations = db_manager.get_all_locations()
        
        if not locations:
            error_message = "❌ Tidak ada lokasi tersedia atau terjadi masalah dengan database."
            logger.warning("No locations available or database error")
            
            if is_callback:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
            return ConversationHandler.END

        keyboard = [[InlineKeyboardButton(c_name, callback_data=str(coverage_id))] 
                   for coverage_id, c_name in locations]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "Silakan pilih lokasi ODP:"

        if is_callback:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
        
        logger.info(f"Location selection displayed with {len(locations)} options")
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

async def show_main_menu(update, is_callback=False):
    """Helper function to display main menu"""
    keyboard = [
        [InlineKeyboardButton("🔍 Cek Ketersediaan Port", callback_data="check_ports")],
        [InlineKeyboardButton("👥 Cari Pelanggan", callback_data="find_customer")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = ("Selamat datang di BNet ODP Management Bot! 🏢\n\n"
              "Silakan pilih fitur yang ingin Anda gunakan:")
    
    if is_callback:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)