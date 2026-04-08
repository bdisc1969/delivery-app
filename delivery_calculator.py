import streamlit as st
import requests
from urllib.parse import quote
import math

# Google Maps API key (stored in secrets.toml)
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Starting address
ORIGIN = "880 East Collin Raye Drive, De Queen, AR 71832"

# =========================
# PRICING (BASE + FUEL LOGIC)
# =========================

# Base pricing (your stable pricing)
FLAT_FEE_WITHIN_6_MILES = 25.00
BASE_FEE_BEYOND_6_MILES = 25.00
PER_MILE_RATE_BEYOND_6_MILES = 1.60

# Fuel pricing inputs (ONLY thing you update going forward)
CURRENT_DIESEL_PRICE = 5.00
BASELINE_DIESEL_PRICE = 3.50

# How aggressively you pass fuel cost through (tune this)
FUEL_COST_FACTOR = 0.20

# Calculated fuel surcharge per mile
FUEL_SURCHARGE_PER_MILE = max(
    0,
    (CURRENT_DIESEL_PRICE - BASELINE_DIESEL_PRICE) * FUEL_COST_FACTOR
)

# =========================
# TIME CALCULATION
# =========================
AVERAGE_SPEED_MPH = 30
UNLOAD_TIME_MINUTES = 30
TIME_INCREMENT = 30
MAX_BLOCK_TIME = 480
MIN_BLOCK_TIME = 30

# =========================
# TRUCK PARAMETERS
# =========================
MALENA_MAX_WEIGHT = 2500
MALENA_MAX_DISTANCE = 15
ORBEN_MAX_WEIGHT = 14000
VONDELL_MAX_WEIGHT = 33000
MULTI_TRIP_MULTIPLIER = 1.5

# =========================
# UI STYLING
# =========================
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
    </style>
""", unsafe_allow_html=True)

# =========================
# LOGO
# =========================
try:
    with open("Bailey Discount - WhiteMan.png", "rb") as file:
        logo_image = file.read()
    st.image(logo_image, width=200, use_container_width=False)
except FileNotFoundError:
    st.write("Logo not available. Upload Bailey Discount - WhiteMan.png to GitHub.")

# =========================
# DISTANCE FUNCTION
# =========================
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

# =========================
# TIME FUNCTION
# =========================
def calculate_block_time(distance):
    travel_time = (distance / AVERAGE_SPEED_MPH) * 60
    total_time = travel_time + UNLOAD_TIME_MINUTES
    rounded_time = math.ceil(total_time / TIME_INCREMENT) * TIME_INCREMENT
    return min(max(rounded_time, MIN_BLOCK_TIME), MAX_BLOCK_TIME)

# =========================
# TRUCK LOGIC
# =========================
def select_truck_and_multiplier(weight_lbs, distance, over_12ft, consolidate_delivery):

    if consolidate_delivery == "Yes":
        if weight_lbs <= VONDELL_MAX_WEIGHT:
            return "Truck #103 – Vondell", 1.0
        else:
            return "Multiple Trips Required", MULTI_TRIP_MULTIPLIER

    if over_12ft == "Yes":
        if weight_lbs <= ORBEN_MAX_WEIGHT:
            return "Truck #101 – Orben", 1.0
        elif weight_lbs <= VONDELL_MAX_WEIGHT:
            return "Truck #103 – Vondell", 1.0
        else:
            return "Multiple Trips Required", MULTI_TRIP_MULTIPLIER

    if weight_lbs <= MALENA_MAX_WEIGHT and distance <= MALENA_MAX_DISTANCE:
        return "Truck #102 – Malena", 1.0
    elif weight_lbs <= ORBEN_MAX_WEIGHT:
        return "Truck #101 – Orben", 1.0
    elif weight_lbs <= VONDELL_MAX_WEIGHT:
        return "Truck #103 – Vondell", 1.0
    else:
        return "Multiple Trips Required", MULTI_TRIP_MULTIPLIER

# =========================
# APP UI
# =========================
st.title("Bailey's Delivery Price Calculator")

destination = st.text_input("Enter Delivery Address")

weight_lbs = st.number_input(
    "Enter Shipment Weight (lbs)",
    min_value=0.0,
    step=100.0
)

over_12ft = st.radio(
    "Any material over 12 feet long?",
    ["No", "Yes"],
    horizontal=True
)

consolidate_delivery = st.radio(
    "Is there already a delivery scheduled that this order should ride with?",
    ["No", "Yes"],
    horizontal=True
)

if st.button("Calculate"):
    if not destination:
        st.error("Please enter an address")
    else:
        distance, error = get_distance(destination)

        if error:
            st.error(error)
        else:
            # Apply fuel-adjusted rate
            effective_rate = PER_MILE_RATE_BEYOND_6_MILES + FUEL_SURCHARGE_PER_MILE

            if distance <= 6:
                base_price = FLAT_FEE_WITHIN_6_MILES
            else:
                base_price = BASE_FEE_BEYOND_6_MILES + (distance * effective_rate)

            truck, multiplier = select_truck_and_multiplier(
                weight_lbs,
                distance,
                over_12ft,
                consolidate_delivery
            )

            total_price = base_price * multiplier
            block_time = calculate_block_time(distance)

            st.markdown(f"""
            <div style="
                background-color:#ffffff;
                color:#000000;
                padding:20px;
                border-radius:10px;
                font-size:18px;
            ">

            <div style="font-size:32px; font-weight:bold; color:#d32f2f;">
            🚚 {truck}
            </div>

            <hr>

            <div><strong>Distance:</strong> {distance:.2f} miles</div>
            <div><strong>Weight:</strong> {weight_lbs:.0f} lbs</div>
            <div><strong>Delivery Price:</strong> ${total_price:.2f}</div>
            <div><strong>Time Block:</strong> {block_time} minutes</div>

            </div>
            """, unsafe_allow_html=True)

# =========================
# QR CODE
# =========================
try:
    with open("qr_code.png", "rb") as file:
        qr_image = file.read()
    st.image(qr_image, caption="Scan to access this app", width=150, use_container_width=False)
except FileNotFoundError:
    st.write("QR code not available.")
