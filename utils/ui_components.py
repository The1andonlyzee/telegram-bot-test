"""UI component utilities for creating consistent keyboard layouts"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class KeyboardBuilder:
    """Helper class for building consistent keyboard layouts"""
    
    @staticmethod
    def main_menu_keyboard():
        """Build main menu keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Cek Ketersediaan Port", callback_data="check_ports")],
            [InlineKeyboardButton("👥 Cari Customer", callback_data="find_customer")]
        ])
    
    @staticmethod
    def customer_lookup_keyboard():
        """Build customer lookup options keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Cari berdasarkan Lokasi", callback_data="customer_by_location")],
            [InlineKeyboardButton("🔎 Cari Nama Customer", callback_data="customer_by_name")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main_menu")]
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
        keyboard.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_to_customer_options")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def odp_selection_keyboard(odps):
        """Build ODP selection keyboard"""
        keyboard = []
        for odp in odps:
            button_text = f"{odp['code_odp']} ({odp['customer_count']} customers)"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"odp_{odp['id_odp']}")])
        
        keyboard.extend([
            [InlineKeyboardButton("🔙 Kembali ke Pilihan Lokasi", callback_data="back_to_customer_locations")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main_menu")]
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
            [InlineKeyboardButton("🔙 Kembali ke Daftar ODP", callback_data="back_to_odp_selection")],
            [InlineKeyboardButton("📍 Ganti Lokasi", callback_data="back_to_customer_locations")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("✅ Selesai", callback_data="finish")]
        ])
    
    @staticmethod
    def search_results_keyboard():
        """Build search results navigation keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Cari Lagi", callback_data="customer_by_name")],
            [InlineKeyboardButton("🔍 Cari berdasarkan Lokasi", callback_data="customer_by_location")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main_menu")],
            [InlineKeyboardButton("✅ Selesai", callback_data="finish")]
        ])
    
    @staticmethod
    def no_results_keyboard():
        """Build no results keyboard"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Cari Lagi", callback_data="customer_by_name")],
            [InlineKeyboardButton("🔍 Cari berdasarkan Lokasi", callback_data="customer_by_location")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="back_to_main_menu")]
        ])

class MessageTemplates:
    """Template messages for consistent UI"""
    
    WELCOME_MESSAGE = (
        "Selamat datang di BNetID ODP Management Bot! 🏢\n\n"
        "Silakan pilih fitur yang ingin Anda gunakan:"
    )   
    
    CUSTOMER_LOOKUP_MESSAGE = (
        "🔍 Opsi Pencarian Customer:\n\n"
        "📍 Cari berdasarkan Lokasi - Cari customer berdasarkan ODP\n"
        "🔎 Cari berdasarkan Nama - Cari customer langsung berdasarkan nama"
    )
    
    SEARCH_PROMPT_MESSAGE = (
        "🔎 Silakan ketik nama customer yang ingin Anda cari:\n\n"
        "💡 Tips:\n"
        "- Anda dapat mencari dengan nama sebagian (contoh: 'Rossi' akan menemukan 'Rossi Putri')\n"
        "- Pencarian tidak sensitif terhadap huruf besar/kecil\n"
        "- Gunakan /cancel untuk membatalkan pencarian"
    )
    
    LOADING_MESSAGE = "⏳ Loading..."
    SEARCHING_MESSAGE = "🔍 Mencari Customer..."
    
    @staticmethod
    def no_customers_found(search_term):
        return (
            f"❌ Tidak ditemukan customer untuk '{search_term}'\n\n"
            f"Saran:\n"
            f"• Periksa ejaan nama\n"
            f"• Coba dengan nama sebagian\n"
            f"• Gunakan 'Telusuri berdasarkan Lokasi' untuk melihat semua customer"
        )
    
    @staticmethod
    def odp_selection_message(location_name):
        return f"📡 ODP di {location_name}:\n\nPilih ODP untuk melihat customer:"
    
    @staticmethod
    def input_too_short():
        return (
            "❌ Silakan masukkan minimal 2 karakter untuk pencarian.\n\n"
            "Coba lagi atau gunakan /cancel untuk membatalkan."
        )