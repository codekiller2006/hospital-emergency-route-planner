#  Hospital Emergency Route Planner

An intelligent emergency route planning system designed to compare the performance of **A* Search** and **Q-Learning** algorithms in dynamic, real-world traffic conditions. This project uses the actual street network of Hyderabad, India, layering simulated traffic congestion and road closures to evaluate how different AI approaches handle emergency vehicle routing.

##  Key Features
* **Real-World Graph Routing:** Built on top of OSMnx and NetworkX to process actual city street data.
* **Dynamic Traffic Simulation:** Generates multiple environmental states (light traffic, heavy traffic, road closures).
* **AI Algorithm Comparison:** 
  * **A* Search:** Enhanced with a custom risk-aware heuristic to avoid congested edges.
  * **Q-Learning:** Implements reward shaping (Haversine distance) to navigate massive state spaces.
* **Interactive Dashboard:** Streamlit and Folium frontend for real-time visualization and metric comparisons.

##  Tech Stack
* **Backend:** FastAPI, Python, Pydantic
* **Frontend:** Streamlit, Folium, Leaflet
* **Data & Algorithms:** OSMnx, NetworkX, scikit-learn, Pandas, Matplotlib

---

##  Local Setup & Installation

Due to GitHub's file size limits, the massive 165MB+ city graph files are not tracked in this repository. **You must generate the local data before starting the servers.**

**1. Clone the repository and install dependencies**

git clone [https://github.com/codekiller2006/hospital-emergency-route-planner.git](https://github.com/codekiller2006/hospital-emergency-route-planner.git)
cd hospital-emergency-route-planner
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
pip install -r requirements.txt
**2. Generate the City Map Data
python source/download_network.py
python source/create_scenarios.py
Running the Application
You will need two separate terminal windows (ensure your virtual environment is active in both).
terminal 1 :
uvicorn backend.main:app --reload
teminal 2:
streamlit run frontend/demo.py
To generate the quantitative comparison reports and charts, ensure the backend server is running, then execute the evaluation scripts sequentially:
python evaluate.py
python metrics.py
python plot_results.py
