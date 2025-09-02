import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from telegram.constants import ParseMode
from database.port_queries import port_db
from utils.constants import user_location, NAVIGATE, SELECT_LOCATION
from utils.helpers import show_location_selection, show_main_menu
from utils.message_formatter import format_port_availability_message
from utils.ui_components import KeyboardBuilder

logger = logging.getLogger(__name__)

async def cekodp(update: Update, context):
    """Check ODP port availability command"""
    print(f'\n' +'=-'*12 + "cekodp called" + '=-'*12)
    return await show_location_selection(update, is_callback=False)

async def location_selected(update: Update, context: CallbackContext):
    """Handle location selection for port checking"""
    print(f'\n' +'=-'*12 + "location_selected called" + '=-'*12)
    
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
            logger.info(f"User {user_id} selected coverage_id: {coverage_id}")
            
            location_data = port_db.get_location_data(coverage_id)
            
            if location_data is None:
                await query.answer("❌ Terjadi kesalahan database")
                await query.edit_message_text("❌ Terjadi kesalahan saat mengakses database.")
                return ConversationHandler.END
            
            if location_data:
                user_location[user_id] = location_data
                location_name = location_data[0].get('c_name', 'Unknown')
                
               # Format the port availability message with coordinates (returns list of messages)
                messages = format_port_availability_message(location_name, location_data)
                
                reply_markup = KeyboardBuilder.port_navigation_keyboard()
                
                await query.answer()
                await query.edit_message_text("Lokasi berhasil diset.")
                
                # Send all messages with Markdown parsing to enable clickable links
                for i, message in enumerate(messages):
                    # Add navigation buttons only to the last message
                    current_markup = reply_markup if i == len(messages) - 1 else None
                    
                    await query.message.reply_text(
                        message, 
                        reply_markup=current_markup, 
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                
                return NAVIGATE
            else:
                await query.answer("❌ Lokasi tidak ditemukan")
                await query.edit_message_text("❌ Lokasi tidak ditemukan di database.")
                return ConversationHandler.END
        
        await query.answer("❌ Pilihan tidak valid")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in location_selected: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END

async def handle_port_navigation(update: Update, context: CallbackContext):
    """Handle navigation buttons for port checking"""
    print(f'\n' +'=-'*12 + "handle_port_navigation called" + '=-'*12)
    
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
        logger.error(f"Error in handle_port_navigation: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END