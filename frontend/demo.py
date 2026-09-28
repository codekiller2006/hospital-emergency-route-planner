import streamlit as st
import requests
import folium
import math
from streamlit_folium import st_folium

# =========================================================
# Configuration & Real Hyderabad Hospitals
# =========================================================
API_URL = "http://127.0.0.1:8000/route"

HOSPITALS = {
    "Osmania General Hospital": (17.3731, 78.4716),
    "Apollo Hospital Jubilee Hills": (17.4168, 78.4074),
    "Yashoda Hospital Somajiguda": (17.4258, 78.4552),
    "Care Hospitals Banjara Hills": (17.4174, 78.4485),
    "KIMS Secunderabad": (17.4402, 78.4851)
}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance in kilometers using the Haversine formula."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    a = math.sin((lat2 - lat1) / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

st.set_page_config(page_title="Hospital Emergency Route Planner", page_icon="🏥", layout="wide")
st.title("🏥 Hospital Emergency Route Planner")
st.write("Automatically locates the nearest hospital and calculates the optimal AI route avoiding traffic jams.")

# =========================================================
# User Input (Start Location Only)
# =========================================================
st.sidebar.header("Emergency Location")
start_lat = st.sidebar.number_input("Incident Latitude", value=17.3850, format="%.6f")
start_lon = st.sidebar.number_input("Incident Longitude", value=78.4867, format="%.6f")

# 1. SMART LOGIC: Find the nearest hospital automatically
closest_hospital = None
min_distance = float('inf')

for name, coords in HOSPITALS.items():
    dist = calculate_distance(start_lat, start_lon, coords[0], coords[1])
    if dist < min_distance:
        min_distance = dist
        closest_hospital = name

end_lat, end_lon = HOSPITALS[closest_hospital]

st.sidebar.markdown("---")
st.sidebar.success(f"**Nearest Facility Found:**\n\n{closest_hospital}\n\nDistance: {min_distance:.2f} km")

if "clicked" not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.sidebar.button("Dispatch Ambulance", on_click=click_button)

# =========================================================
# Execute API & Render
# =========================================================
if st.session_state.clicked:
    payload = {
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon
    }

    try:
        with st.spinner("Analyzing traffic and calculating AI routes..."):
            response = requests.post(API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

        astar = data["astar"]
        q_learning = data["q_learning"]

        astar_path = astar.get("path", [])
        q_learning_path = q_learning.get("path", [])

        route_map = folium.Map(
            location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2],
            zoom_start=14
        )

        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            attr="Tiles © Esri",
            name="Esri World Street Map"
        ).add_to(route_map)

        # Markers
        folium.Marker([start_lat, start_lon], popup="Emergency Start", tooltip="Incident", icon=folium.Icon(color="green", icon="warning-sign")).add_to(route_map)
        folium.Marker([end_lat, end_lon], popup=closest_hospital, tooltip=closest_hospital, icon=folium.Icon(color="red", icon="plus")).add_to(route_map)

        if astar_path:
            folium.PolyLine(astar_path, tooltip="A* Route", color="#3388ff", weight=6).add_to(route_map)
        if q_learning_path:
            folium.PolyLine(q_learning_path, tooltip="Q-Learning Route", color="#ff3333", weight=6).add_to(route_map)

        st_folium(route_map, width=1200, height=600, returned_objects=[])

        # Metrics
        st.subheader("Route Performance")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### A* Search")
            st.metric("Execution Time", f"{astar['execution_time']:.6f} s")
            if astar.get('travel_time') is not None and astar.get('travel_time') != float('inf'):
                st.metric("Simulated Travel Time", f"{astar['travel_time']:.2f} s")
                st.metric("Distance", f"{astar['distance']:.2f} m")
            else:
                st.metric("Status", "Route Failed")

        with col2:
            st.markdown("### Q-Learning")
            st.metric("Execution Time", f"{q_learning['execution_time']:.6f} s")
            if q_learning.get('travel_time') is not None and q_learning.get('travel_time') != float('inf'):
                st.metric("Simulated Travel Time", f"{q_learning['travel_time']:.2f} s")
                st.metric("Distance", f"{q_learning['distance']:.2f} m")
            else:
                st.metric("Status", "Route Failed (Timed out)")

    except Exception as e:
        st.error(f"Error connecting to backend or parsing data: {e}")