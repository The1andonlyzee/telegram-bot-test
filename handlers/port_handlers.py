import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database.db_manager import db_manager
from utils.constants import user_location, NAVIGATE, SELECT_LOCATION
from utils.helpers import show_location_selection, show_main_menu
from handlers.common_handlers import cancel

logger = logging.getLogger(__name__)

async def cekodp(update: Update, context):
    """Check ODP port availability command"""
    print(f'\n' +'=-'*12 + "cekodp called" + '=-'*12)
    return await show_location_selection(update, is_callback=False)

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
            # TODO: Implement customer lookup
            await query.edit_message_text("Customer lookup feature coming soon!")
            return ConversationHandler.END
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal. Silakan mulai ulang dengan /start")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_main_menu: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem. Silakan coba lagi dengan /start")
        return ConversationHandler.END

async def location_selected(update: Update, context: CallbackContext):
    """Handle location selection for port checking"""
    print(f'\n' +'=-'*12 + "location_selected called" + '=-'*12)
    
    try:
        query = update.callback_query
        user_id = query.from_user.id
        selected_data = query.data
        
        # Handle main menu selections
        if selected_data in ["check_ports", "find_customer"]:
            return await handle_main_menu(update, context)
        
        # Handle port check location selection
        if selected_data.isdigit():
            coverage_id = int(selected_data)
            logger.info(f"User {user_id} selected coverage_id: {coverage_id}")
            
            location_data = db_manager.get_location_data(coverage_id)
            
            if location_data is None:
                await query.answer("❌ Terjadi kesalahan database")
                await query.edit_message_text("❌ Terjadi kesalahan saat mengakses database.")
                return ConversationHandler.END
            
            if location_data:
                user_location[user_id] = location_data
                messages = ""
                location_name = location_data[0].get('LocationName', 'Unknown')
                
                for entry in location_data:
                    messages += (
                        f"🔌 ODC Code: {entry.get('ODCCode', 'N/A')}\n"
                        f"📡 ODP Code: {entry.get('ODPCode', 'N/A')}\n"
                        f"🔟 Total Port: {entry.get('ODPTotalPort', 'N/A')}\n"
                        f"🟢 Port Tersedia: {entry.get('ODPAvailablePort', 'N/A')}\n\n"
                    )
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Pilih Lokasi Lain", callback_data="back_to_locations")],
                    [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main_menu")],
                    [InlineKeyboardButton("❌ Selesai", callback_data="finish")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.answer()
                await query.edit_message_text("Lokasi berhasil diset.")
                await query.message.reply_text(
                    f"📍 Lokasi: {location_name}\n\n{messages}",
                    reply_markup=reply_markup
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

async def handle_navigation(update: Update, context: CallbackContext):
    """Handle navigation buttons"""
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
            return await cancel(update, context)
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal.")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_navigation: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END