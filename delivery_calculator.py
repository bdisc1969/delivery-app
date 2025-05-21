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
    /* Main background */
    .stApp {
        background-color: #2a2e7f;
        color: #ffffff;
    }
    /* White search bar */
    .stTextInput > div > input {
        background-color: #ffffff;
        color: #000000;
        font-size: 18px;
        padding: 10px;
        border-radius: 5px;
    }
    /* White button with blue text */
    .stButton > button {
        background-color: #ffffff;
        color: #2a2e7f;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 5px;
    }
    /* White text for labels and errors */
    .stMarkdown, .stError {
        color: #ffffff;
    }
    /* Red box with white text for results */
    .stSuccess {
        background-color: #ff0000 !important;
        color: #ffffff !important;
        padding: 10px;
        border-radius: 5px;
        font-size: 18px;
    }
    /* Center logo */
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 200px;
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
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_encoded}&destinations={destination_encoded}&key={API_KEY}"
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
    block_time = min(max(rounded_time, MIN_BLOCK_TIME), MAX_BLOCK_TIME)
    return block_time

# Web app layout
st.title("Bailey's Delivery Price Calculator")
destination = st.text_input("Enter Delivery Address (e.g., 100 W New York Ave, De Queen, AR 71832)")
if st.button("Calculate"):
    if not destination:
        st.error("Please enter an address")
    else:
        distance, error = get_distance(destination)
        if error:
            st.error(error)
        else:
            if distance <= 6:
                total_price = FLAT_FEE_WITHIN_6_MILES
            else:
                total_price = BASE_FEE_BEYOND_6_MILES + (distance * PER_MILE_RATE_BEYOND_6_MILES)
            block_time = calculate_block_time(distance)
            st.success(f"Distance: {distance:.2f} miles\nTotal Price: ${total_price