"""Message formatting utilities for consistent Telegram message display"""

def convert_dms_to_decimal(dms_str):
    """Convert DMS (Degrees, Minutes, Seconds) to decimal degrees"""
    print(f'\n' +'=-'*12 + "convert_dms_to_decimal called" + '=-'*12)
    try:

        dms_str = str(dms_str).strip().replace(' ','')
        
        # Check if it's already in decimal format
        if '°' not in dms_str or ("'" not in dms_str and '"' not in dms_str):
            # Try to parse as decimal
            clean_str = dms_str.replace('°', '').strip()
            return float(clean_str)
        
        # Parse DMS format like: 5°10'49.46"S or 119°27'40.94"T
        import re
        
        # Extract numbers and direction
        pattern = r"(\d+)°(\d+)'([\d.]+)\"([NSEWT])"
        match = re.match(pattern, dms_str)
        
        if not match:
            print("error bjir di match!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return None
            
        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        direction = match.group(4).upper()
        
        # Convert to decimal
        decimal = degrees + minutes/60 + seconds/3600
        
        # Apply direction (S and W are negative, T is treated as E for East)
        if direction in ['S', 'W']:
            decimal = -decimal
        elif direction == 'T':  # T seems to be used for Timur (East in Indonesian)
            decimal = decimal
        
        print(f"decimal of {dms_str} is : {decimal} ")
        # print(decimal)
                
        return decimal
        
    except Exception:
        return None

def create_google_maps_url(latitude, longitude):
    """Create Google Maps URL from coordinates (handles both DMS and decimal formats)"""
    try:
        # Clean and validate coordinates
        lat_str = str(latitude).strip()
        lng_str = str(longitude).strip()
        
        # Check if coordinates are valid (not empty or null)
        if not lat_str or not lng_str or lat_str in ['', '0', 'NULL', 'null'] or lng_str in ['', '0', 'NULL', 'null']:
            return None
        
        # Convert DMS to decimal if needed
        lat_decimal = convert_dms_to_decimal(lat_str)
        lng_decimal = convert_dms_to_decimal(lng_str)
        
        if lat_decimal is None or lng_decimal is None:
            return None
            
        # Validate reasonable coordinate ranges
        if not (-90 <= lat_decimal <= 90) or not (-180 <= lng_decimal <= 180):
            return None
            
        # Create Google Maps URL with decimal coordinates
        return f"https://maps.google.com/maps?q={lat_decimal},{lng_decimal}"
        
    except Exception:
        return None

def format_port_availability_message(location_name, location_data):
    """Format port availability data into readable messages with coordinates and long message handling"""
    
    # Handle empty data
    if not location_data:
        return [f"📊 Lokasi: {location_name}\n\n❌ Tidak ada data ODP tersedia."]
    
    messages = []
    current_message = f"📊 Lokasi: {location_name}\n\n"
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
        
        # Build the entry text
        entry_text = ""
        
        # Show ODC info only when it changes (grouped display)
        if current_odc != odc_code:
            current_odc = odc_code
            entry_text += f"**🔌 ODC: {odc_code}**\n"
            
            # Add ODC coordinates if available
            odc_maps_url = create_google_maps_url(odc_lat, odc_lng)
            if odc_maps_url:
                entry_text += f"   📍 ODC Location: [View on Maps]({odc_maps_url})\n" # ini utk markdown
                # entry_text += f"   📍 ODC Location: {odc_maps_url}\n"
            else:
                entry_text += f"   📍 ODC Location: Not available\n"
            entry_text += "\n"
        
        # ODP information
        entry_text += f"  📡 ODP: {odp_code}\n"
        entry_text += f"  📢 Total Port: {total_port}\n"
        entry_text += f"  🟢 Port Tersedia: {available_port}\n"
        entry_text += f"  🟢 LATITUDEEEEE: {odp_lat}\n"
        entry_text += f"  🟢 LONGITUDEEEEE: {odp_lng}\n"
        
        # Add ODP coordinates if available
        odp_maps_url = create_google_maps_url(odp_lat, odp_lng)
        if odp_maps_url:
            entry_text += f"  📍 ODP Location: [View on Maps]({odp_maps_url})\n" #ini utk markdown
            # entry_text += f"  📍 ODP Location: {odp_maps_url}\n"
        else:
            entry_text += f"  📍 ODP Location: Not available\n"
        
        entry_text += "\n"
        
        # Check if adding this entry would exceed Telegram's limit
        if len(current_message + entry_text) > 4000:
            # Save current message and start a new one
            messages.append(current_message.rstrip())
            current_message = f"📊 Lokasi: {location_name} (continued...)\n\n" + entry_text
        else:
            current_message += entry_text
    
    # Add the last message
    if current_message.strip():
        messages.append(current_message.rstrip())
    
    # If no messages were created (edge case), return a default message
    if not messages:
        messages = [f"📊 Lokasi: {location_name}\n\n❌ Tidak ada data ODP tersedia."]
    
    return messages

def format_customer_search_results(search_term, customers):
    """Format customer search results into readable messages"""
    messages = []
    current_message = f"🔍 Search Results for '{search_term}'\n"
    current_message += f"Found {len(customers)} customer(s):\n\n"
    
    for i, customer in enumerate(customers, 1):
        
        # ODP coordinates  
        odp_lat = customer.get('odp_latitude', '')
        odp_lng = customer.get('odp_longitude', '')        
        odp_maps_url = create_google_maps_url(odp_lat, odp_lng)
        
        # Add ODP coordinates if available
        location_markdown = f"[View on Maps]({odp_maps_url})" if odp_maps_url else ""

        customer_info = (
            f"{i}. 👤 {customer.get('name', 'N/A')}\n"
            f"   🏠 Address: {customer.get('address', 'N/A')}\n"
            f"   📍 Location: {customer.get('c_name', 'N/A')}\n"
            f"   🔌 ODC: {customer.get('code_odc', 'N/A')}\n"
            f"   📡 ODP: {customer.get('code_odp', 'N/A')} {location_markdown}\n"
            f"   📢 Port: {customer.get('no_port_odp', 'N/A')}\n"
            f"   📞 Phone: {customer.get('no_wa', 'N/A')}\n\n"
        )

        # Check if adding this entry would exceed Telegram's limit
        if len(current_message + customer_info) > 4000:
            # Save current message and start a new one
            messages.append(current_message.rstrip())
            current_message = f"🔍 Search Results for '{search_term}' (continued...)\n\n" + customer_info
        else:
            current_message += customer_info
    
    # Add the last message
    if current_message.strip():
        messages.append(current_message.rstrip())
    
    return messages

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