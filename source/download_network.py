import os
import osmnx as ox


CITY = "Hyderabad, India"

OUTPUT_FILE = os.path.join(
    "data",
    "raw",
    "hyderabad.graphml"
)


def get_speed(data):
    speed = data.get("maxspeed")

    if isinstance(speed, list):
        speed = speed[0]

    if speed is not None:
        try:
            speed = str(speed).replace(" km/h", "").strip()
            return float(speed)
        except ValueError:
            pass

    highway = data.get("highway")

    if isinstance(highway, list):
        highway = highway[0]

    default_speeds = {
        "motorway": 80,
        "trunk": 70,
        "primary": 50,
        "secondary": 40,
        "tertiary": 35,
        "residential": 30,
        "unclassified": 30,
        "service": 20
    }

    return default_speeds.get(highway, 30)


def add_travel_time(G):

    for u, v, key, data in G.edges(
        keys=True,
        data=True
    ):

        length = float(data.get("length", 0))

        speed = get_speed(data)

        speed_mps = speed * 1000 / 3600

        if speed_mps > 0:
            travel_time = length / speed_mps
        else:
            travel_time = float("inf")

        data["speed_kph"] = speed
        data["travel_time"] = travel_time
        data["status"] = "open"

    return G


def download_network():

    print("Downloading road network...")
    print("City:", CITY)

    G = ox.graph_from_place(
        CITY,
        network_type="drive",
        simplify=True
    )

    G = add_travel_time(G)

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    ox.save_graphml(
        G,
        OUTPUT_FILE
    )

    print()
    print("Download completed.")
    print("Nodes:", len(G.nodes))
    print("Edges:", len(G.edges))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    download_network()