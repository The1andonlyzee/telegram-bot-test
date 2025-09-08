import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.constants import user_location, SELECT_LOCATION
from utils.helpers import show_main_menu
from utils.error_handler import ErrorHandler


logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler with main menu"""
    
    ErrorHandler.log_handler_entry("start", update)
    
    try:
        user_id = update.effective_user.id
        
        # Clear any existing conversation state
        if user_id in user_location:
            del user_location[user_id]
            logger.info(f"Cleared conversation state for user {user_id}")
        
        await show_main_menu(update, is_callback=False)
        logger.info(f"Start command executed for user {user_id}")
        return SELECT_LOCATION
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, context, e, "system_error", ConversationHandler.END)
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel command handler"""
    ErrorHandler.log_handler_entry("cancel", update)
    
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.info(f"Cancel command executed for user {user_id}")
        
        message = "Proses dibatalkan. Gunakan /cancel kapan saja untuk membatalkan operasi."
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message)
        else:
            await update.message.reply_text(message)
        
        return ConversationHandler.END
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, context, e, "system_error", ConversationHandler.END)