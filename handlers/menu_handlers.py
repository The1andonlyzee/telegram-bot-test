import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from utils.helpers import show_location_selection
from handlers.customer_handlers import show_customer_lookup_options
from handlers.base_handler import BaseHandler
from utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

async def handle_main_menu(update: Update, context: CallbackContext):
    """Handle main menu selections"""
    ErrorHandler.log_handler_entry("handle_main_menu", update)

    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        await BaseHandler.safe_callback_answer(update)
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
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def handle_navigation(update: Update, context: CallbackContext):
    """Handle general navigation buttons"""
    ErrorHandler.log_handler_entry("handle_navigation", update)    
    try:
        query = update.callback_query
        await BaseHandler.safe_callback_answer(update)
        
        common_result = await BaseHandler.handle_common_navigation(update, context, query.data)
        if common_result is not None:
            return common_result
            
        # Handle menu-specific navigation
        if query.data == "back_to_locations":
            return await show_location_selection(update, is_callback=True)
        else:
            from utils.error_handler import ErrorHandler
            return await ErrorHandler.handle_error(update, context, "Unknown option", "invalid_selection", ConversationHandler.END)
    
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)
