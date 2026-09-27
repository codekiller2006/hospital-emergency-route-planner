# import folium
# import os


# # =========================================================
# # Temporary API response
# # =========================================================
# # Role 4's FastAPI will eventually provide this data.
# # For now, we use dummy data to test our frontend.
# # =========================================================

# api_result = {
#     "astar": {
#         "path": [
#             [23.3441, 85.3096],
#             [23.3500, 85.3150],
#             [23.3600, 85.3220],
#             [23.3700, 85.3300]
#         ],
#         "execution_time": 0.012,
#         "travel_time": 542.4,
#         "distance": 3840.2
#     },

#     "q_learning": {
#         "path": [
#             [23.3441, 85.3096],
#             [23.3480, 85.3200],
#             [23.3580, 85.3270],
#             [23.3700, 85.3300]
#         ],
#         "execution_time": 0.034,
#         "travel_time": 481.7,
#         "distance": 4210.5
#     }
# }


# # =========================================================
# # Extract routes
# # =========================================================

# astar = api_result["astar"]
# q_learning = api_result["q_learning"]

# astar_route = astar["path"]
# q_learning_route = q_learning["path"]

# start = astar_route[0]
# destination = astar_route[-1]


# # =========================================================
# # Calculate map center
# # =========================================================

# center = (
#     (start[0] + destination[0]) / 2,
#     (start[1] + destination[1]) / 2
# )


# # =========================================================
# # Create map
# # =========================================================

# route_map = folium.Map(
#     location=center,
#     zoom_start=13
# )


# # =========================================================
# # Add Esri street map
# # =========================================================

# folium.TileLayer(
#     tiles=(
#         "https://server.arcgisonline.com/ArcGIS/rest/services/"
#         "World_Street_Map/MapServer/tile/{z}/{y}/{x}"
#     ),
#     attr="Tiles © Esri",
#     name="Esri World Street Map"
# ).add_to(route_map)


# # =========================================================
# # Start marker
# # =========================================================

# folium.Marker(
#     location=start,
#     popup="Emergency Route Start",
#     tooltip="Start",
#     icon=folium.Icon(color="green", icon="play")
# ).add_to(route_map)


# # =========================================================
# # Destination marker
# # =========================================================

# folium.Marker(
#     location=destination,
#     popup="Hospital / Destination",
#     tooltip="Destination",
#     icon=folium.Icon(color="red", icon="plus")
# ).add_to(route_map)


# # =========================================================
# # A* route
# # =========================================================

# folium.PolyLine(
#     locations=astar_route,
#     tooltip="A* Route",
#     weight=6
# ).add_to(route_map)


# # =========================================================
# # Q-Learning route
# # =========================================================

# folium.PolyLine(
#     locations=q_learning_route,
#     tooltip="Q-Learning Route",
#     weight=6
# ).add_to(route_map)


# # =========================================================
# # Add metrics to the map
# # =========================================================

# metrics_html = f"""
# <div style="
#     position: fixed;
#     bottom: 30px;
#     left: 30px;
#     width: 280px;
#     background-color: white;
#     border: 2px solid grey;
#     z-index: 9999;
#     padding: 15px;
#     font-size: 14px;
# ">

# <h4>Route Comparison</h4>

# <b>A* Search</b><br>
# Execution time: {astar["execution_time"]:.4f} s<br>
# Travel time: {astar["travel_time"]:.2f} s<br>
# Distance: {astar["distance"]:.2f} m

# <hr>

# <b>Q-Learning</b><br>
# Execution time: {q_learning["execution_time"]:.4f} s<br>
# Travel time: {q_learning["travel_time"]:.2f} s<br>
# Distance: {q_learning["distance"]:.2f} m

# </div>
# """

# route_map.get_root().html.add_child(
#     folium.Element(metrics_html)
# )


# # =========================================================
# # Layer control
# # =========================================================

# folium.LayerControl().add_to(route_map)


# # =========================================================
# # Save output
# # =========================================================

# os.makedirs("outputs", exist_ok=True)

# output_file = "outputs/route_comparison.html"

# route_map.save(output_file)

# print(f"Map generated successfully: {output_file}")

# -----------------------------------------BELOW CODE IS AFTER BACKEND --------------------------------------

import os
import requests
import folium


