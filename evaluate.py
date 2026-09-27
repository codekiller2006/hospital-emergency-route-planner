import requests
import csv
import os
import json


# =========================================================
# Configuration
# =========================================================

API_URL = "http://127.0.0.1:8000/route"

OUTPUT_DIR = "outputs"

CSV_FILE = os.path.join(OUTPUT_DIR, "results.csv")
JSON_FILE = os.path.join(OUTPUT_DIR, "results.json")


# =========================================================
# Test routes
# =========================================================
# These are temporary coordinates.
# Later we can replace them with actual hospital/emergency
# locations selected for the project.
# =========================================================

TEST_ROUTES = [
    {
        "name": "Route 1",
        "start_lat": 23.3441,
        "start_lon": 85.3096,
        "end_lat": 23.3700,
        "end_lon": 85.3300
    },
    {
        "name": "Route 2",
        "start_lat": 23.3500,
        "start_lon": 85.3000,
        "end_lat": 23.3800,
        "end_lon": 85.3400
    },
    {
        "name": "Route 3",
        "start_lat": 23.3300,
        "start_lon": 85.3200,
        "end_lat": 23.3600,
        "end_lon": 85.3500
    }
]


# =========================================================
# Storage for experiment results
# =========================================================

results = []


# =========================================================
# Run experiments
# =========================================================

for route in TEST_ROUTES:

    print(f"Running {route['name']}...")

    try:

        response = requests.post(
            API_URL,
            json={
                "start_lat": route["start_lat"],
                "start_lon": route["start_lon"],
                "end_lat": route["end_lat"],
                "end_lon": route["end_lon"]
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        astar = data["astar"]
        q_learning = data["q_learning"]

        results.append({
            "route": route["name"],

            "astar_execution_time": astar["execution_time"],
            "astar_travel_time": astar["travel_time"],
            "astar_distance": astar["distance"],

            "q_learning_execution_time": q_learning["execution_time"],
            "q_learning_travel_time": q_learning["travel_time"],
            "q_learning_distance": q_learning["distance"]
        })

        print("  Success")

    except requests.exceptions.RequestException as error:

        print(f"  API error: {error}")

    except KeyError as error:

        print(f"  Unexpected API response. Missing field: {error}")


# =========================================================
# Stop if no experiments succeeded
# =========================================================

if not results:

    print("\nNo results were collected.")
    print("Make sure the FastAPI server is running.")
    exit()


# =========================================================
# Create output directory
# =========================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# Save CSV
# =========================================================

with open(CSV_FILE, "w", newline="") as file:

    fieldnames = results[0].keys()

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


# =========================================================
# Save JSON
# =========================================================

with open(JSON_FILE, "w") as file:

    json.dump(
        results,
        file,
        indent=4
    )


# =========================================================
# Calculate averages
# =========================================================

avg_astar_execution = sum(
    r["astar_execution_time"] for r in results
) / len(results)

avg_q_execution = sum(
    r["q_learning_execution_time"] for r in results
) / len(results)

avg_astar_travel = sum(
    r["astar_travel_time"] for r in results
) / len(results)

avg_q_travel = sum(
    r["q_learning_travel_time"] for r in results
) / len(results)


# =========================================================
# Print summary
# =========================================================

print("\n========================================")
print("EXPERIMENT SUMMARY")
print("========================================")

print(f"Experiments completed: {len(results)}")

print(
    f"\nAverage A* execution time: "
    f"{avg_astar_execution:.6f} seconds"
)

print(
    f"Average Q-Learning execution time: "
    f"{avg_q_execution:.6f} seconds"
)

print(
    f"\nAverage A* travel time: "
    f"{avg_astar_travel:.2f} seconds"
)

print(
    f"Average Q-Learning travel time: "
    f"{avg_q_travel:.2f} seconds"
)

print("\nResults saved to:")
print(CSV_FILE)
print(JSON_FILE)