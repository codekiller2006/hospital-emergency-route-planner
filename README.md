# Hospital Emergency Route Planner

Compares **A\* Search** and **Q-Learning** for ambulance routing on Hyderabad's real road network, under simulated traffic congestion and road closures.

---

## Overview

In an emergency, the shortest route on a map is not always the fastest one in practice. Congestion and closed roads change the picture minute by minute.

This project builds a routing system on the **actual street network of Hyderabad, India** (from OpenStreetMap), layers simulated traffic and road closures on top, and runs two very different AI approaches on the same request:

| | A\* Search | Q-Learning |
|---|---|---|
| **Type** | Informed graph search | Reinforcement learning |
| **Idea** | A custom risk-aware heuristic steers the search away from congested or closed edges | The agent learns a route by trial and error, guided by reward shaping |
| **Strength** | Fast and deterministic | Learns directly from the traffic conditions |
| **Cost** | Near-instant | Trains on every request |

A Streamlit dashboard finds the nearest hospital to an incident location, sends the request to a FastAPI backend, and draws both routes on one map with a side-by-side metric comparison.

---

## Tech Stack

| Layer | Tools |
|---|---|
| **Language** | Python 3.11+ |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **Frontend** | Streamlit, Folium, streamlit-folium |
| **Graph and data** | OSMnx, NetworkX, Pandas, NumPy |
| **Evaluation** | Matplotlib, Pandas |

---

## Features

- **Real-world routing** on OSMnx / NetworkX street data for Hyderabad.
- **Traffic scenarios:** normal, light traffic, heavy traffic, and road closures, generated reproducibly with a fixed seed.
- **Two algorithms, one request:** A\* and Q-Learning both run for every route request and are returned together.
- **Automatic nearest-hospital selection** from five Hyderabad hospitals using the Haversine formula.
- **Interactive dashboard** with a Folium map and side-by-side metrics: execution time, simulated travel time, and distance.
- **Evaluation pipeline** that runs test routes and produces CSV/JSON results, a summary, and comparison charts.

---

## How It Works

The system has two stages: a one-time data preparation step, and a runtime flow for each route request.

```text
DATA PREPARATION (run once)

    OpenStreetMap
         |
         v
    source/download_network.py    ->    data/raw/hyderabad.graphml
         |
         v
    source/create_scenarios.py    ->    data/simulated/*.graphml


RUNTIME (for every route request)

    Streamlit dashboard  (frontend/demo.py)
         |
         |   sends incident location + nearest hospital
         v
    FastAPI backend  (backend/main.py)
         |
         |-----> A* router          (algorithms/a_star.py)
         |
         |-----> Q-Learning router  (algorithms/q_learning.py)
         |
         v
    Both routes + metrics returned to the dashboard
         |
         v
    Folium map + comparison panel
```

### Traffic scenarios

`source/create_scenarios.py` builds four scenarios from the base graph, selecting edges at random with `seed=42`.

| Scenario | Effect | Output file |
|---|---|---|
| Normal | Unmodified graph | `data/simulated/normal.graphml` |
| Light traffic | 5% of edges, travel time x1.5 | `data/simulated/light_traffic.graphml` |
| Heavy traffic | 15% of edges, travel time x3.0 | `data/simulated/heavy_traffic.graphml` |
| Road closure | 5% of edges closed (`travel_time = inf`) | `data/simulated/road_closure.graphml` |

> The backend currently loads **`heavy_traffic.graphml`**. To try another scenario, change `graph_path` in `backend/main.py`.

---

## Project Structure

```text
hospital-emergency-route-planner/
|-- algorithms/
|   |-- a_star.py             # A* search with custom dynamic heuristic
|   `-- q_learning.py         # Q-Learning router with reward shaping
|-- backend/
|   |-- main.py               # FastAPI app: loads graph, exposes POST /route
|   `-- schemas.py            # Pydantic request/response models
|-- frontend/
|   |-- demo.py               # Streamlit dashboard (main UI)
|   `-- app.py                # Standalone script that saves a static HTML map
|-- source/
|   |-- download_network.py   # Downloads Hyderabad's road graph via OSMnx
|   |-- create_scenarios.py   # Generates the traffic / closure scenarios
|   |-- environment.py        # Graph loading and simulation helpers
|   `-- test_environment.py   # Quick shortest-path sanity check
|-- evaluate.py               # Runs test routes against the backend -> results.csv/json
|-- metrics.py                # Averages and % differences -> summary.json
|-- plot_results.py           # Generates comparison charts
|-- requirements.txt
`-- .gitignore
```

---

## Getting Started

### Prerequisites

- Python 3.11 or newer (recommended, given the pinned package versions)
- An internet connection for the one-time map download

### 1. Clone and install

```bash
git clone https://github.com/codekiller2006/hospital-emergency-route-planner.git
cd hospital-emergency-route-planner

