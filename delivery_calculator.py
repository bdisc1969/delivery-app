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

# Custom CSS for Bailey Blue background, white search bar, and white text
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
    /* White text for labels and output */
    .stMarkdown, .stSuccess, .stError {
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

def get_distance(destination):
    try:
        origin_encoded = quote(ORIGIN)
        destination_encoded = quote(destination)
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin_encoded}&destinations={destination_encoded}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data["status"] != "OK