import csv
import json
import os


# =========================================================
# File configuration
# =========================================================

INPUT_FILE = "outputs/results.csv"
OUTPUT_FILE = "outputs/summary.json"


# =========================================================
# Load experiment results
# =========================================================

if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} does not exist.")
    print("Run the evaluation after the FastAPI server is available.")
    exit()


with open(INPUT_FILE, "r") as file:
    reader = csv.DictReader(file)
    results = list(reader)


if not results:
    print("No experiment results found.")
    exit()


# =========================================================
# Convert numerical values from strings to floats
# =========================================================

for result in results:

    for key in result:

        if key != "route":
            result[key] = float(result[key])


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

avg_astar_distance = sum(
    r["astar_distance"] for r in results
) / len(results)

avg_q_distance = sum(
    r["q_learning_distance"] for r in results
) / len(results)


# =========================================================
# Calculate percentage differences
# =========================================================

def percentage_difference(a, b):
    """
    Calculate the percentage change from A to B.
    """
    if a == 0:
        return 0

    return ((b - a) / a) * 100


execution_difference = percentage_difference(
    avg_astar_execution,
    avg_q_execution
)

travel_difference = percentage_difference(
    avg_astar_travel,
    avg_q_travel
)

distance_difference = percentage_difference(
    avg_astar_distance,
    avg_q_distance
)


# =========================================================
# Create summary
# =========================================================

summary = {

    "experiments": len(results),

    "average_metrics": {

        "astar": {
            "execution_time_seconds": avg_astar_execution,
            "travel_time_seconds": avg_astar_travel,
            "distance_meters": avg_astar_distance
        },

        "q_learning": {
            "execution_time_seconds": avg_q_execution,
            "travel_time_seconds": avg_q_travel,
            "distance_meters": avg_q_distance
        }
    },

    "percentage_difference_q_learning_vs_astar": {

        "execution_time": execution_difference,
        "travel_time": travel_difference,
        "distance": distance_difference
    }
}


# =========================================================
# Save summary
# =========================================================

with open(OUTPUT_FILE, "w") as file:

    json.dump(
        summary,
        file,
        indent=4
    )


# =========================================================
# Display results
# =========================================================

print("\n========================================")
print("QUANTITATIVE COMPARISON")
print("========================================")

print(f"Experiments: {len(results)}")

print("\nAverage metrics:")

print(
    f"A* execution time: "
    f"{avg_astar_execution:.6f} s"
)

print(
    f"Q-Learning execution time: "
    f"{avg_q_execution:.6f} s"
)

print(
    f"\nA* travel time: "
    f"{avg_astar_travel:.2f} s"
)

print(
    f"Q-Learning travel time: "
    f"{avg_q_travel:.2f} s"
)

print(
    f"\nA* distance: "
    f"{avg_astar_distance:.2f} m"
)

print(
    f"Q-Learning distance: "
    f"{avg_q_distance:.2f} m"
)

print("\nPercentage difference (Q-Learning vs A*)")

print(
    f"Execution time: "
    f"{execution_difference:+.2f}%"
)

print(
    f"Travel time: "
    f"{travel_difference:+.2f}%"
)

print(
    f"Distance: "
    f"{distance_difference:+.2f}%"
)

print(f"\nSummary saved to {OUTPUT_FILE}")