import logging
from telegram.ext import ConversationHandler
from utils.ui_components import MessageTemplates

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for consistent user experience"""
    
    @staticmethod
    async def handle_error(update, context, error, error_type="system_error", return_state=ConversationHandler.END):
        """Handle errors consistently across all handlers"""
        try:
            user_id = update.effective_user.id if update.effective_user else "unknown"
            logger.error(f"Error for user {user_id}: {error}")
            
            error_messages = {
                'system_error': 'âŒ Terjadi kesalahan sistem. Silakan coba lagi dengan /start',
                'database_error': 'âŒ Terjadi kesalahan database. Silakan coba lagi nanti.',
                'invalid_selection': 'âŒ Pilihan tidak dikenal. Silakan mulai ulang dengan /start',
                'no_data': 'âŒ Data tidak ditemukan.',
                'user_input_error': 'âŒ Input tidak valid. Silakan coba lagi.'
            }
            
            message = error_messages.get(error_type, error_messages['system_error'])
            
            if update.callback_query:
                await update.callback_query.edit_message_text(message)
            elif update.message:
                await update.message.reply_text(message)
                
            return return_state
            
        except Exception as reply_error:
            logger.error(f"Failed to send error message: {reply_error}")
            return ConversationHandler.END
    
    @staticmethod
    def log_handler_entry(handler_name, update):
        """Log handler entry consistently"""
        user_id = update.effective_user.id if update.effective_user else "unknown"
        print(f'\n' + '=-'*12 + f"{handler_name} called" + '=-'*12)
        logger.info(f"{handler_name} called by user {user_id}")