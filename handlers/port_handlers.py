import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from database.db_manager import db_manager
from utils.constants import user_location, NAVIGATE, SELECT_LOCATION, CUSTOMER_SELECT_LOCATION, CUSTOMER_SELECT_ODP, CUSTOMER_NAVIGATE, CUSTOMER_NAME_SEARCH
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
            return await show_customer_lookup_options(update, context)
        else:
            await query.edit_message_text("❌ Pilihan tidak dikenal. Silakan mulai ulang dengan /start")
            return ConversationHandler.END
    
    except Exception as e:
        logger.error(f"Error in handle_main_menu: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem. Silakan coba lagi dengan /start")
        return ConversationHandler.END

async def show_customer_lookup_options(update: Update, context: CallbackContext):
    """Show customer lookup options"""
    print(f'\n' +'=-'*12 + "show_customer_lookup_options called" + '=-'*12)
    
    try:
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("📍 Browse by Location", callback_data="customer_by_location")],
            [InlineKeyboardButton("🔍 Search by Name", callback_data="customer_by_name")],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = ("🔍 Customer Lookup Options:\n\n"
                  "📍 Browse by Location - Navigate through coverage areas and ODPs\n"
                  "🔍 Search by Name - Directly search for customer by name")
        
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
            await query.edit_message_text(
                "🔍 Please type the customer name you want to search for:\n\n"
                "💡 Tips:\n"
                "- You can search with partial names (e.g., 'john' will find 'John Doe')\n"
                "- Search is case-insensitive\n"
                "- Use /cancel to abort the search"
            )
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
        locations = db_manager.get_all_locations()
        
        if not locations:
            await query.edit_message_text("❌ Tidak ada lokasi tersedia.")
            return ConversationHandler.END

        keyboard = [[InlineKeyboardButton(c_name, callback_data=f"cust_loc_{coverage_id}")] 
                   for coverage_id, c_name in locations]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_customer_options")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "📍 Pilih lokasi untuk melihat pelanggan:"

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
        odps = db_manager.get_odps_by_coverage(coverage_id)
        
        if not odps:
            await query.edit_message_text(
                "❌ Tidak ada ODP dengan pelanggan aktif di lokasi ini.\n\n"
                "Gunakan /start untuk kembali ke menu utama."
            )
            return ConversationHandler.END

        keyboard = []
        location_name = odps[0]['c_name'] if odps else "Unknown"
        
        for odp in odps:
            button_text = f"{odp['code_odp']} ({odp['customer_count']} customers)"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"odp_{odp['id_odp']}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Locations", callback_data="back_to_customer_locations")])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"📡 ODPs in {location_name}:\n\nSelect an ODP to view customers:"

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
        elif query.data.startswith("odp_"):
            id_odp = int(query.data.replace("odp_", ""))
            return await show_customers_in_odp(update, context, id_odp)
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
            await update.message.reply_text(
                "❌ Please enter at least 2 characters for the search.\n\n"
                "Try again or use /cancel to abort."
            )
            return CUSTOMER_NAME_SEARCH
        
        # Show searching message
        searching_message = await update.message.reply_text("🔍 Searching customers...")
        
        # Search customers
        customers = db_manager.search_customers_by_name(user_input)
        
        if not customers:
            keyboard = [
                [InlineKeyboardButton("🔍 Search Again", callback_data="customer_by_name")],
                [InlineKeyboardButton("📍 Browse by Location", callback_data="customer_by_location")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await searching_message.edit_text(
                f"❌ No customers found for '{user_input}'\n\n"
                f"Suggestions:\n"
                f"• Check the spelling\n"
                f"• Try with partial names\n"
                f"• Use Browse by Location to see all customers",
                reply_markup=reply_markup
            )
            return CUSTOMER_SELECT_LOCATION
        
        # Format search results
        message = f"🔍 Search Results for '{user_input}'\n"
        message += f"Found {len(customers)} customer(s):\n\n"
        
        for i, customer in enumerate(customers, 1):
            message += f"{i}. 👤 {customer.get('name', 'N/A')}\n"
            message += f"   🏠 Address: {customer.get('address', 'N/A')}\n"
            message += f"   📍 Location: {customer.get('c_name', 'N/A')}\n"
            message += f"   🔌 ODC: {customer.get('code_odc', 'N/A')}\n"
            message += f"   📡 ODP: {customer.get('code_odp', 'N/A')}\n"
            message += f"   🔢 Port: {customer.get('no_port_odp', 'N/A')}\n"
            message += f"   📞 Phone: {customer.get('no_wa', 'N/A')}\n\n"
            # message += f"   📅 Connected: {customer.get('connection_date', 'N/A')}\n"
            # message += f"   ✅ Status: {customer.get('c_status', 'N/A')}\n\n"
        
        # Handle long messages
        if len(message) > 4000:
            messages = []
            current_msg = f"🔍 Search Results for '{user_input}'\nFound {len(customers)} customer(s):\n\n"
            
            for i, customer in enumerate(customers, 1):
                customer_info = (
                    f"{i}. 👤 {customer.get('name', 'N/A')}\n"
                    f"   🏠 Address: {customer.get('address', 'N/A')}\n"
                    f"   📍 Location: {customer.get('c_name', 'N/A')}\n"
                    f"   🔌 ODC: {customer.get('code_odc', 'N/A')}\n"
                    f"   📡 ODP: {customer.get('code_odp', 'N/A')}\n"
                    f"   🔢 Port: {customer.get('no_port_odp', 'N/A')}\n"
                    f"   📞 Phone: {customer.get('no_wa', 'N/A')}\n\n"
                    # f"   📅 Connected: {customer.get('connection_date', 'N/A')}\n"
                    # f"   ✅ Status: {customer.get('c_status', 'N/A')}\n\n"
                )
                
                if len(current_msg + customer_info) > 4000:
                    messages.append(current_msg)
                    current_msg = customer_info
                else:
                    current_msg += customer_info
            
            messages.append(current_msg)
            
            # Send all messages except the last one
            for msg in messages[:-1]:
                await update.message.reply_text(msg)
            
            message = messages[-1]
        
        # Navigation buttons
        keyboard = [
            [InlineKeyboardButton("🔍 Search Again", callback_data="customer_by_name")],
            [InlineKeyboardButton("📍 Browse by Location", callback_data="customer_by_location")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("✅ Finish", callback_data="finish")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await searching_message.edit_text(message, reply_markup=reply_markup)
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
        customers = db_manager.get_customers_by_odp(id_odp)
        
        if not customers:
            await query.edit_message_text("❌ Tidak ada pelanggan aktif di ODP ini.")
            return ConversationHandler.END
        
        # Build customer list message
        first_customer = customers[0]
        location_name = first_customer.get('c_name', 'Unknown')
        odc_code = first_customer.get('code_odc', 'N/A')
        odp_code = first_customer.get('code_odp', 'N/A')
        
        message = f"👥 Customers in ODP {odp_code}\n"
        message += f"📍 Location: {location_name}\n"
        message += f"🔌 ODC: {odc_code}\n\n"
        
        for i, customer in enumerate(customers, 1):
            message += f"{i}. 👤 {customer.get('name', 'N/A')}\n"
            message += f"   🏠 Address: {customer.get('address', 'N/A') if 'address' in customer else 'N/A'}\n"
            message += f"   🔢 Port: {customer.get('no_port_odp', 'N/A')}\n\n"
        
        # Telegram message limit is around 4096 characters
        if len(message) > 4000:
            # Split into multiple messages
            messages = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for msg in messages[:-1]:
                await query.message.reply_text(msg)
            message = messages[-1]
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to ODPs", callback_data="back_to_odp_selection")],
            [InlineKeyboardButton("📍 Change Location", callback_data="back_to_customer_locations")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("✅ Finish", callback_data="finish")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        return CUSTOMER_NAVIGATE
        
    except Exception as e:
        logger.error(f"Error in show_customers_in_odp: {e}")
        await query.edit_message_text("❌ Terjadi kesalahan sistem.")
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
                location_name = location_data[0].get('c_name', 'Unknown')
                
                for entry in location_data:
                    messages += (
                        f"🔌 ODC Code: {entry.get('code_odc', 'N/A')}\n"
                        f"📡 ODP Code: {entry.get('code_odp', 'N/A')}\n"
                        f"🔢 Total Port: {entry.get('total_port', 'N/A')}\n"
                        f"🟢 Port Tersedia: {entry.get('odp_available_port', 'N/A')}\n\n"
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
        elif query.data == "back_to_odp_selection":
            # Need to store coverage_id in context for this to work
            # For now, redirect to location selection
            return await show_customer_location_selection(update, context)
        elif query.data == "back_to_customer_locations":
            return await show_customer_location_selection(update, context)
        elif query.data == "back_to_customer_options":
            return await show_customer_lookup_options(update, context)
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