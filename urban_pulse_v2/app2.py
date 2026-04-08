import streamlit as st
import pandas as pd
import os
from core.orchestrator import urban_pulse_app
from ui.styles import apply_custom_styles
from ui.sidebar import render_sidebar

from ui.views.step_1_gatekeeper import render as render_step_1
from ui.views.step_2_context_detector import render as render_step_2
from ui.views.step_3_semantic_shaper import render as render_step_3
from ui.views.step_4_cluster_agent import render as render_step_4
from ui.views.step_5_category_escalation import render as render_step_5
from ui.views.step_6_platform_signal import render as render_step_6
from ui.views.step_7_novelty_score import render as render_step_7

from dotenv import load_dotenv

# Load variables from .env into the system environment
load_dotenv()

# Quick debug check (Optional)
if not os.getenv("GEMINI_API_KEY"):
    st.error("⚠️ GEMINI_API_KEY not found! Check your .env file.")

def initialize_state():
    """Initializes the UrbanPulseState in Streamlit Session State if not present."""
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    if "completed_steps" not in st.session_state:
        st.session_state.completed_steps = []
    if "filters_locked" not in st.session_state:
        st.session_state.filters_locked = False
    if "raw_df" not in st.session_state:
        st.session_state.raw_df = None
    if "active_filters" not in st.session_state:
        st.session_state.active_filters = {}
    if "pipeline_run_complete" not in st.session_state:
        st.session_state.pipeline_run_complete = False

    # --- AGENT 1 DEFAULT KEYS (The Fix) ---
    if "A1_is_valid" not in st.session_state: st.session_state.A1_is_valid = False
    if "A1_routing_decision" not in st.session_state: st.session_state.A1_routing_decision = "Pending..."
    if "A1_validation_checks" not in st.session_state: st.session_state.A1_validation_checks = {}
    if "A1_reasoning" not in st.session_state: st.session_state.A1_reasoning = "Waiting for analysis..."

def normalize_dataframe(df):
    """Enforce lowercase schema expected by filters and agent pipeline."""
    normalized = df.copy()
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]
    return normalized

def apply_filters(df, filters):
    if df is None or not filters:
        return df
    
    filtered = df.copy()
    filtered['date'] = pd.to_datetime(filtered['date'])

    # 1. Date Range
    if "date_range" in filters and len(filters["date_range"]) == 2:
        start, end = filters["date_range"]
        filtered = filtered[(filtered['date'].dt.date >= start) & 
                            (filtered['date'].dt.date <= end)]

    # 2. Dynamic City/Platform/Category
    for key in ['city', 'platform', 'category']:
        if key in filters and filters[key]:
            filtered = filtered[filtered[key].isin(filters[key])]
        
    return filtered

def render_landing_page():
    """Always-visible landing page so the app never renders as a blank canvas."""
    st.title("UrbanPulse V2 Intelligence Dashboard")
    st.caption("GenAI multi-agent review intelligence for urban commerce signals.")

    raw_df = st.session_state.raw_df
    is_locked = st.session_state.filters_locked
    run_complete = st.session_state.pipeline_run_complete

    col1, col2, col3 = st.columns(3)
    if raw_df is None:
        col1.metric("Total Reviews", "0")
        col2.metric("Cities", "N/A")
        col3.metric("Platforms", "N/A")
        st.subheader("Data Preview")
        st.info("No dataset loaded yet. Upload a CSV or use sample data from the sidebar.")
    else:
        total_rows = len(raw_df)
        city_col = "city" if "city" in raw_df.columns else None
        platform_col = "platform" if "platform" in raw_df.columns else None
        col1.metric("Total Reviews", f"{total_rows:,}")
        col2.metric("Cities", raw_df[city_col].nunique() if city_col else "N/A")
        col3.metric("Platforms", raw_df[platform_col].nunique() if platform_col else "N/A")
        st.subheader("Data Preview")
        st.dataframe(raw_df.head(20), use_container_width=True)

    if raw_df is None:
        st.warning("No dataset loaded. Expected columns: date, city, platform, category, raw_text.")
    elif not is_locked:
        st.info("Dataset ready. Configure and lock filters in the sidebar to start the agent pipeline.")
    elif run_complete:
        st.success("Pipeline run complete. Use the step navigation to inspect agent outputs.")
    else:
        st.info("Filters locked. Pipeline will run and results will appear below.")

def main():
    st.set_page_config(
        page_title="UrbanPulse V2 | Intelligence Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_state()

    # 1. Data Loading Logic (Runs before UI)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_DATA_PATH = os.path.join(base_dir, "data", "raw", "urban_reviews.csv")
    
    if st.session_state.raw_df is None and os.path.exists(DEFAULT_DATA_PATH):
        try:
            st.session_state.raw_df = normalize_dataframe(pd.read_csv(DEFAULT_DATA_PATH))
        except Exception:
            st.session_state.raw_df = None

    # 2. Sidebar Component
    uploaded_file = render_sidebar()

    # 3. Handle New Uploads
    if uploaded_file is not None:
        st.session_state.raw_df = normalize_dataframe(pd.read_csv(uploaded_file))
        st.session_state.pipeline_run_complete = False
        st.session_state.filtered_df = None

    # 4. Main UI Logic
    if not st.session_state.filters_locked:
        # Show landing page if filters aren't locked
        render_landing_page()
    else:
        # 5. Pipeline Execution Logic
        # 5. Main Execution Logic
        if st.session_state.filters_locked and st.session_state.raw_df is not None:
            
            # 1. Capture the Filtered DataFrame (ensures it is NOT None)
            current_filtered_df = apply_filters(
                st.session_state.raw_df, 
                st.session_state.active_filters
            )
            st.session_state.filtered_df = current_filtered_df

            # 2. Safety Check before calling Agents
            if current_filtered_df is None or current_filtered_df.empty:
                st.error("🚨 Filtered data is empty. Adjust your selection in the sidebar.")
                st.session_state.filters_locked = False
            
            elif not st.session_state.pipeline_run_complete:
                # 3. Prepare Safe Filters (Lists to Tuples)
                safe_filters = {
                    k: tuple(v) if isinstance(v, list) else v 
                    for k, v in st.session_state.active_filters.items()
                }

                with st.spinner("🤖 Agent Swarm is analyzing the Urban Pulse..."):
                    input_state = {
                        # This maps your filtered DataFrame to the key the node expects
                        "raw_df": current_filtered_df, 
                        "filtered_df": current_filtered_df,
                        "active_filters": safe_filters,
                        "current_step": 1,
                        "completed_steps": [],
                        "system_logs": [],
                        "A1_is_valid": False,
                        "A1_routing_decision": "Processing...",
                        "A1_validation_checks": {},
                        "A1_reasoning": ""
                    }

                    try:
                        # 4. Invoke the Swarm
                        output_state = urban_pulse_app.invoke(input_state)
                        
                        # 5. Sync results back
                        for key, value in output_state.items():
                            st.session_state[key] = value
                        
                        st.session_state.pipeline_run_complete = True
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Agent Swarm Error: {e}")
                        st.session_state.filters_locked = False
                        
            # 7. Routing to Modular Views
            step = st.session_state.get('current_step', 1)
            view_map = {
                1: render_step_1, 2: render_step_2, 3: render_step_3,
                4: render_step_4, 5: render_step_5, 6: render_step_6, 7: render_step_7
            }
            
            if step in view_map:
                view_map[step](st.session_state)

if __name__ == "__main__":
    main()