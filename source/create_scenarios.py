from environment import (
    load_graph,
    simulate_traffic,
    simulate_road_closures,
    save_graph
)


INPUT_GRAPH = "data/raw/hyderabad.graphml"


def main():

    print("Loading base graph...")

    G = load_graph(INPUT_GRAPH)

    print("Base graph loaded.")
    print("Nodes:", len(G.nodes))
    print("Edges:", len(G.edges))

    print()
    print("Creating normal scenario...")

    save_graph(
        G,
        "data/simulated/normal.graphml"
    )

    print()
    print("Creating light traffic scenario...")

    light_traffic = simulate_traffic(
        G,
        percentage=5,
        multiplier=1.5,
        seed=42
    )

    save_graph(
        light_traffic,
        "data/simulated/light_traffic.graphml"
    )

    print()
    print("Creating heavy traffic scenario...")

    heavy_traffic = simulate_traffic(
        G,
        percentage=15,
        multiplier=3.0,
        seed=42
    )

    save_graph(
        heavy_traffic,
        "data/simulated/heavy_traffic.graphml"
    )

    print()
    print("Creating road closure scenario...")

    road_closure = simulate_road_closures(
        G,
        percentage=5,
        seed=42
    )

    save_graph(
        road_closure,
        "data/simulated/road_closure.graphml"
    )

    print()
    print("All scenarios created successfully.")


if __name__ == "__main__":
    main()