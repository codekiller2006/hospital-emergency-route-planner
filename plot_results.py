import os

import pandas as pd
import matplotlib.pyplot as plt


# =========================================================
# Configuration
# =========================================================

INPUT_FILE = "outputs/results.csv"
OUTPUT_DIR = "outputs/charts"


# =========================================================
# Check input file
# =========================================================

if not os.path.exists(INPUT_FILE):
    print(f"Error: {INPUT_FILE} does not exist.")
    print("Run the evaluation first to generate results.csv.")
    exit()


# =========================================================
# Create output directory
# =========================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# Load results
# =========================================================

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} experiment results.")


# =========================================================
# Chart 1 — Execution Time
# =========================================================

plt.figure()

plt.plot(
    df["route"],
    df["astar_execution_time"],
    marker="o",
    label="A*"
)

plt.plot(
    df["route"],
    df["q_learning_execution_time"],
    marker="o",
    label="Q-Learning"
)

plt.xlabel("Experiment")
plt.ylabel("Execution Time (seconds)")
plt.title("A* vs Q-Learning Execution Time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "execution_time.png"
    ),
    dpi=300
)

plt.close()


# =========================================================
# Chart 2 — Simulated Travel Time
# =========================================================

plt.figure()

plt.plot(
    df["route"],
    df["astar_travel_time"],
    marker="o",
    label="A*"
)

plt.plot(
    df["route"],
    df["q_learning_travel_time"],
    marker="o",
    label="Q-Learning"
)

plt.xlabel("Experiment")
plt.ylabel("Simulated Travel Time (seconds)")
plt.title("A* vs Q-Learning Simulated Travel Time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "travel_time.png"
    ),
    dpi=300
)

plt.close()


# =========================================================
# Chart 3 — Route Distance
# =========================================================

plt.figure()

plt.plot(
    df["route"],
    df["astar_distance"],
    marker="o",
    label="A*"
)

plt.plot(
    df["route"],
    df["q_learning_distance"],
    marker="o",
    label="Q-Learning"
)

plt.xlabel("Experiment")
plt.ylabel("Distance (meters)")
plt.title("A* vs Q-Learning Route Distance")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "distance.png"
    ),
    dpi=300
)

plt.close()


# =========================================================
# Completion message
# =========================================================

print("\nCharts generated successfully.")

print(
    f"Charts saved in: {OUTPUT_DIR}"
)

print("\nGenerated files:")

print("1. execution_time.png")
print("2. travel_time.png")
print("3. distance.png")