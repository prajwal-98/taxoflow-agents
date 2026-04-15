import streamlit as st
import pandas as pd
import os
import plotly.express as px
import altair as alt
from core.orchestrator import urban_pulse_app
from ui.styles import apply_custom_styles
from ui.sidebar import render_sidebar
from utils.state_utils import load_state_snapshot, save_state_snapshot 
from ui.views.landing_page import render_landing_page
from ui.views.step_1_gatekeeper import render as render_step_1
from ui.views.step_2_context_detector import render as render_step_2
from ui.views.step_3_semantic_shaper import render as render_step_3
from ui.views.step_4_cluster_agent import render as render_step_4
from ui.views.step_5_category_escalation import render as render_step_5
from ui.views.step_6_platform_signal import render as render_step_6
from ui.views.step_7_novelty_score import render as render_step_7
from ui.views.step_8_master_dashboard import render as render_step_8

from dotenv import load_dotenv

# Load variables from .env into the system environment
load_dotenv()

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
    """
    Standardizes column names to lowercase and sanitizes 'raw_text' 
    to prevent LLM JSON formatting crashes.
    """
    normalized = df.copy()
    
    # 1. Standardize column names (lowercase + whitespace removal)
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]
    
    # 2. Scrub the 'raw_text' column for JSON safety
    if 'raw_text' in normalized.columns:
        # Replace newlines, tabs, and carriage returns with a space
        normalized['raw_text'] = normalized['raw_text'].str.replace(r'[\n\r\t]', ' ', regex=True)
        
        # Swap double quotes with single quotes to avoid breaking JSON structure
        normalized['raw_text'] = normalized['raw_text'].str.replace('"', "'")
        
        # Final trim of leading/trailing whitespace
        normalized['raw_text'] = normalized['raw_text'].str.strip()
        
    return normalized

# --- UPDATED FILTER LOGIC (Empty = All) ---
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
        # CHANGE: Only filter if the user selected specific items. 
        # If empty, it defaults to showing everything.
        if key in filters and filters[key]:
            filtered = filtered[filtered[key].isin(filters[key])]
        
    return filtered

# # --- NEW: PIPELINE PROGRESS UI ---
# def render_pipeline_progress():
#     steps = ["Gatekeeper", "Context Detection", "Semantic Mapping", "Clustering", "Risk & Category", "Platform Signals", "Novelty Score"]
#     current = st.session_state.get("current_step", 1)
#     cols = st.columns(len(steps))
#     for i, (col, name) in enumerate(zip(cols, steps), 1):
#         with col:
#             if i < current: col.caption(f"✅ {name}")
#             elif i == current: col.markdown(f"**🔵 {name}**"); st.divider()
#             else: col.caption(f"🔒 {name}")




import streamlit as st
import os
import pandas as pd
from utils.state_utils import load_state_snapshot, save_state_snapshot

