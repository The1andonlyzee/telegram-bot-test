import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from config.settings import TELEGRAM_TOKEN, validate_environment
from utils.constants import SELECT_LOCATION, NAVIGATE, CUSTOMER_SELECT_LOCATION, CUSTOMER_SELECT_ODP, CUSTOMER_NAVIGATE, CUSTOMER_NAME_SEARCH
from handlers.common_handlers import start, cancel
from handlers.port_handlers import (
    cekodp, location_selected, handle_navigation,
    handle_customer_lookup_selection, handle_customer_location_selection,
    handle_customer_navigation, handle_customer_name_search
)

logger = logging.getLogger(__name__)

def create_application():
    """Create and configure the bot application"""
    try:
        # Validate environment
        validate_environment()
        
        # Create application
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Create conversation handler
        main_conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", start),
                CommandHandler("cekodp", cekodp)
            ],
            states={
                SELECT_LOCATION: [CallbackQueryHandler(location_selected)],
                NAVIGATE: [CallbackQueryHandler(handle_navigation)],
                CUSTOMER_SELECT_LOCATION: [CallbackQueryHandler(handle_customer_lookup_selection)],
                CUSTOMER_SELECT_ODP: [CallbackQueryHandler(handle_customer_location_selection)],
                CUSTOMER_NAVIGATE: [CallbackQueryHandler(handle_customer_navigation)],
                CUSTOMER_NAME_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_name_search)]
            },
            fallbacks=[
                CommandHandler("cancel", cancel),
                CommandHandler("start", start),
                CommandHandler("cekodp", cekodp),
            ],
            allow_reentry=True,
        )
        
        # Register handlers
        application.add_handler(main_conv_handler)
        application.add_handler(CommandHandler("cancel", cancel))
        
        logger.info("Bot application configured successfully")
        return application
        
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise

def main():
    """Main entry point"""
    try:
        print(f'\n' + '='*50)
        print("🤖 Starting BNet ODP Management Bot")
        print(f'='*50)
        
        application = create_application()
        
        print("✅ Bot started successfully!")
        print("📡 Polling for messages...")
        
        application.run_polling()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"❌ Critical error: {e}")
        exit(1)

if __name__ == '__main__':
    main()