# =========================================================
# Configuration
# =========================================================

API_URL = "http://127.0.0.1:8000/route"

OUTPUT_FILE = "outputs/route_comparison.html"


# =========================================================
# Test coordinates
# =========================================================
# These will eventually be entered by the user through
# the frontend.

start = (23.3441, 85.3096)
destination = (23.3700, 85.3300)


# =========================================================
# Request route information from FastAPI
# =========================================================

def get_routes_from_api(start, destination):

    payload = {
        "start_lat": start[0],
        "start_lon": start[1],
        "end_lat": destination[0],
        "end_lon": destination[1]
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# Get data from API
# =========================================================

try:

    api_result = get_routes_from_api(
        start,
        destination
    )

    print("Successfully received data from FastAPI.")

except requests.exceptions.RequestException as error:

    print("Could not connect to FastAPI.")
    print(f"Error: {error}")

    print("\nUsing temporary test data instead.")

    # -----------------------------------------------------
    # Temporary data for frontend testing
    # -----------------------------------------------------

    api_result = {

        "astar": {

            "path": [
                [23.3441, 85.3096],
                [23.3500, 85.3150],
                [23.3600, 85.3220],
                [23.3700, 85.3300]
            ],

            "execution_time": 0.012,
            "travel_time": 542.4,
            "distance": 3840.2
        },

        "q_learning": {

            "path": [
                [23.3441, 85.3096],
                [23.3480, 85.3200],
                [23.3580, 85.3270],
                [23.3700, 85.3300]
            ],

            "execution_time": 0.034,
            "travel_time": 481.7,
            "distance": 4210.5
        }
    }


# =========================================================
# Extract algorithm results
# =========================================================

astar = api_result["astar"]
q_learning = api_result["q_learning"]

astar_route = astar["path"]
q_learning_route = q_learning["path"]


# =========================================================
# Create map
# =========================================================

center = (
    (start[0] + destination[0]) / 2,
    (start[1] + destination[1]) / 2
)

route_map = folium.Map(
    location=center,
    zoom_start=13
)


# =========================================================
# Add Esri street map
# =========================================================

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Street_Map/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Tiles © Esri",
    name="Esri World Street Map"
).add_to(route_map)


# =========================================================
# Add start marker
# =========================================================

folium.Marker(
    location=start,
    popup="Emergency Route Start",
    tooltip="Start",
    icon=folium.Icon(
        color="green",
        icon="play"
    )
).add_to(route_map)


# =========================================================
# Add destination marker
# =========================================================

folium.Marker(
    location=destination,
    popup="Hospital / Destination",
    tooltip="Destination",
    icon=folium.Icon(
        color="red",
        icon="plus"
    )
).add_to(route_map)


# =========================================================
# Draw A* route
# =========================================================

folium.PolyLine(
    locations=astar_route,
    tooltip="A* Route",
    weight=6
).add_to(route_map)


# =========================================================
# Draw Q-Learning route
# =========================================================

folium.PolyLine(
    locations=q_learning_route,
    tooltip="Q-Learning Route",
    weight=6
).add_to(route_map)


# =========================================================
# Display metrics
# =========================================================

metrics_html = f"""
<div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    width: 300px;
    background-color: white;
    border: 2px solid grey;
    z-index: 9999;
    padding: 15px;
    font-size: 14px;
">

<h3>Route Comparison</h3>

<b>A* Search</b><br>
Execution time:
{astar["execution_time"]:.6f} s<br>

Simulated travel time:
{astar["travel_time"]:.2f} s<br>

Distance:
{astar["distance"]:.2f} m

<hr>

<b>Q-Learning</b><br>
Execution time:
{q_learning["execution_time"]:.6f} s<br>

Simulated travel time:
{q_learning["travel_time"]:.2f} s<br>

Distance:
{q_learning["distance"]:.2f} m

</div>
"""

route_map.get_root().html.add_child(
    folium.Element(metrics_html)
)


# =========================================================
# Add layer control
# =========================================================

folium.LayerControl().add_to(route_map)


# =========================================================
# Save map
# =========================================================

os.makedirs("outputs", exist_ok=True)

route_map.save(OUTPUT_FILE)

print(f"\nMap generated successfully:")
print(OUTPUT_FILE)