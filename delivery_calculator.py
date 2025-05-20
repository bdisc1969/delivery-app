import streamlit as st
import requests
from urllib.parse import quote
import base64

# Google Maps API key (stored in secrets.toml)
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Starting address
ORIGIN = "880 East Collin Raye Drive, De Queen, AR 71832"

# Pricing
FLAT_FEE_WITHIN_6_MILES = 20.00  # $20 flat fee for <= 6 miles
BASE_FEE_BEYOND_6_MILES = 20.00  # $20 base fee for > 6 miles
PER_MILE_RATE_BEYOND_6_MILES = 1.40  # $1.40 per mile for > 6 miles

# Custom CSS for Bailey Blue background, white search bar, white text, and red results box
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
        background-color: #ff0000;
        color: #ffffff;
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

# Display logo (if uploaded to GitHub as Bailey Discount - WhiteMan.png)
try:
    with open("Bailey Discount - WhiteMan.png", "rb") as file:
        logo_image = file.read()
    st.image(logo_image, width=200, use_column_width=False)
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
        distance_miles = distance_meters / 1609.34  # Convert to miles
        return distance_miles, None
    except Exception as e:
        return None, f"Error: {str(e)}"

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
            # Calculate price based on distance
            if distance <= 6:
                total_price = FLAT_FEE_WITHIN_6_MILES
            else:
                total_price = BASE_FEE_BEYOND_6_MILES + (distance * PER_MILE_RATE_BEYOND_6_MILES)
            st.success(f"Distance: {distance:.2f} miles\nTotal Price: ${total_price:.2f}")

# Display QR code (if uploaded to GitHub as qr_code.png)
try:
    with open("qr_code.png", "rb") as file:
        qr_image = file.read()
    st.image(qr_image, caption="Scan to access this app", width=150)
except FileNotFoundError:
    st.write("QR code not available. Upload qr_code.png to GitHub.")