import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# =========================================================
# Configuration
# =========================================================
API_URL = "http://127.0.0.1:8000/route"

st.set_page_config(page_title="Hospital Emergency Route Planner", page_icon="🏥", layout="wide")
st.title("🏥 Hospital Emergency Route Planner")
st.write("Compare A* Search and Q-Learning routes under simulated dynamic traffic conditions.")

# =========================================================
# Coordinate input
# =========================================================
st.sidebar.header("Route Configuration")
start_lat = st.sidebar.number_input("Start Latitude", value=17.3850, format="%.6f")
start_lon = st.sidebar.number_input("Start Longitude", value=78.4867, format="%.6f")
end_lat = st.sidebar.number_input("Destination Latitude", value=17.3880, format="%.6f")
end_lon = st.sidebar.number_input("Destination Longitude", value=78.4900, format="%.6f")

# 1. FIX: Use session state to remember the button was clicked even when the page refreshes
if "clicked" not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.sidebar.button("Calculate Routes", on_click=click_button)

# =========================================================
# Calculate routes
# =========================================================
if st.session_state.clicked:
    payload = {
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon
    }

    try:
        with st.spinner("Calculating emergency routes..."):
            response = requests.post(API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

        st.success("Routes calculated successfully!")
        astar = data["astar"]
        q_learning = data["q_learning"]

        astar_path = astar.get("path", [])
        q_learning_path = q_learning.get("path", [])

        route_map = folium.Map(
            location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2],
            zoom_start=15
        )

        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            attr="Tiles © Esri",
            name="Esri World Street Map"
        ).add_to(route_map)

        folium.Marker([start_lat, start_lon], popup="Emergency Start", tooltip="Start", icon=folium.Icon(color="green", icon="play")).add_to(route_map)
        folium.Marker([end_lat, end_lon], popup="Hospital", tooltip="Destination", icon=folium.Icon(color="red", icon="plus")).add_to(route_map)

        if astar_path:
            folium.PolyLine(astar_path, tooltip="A* Route", color="#3388ff", weight=6).add_to(route_map)
        if q_learning_path:
            folium.PolyLine(q_learning_path, tooltip="Q-Learning Route", color="#ff3333", weight=6).add_to(route_map)

        # 2. FIX: Add returned_objects=[] to stop the map from forcing a page refresh
        st_folium(route_map, width=1200, height=600, returned_objects=[])

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