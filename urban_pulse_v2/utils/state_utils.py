import pickle
import os
import streamlit as st
import pandas as pd

def save_state_snapshot():
    # Get the project root (one level up from utils/)
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(utils_dir)
    
    # Define absolute paths
    file_path = os.path.join(project_root, "data", "demo", "state_snapshot.pkl")
    csv_path = os.path.join(project_root, "data", "demo", "demo_source.csv")

    # Create directories if missing
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # pipeline_keys = [
    #     "raw_df", "filtered_df", "active_filters", "filters_locked",
    #     "A1_validation_checks", "A1_routing_decision", "A1_is_valid",
    #     "A3_vector_coords", "A3_reasoning",
    #     "A4_cluster_stats", "A4_reasoning", "A5_category_data", 
    #     "A6_market_insights", "A7_novelty_data", "A7_reasoning",
    #     "completed_steps", "pipeline_run_complete"
    # ]
    pipeline_keys = [
        "raw_df", "filtered_df", "active_filters", "filters_locked",
        "A1_validation_checks", "A1_routing_decision", "A1_is_valid",
        "A1_metrics", "A1_charts", "A1_highlights", "A1_data_quality", "A1_sample",
        "A2_output", "A2_context_signals", "A2_slang_map", "A2_reasoning",
        "A3_output", "A3_reasoning",
        "A4_output", "A4_reasoning", 
        "A5_output", "A5_reasoning", 
        "A6_output", "A6_reasoning"
        "A6_market_insights", "A6_reasoning", 
        "A7_output", "A7_reasoning", "A8_output",
        "completed_steps", "pipeline_run_complete"
    ]
    
    # 1. Capture and save the Intelligence Layer
    snapshot = {key: st.session_state[key] for key in pipeline_keys if key in st.session_state}
    with open(file_path, "wb") as f:
        pickle.dump(snapshot, f)
    
    # 2. Capture and save the Data Layer
    if "filtered_df" in st.session_state and st.session_state.filtered_df is not None:
        # Save the current filtered data to the demo CSV
        st.session_state.filtered_df.to_csv(csv_path, index=False)
        return f"Success: Saved {len(st.session_state.filtered_df)} rows to {csv_path}"
    
    return "Error: No filtered_df found to save"

def load_state_snapshot():
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(utils_dir)
    file_path = os.path.join(project_root, "data", "demo", "state_snapshot.pkl")

    if not os.path.exists(file_path):
        return False, f"Error: No snapshot found at {file_path}"

    try:
        with open(file_path, "rb") as f:
            snapshot = pickle.load(f)
        
        for key, value in snapshot.items():
            st.session_state[key] = value
            
        return True, "Success: Demo state loaded"
    except Exception as e:
        return False, f"Error: {str(e)}"