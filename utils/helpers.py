import logging
from telegram.ext import ConversationHandler
from database.port_queries import port_db
from utils.constants import SELECT_LOCATION
from utils.ui_components import KeyboardBuilder, MessageTemplates
from database.shared_queries import shared_db
from utils.error_handler import ErrorHandler


logger = logging.getLogger(__name__)

async def show_location_selection(update, context, is_callback=False):
    """Helper function to display location selection menu"""
    ErrorHandler.log_handler_entry("show_location_selection", update)
    
    try:
        locations = shared_db.get_all_locations()        
        if not locations:
            error_message = "❌ Tidak ada lokasi tersedia atau terjadi masalah dengan database."
            logger.warning("No locations available or database error")
            
            if is_callback:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
            return ConversationHandler.END

        reply_markup = KeyboardBuilder.location_selection_keyboard(locations)
        message = "Silakan pilih lokasi ODP:"

        if is_callback:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
        
        logger.info(f"Location selection displayed with {len(locations)} options")
        return SELECT_LOCATION
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, context, e, "system_error", ConversationHandler.END)


async def show_main_menu(update, is_callback=False):
    """Helper function to display main menu"""
    reply_markup = KeyboardBuilder.main_menu_keyboard()
    message = MessageTemplates.WELCOME_MESSAGE
    
    if is_callback:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)