import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from utils.constants import SELECT_LOCATION
from utils.helpers import show_main_menu
from utils.helpers import show_location_selection
from handlers.customer_handlers import show_customer_lookup_options

logger = logging.getLogger(__name__)

async def handle_main_menu(update: Update, context: CallbackContext):
    """Handle main menu selections"""
    print(f'\n' +'=-'*12 + "handle_main_menu called" + '=-'*12)
    
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        logger.info(f"User {user_id} selected menu option: {query.data}")
        
        if query.data == "check_ports":
            await query.edit_message_text("Loading locations...")
            return await show_location_selection(update, is_callback=True)
        elif query.data == "find_customer":
            return await show_customer_lookup_options(update, context)
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal. Silakan mulai ulang dengan /start")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_main_menu: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem. Silakan coba lagi dengan /start")
        return ConversationHandler.END

async def handle_navigation(update: Update, context: CallbackContext):
    """Handle general navigation buttons"""
    print(f'\n' +'=-'*12 + "handle_navigation called" + '=-'*12)
    
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back_to_locations":
            return await show_location_selection(update, is_callback=True)
        elif query.data == "back_to_main_menu":
            await show_main_menu(update, is_callback=True)
            return SELECT_LOCATION
        elif query.data == "finish":
            await query.edit_message_text("✅ Terima kasih!")
            from handlers.common_handlers import cancel
            return await cancel(update, context)
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal.")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_navigation: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END