def main():
    # 1. Determine sidebar state based on whether the pipeline is running
    # If filters are locked, we collapse the sidebar to show the Agent UI full-screen
    sidebar_state = "collapsed" if st.session_state.get("filters_locked", False) else "expanded"

    st.set_page_config(
        page_title="UrbanPulse V2 | Intelligence Dashboard",
        layout="wide",
        initial_sidebar_state=sidebar_state
    )

    st.markdown("""
<style>
    /* Remove top spacing */
    .block-container {
        padding-top: 1rem !important;
    }

    /* Remove extra header height */
    header[data-testid="stHeader"] {
        height: 0px;
    }

    /* Reduce top spacing even more */
    .stApp {
        margin-top: -10px;
    }
</style>
""", unsafe_allow_html=True)
    
    initialize_state()

    # 1. Define Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_DATA_PATH = os.path.join(base_dir, "data", "raw", "urban_reviews.csv")
    # Note: Using your demo folder path
    DEMO_DATA_PATH = os.path.join(base_dir, "data", "demo", "demo_source.csv")
    
    # 2. Track Mode in State
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = "Live API"

    # --- 3. LOAD DATA BEFORE SIDEBAR (Fixes Filter Visibility) ---
    # We use the existing session state mode to decide what to load
    target_path = DEMO_DATA_PATH if st.session_state.app_mode == "Demo Mode" else DEFAULT_DATA_PATH
    
    if st.session_state.raw_df is None and os.path.exists(target_path):
        try:
            st.session_state.raw_df = normalize_dataframe(pd.read_csv(target_path))
        except Exception:
            st.session_state.raw_df = None

    # 4. Render Sidebar
    uploaded_file, selected_mode = render_sidebar()

    # 5. Handle Mode Switch (Resets state if you toggle the radio button)
    if selected_mode != st.session_state.app_mode:
        st.session_state.app_mode = selected_mode
        st.session_state.raw_df = None 
        st.session_state.filters_locked = False
        st.session_state.pipeline_run_complete = False
        st.rerun()

    # --- 6. RESTORED: LAUNCH DEMO BUTTON ---
    if selected_mode == "Demo Mode" and not st.session_state.pipeline_run_complete:
        if st.sidebar.button("🚀 Launch Demo Analysis",type="primary",use_container_width=True):
            success, message = load_state_snapshot()
            if success:
                st.session_state.filters_locked = True
                st.session_state.pipeline_run_complete = True
                st.session_state.current_step = 1
                st.session_state.completed_steps = [1, 2, 3, 4, 5, 6, 7, 8]
                st.session_state.A1_is_valid = True
                st.session_state.A1_routing_decision = "Success: Data Validated"
                st.rerun()
            else:
                st.sidebar.error(message)

    # 7. Handle New Uploads
    if uploaded_file is not None:
        st.session_state.raw_df = normalize_dataframe(pd.read_csv(uploaded_file))
        st.session_state.pipeline_run_complete = False
        st.session_state.filtered_df = None

    # 8. Main UI Logic
    if not st.session_state.filters_locked:
        render_landing_page()
    else:
    #     render_pipeline_progress()

        # 9. Execution Logic
        if st.session_state.filters_locked and st.session_state.raw_df is not None:
            current_filtered_df = apply_filters(
                st.session_state.raw_df, 
                st.session_state.active_filters
            )
            st.session_state.filtered_df = current_filtered_df

            if current_filtered_df is None or current_filtered_df.empty:
                st.error("Filtered data is empty. Adjust selection.")
                st.session_state.filters_locked = False
            
            elif not st.session_state.pipeline_run_complete:
                # Live Swarm Execution
                safe_filters = {
                    k: tuple(v) if isinstance(v, list) else v 
                    for k, v in st.session_state.active_filters.items()
                }

                with st.spinner("🤖 Agent Swarm is analyzing..."):
                    input_state = {
                        "raw_df": current_filtered_df, 
                        "filtered_df": current_filtered_df,
                        "active_filters": safe_filters,
                        "current_step": 1,
                        "completed_steps": [],
                        "system_logs": [],
                        "A1_is_valid": False,
                        "A1_routing_decision": "Processing...",
                        "A1_validation_checks": {},
                        "A1_reasoning": "",
                        "api_key": st.session_state.get("api_key"),
                        "model": st.session_state.get("model")
                    }

                    try:
                        preserved_filters = st.session_state.active_filters
                        output_state = urban_pulse_app.invoke(input_state)

                        # DEBUG — print everything except large dataframes
                        for key, value in output_state.items():
                            if key not in ['raw_df', 'filtered_df', 'A1_sample']:
                                print(f"{key}: {value}")

                        for key, value in output_state.items():
                            st.session_state[key] = value
                        st.session_state.active_filters = preserved_filters

                        st.session_state.current_step = 1
                        st.session_state.pipeline_run_complete = True
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Agent Swarm Error: {e}")
                        st.session_state.filters_locked = False
            
            # Developer Snapshot Capture
            if selected_mode == "Live API" and st.session_state.pipeline_run_complete:
                if st.sidebar.button("💾 Save as Demo Snapshot"):
                    msg = save_state_snapshot()
                    st.sidebar.success(msg)

            # Routing to Views
            step = st.session_state.get('current_step', 1)
            view_map = {
                1: render_step_1, 2: render_step_2, 3: render_step_3,
                4: render_step_4, 5: render_step_5, 6: render_step_6, 
                7: render_step_7, 8: render_step_8
            }
            
            if step in view_map:
                view_map[step](st.session_state)

if __name__ == "__main__":
    main()