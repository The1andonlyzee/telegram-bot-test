"""Message formatting utilities for consistent Telegram message display"""

def create_google_maps_url(latitude, longitude):
    """Create Google Maps URL from coordinates"""
    try:
        # Clean and validate coordinates
        lat = str(latitude).strip()
        lng = str(longitude).strip()
        
        # Check if coordinates are valid (not empty or null)
        if not lat or not lng or lat in ['', '0', 'NULL', 'null'] or lng in ['', '0', 'NULL', 'null']:
            return None
            
        # Create Google Maps URL
        return f"https://maps.google.com/maps?q={lat},{lng}"
    except:
        return None

def format_port_availability_message(location_name, location_data):
    """Format port availability data into a readable message with coordinates"""
    message = f"📊 Lokasi: {location_name}\n\n"
    
    current_odc = None
    
    for entry in location_data:
        odc_code = entry.get('code_odc', 'N/A')
        odp_code = entry.get('code_odp', 'N/A')
        total_port = entry.get('total_port', 'N/A')
        available_port = entry.get('odp_available_port', 'N/A')
        
        # ODC coordinates
        odc_lat = entry.get('odc_latitude', '')
        odc_lng = entry.get('odc_longitude', '')
        
        # ODP coordinates  
        odp_lat = entry.get('odp_latitude', '')
        odp_lng = entry.get('odp_longitude', '')
        
        # Show ODC info only when it changes (grouped display)
        if current_odc != odc_code:
            current_odc = odc_code
            message += f"🔌 ODC: {odc_code}\n"
            
            # Add ODC coordinates if available
            odc_maps_url = create_google_maps_url(odc_lat, odc_lng)
            if odc_maps_url:
                message += f"   📍 ODC Location: [View on Maps]({odc_maps_url})\n"
            else:
                message += f"   📍 ODC Location: Not available\n"
            message += "\n"
        
        # ODP information
        message += f"  📡 ODP: {odp_code}\n"
        message += f"  📢 Total Port: {total_port}\n"
        message += f"  🟢 Port Tersedia: {available_port}\n"
        
        # Add ODP coordinates if available
        odp_maps_url = create_google_maps_url(odp_lat, odp_lng)
        if odp_maps_url:
            message += f"  📍 ODP Location: [View on Maps]({odp_maps_url})\n"
        else:
            message += f"  📍 ODP Location: Not available\n"
        
        message += "\n"
    
    return message

def format_customer_search_results(search_term, customers):
    """Format customer search results into readable messages"""
    message = f"🔍 Search Results for '{search_term}'\n"
    message += f"Found {len(customers)} customer(s):\n\n"
    
    for i, customer in enumerate(customers, 1):
        customer_info = (
            f"{i}. 👤 {customer.get('name', 'N/A')}\n"
            f"   🏠 Address: {customer.get('address', 'N/A')}\n"
            f"   📍 Location: {customer.get('c_name', 'N/A')}\n"
            f"   🔌 ODC: {customer.get('code_odc', 'N/A')}\n"
            f"   📡 ODP: {customer.get('code_odp', 'N/A')}\n"
            f"   📢 Port: {customer.get('no_port_odp', 'N/A')}\n"
            f"   📞 Phone: {customer.get('no_wa', 'N/A')}\n\n"
        )
        message += customer_info
    
    # Split long messages into chunks
    if len(message) > 4000:
        messages = []
        current_msg = f"🔍 Search Results for '{search_term}'\nFound {len(customers)} customer(s):\n\n"
        
        for i, customer in enumerate(customers, 1):
            customer_info = (
                f"{i}. 👤 {customer.get('name', 'N/A')}\n"
                f"   🏠 Address: {customer.get('address', 'N/A')}\n"
                f"   📍 Location: {customer.get('c_name', 'N/A')}\n"
                f"   🔌 ODC: {customer.get('code_odc', 'N/A')}\n"
                f"   📡 ODP: {customer.get('code_odp', 'N/A')}\n"
                f"   📢 Port: {customer.get('no_port_odp', 'N/A')}\n"
                f"   📞 Phone: {customer.get('no_wa', 'N/A')}\n\n"
            )
            
            if len(current_msg + customer_info) > 4000:
                messages.append(current_msg)
                current_msg = customer_info
            else:
                current_msg += customer_info
        
        messages.append(current_msg)
        return messages
    
    return [message]

def format_customers_in_odp(customers):
    """Format customers in ODP data into a readable message"""
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
        message += f"   📢 Port: {customer.get('no_port_odp', 'N/A')}\n\n"
    
    return message

def format_error_message(error_type, details=None):
    """Format error messages consistently"""
    error_messages = {
        'database_error': '❌ Terjadi kesalahan database.',
        'no_data': '❌ Data tidak ditemukan.',
        'invalid_input': '❌ Input tidak valid.',
        'system_error': '❌ Terjadi kesalahan sistem.'
    }
    
    base_message = error_messages.get(error_type, '❌ Terjadi kesalahan.')
    
    if details:
        return f"{base_message}\n\n{details}"
    
    return base_message

def format_success_message(message_type, details=None):
    """Format success messages consistently"""
    success_messages = {
        'data_found': '✅ Data berhasil ditemukan.',
        'operation_complete': '✅ Operasi berhasil diselesaikan.',
        'search_complete': '✅ Pencarian selesai.'
    }
    
    base_message = success_messages.get(message_type, '✅ Berhasil.')
    
    if details:
        return f"{base_message}\n\n{details}"
    
    return base_message