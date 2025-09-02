
import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from database.customer_queries import customer_db
from utils.constants import (
    SELECT_LOCATION, CUSTOMER_SELECT_LOCATION, CUSTOMER_SELECT_ODP, 
    CUSTOMER_NAVIGATE, CUSTOMER_NAME_SEARCH
)
from utils.message_formatter import format_customer_search_results, format_customers_in_odp
from utils.ui_components import KeyboardBuilder, MessageTemplates
from utils.helpers import show_main_menu

logger = logging.getLogger(__name__)

async def show_customer_lookup_options(update: Update, context: CallbackContext):
    """Show customer lookup options"""
    print(f'\n' +'=-'*12 + "show_customer_lookup_options called" + '=-'*12)
    
    try:
        query = update.callback_query
        
        reply_markup = KeyboardBuilder.customer_lookup_keyboard()
        message = MessageTemplates.CUSTOMER_LOOKUP_MESSAGE
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_SELECT_LOCATION
        
    except Exception as e:
        logger.error(f"Error in show_customer_lookup_options: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END

async def handle_customer_lookup_selection(update: Update, context: CallbackContext):
    """Handle customer lookup method selection"""
    print(f'\n' +'=-'*12 + "handle_customer_lookup_selection called" + '=-'*12)
    
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == "customer_by_location":
            return await show_customer_location_selection(update, context)
        elif query.data == "customer_by_name":
            await query.edit_message_text(MessageTemplates.SEARCH_PROMPT_MESSAGE)
            return CUSTOMER_NAME_SEARCH  
        elif query.data == "back_to_main_menu":
            await show_main_menu(update, is_callback=True)
            return SELECT_LOCATION
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal.")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_customer_lookup_selection: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END

async def show_customer_location_selection(update: Update, context: CallbackContext):
    """Show location selection for customer lookup"""
    print(f'\n' +'=-'*12 + "show_customer_location_selection called" + '=-'*12)
    
    try:
        query = update.callback_query
        locations = customer_db.get_all_locations()
        
        if not locations:
            await query.edit_message_text("❌ Tidak ada lokasi tersedia.")
            return ConversationHandler.END

        reply_markup = KeyboardBuilder.customer_location_keyboard(locations)
        message = "🔍 Pilih lokasi untuk melihat pelanggan:"

        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_SELECT_ODP
        
    except Exception as e:
        logger.error(f"Error in show_customer_location_selection: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END

async def handle_customer_location_selection(update: Update, context: CallbackContext):
    """Handle customer location selection"""
    print(f'\n' +'=-'*12 + "handle_customer_location_selection called" + '=-'*12)
    
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back_to_customer_options":
            return await show_customer_lookup_options(update, context)
        
        if query.data.startswith("cust_loc_"):
            coverage_id = int(query.data.replace("cust_loc_", ""))
            return await show_odp_selection(update, context, coverage_id)
        
        await query.edit_message_text("❌ Pilihan tidak valid.")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in handle_customer_location_selection: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END

async def show_odp_selection(update: Update, context: CallbackContext, coverage_id: int):
    """Show ODP selection for customer lookup"""
    print(f'\n' +'=-'*12 + "show_odp_selection called" + '=-'*12)
    
    try:
        query = update.callback_query
        odps = customer_db.get_odps_by_coverage(coverage_id)
        
        if not odps:
            await query.edit_message_text(
                "❌ Tidak ada ODP dengan pelanggan aktif di lokasi ini.\n\n"
                "Gunakan /start untuk kembali ke menu utama."
            )
            return ConversationHandler.END

        location_name = odps[0]['c_name'] if odps else "Unknown"
        reply_markup = KeyboardBuilder.odp_selection_keyboard(odps)
        message = MessageTemplates.odp_selection_message(location_name)

        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_NAVIGATE
        
    except Exception as e:
        logger.error(f"Error in show_odp_selection: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END

async def handle_customer_navigation(update: Update, context: CallbackContext):
    """Handle customer lookup navigation"""
    print(f'\n' +'=-'*12 + "handle_customer_navigation called" + '=-'*12)
    
    try:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back_to_customer_locations":
            return await show_customer_location_selection(update, context)
        elif query.data == "back_to_customer_options":
            return await show_customer_lookup_options(update, context)
        elif query.data == "back_to_main_menu":
            await show_main_menu(update, is_callback=True)
            return SELECT_LOCATION
        elif query.data == "back_to_odp_selection":
            return await show_customer_location_selection(update, context)
        elif query.data.startswith("odp_"):
            id_odp = int(query.data.replace("odp_", ""))
            return await show_customers_in_odp(update, context, id_odp)
        elif query.data == "finish":
            await query.edit_message_text("✅ Terima kasih!")
            from handlers.common_handlers import cancel
            return await cancel(update, context)
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal.")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_customer_navigation: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END

async def handle_customer_name_search(update: Update, context: CallbackContext):
    """Handle customer name search input"""
    print(f'\n' +'=-'*12 + "handle_customer_name_search called" + '=-'*12)
    
    try:
        user_input = update.message.text.strip()
        user_id = update.effective_user.id
        
        logger.info(f"User {user_id} searching for customer: {user_input}")
        
        # Validate input
        if len(user_input) < 2:
            await update.message.reply_text(MessageTemplates.input_too_short())
            return CUSTOMER_NAME_SEARCH
        
        # Show searching message
        searching_message = await update.message.reply_text(MessageTemplates.SEARCHING_MESSAGE)
        
        # Search customers
        customers = customer_db.search_customers_by_name(user_input)
        print(customers)
        
        if not customers:
            reply_markup = KeyboardBuilder.no_results_keyboard()
            
            await searching_message.edit_text(
                MessageTemplates.no_customers_found(user_input),
                reply_markup=reply_markup
            )
            return CUSTOMER_SELECT_LOCATION
        
        # Format and send results
        messages = format_customer_search_results(user_input, customers)
        
        # Send all messages except the last one
        for msg in messages[:-1]:
            await update.message.reply_text(msg)
        
        # Navigation buttons for the last message
        reply_markup = KeyboardBuilder.search_results_keyboard()
        
        await searching_message.edit_text(messages[-1], reply_markup=reply_markup)
        return CUSTOMER_SELECT_LOCATION
        
    except Exception as e:
        logger.error(f"Error in handle_customer_name_search: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan saat mencari customer.")
        return ConversationHandler.END

async def show_customers_in_odp(update: Update, context: CallbackContext, id_odp: int):
    """Show customers connected to specific ODP"""
    print(f'\n' +'=-'*12 + "show_customers_in_odp called" + '=-'*12)
    
    try:
        query = update.callback_query
        customers = customer_db.get_customers_by_odp(id_odp)
        
        if not customers:
            await query.edit_message_text("❌ Tidak ada pelanggan aktif di ODP ini.")
            return ConversationHandler.END
        
        # Format customer list message
        message = format_customers_in_odp(customers)
        
        # Handle long messages
        if len(message) > 4000:
            messages = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for msg in messages[:-1]:
                await query.message.reply_text(msg)
            message = messages[-1]
        
        reply_markup = KeyboardBuilder.customer_navigation_keyboard()
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_NAVIGATE
        
    except Exception as e:
        logger.error(f"Error in show_customers_in_odp: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
        return ConversationHandler.END