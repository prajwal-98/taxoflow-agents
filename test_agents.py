import pandas as pd
from urban_pulse_v2.agents.A4_cluster_agent import cluster_agent_node

# 1. Load a small local CSV (or one of your intermediate processed files)
df = pd.read_csv("data/demo/demo_source.csv").head(15) 

# 2. Mock the state that Agent 4 expects to receive
mock_state = {
    "filtered_df": df,
    "completed_steps": [1, 2, 3],
    "current_step": 4,
    "api_key": "AIzaSyC2MKrjxHMWoGoABDu_5LyEYl4WOCvpWn8", # Put your key here just for testing
    "model": "gemini-1.5-flash"
}

# 3. Run ONLY Agent 4
print("Running Agent 4...")
new_state = cluster_agent_node(mock_state)

# 4. Print the output to your terminal
print("\n--- RESULTS ---")
print(new_state.get("A4_output"))