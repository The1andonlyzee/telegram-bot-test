"""UI component utilities for creating consistent keyboard layouts"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class KeyboardBuilder:
    """Helper class for building consistent keyboard layouts"""
    
    @staticmethod
    def main_menu_keyboard():
        """Build main menu keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Cek Ketersediaan Port", callback_data="check_ports")],
            [InlineKeyboardButton("👥 Cari Pelanggan", callback_data="find_customer")]
        ])
    
    @staticmethod
    def customer_lookup_keyboard():
        """Build customer lookup options keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Browse by Location", callback_data="customer_by_location")],
            [InlineKeyboardButton("🔎 Search by Name", callback_data="customer_by_name")],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_main_menu")]
        ])
    
    @staticmethod
    def location_selection_keyboard(locations, prefix=""):
        """Build location selection keyboard"""
        keyboard = []
        for coverage_id, c_name in locations:
            callback_data = f"{prefix}{coverage_id}" if prefix else str(coverage_id)
            keyboard.append([InlineKeyboardButton(c_name, callback_data=callback_data)])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def customer_location_keyboard(locations):
        """Build customer location selection keyboard"""
        keyboard = [[InlineKeyboardButton(c_name, callback_data=f"cust_loc_{coverage_id}")] 
                   for coverage_id, c_name in locations]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_customer_options")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def odp_selection_keyboard(odps):
        """Build ODP selection keyboard"""
        keyboard = []
        for odp in odps:
            button_text = f"{odp['code_odp']} ({odp['customer_count']} customers)"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"odp_{odp['id_odp']}")])
        
        keyboard.extend([
            [InlineKeyboardButton("🔙 Back to Locations", callback_data="back_to_customer_locations")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")]
        ])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def port_navigation_keyboard():
        """Build port checking navigation keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Pilih Lokasi Lain", callback_data="back_to_locations")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("❌ Selesai", callback_data="finish")]
        ])
    
    @staticmethod
    def customer_navigation_keyboard():
        """Build customer lookup navigation keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to ODPs", callback_data="back_to_odp_selection")],
            [InlineKeyboardButton("📍 Change Location", callback_data="back_to_customer_locations")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("✅ Finish", callback_data="finish")]
        ])
    
    @staticmethod
    def search_results_keyboard():
        """Build search results navigation keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Search Again", callback_data="customer_by_name")],
            [InlineKeyboardButton("🔍 Browse by Location", callback_data="customer_by_location")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("✅ Finish", callback_data="finish")]
        ])
    
    @staticmethod
    def no_results_keyboard():
        """Build no results keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Search Again", callback_data="customer_by_name")],
            [InlineKeyboardButton("🔍 Browse by Location", callback_data="customer_by_location")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu")]
        ])

class MessageTemplates:
    """Template messages for consistent UI"""
    
    WELCOME_MESSAGE = (
        "Selamat datang di BNet ODP Management Bot! 🏢\n\n"
        "Silakan pilih fitur yang ingin Anda gunakan:"
    )
    
    CUSTOMER_LOOKUP_MESSAGE = (
        "🔍 Customer Lookup Options:\n\n"
        "🔍 Browse by Location - Navigate through coverage areas and ODPs\n"
        "🔎 Search by Name - Directly search for customer by name"
    )
    
    SEARCH_PROMPT_MESSAGE = (
        "🔎 Please type the customer name you want to search for:\n\n"
        "💡 Tips:\n"
        "- You can search with partial names (e.g., 'john' will find 'John Doe')\n"
        "- Search is case-insensitive\n"
        "- Use /cancel to abort the search"
    )
    
    LOADING_MESSAGE = "⏳ Loading..."
    SEARCHING_MESSAGE = "🔍 Searching customers..."
    
    @staticmethod
    def no_customers_found(search_term):
        return (
            f"❌ No customers found for '{search_term}'\n\n"
            f"Suggestions:\n"
            f"• Check the spelling\n"
            f"• Try with partial names\n"
            f"• Use Browse by Location to see all customers"
        )
    
    @staticmethod
    def odp_selection_message(location_name):
        return f"📡 ODPs in {location_name}:\n\nSelect an ODP to view customers:"
    
    @staticmethod
    def input_too_short():
        return (
            "❌ Please enter at least 2 characters for the search.\n\n"
            "Try again or use /cancel to abort."
        )