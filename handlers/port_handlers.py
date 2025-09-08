import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from database.port_queries import port_db
from utils.constants import user_location, NAVIGATE, SELECT_LOCATION
from utils.helpers import show_location_selection
from utils.message_formatter import format_port_availability_message
from utils.ui_components import KeyboardBuilder
from utils.error_handler import ErrorHandler
from handlers.base_handler import BaseHandler



logger = logging.getLogger(__name__)

async def cekodp(update: Update, context):
    """Check ODP port availability command"""
    ErrorHandler.log_handler_entry("cekodp", update)
    return await show_location_selection(update, is_callback=False)

async def location_selected(update: Update, context: CallbackContext):
    """Handle location selection for port checking"""
    ErrorHandler.log_handler_entry("location_selected", update)

    try:
        query = update.callback_query
        user_id = query.from_user.id
        selected_data = query.data
        
        # Handle main menu selections
        if selected_data in ["check_ports", "find_customer"]:
            from handlers.menu_handlers import handle_main_menu
            return await handle_main_menu(update, context)
        
        # Handle port check location selection
        if selected_data.isdigit():
            coverage_id = int(selected_data)
            location_data = port_db.get_location_data(coverage_id)
            
            if location_data is None:
                await query.answer("âŒ Terjadi kesalahan database")
            
            if location_data:
                user_location[user_id] = location_data
                location_name = location_data[0].get('c_name', 'Unknown')
                
                messages = format_port_availability_message(location_name, location_data)
                reply_markup = KeyboardBuilder.port_navigation_keyboard()
                
                await BaseHandler.safe_callback_answer(update)
                await query.edit_message_text("Lokasi berhasil diset.")
                
                from utils.message_handler import MessageHandler
                await MessageHandler.send_long_message(update, messages, reply_markup, is_callback=True)
                
                return NAVIGATE
            else:
                await query.answer("âŒ Lokasi tidak ditemukan")

        await query.answer("âŒ Pilihan tidak valid")
        return ConversationHandler.END
    
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def handle_port_navigation(update: Update, context: CallbackContext):
    """Handle navigation buttons for port checking"""

    ErrorHandler.log_handler_entry("location_selected", update)

    try:
        query = update.callback_query
        await BaseHandler.safe_callback_answer(update)
        
        common_result = await BaseHandler.handle_common_navigation(update, context, query.data)
        if common_result is not None:
            return common_result
            
        # Handle port-specific navigation
        if query.data == "back_to_locations":
            return await show_location_selection(update, is_callback=True)
        else:
            return await ErrorHandler.handle_error(update, context, "Unknown option", "invalid_selection", ConversationHandler.END)

    
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)
