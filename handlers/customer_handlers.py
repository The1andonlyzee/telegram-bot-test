
import logging
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from telegram.constants import ParseMode
from database.customer_queries import customer_db
from utils.constants import     SELECT_LOCATION, CUSTOMER_SELECT_LOCATION, CUSTOMER_SELECT_ODP, CUSTOMER_NAVIGATE, CUSTOMER_NAME_SEARCH
from utils.message_formatter import format_customer_search_results, format_customers_in_odp
from utils.ui_components import KeyboardBuilder, MessageTemplates
from utils.helpers import show_main_menu
from utils.message_handler import MessageHandler
from utils.error_handler import ErrorHandler
from database.shared_queries import shared_db
from handlers.base_handler import BaseHandler


logger = logging.getLogger(__name__)

async def show_customer_lookup_options(update: Update, context: CallbackContext):
    """Show customer lookup options"""
    ErrorHandler.log_handler_entry("show_customer_lookup_options", update)

    
    try:
        query = update.callback_query
        user_id = query.from_user.id
        
        reply_markup = KeyboardBuilder.customer_lookup_keyboard()
        message = MessageTemplates.CUSTOMER_LOOKUP_MESSAGE
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_SELECT_LOCATION
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def handle_customer_lookup_selection(update: Update, context: CallbackContext):
    """Handle customer lookup method selection"""
    ErrorHandler.log_handler_entry("handle_customer_lookup_selection", update)
    
    try:
        query = update.callback_query
        await BaseHandler.safe_callback_answer(update)
        
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
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def show_customer_location_selection(update: Update, context: CallbackContext):
    """Show location selection for customer lookup"""
    ErrorHandler.log_handler_entry("show_customer_location_selection", update)
    
    try:
        query = update.callback_query
        locations = shared_db.get_all_locations()
        
        if not locations:
            await query.edit_message_text("❌ Tidak ada lokasi tersedia.")
            return ConversationHandler.END

        reply_markup = KeyboardBuilder.customer_location_keyboard(locations)
        message = "🔍 Pilih lokasi untuk melihat pelanggan:"

        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_SELECT_ODP
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def handle_customer_location_selection(update: Update, context: CallbackContext):
    """Handle customer location selection"""
    ErrorHandler.log_handler_entry("handle_customer_location_selection", update)

    
    try:
        query = update.callback_query
        await BaseHandler.safe_callback_answer(update)
        
        if query.data == "back_to_customer_options":
            return await show_customer_lookup_options(update, context)
        
        if query.data.startswith("cust_loc_"):
            coverage_id = int(query.data.replace("cust_loc_", ""))
            return await show_odp_selection(update, context, coverage_id)
        
        await query.edit_message_text("❌ Pilihan tidak valid.")
        return ConversationHandler.END
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def show_odp_selection(update: Update, context: CallbackContext, coverage_id: int):
    """Show ODP selection for customer lookup"""
    ErrorHandler.log_handler_entry("show_odp_selection", update)
    
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
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def handle_customer_navigation(update: Update, context: CallbackContext):
    """Handle customer lookup navigation"""
    ErrorHandler.log_handler_entry("handle_customer_navigation", update)
    
    try:
        query = update.callback_query
        await BaseHandler.safe_callback_answer(update)
        
        common_result = await BaseHandler.handle_common_navigation(update, context, query.data)
        if common_result is not None:
            return common_result
        
        # Handle customer-specific navigation
        if query.data.startswith("odp_"):
            id_odp = int(query.data.replace("odp_", ""))
            return await show_customers_in_odp(update, context, id_odp)
        elif query.data == "back_to_odp_selection":
            # Need to get coverage_id from context or state
            pass  # You'll need to implement this
        elif query.data == "back_to_customer_locations":
            return await show_customer_location_selection(update, context)
        
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal.")
            return ConversationHandler.END
    
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def handle_customer_name_search(update: Update, context: CallbackContext):
    """Handle customer name search input"""
    ErrorHandler.log_handler_entry("handle_customer_name_search", update)

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

        if not customers:
            reply_markup = KeyboardBuilder.no_results_keyboard()
            
            await searching_message.edit_text(
                MessageTemplates.no_customers_found(user_input),
                reply_markup=reply_markup
            )
            return CUSTOMER_SELECT_LOCATION
        
        # Format and send results
        messages = format_customer_search_results(user_input, customers)
        reply_markup = KeyboardBuilder.search_results_keyboard()
        await MessageHandler.send_long_message(update, messages, reply_markup, is_callback=False)
        
        return CUSTOMER_SELECT_LOCATION
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)

async def show_customers_in_odp(update: Update, context: CallbackContext, id_odp: int):
    """Show customers connected to specific ODP"""
    ErrorHandler.log_handler_entry("show_customers_in_odp", update)

    try:
        query = update.callback_query
        customers = customer_db.get_customers_by_odp(id_odp)
        
        if not customers:
            await query.edit_message_text("❌ Tidak ada pelanggan aktif di ODP ini.")
            return ConversationHandler.END
        
        # Format customer list message
        message = format_customers_in_odp(customers)
        
        # Handle long messages
        if len(message) > MessageHandler.MAX_MESSAGE_LENGTH:
            messages = [message[i:i+MessageHandler.MAX_MESSAGE_LENGTH] for i in range(0, len(message), MessageHandler.MAX_MESSAGE_LENGTH)]
            await MessageHandler.send_long_message(update, messages[:-1], None, is_callback=True)
            message = messages[-1]

        
        reply_markup = KeyboardBuilder.customer_navigation_keyboard()
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_NAVIGATE
        
    except Exception as e:
        return await ErrorHandler.handle_error(update, e, "system_error", ConversationHandler.END)