import logging
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

class MessageHandler:
    """Centralized message handling for long messages"""
    
    MAX_MESSAGE_LENGTH = 4000
    
    @staticmethod
    async def send_long_message(update, messages, reply_markup=None, parse_mode=ParseMode.MARKDOWN, is_callback=True):
        """Send potentially long messages, splitting if necessary"""
        try:
            for i, message in enumerate(messages):
                current_markup = reply_markup if i == len(messages) - 1 else None
                
                if is_callback and i == 0:
                    # Edit first message for callback queries
                    await update.callback_query.edit_message_text(
                        message,
                        reply_markup=current_markup,
                        parse_mode=parse_mode,
                        disable_web_page_preview=True
                    )
                else:
                    # Reply for subsequent messages or non-callback
                    target = update.callback_query.message if is_callback else update.message
                    await target.reply_text(
                        message,
                        reply_markup=current_markup,
                        parse_mode=parse_mode,
                        disable_web_page_preview=True
                    )
        except Exception as e:
            logger.error(f"Error sending long message: {e}")
            raise