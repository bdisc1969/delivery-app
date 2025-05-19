import streamlit as st
import requests
from urllib.parse import quote

# Google Maps API key (stored in secrets.toml)
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Starting address
ORIGIN = "880 East Collin Raye Drive, De Queen, AR 71832"

# Pricing
FLAT_FEE_WITHIN_6_MILES = 20.00  # $20 flat fee for <= 6 miles
BASE_FEE_BEYOND_6_MILES = 20.00  # $20 base fee for > 6 miles
PER_MILE_RATE_BEYOND_6_MILES = 1.40  # $1.40 per mile for > 6 miles

def get_distance(destination):
    try:
        origin_encoded = quote(ORIGIN)
        destination_encoded = quote(destination)
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_encoded}&destinations={destination_encoded}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data["status"] != "OK":
            return None, f"API Error: {data.get('error_message', 'Unknown error')}"
        element = data["rows"][0]["elements"][0]
        if element["status"] != "OK":
            return None, "Cannot find route to address"
        distance_meters = element["distance"]["value"]
        distance_miles = distance_meters / 1609.34  # Convert to miles
        return distance_miles, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# Web app layout
st.title("Delivery Price Calculator")
destination = st.text_input("Enter Delivery Address (e.g., 123 Main St, Texarkana, AR)")
if st.button("Calculate"):
    if not destination:
        st.error("Please enter an address")
    else:
        distance, error = get_distance(destination)
        if error:
            st.error(error)
        else:
            # Calculate price based on distance
            if distance <= 6:
                total_price = FLAT_FEE_WITHIN_6_MILES
            else:
                total_price = BASE_FEE_BEYOND_6_MILES + (distance * PER_MILE_RATE_BEYOND_6_MILES)
            st.success(f"Distance: {distance:.2f} miles\nTotal Price: ${total_price:.2f}")