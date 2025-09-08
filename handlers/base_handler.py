import logging
from telegram.ext import ConversationHandler
from utils.constants import SELECT_LOCATION
from utils.helpers import show_main_menu
from utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class BaseHandler:
    """Base handler class with common functionality"""
    
    @staticmethod
    async def handle_common_navigation(update, context, callback_data):
        """Handle common navigation patterns across handlers"""
        try:
            query = update.callback_query
            await query.answer()
            
            if callback_data == "back_to_main_menu":
                await show_main_menu(update, is_callback=True)
                return SELECT_LOCATION
            elif callback_data == "finish":
                await query.edit_message_text("âœ… Terima kasih!")
                from handlers.common_handlers import cancel
                return await cancel(update, context)
            else:
                return None  # Let specific handler deal with it
                
        except Exception as e:
            return await ErrorHandler.handle_error(update, context, e, "system_error", ConversationHandler.END)
    
    @staticmethod
    async def safe_callback_answer(update):
        """Safely answer callback queries"""
        try:
            if update.callback_query:
                await update.callback_query.answer()
        except Exception as e:
            logger.warning(f"Failed to answer callback query: {e}")