python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Generate the city data

The Hyderabad graph files are **165 MB+**, so they are not stored in the repository (`data/` is git-ignored). Generate them locally, **from the project root**:

```bash
python source/download_network.py    # downloads the road network  ->  data/raw/
python source/create_scenarios.py    # builds the scenarios        ->  data/simulated/
```

### 3. Run the application

Use two terminals, both with the virtual environment active.

**Terminal 1: backend**

```bash
uvicorn backend.main:app --reload
```

Wait for the message `Hyderabad city graph loaded and attributes adapted successfully.` before using the dashboard. Interactive docs are served at <http://127.0.0.1:8000/docs>.

**Terminal 2: dashboard**

```bash
streamlit run frontend/demo.py
```

Enter an incident latitude and longitude in the sidebar, check the nearest hospital it selects, and click **Dispatch Ambulance**.

---

## Evaluation

With the backend running, generate the quantitative comparison by running these scripts in order:

```bash
python evaluate.py       # runs the test routes   ->  outputs/results.csv, results.json
python metrics.py        # averages + % change    ->  outputs/summary.json
python plot_results.py   # comparison charts      ->  outputs/charts/
```

Charts produced: `execution_time.png`, `travel_time.png`, `distance.png`.

---

## Hospitals in the Dashboard

| Hospital | Latitude | Longitude |
|---|---|---|
| Osmania General Hospital | 17.3731 | 78.4716 |
| Apollo Hospital, Jubilee Hills | 17.4168 | 78.4074 |
| Yashoda Hospital, Somajiguda | 17.4258 | 78.4552 |
| Care Hospitals, Banjara Hills | 17.4174 | 78.4485 |
| KIMS, Secunderabad | 17.4402 | 78.4851 |

---

## Algorithm Details

### A\* with a risk-aware heuristic

Implemented in `algorithms/a_star.py`.

- **Edge cost:** `length / free-flow speed (40 km/h) x traffic_weight`, plus a **120 s penalty** on high-risk (closed) edges.
- **Heuristic:** straight-line (Haversine) travel time to the goal, plus a weighted term for the average traffic level on neighbouring edges, plus a weighted risk term if any neighbouring edge is high-risk.

### Q-Learning with reward shaping

Implemented in `algorithms/q_learning.py`. Plain Q-Learning struggles on a city-sized graph because the goal reward is sparse. This implementation adds:

- **Reward shaping:** a bonus proportional to how much closer (by Haversine distance) each step moves the agent to the destination.
- **Cost-based rewards:** each step's reward is the negative of its travel time, with an extra penalty of 500 for congested edges.
- **Loop penalty** of 100 for revisiting nodes, and a **goal reward** of 2000.
- **Epsilon-greedy exploration** starting at 0.5 and decaying to 0.05.

| Parameter | Value |
|---|---|
| Learning rate (`alpha`) | 0.3 |
| Discount factor (`gamma`) | 0.95 |
| Max steps per episode | 800 |
| Episodes per API request | 200 |

---

## Known Limitations

- **Test coordinates are not in Hyderabad.** `evaluate.py` and `frontend/app.py` use placeholder coordinates around 23.34 N, 85.31 E. Replace them with Hyderabad points (for example the hospitals above) before trusting the evaluation results.
- **The two algorithms use different cost models.** A\* estimates time from road length at a fixed 40 km/h, while Q-Learning uses each edge's stored `travel_time`. Their travel-time figures are therefore not perfectly like-for-like.
- **Q-Learning trains on every request,** so it is much slower than A\* and its result can vary between runs.
- **The A\* heuristic is a practical, risk-weighted one,** not a strictly admissible one, so optimal paths are not guaranteed.
- **`source/test_environment.py` needs an import fix.** It imports from `src.environment`, but the folder is named `source`.
- **Only one scenario (heavy traffic) is served by the backend at a time.**

---

## Contributors

Rohan
Surbhi
Tanisha
Bhuvan
Satyam
