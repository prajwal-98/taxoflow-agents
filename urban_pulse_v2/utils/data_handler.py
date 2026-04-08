import pandas as pd
import os
import json
from datetime import datetime

def load_raw_data(file_path):
    """
    Ingests the raw CSV dataset.
    Handles basic formatting, stripping whitespace, and initial null checks.
    Signals: Professional Data Engineering standard.
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        df = pd.read_csv(file_path)
        
        # Standardize column names (stripping whitespace) to prevent key errors
        df.columns = [col.strip() for col in df.columns]
        
        # Basic Cleaning: Remove rows where 'Review Text' is empty as LLMs can't process them
        if "Review Text" in df.columns:
            df = df.dropna(subset=["Review Text"])
            # Remove extremely short noise (e.g., "." or " ")
            df = df[df["Review Text"].str.len() > 2]
            
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def apply_business_filters(df, city=None, platform=None, date_range=None):
    """
    Applies the Global Filter Lock logic.
    Ensures that the entire Multi-Agent pipeline operates on a consistent 
    subset of data (e.g., Only Bangalore, Only Zepto).
    """
    if df is None or df.empty:
        return None
    
    filtered_df = df.copy()
    
    # 1. City Filter: Exact match for localized context detector (Agent 2)
    if city and city != "All" and "City" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["City"] == city]
        
    # 2. Platform Filter: Market segmentation for platform signal agent (Agent 6)
    if platform and platform != "All" and "Platform" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Platform"] == platform]
        
    # 3. Date Filter: Temporal grounding for novelty scoring (Agent 7)
    if date_range and "Date" in filtered_df.columns:
        try:
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
            start_date, end_date = date_range
            mask = (filtered_df['Date'] >= pd.Timestamp(start_date)) & \
                   (filtered_df['Date'] <= pd.Timestamp(end_date))
            filtered_df = filtered_df.loc[mask]
        except Exception:
            # If date parsing fails, we skip and keep the current filter state
            pass
            
    return filtered_df

def save_processed_artifact(df, stage_name):
    """
    Saves intermediate dataframes to the data/processed directory.
    Essential for Audit Trails and checking Agent logic without re-running.
    """
    output_dir = "data/processed"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{stage_name}_{timestamp}.csv"
    save_path = os.path.join(output_dir, filename)
    
    df.to_csv(save_path, index=False)
    return save_path

def save_json_insights(data, filename):
    """
    Saves agent-generated JSON insights (Personas, Escalations, etc.)
    for persistence and potential UI re-loading.
    """
    output_dir = "data/processed"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(os.path.join(output_dir, filename), "w") as f:
        json.dump(data, f, indent=4)

def initialize_pipeline_state(df):
    """
    Prepares the initial state dictionary for the LangGraph orchestrator.
    """
    return {
        "raw_df": df,
        "filtered_df": df,
        "active_filters": {},
        "filters_locked": False,
        "current_step": 1,
        "completed_steps": [],
        "A1_is_valid": False,
        "system_logs": [f"Pipeline initialized at {datetime.now()}"]
    }