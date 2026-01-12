import streamlit as st
import requests
from urllib.parse import quote
import math

# Google Maps API key (stored in secrets.toml)
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Starting address
ORIGIN = "880 East Collin Raye Drive, De Queen, AR 71832"

# Pricing
FLAT_FEE_WITHIN_6_MILES = 20.00
BASE_FEE_BEYOND_6_MILES = 20.00
PER_MILE_RATE_BEYOND_6_MILES = 1.40

# Time calculation parameters
AVERAGE_SPEED_MPH = 30
UNLOAD_TIME_MINUTES = 30
TIME_INCREMENT = 30
MAX_BLOCK_TIME = 480
MIN_BLOCK_TIME = 30

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #2a2e7f;
        color: #ffffff;
    }
    .stTextInput > div > input,
    .stNumberInput > div > input {
        background-color: #ffffff;
        color: #000000;
        font-size: 18px;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton > button {
        background-color: #ffffff;
        color: #2a2e7f;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stMarkdown, .stError {
        color: #ffffff;
    }
    .stSuccess {
        background-color: #ff0000 !important;
        color: #ffffff !important;
        padding: 10px;
        border-radius: 5px;
        font-size: 18px;
        white-space: pre-line;
    }
    </style>
""", unsafe_allow_html=True)

# Display logo
try:
    with open("Bailey Discount - WhiteMan.png", "rb") as file:
        logo_image = file.read()
    st.image(logo_image, width=200, use_container_width=False)
except FileNotFoundError:
    st.write("Logo not available. Upload Bailey Discount - WhiteMan.png to GitHub.")

def get_distance(destination):
    try:
        origin_encoded = quote(ORIGIN)
        destination_encoded = quote(destination)
        url = (
            "https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origin_encoded}&destinations={destination_encoded}&key={API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        if data["status"] != "OK":
            return None, f"API Error: {data.get('error_message', 'Unknown error')}"

        element = data["rows"][0]["elements"][0]
        if element["status"] != "OK":
            return None, "Cannot find route to address"

        distance_meters = element["distance"]["value"]
        distance_miles = distance_meters / 1609.34
        return distance_miles, None

    except Exception as e:
        return None, f"Error: {str(e)}"

def calculate_block_time(distance):
    travel_time = (distance / AVERAGE_SPEED_MPH) * 60
    total_time = travel_time + UNLOAD_TIME_MINUTES
    rounded_time = math.ceil(total_time / TIME_INCREMENT) * TIME_INCREMENT
    return min(max(rounded_time, MIN_BLOCK_TIME), MAX_BLOCK_TIME)

def select_truck_and_multiplier(weight_lbs):
    """
    Returns:
    - truck_description (str)
    - price_multiplier (float)
    """
    if weight_lbs < 4000:
        return "Truck #102 – Malena", 1.0
    elif weight_lbs < 14000:
        return "Truck #101 – Orben", 1.0
    elif weight_lbs < 33000:
        return "Truck #103 – Vondell", 1.0
    else:
        return "Multiple Trips Required", 1.5

# Web app layout
st.title("Bailey's Delivery Price Calculator")

destination = st.text_input(
    "Enter Delivery Address (e.g., 100 W New York Ave, De Queen, AR 71832)"
)

weight_lbs = st.number_input(
    "Enter Shipment Weight (lbs)",
    min_value=0.0,
    step=100.0
)

if st.button("Calculate"):
    if not destination:
        st.error("Please enter an address")
    else:
        distance, error = get_distance(destination)

        if error:
            st.error(error)
        else:
            # Base pricing
            if distance <= 6:
                base_price = FLAT_FEE_WITHIN_6_MILES
            else:
                base_price = BASE_FEE_BEYOND_6_MILES + (distance * PER_MILE_RATE_BEYOND_6_MILES)

            # Truck selection & multiplier
            truck, multiplier = select_truck_and_multiplier(weight_lbs)
            total_price = base_price * multiplier

            # Time
            block_time = calculate_block_time(distance)

            st.success(
                f"Distance: {distance:.2f} miles\n"
                f"Shipment Weight: {weight_lbs:.0f} lbs\n"
                f"Assigned Truck: {truck}\n"
                f"Price Multiplier: {multiplier}x\n"
                f"Total Price: ${total_price:.2f}\n"
                f"Block Off Time: {block_time} minutes"
            )

# Display QR code
try:
    with open("qr_code.png", "rb") as file:
        qr_image = file.read()
    st.image(qr_image, caption="Scan to access this app", width=150, use_container_width=False)
except FileNotFoundError:
    st.write("QR code not available. Upload qr_code.png to GitHub.")
