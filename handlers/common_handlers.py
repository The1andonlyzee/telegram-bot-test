import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.constants import user_location, SELECT_LOCATION
from utils.helpers import show_main_menu

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler with main menu"""
    print(f'\n' +'=-'*12 + "start called" + '=-'*12)
    
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
        logger.error(f"Error in start command: {e}")
        try:
            await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        except Exception as reply_error:
            logger.error(f"Failed to send error message in start: {reply_error}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel command handler"""
    print(f'\n' +'=-'*12 + "cancel called" + '=-'*12)
    
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
        logger.error(f"Error in cancel function: {e}")
        try:
            if update.callback_query:
                await update.callback_query.message.reply_text("❌ Proses dibatalkan dengan kesalahan.")
            elif update.message:
                await update.message.reply_text("❌ Proses dibatalkan dengan kesalahan.")
        except Exception as reply_error:
            logger.error(f"Failed to send error message in cancel: {reply_error}")
        return ConversationHandler.END