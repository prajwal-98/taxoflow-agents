## FILE: app2.py

```python
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
```

## FILE: agents\A1_gatekeeper.py

```python
import pandas as pd
from core.schema import UrbanPulseState


def gatekeeper_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 1 — Data Readiness (Gatekeeper)

    Responsibilities:
    - Validate dataset
    - Generate summary metrics for UI
    - Provide data quality signals
    """

    df = state.get("raw_df")

    # -------------------------------
    # 1. BASIC VALIDATION
    # -------------------------------
    if df is None or not hasattr(df, "columns") or df.empty:
        state["A1_is_valid"] = False
        state["A1_reasoning"] = "Dataset is empty or not loaded"
        state["current_step"] = 1
        return state

    required_columns = ["raw_text", "star_rating", "city", "platform"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        state["A1_is_valid"] = False
        state["A1_reasoning"] = f"Missing columns: {missing}"
        state["current_step"] = 1
        return state

    # API key check (only for Live mode)
    if state.get("mode") == "Live API" and not state.get("api_key"):
        state["A1_is_valid"] = False
        state["A1_reasoning"] = "Missing API Key"
        state["current_step"] = 1
        return state

    # -------------------------------
    # 2. METRICS (FOR UI CARDS)
    # -------------------------------
    total_reviews = len(df)
    total_cities = df["city"].nunique() if "city" in df.columns else 0
    total_platforms = df["platform"].nunique() if "platform" in df.columns else 0
    total_categories = df["category"].nunique() if "category" in df.columns else 0

    state["A1_metrics"] = {
        "total_reviews": total_reviews,
        "cities": total_cities,
        "platforms": total_platforms,
        "categories": total_categories,
    }

    # -------------------------------
    # 3. CHART DATA (FOR UI)
    # -------------------------------
    try:
        platform_dist = (
            df["platform"].value_counts().reset_index().values.tolist()
            if "platform" in df.columns else []
        )

        category_dist = (
            df["category"].value_counts().reset_index().values.tolist()
            if "category" in df.columns else []
        )

        trend = []
        if "date" in df.columns:
            temp_df = df.copy()
            temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
            temp_df = temp_df.dropna(subset=["date"])
            trend = (
                temp_df.groupby(temp_df["date"].dt.to_period("M"))
                .size()
                .reset_index(name="count")
                .values.tolist()
            )

        state["A1_charts"] = {
            "platform_distribution": platform_dist,
            "category_distribution": category_dist,
            "review_trend": trend,
        }

    except Exception:
        state["A1_charts"] = {}

    # -------------------------------
    # 4. KEY HIGHLIGHTS
    # -------------------------------
    try:
        top_platform = df["platform"].mode()[0] if "platform" in df.columns else None
        top_category = df["category"].mode()[0] if "category" in df.columns else None

        peak_month = None
        if "date" in df.columns:
            temp_df = df.copy()
            temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
            temp_df = temp_df.dropna(subset=["date"])
            if not temp_df.empty:
                peak_month = (
                    temp_df["date"]
                    .dt.to_period("M")
                    .value_counts()
                    .idxmax()
                    .strftime("%B")
                )

        state["A1_highlights"] = {
            "top_platform": top_platform,
            "top_category": top_category,
            "peak_month": peak_month,
        }

    except Exception:
        state["A1_highlights"] = {}

    # -------------------------------
    # 5. DATA QUALITY
    # -------------------------------
    missing_ratio = df.isnull().mean().mean()

    state["A1_data_quality"] = {
        "schema_valid": True,
        "missing_data_ok": missing_ratio < 0.2,
        "format_valid": True,
    }

    # -------------------------------
    # 6. SAMPLE DATA
    # -------------------------------
    state["A1_sample"] = df.head(10)

    # -------------------------------
    # 7. FINAL STATE
    # -------------------------------
    state["A1_is_valid"] = True
    state["A1_reasoning"] = "Dataset validated successfully"

    df = state.get("filtered_df")

    if df is not None and not df.empty:
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        state["A1_metrics"] = {
            "total_reviews": len(df),
            "cities": df["city"].nunique() if "city" in df.columns else 0,
            "platforms": df["platform"].nunique() if "platform" in df.columns else 0,
            "categories": df["category"].nunique() if "category" in df.columns else 0,
        }

        state["A1_charts"] = {
            "platform_distribution": df["platform"].value_counts().reset_index().values.tolist() if "platform" in df.columns else [],
            "category_distribution": df["category"].value_counts().reset_index().values.tolist() if "category" in df.columns else [],
            # "review_trend": df.groupby(df["date"].dt.to_period("M")).size().reset_index().values.tolist() if "date" in df.columns else [],
            # with this
            "review_trend": (
                df.groupby(df["date"].dt.to_period("M"))
                .size()
                .reset_index(name="count")
                .assign(date=lambda x: x["date"].astype(str))  # converts Period → string for plotly
                [["date", "count"]]
                .values.tolist()
            ) if "date" in df.columns else [],
        }

        state["A1_highlights"] = {
            "top_platform": df["platform"].mode()[0] if "platform" in df.columns else None,
            "top_category": df["category"].mode()[0] if "category" in df.columns else None,
            "peak_month": str(df["date"].dt.to_period("M").mode()[0]) if "date" in df.columns else None,
        }

        state["A1_data_quality"] = {
            "schema_valid": True,
            "missing_data_ok": not df.isnull().any().any(),
            "format_valid": True,
        }

        state["A1_sample"] = df.head(10)

    else:
        state["A1_metrics"] = {}
        state["A1_charts"] = {}
        state["A1_highlights"] = {}
        state["A1_data_quality"] = {}
        state["A1_sample"] = None

    steps = state.get("completed_steps", [])
    
    if 1 not in steps:
        steps.append(1)
    state["completed_steps"] = steps
    state["current_step"] = 2
    
    return state
```

## FILE: agents\A2_context_detector.py

```python
import pandas as pd
import json
from core.schema import UrbanPulseState
from core.constants import CITY_SLANG_MAP
from utils.llm_client import generate_response


def context_detector_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 2 — Context Detection (A2)
    """

    df = state.get("filtered_df")

    # -------------------------------
    # 1. SAFETY CHECK
    # -------------------------------
    if df is None or df.empty:
        state["A2_output"] = _empty_output("No data available")
        state["A2_reasoning"] = "No data available"
        state["current_step"] = 2
        return state

    # -------------------------------
    # 2. CITY CONTEXT
    # -------------------------------
    active_filters = state.get("active_filters", {})
    city = (active_filters.get("city") or ["Bangalore"])[0]

    slang_reference = CITY_SLANG_MAP.get(city, [])

    # -------------------------------
    # 3. SAMPLE REVIEWS
    # -------------------------------
    sample_reviews = (
        df.get("raw_text", pd.Series())
        .dropna()
        .astype(str)
        .head(10)
        .tolist()
    )

    # -------------------------------
    # 4. PROMPT
    # -------------------------------
    prompt = f"""
    You are a Local Market Analyst for Q-Commerce in {city}.

    Slang Reference: {slang_reference}

    Reviews:
    {sample_reviews}

    Return STRICT JSON:

    {{
        "localized_sentiment": "short summary",
        "slang_detected": ["list"],
        "operational_context": "what is going wrong",
        "top_themes": ["3-5 issues"]
    }}
    """

    # -------------------------------
    # 5. LLM CALL
    # -------------------------------
    try:
        raw_response = generate_response(prompt, state)

    except Exception as e:
        state["A2_output"] = _empty_output("LLM failed")
        state["A2_reasoning"] = str(e)
        state["current_step"] = 2
        return state

    # -------------------------------
    # 6. SAFE PARSE (IMPORTANT FIX)
    # -------------------------------
    parsed = _safe_parse(raw_response)

    # -------------------------------
    # 7. STORE OUTPUT
    # -------------------------------
    state["A2_output"] = {
        "localized_sentiment": parsed.get("localized_sentiment", ""),
        "slang_detected": parsed.get("slang_detected", []),
        "operational_context": parsed.get("operational_context", ""),
        "top_themes": parsed.get("top_themes", [])
    }

    state["A2_reasoning"] = "Success"

    # -------------------------------
    # 8. STEP UPDATE
    # -------------------------------
    steps = state.get("completed_steps", [])
    if 2 not in steps:
        steps.append(2)

    state["completed_steps"] = steps
    state["current_step"] = 3

    return state


# -------------------------------
# HELPERS
# -------------------------------

def _empty_output(msg):
    return {
        "localized_sentiment": msg,
        "slang_detected": [],
        "operational_context": msg,
        "top_themes": []
    }


import json

def _safe_parse(raw):
    if isinstance(raw, dict):
        return raw

    if isinstance(raw, str):
        # 1. Clean whitespace and Markdown wrappers
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:-3].strip()  # Remove ```json and trailing ```
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:-3].strip()  # Remove ``` and trailing ```
        
        try:
            return json.loads(cleaned)
        except Exception:
            # 2. If it still fails, it might be a partial string or badly formatted
            return {}

    return {}
```

## FILE: agents\A3_semantic_shaper.py

```python
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from core.schema import UrbanPulseState
import json

def semantic_shaper_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 3: Transforms unstructured review text into a 2D semantic space.
    This allows for visual clustering and pattern identification.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A3_reasoning"] = "Error: No data available for semantic mapping."
        return state

    try:
        # 1. Text Vectorization
        # Using sublinear_tf to scale the impact of high-frequency words
        tfidf = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            sublinear_tf=True,
            ngram_range=(1, 2)
        )
        
        # We fill NaNs to prevent the vectorizer from crashing
        review_corpus = df["raw_text"].fillna("").tolist()
        tfidf_matrix = tfidf.fit_transform(review_corpus)
        
        # 2. Dimensionality Reduction (SVD)
        # We project the sparse matrix into a dense 2D space for the UI
        svd = TruncatedSVD(n_components=2, random_state=42)
        vectors_2d = svd.fit_transform(tfidf_matrix)
        
        # 3. Coordinate Assignment
        # Creating a dataframe of (x, y) points mapped to the original index
        coords_df = pd.DataFrame(
            vectors_2d, 
            columns=['x', 'y'], 
            index=df.index
        )
        
        state["A3_vector_coords"] = coords_df
        
        reasoning_steps.append("Status: Semantic Shaper initialized.")
        reasoning_steps.append("Technique: TF-IDF Vectorization followed by Truncated SVD Projection.")
        reasoning_steps.append("Result: Multi-dimensional text space compressed to 2D coordinates for UI visualization.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Semantic Shaper Error: {str(e)}")

    # Update State Reasoning
    state["A3_reasoning"] = "\n".join(reasoning_steps)
    
    # Navigation Logic
    if 3 not in state["completed_steps"]:
        state["completed_steps"].append(3)
    
    # Move to Cluster Agent (A4)
    state["current_step"] = 4
    
    return state
```

## FILE: agents\A4_cluster_agent.py

```python
import os
import json
from google import genai
from core.schema import UrbanPulseState

def cluster_agent_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 4: Translates semantic clusters into actionable customer personas.
    Synthesizes feedback patterns into human-centric business segments.
    """
    df = state.get("filtered_df")
    coords = state.get("A3_vector_coords")
    reasoning_steps = []

    if df is None or df.empty:
        state["A4_reasoning"] = "Error: No data available for persona clustering."
        return state

    try:
        # Initialize the 2026 SDK Client        
        # We provide a diverse sample of reviews to the LLM
        # In a full-scale version, we would pass cluster centroids
        review_samples = df["raw_text"].sample(min(20, len(df))).tolist()
        
        prompt = f"""
        Act as a Consumer Insights Strategist for Q-Commerce.
        
        Task: 
        Analyze the following review samples and group them into 3 distinct 'Customer Personas'.
        
        Reviews:
        {review_samples}
        
        For each persona, provide:
        1. A catchy Name (e.g., 'The Weekend Host', 'The Office Snacker').
        2. Core Pain Point (What is their primary complaint?).
        3. Business Impact (Why does this segment matter for retention?).
        
        Output ONLY a JSON object with the key "personas" containing a list of these details.
        """

        # Using Gemini 3 Flash for synthesis
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                    "max_output_tokens": 350, 
                    "temperature": 0.1      
                }  
        )
        
        # Parse the JSON Persona data
        raw_text = response_text.strip().replace("```json", "").replace("```", "")
        category = response_json.get("category_distribution", {})
        
        # Update State
        state["A4_cluster_stats"] = data
        
        reasoning_steps.append("Status: Persona Synthesis complete.")
        reasoning_steps.append("Method: Zero-shot clustering via LLM summarization.")
        reasoning_steps.append(f"Output: Identified {len(data.get('personas', []))} distinct customer segments.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Cluster Agent Error: {str(e)}")

    # Update State Reasoning
    state["A4_reasoning"] = "\n".join(reasoning_steps)
    
    # Navigation Logic
    if 4 not in state["completed_steps"]:
        state["completed_steps"].append(4)
    
    # Move to Category & Escalation Agent (A5)
    state["current_step"] = 5
    
    return state
```

## FILE: agents\A5_category_escalation.py

```python
import os
from core.schema import UrbanPulseState
from core.constants import BUSINESS_CATEGORIES
from utils.llm_client import generate_response


def category_escalation_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 5: Categorizes feedback into business domains and flags critical 
    issues for immediate human intervention.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A5_reasoning"] = "Error: No data available for categorization."
        return state

    try:
        review_batch = df["raw_text"].head(20).tolist() if "raw_text" in df.columns else []

        prompt = f"""
        Act as a Senior Operations Manager for Q-Commerce.
        
        Categories: {BUSINESS_CATEGORIES}
        
        Task:
        1. Categorize the following reviews into the provided categories.
        2. Identify 'High-Risk' escalations (e.g., product tampering, delivery partner 
           misbehavior, missing high-value items, or safety concerns).
        
        Reviews:
        {review_batch}
        
        Output ONLY a JSON object with:
        "category_distribution": dict (category name: percentage),
        "escalations": list (objects with "original_text" and "priority_reason"),
        "summary": str
        """

        response_text = generate_response(prompt, state, temperature=0.1, parse_json=True)

        category_distribution = response_text.get("category_distribution", {})
        escalations = response_text.get("escalations", [])

        state["A5_business_categories"] = category_distribution
        state["A5_escalation_list"] = escalations

        reasoning_steps.append("Status: Operations Triage complete.")
        reasoning_steps.append(f"Metrics: Analyzed {len(review_batch)} items for categorical distribution.")
        reasoning_steps.append(f"Alerts: {len(escalations)} high-risk items identified for escalation.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Category/Escalation Agent Error: {str(e)}")

    state["A5_reasoning"] = "\n".join(reasoning_steps)

    if 5 not in state["completed_steps"]:
        state["completed_steps"].append(5)

    state["current_step"] = 6

    return state
```

## FILE: agents\A6_platform_signal.py

```python
import os
from core.schema import UrbanPulseState
from utils.llm_client import generate_response


def platform_signal_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 6: Extracts competitive intelligence and market positioning signals.
    Identifies mentions of rival platforms and relative performance benchmarks.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A6_reasoning"] = "Error: No data available for platform signal analysis."
        return state

    try:
        review_samples = df["raw_text"].sample(min(20, len(df))).tolist() if "raw_text" in df.columns else []

        prompt = f"""
        Act as a Competitive Intelligence Analyst for the Indian Q-Commerce market.
        
        Competitors to track: Zepto, Blinkit, Swiggy Instamart, BigBasket (BB Now), Dunzo.
        
        Task:
        1. Identify any reviews that explicitly or implicitly compare the current platform 
           to a competitor.
        2. Determine the 'Market Sentiment': Is the current platform winning or losing 
           in these specific comparisons?
        3. Extract 'Feature Gaps': What does the competitor have that the customer misses here?
        
        Reviews:
        {review_samples}
        
        Output ONLY a valid JSON object with:
        "competitor_mentions": list of strings,
        "sentiment_bias": str (Winning/Neutral/Losing),
        "key_benchmarks": list of strings (e.g., "Better delivery tracking", "Fresher vegetables"),
        "analysis_summary": str
        """

        response_text = generate_response(prompt, state, temperature=0.1, parse_json=True)

        state["A6_market_insights"] = response_text

        reasoning_steps.append("Status: Competitive Benchmarking complete.")
        reasoning_steps.append(f"Competitors Detected: {', '.join(response_text.get('competitor_mentions', ['None']))}")
        reasoning_steps.append(f"Market Positioning: Currently {response_text.get('sentiment_bias')} in comparative feedback.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Platform Signal Agent Error: {str(e)}")

    state["A6_reasoning"] = "\n".join(reasoning_steps)

    if 6 not in state["completed_steps"]:
        state["completed_steps"].append(6)

    state["current_step"] = 7

    return state
```

## FILE: agents\A7_novelty_score.py

```python
import os
from core.schema import UrbanPulseState
from utils.llm_client import generate_response


def novelty_score_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 7: Calculates the 'Novelty Index' of current feedback.
    Determines if detected issues are recurring known problems or 
    emerging anomalies that require a strategic pivot.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A7_reasoning"] = "Error: No data available for novelty scoring."
        return state

    try:
        context_summary = state.get("A2_context_signals", [{}])[0].get("signal_analysis", "N/A")
        persona_summary = state.get("A4_cluster_stats", {}).get("persona_summary", "N/A")
        market_intel = state.get("A6_market_insights", {}).get("analysis_summary", "N/A")

        prompt = f"""
        Act as a Strategic Innovation Lead for a Q-Commerce firm.
        
        Baseline Knowledge:
        Standard issues include: Late delivery, crushed bread, missing items, and high delivery fees.
        
        Current Pipeline Findings:
        - Local Context: {context_summary}
        - Detected Personas: {persona_summary}
        - Market Signals: {market_intel}
        
        Task:
        1. Assign a 'Novelty Score' from 0.0 to 1.0. 
           (0.0 = Business as usual/Legacy issues, 1.0 = Highly anomalous/New market shift).
        2. Identify 'Emerging Anomalies': Are there new patterns not mentioned in the baseline?
        3. Strategic Recommendation: What is the single most important action for the COO?
        
        Output ONLY a valid JSON object with:
        "novelty_score": float,
        "is_anomaly": bool,
        "anomalous_patterns": list of strings,
        "strategic_recommendation": str
        """

        response_text = generate_response(prompt, state, temperature=0.1, parse_json=True)

        state["A7_novelty_data"] = response_text

        reasoning_steps.append("Status: Final Novelty Assessment finalized.")
        reasoning_steps.append(f"Novelty Index: {response_text.get('novelty_score')} ({'High Alert' if response_text.get('is_anomaly') else 'Stable Patterns'})")
        
        recommendation = response_text.get('strategic_recommendation', '')
        reasoning_steps.append(f"Strategic Recommendation: {recommendation[:100]}...")

    except Exception as e:
        reasoning_steps.append(f"Warning: Novelty Score Agent Error: {str(e)}")

    state["A7_reasoning"] = "\n".join(reasoning_steps)

    if 7 not in state["completed_steps"]:
        state["completed_steps"].append(7)

    return state
```

## FILE: agents\__init__.py

```python

```

## FILE: config\__init__.py

```python

```

## FILE: core\constants.py

```python
# City-specific slang and operational signals for Q-Commerce grounding
CITY_SLANG_MAP = {
    "Bangalore": [
        "Potadi",      # Refers to bags/packets
        "Sakkath",     # High quality/Great
        "Bega",        # Fast/Quickly
        "Maga",        # Casual address
        "Guru"         # Addressing someone (delivery partner)
    ],
    "Mumbai": [
        "Lafda",       # Issue/Problem
        "Kadak",       # Excellent/Strong
        "Bantai",      # Casual address
        "Ek Number",   # Top tier quality
        "Chindi"       # Low quality/Small issues
    ],
    "Delhi": [
        "Bhasad",      # Chaos/Traffic/Confusion
        "Gajab",       # Amazing
        "Scene",       # Situation/Problem
        "Tashan",      # Style/Attitude
        "Vibe"         # Atmosphere
    ],
    "Hyderabad": [
        "Kaiku",       # Why (used in complaints)
        "Hau",         # Yes
        "Nakko",       # No/Don't want
        "Kirrak",      # Awesome
        "Ustad"        # Addressing someone expert
    ],
    "Pune": [
        "Lay Bhari",   # Very good
        "Kalti",       # To leave/avoid
        "Raav",        # Respectful address
        "Jakaas",      # Fantastic
        "Vishesh"      # Special/Specifically
    ]
}

# Standardized business categories for Agent 5
BUSINESS_CATEGORIES = [
    "Logistics",
    "Pricing",
    "Product Quality",
    "App Experience",
    "Customer Support"
]
```

## FILE: core\orchestrator.py

```python
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from core.schema import UrbanPulseState


# Import Agents (These will be implemented in the /agents folder)
from agents.A1_gatekeeper import gatekeeper_node
from agents.A2_context_detector import context_detector_node
from agents.A3_semantic_shaper import semantic_shaper_node
from agents.A4_cluster_agent import cluster_agent_node
from agents.A5_category_escalation import category_escalation_node
from agents.A6_platform_signal import platform_signal_node
from agents.A7_novelty_score import novelty_score_node

def check_validation(state: UrbanPulseState):
    """
    Conditional logic for Agent 1.
    If the dataset is invalid, we stop the pipeline immediately.
    """
    if state.get("A1_is_valid", False):
        return "A2_context_detector"
    return "end"

def build_urban_pulse_graph():
    """
    Constructs the LangGraph for the UrbanPulse V2 Sequential Pipeline.
    """
    # 1. Initialize Graph with our Shared State Schema
    workflow = StateGraph(UrbanPulseState)

    # 2. Add Nodes for all 7 Agents
    workflow.add_node("A1_gatekeeper", gatekeeper_node)
    workflow.add_node("A2_context_detector", context_detector_node)
    workflow.add_node("A3_semantic_shaper", semantic_shaper_node)
    workflow.add_node("A4_cluster_agent", cluster_agent_node)
    workflow.add_node("A5_category_escalation", category_escalation_node)
    workflow.add_node("A6_platform_signal", platform_signal_node)
    workflow.add_node("A7_novelty_score", novelty_score_node)

    # 3. Define the Flow (Edges)
    
    # Entry Point: Always starts with Gatekeeper
    workflow.set_entry_point("A1_gatekeeper")

    # Conditional Routing from A1
    workflow.add_conditional_edges(
        "A1_gatekeeper",
        check_validation,
        {
            "A2_context_detector": "A2_context_detector",
            "end": END
        }
    )

    # Sequential Logic (A2 -> A7)
    workflow.add_edge("A2_context_detector", "A3_semantic_shaper")
    workflow.add_edge("A3_semantic_shaper", "A4_cluster_agent")
    workflow.add_edge("A4_cluster_agent", "A5_category_escalation")
    workflow.add_edge("A5_category_escalation", "A6_platform_signal")
    workflow.add_edge("A6_platform_signal", "A7_novelty_score")
    workflow.add_edge("A7_novelty_score", END)

    # 4. Compile the Graph
    return workflow.compile()

# This compiled graph can now be invoked in app.py or via a button click
urban_pulse_app = build_urban_pulse_graph()
```

## FILE: core\schema.py

```python
from typing import TypedDict, List, Dict, Optional, Any
import pandas as pd

class UrbanPulseState(TypedDict):
    """
    The Central State for UrbanPulse V2.
    Acts as the source of truth for all 7 Agents and the UI components.
    """
    # --- GLOBAL DATA & FILTERS ---
    raw_df: Optional[pd.DataFrame]          # Original uploaded dataset
    filtered_df: Optional[pd.DataFrame]     # Dataset after City/Platform/Date filters are locked
    active_filters: Dict[str, Any]          # {Date: ..., City: ..., Platform: ...}
    filters_locked: bool                    # UI State: True = filters applied and locked
    
    # --- NAVIGATION & PROGRESS ---
    current_step: int                       # 1 to 7 tracking the active module
    completed_steps: List[int]              # IDs of steps that have finished successfully
    
    # --- A1: GATEKEEPER ---
    A1_is_valid: bool
    A1_routing_decision: str
    A1_validation_checks: Dict[str, bool]
    A1_reasoning: str
    A1_metrics: Optional[Dict[str, Any]]        # total_reviews, cities, platforms, categories
    A1_charts: Optional[Dict[str, Any]]         # platform_distribution, category_distribution, review_trend
    A1_highlights: Optional[Dict[str, Any]]     # top_platform, top_category, peak_month
    A1_data_quality: Optional[Dict[str, Any]]   # schema_valid, missing_data_ok, format_valid
    A1_sample: Optional[Any]                    # df.head(10)
    
    # --- A2: CONTEXT DETECTOR ---
    A2_output: Dict[str, Any]               
    A2_context_signals: List[Dict[str, Any]]# Signals extracted per review
    A2_slang_map: Dict[str, str]            # Localized slang interpretations found
    A2_reasoning: str                       # Agent 2 reasoning trace
    
    # --- A3: SEMANTIC SHAPER ---
    A3_vector_coords: Optional[pd.DataFrame]# x, y, z coordinates for the 3D Plotly Map
    A3_reasoning: str                       # Agent 3 reasoning trace
    
    # --- A4: CLUSTER AGENT ---
    A4_cluster_stats: Dict[str, Any]        # Persona definitions and root cause stats
    A4_reasoning: str                       # Agent 4 reasoning trace
    
    # --- A5: CATEGORY + ESCALATION AGENT ---
    A5_business_categories: Dict[str, str]  # Review ID -> Category mapping
    A5_escalation_list: List[str]           # IDs flagged for high-priority action
    A5_reasoning: str                       # Agent 5 reasoning trace
    
    # --- A6: PLATFORM SIGNAL AGENT ---
    A6_market_insights: Dict[str, Any]      # Comparative metrics (Zepto vs Competitors)
    A6_reasoning: str                       # Agent 6 reasoning trace
    
    # --- A7: NOVELTY SCORE ---
    A7_novelty_data: Dict[str, float]       # Novelty scores and trend labels
    A7_reasoning: str                       # Agent 7 reasoning trace
    
    # --- SYSTEM & LOGGING ---
    system_logs: List[str]                  # Execution timestamps and internal error tracking

    api_key: Optional[str]
    model: Optional[str]
```

## FILE: core\__init__.py

```python

```

## FILE: data\__init__.py

```python

```

## FILE: ui\sidebar.py

```python


import streamlit as st
import pandas as pd

_IC_CAL = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>"""
_IC_PIN = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><path d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>"""
_IC_LAY = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>"""
_IC_TAG = """<svg class="up-sb-ic" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#737373" stroke-width="1.5"><path d="M12 2H2v10l10 10 10-10L12 2z"/><circle cx="7" cy="7" r="1.5" fill="#737373" stroke="none"/></svg>"""


def _sb_br(count: int = 1) -> None:
    st.sidebar.markdown("<br>" * count, unsafe_allow_html=True)


def _scope_field_label(icon_html: str, text: str) -> None:
    st.sidebar.markdown(
        f'<div class="up-sb-field-hint">{icon_html}<span>{text}</span></div>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    # Scoped theme only — do NOT set gap/margin on all stVerticalBlock (breaks nested widgets / overlap).
    st.markdown(
        """
    <style>
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            background-color: #000000 !important;
        }
        [data-testid="stSidebar"] h1 {
            font-size: 1.35rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            margin: 0 0 0.2rem 0 !important;
            padding: 0 !important;
            letter-spacing: -0.02em;
            line-height: 1.2 !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] div[data-testid="stCaption"] {
            color: #888888 !important;
            font-size: 0.8rem !important;
            margin-top: 0 !important;
        }
        .up-sb-section {
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
            color: #737373 !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.2 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] {
            margin-top: -1.5 rem !important;
        
        .up-sb-field-hint {
            display: flex !important;
            align-items: center !important;
            gap: 0.45rem !important;
            margin: 0.4rem 0 0.15rem 0 !important;
            color: #737373 !important;
            font-size: 0.78rem !important;
            line-height: 1.2 !important;
        }
        .up-sb-field-hint .up-sb-ic { flex-shrink: 0; opacity: 0.95; }
        .up-upload-status {
            font-size: 0.78rem !important;
            color: #00C87E !important;
            margin: 0.25rem 0 0 0 !important;
            padding: 0 !important;
            line-height: 1.3 !important;
        }
        .up-upload-status--muted {
            color: #737373 !important;
        }
        .up-dataset-size {
            font-size: 0.72rem !important;
            color: #737373 !important;
            margin: 0.5rem 0 0.35rem 0 !important;
        }
        /* MODE — horizontal radio uses stHorizontalBlock in Streamlit 1.5x; avoid flex hacks on wrong wrappers. */
        [data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stHorizontalBlock"] {
            background: #2a2a2a !important;
            padding: 4px !important;
            border-radius: 8px !important;
            gap: 6px !important;
            align-items: stretch !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="column"] {
            padding: 0 2px !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0.26rem 0.3rem !important;
            border-radius: 6px !important;
            font-size: 0.7rem !important;
            font-weight: 600 !important;
            color: #a3a3a3 !important;
            background: transparent !important;
            line-height: 1.2 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label p {
            color: inherit !important;
            font-size: inherit !important;
            margin: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: #404040 !important;
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
            color: #ffffff !important;
        }
        /* Upload — only the dropzone shell (no nested VerticalBlock hacks). */
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            border: 1px solid #00C87E !important;
            border-radius: 10px !important;
            background: #1a1a1a !important;
            padding: 0.25rem 0.45rem !important;
            line-height: 1.1 !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] p {
            font-size: 0.74rem !important;
            margin: 0.1rem 0 !important;
            line-height: 1.25 !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
            font-size: 0.65rem !important;
            color: #888888 !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            padding: 0.22rem 0.5rem !important;
            font-size: 0.68rem !important;
        }
        /* Compact scope widgets */
        [data-testid="stSidebar"] .stDateInput [data-baseweb="input"] {
            min-height: 2.1rem !important;
            font-size: 0.8rem !important;
            border-radius: 999px !important;
            background-color: #1a1a1a !important;
            border-color: #333333 !important;
        }
        [data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {
            min-height: 2.1rem !important;
            font-size: 0.8rem !important;
            border-radius: 999px !important;
            background-color: #1a1a1a !important;
            border-color: #333333 !important;
        }
        [data-testid="stSidebar"] button[kind="primary"] {
            background-color: #00C87E !important;
            color: #000000 !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.82rem !important;
        }
        [data-testid="stSidebar"] button[kind="primary"]:hover {
            background-color: #00e08f !important;
            color: #000000 !important;
        }
        [data-testid="stSidebar"] button[kind="secondary"] {
            background-color: #2a2a2a !important;
            color: #a3a3a3 !important;
            border: 1px solid #404040 !important;
            border-radius: 10px !important;
            font-size: 0.82rem !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # --- HEADER ---
    st.sidebar.title("UrbanPulse")
    st.sidebar.caption("Multi-Agent Intelligence")
    st.sidebar.divider()
    uploaded_file = None

    # --- MODE (TOP PRIORITY) ---
    st.sidebar.markdown(
        '<p class="up-sb-section">MODE</p>', unsafe_allow_html=True
    )

    app_mode = st.sidebar.radio(
        "",
        options=["Demo Mode", "Live API"],  # Demo first
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    # --- LIVE MODE BLOCK ---
    if app_mode == "Live API":

        # API KEY
        st.sidebar.markdown(
            '<p class="up-sb-section">API KEY</p>', unsafe_allow_html=True
        )

        api_key = st.sidebar.text_input(
            "",
            type="password",
            label_visibility="collapsed"
        )

        st.session_state.api_key = api_key

        # MODEL
        st.sidebar.markdown(
            '<p class="up-sb-section">MODEL</p>', unsafe_allow_html=True
        )

        model = st.sidebar.selectbox(
            "",
            ["gemini-3.1-flash-lite-preview", "gemini-1.5-flash", "gemini-1.5-pro"],
            disabled=not bool(api_key),
            label_visibility="collapsed"
        )

        st.session_state.model = model

        # _sb_br(1)

        # --- FILE UPLOAD (EPHEMERAL) ---
        if not st.session_state.get("file_uploaded", False):

            uploaded_file = st.sidebar.file_uploader(
                "",
                type=["csv"],
                label_visibility="collapsed"
            )

            if uploaded_file is not None:
                st.session_state.file_uploaded = True
                st.session_state.uploaded_file = uploaded_file
                st.rerun()

        else:
            # GREEN SUCCESS BANNER
            st.sidebar.markdown(
            """
            <div style="
                background: rgba(0, 200, 126, 0.12);
                color: #00C87E;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 500;
                text-align: center;
                margin: 6px 0;
                border: 1px solid rgba(0, 200, 126, 0.3);
            ">
                Data loaded successfully
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- DEMO MODE ---
    else:
        st.session_state.file_uploaded = False

        # GREEN DEMO BANNER
        st.sidebar.markdown(
        """
        <div style="
            background: rgba(255, 255, 255, 0.06);
            color: #00C87E;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
            text-align: center;
            margin: 6px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        ">
            Using demo dataset
        </div>
        """,
        unsafe_allow_html=True
    )

    _sb_br(1)
    
    df = st.session_state.raw_df if "raw_df" in st.session_state else None

    # --- Data scope & actions (stacked; no overlap) ---
    if df is not None:
        st.sidebar.markdown(
            '<p class="up-sb-section">DATA SCOPE</p>', unsafe_allow_html=True
        )
        # _sb_br(1)

        is_locked = st.session_state.get("filters_locked", False)

        required_cols = {"date", "city", "platform", "category", "raw_text"}

        if not required_cols.issubset(set(df.columns)):
            st.sidebar.error("Dataset missing required columns")
        else:
            working_df = df.copy()

            if not pd.api.types.is_datetime64_any_dtype(working_df["date"]):
                working_df["date"] = pd.to_datetime(working_df["date"], errors="coerce")

            working_df = working_df.dropna(subset=["date"])

            if working_df.empty:
                st.sidebar.error("No valid rows available")
            else:
                abs_min = working_df["date"].min().date()
                abs_max = working_df["date"].max().date()

                # _scope_field_label(_IC_CAL, "Date Range")
                date_selection = st.sidebar.date_input(
                    "Date",
                    value=(abs_min, abs_max),
                    min_value=abs_min,
                    max_value=abs_max,
                    disabled=is_locked,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                def get_opts(col):
                    return sorted(working_df[col].dropna().unique().tolist())

                # _scope_field_label(_IC_PIN, "City")
                selected_cities = st.sidebar.multiselect(
                    "City",
                    options=get_opts("city"),
                    default=[],
                    placeholder="City",
                    disabled=is_locked,
                    max_selections=3,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                # _scope_field_label(_IC_LAY, "Platform")
                selected_platforms = st.sidebar.multiselect(
                    "Platform",
                    options=get_opts("platform"),
                    default=[],
                    placeholder="Platform",
                    disabled=is_locked,
                    max_selections=3,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                # _scope_field_label(_IC_TAG, "Category")
                selected_categories = st.sidebar.multiselect(
                    "Category",
                    options=get_opts("category"),
                    default=[],
                    placeholder="Category",
                    disabled=is_locked,
                    max_selections=3,
                    label_visibility="collapsed",
                )
                # _sb_br(1)

                temp_df = working_df.copy()

                if selected_cities:
                    temp_df = temp_df[temp_df["city"].isin(selected_cities)]

                if selected_platforms:
                    temp_df = temp_df[temp_df["platform"].isin(selected_platforms)]

                if selected_categories:
                    temp_df = temp_df[temp_df["category"].isin(selected_categories)]

                if isinstance(date_selection, (list, tuple)) and len(date_selection) == 2:
                    temp_df = temp_df[
                        (temp_df["date"].dt.date >= date_selection[0])
                        & (temp_df["date"].dt.date <= date_selection[1])
                    ]

                row_count = len(temp_df)

                st.sidebar.markdown(
                    f'<p class="up-dataset-size">Dataset Size: {row_count:,}</p>',
                    unsafe_allow_html=True,
                )
                # _sb_br(1)

                is_demo = (app_mode == "Demo Mode")
                has_api_key = bool(st.session_state.get("api_key"))

                button_disabled = (
                    is_demo or
                    (app_mode == "Live API" and not has_api_key) or
                    row_count == 0
                )
                button_type = "primary" if not button_disabled else "secondary"
                if not is_locked:
                    if st.sidebar.button(
                        "Lock & Run Pipeline",
                        use_container_width=True,
                        type=button_type,
                        disabled = button_disabled
                    ):
                        if row_count > 0:
                            st.session_state.filters_locked = True
                            st.session_state.active_filters = {
                                "date_range": date_selection,
                                "city": selected_cities,
                                "platform": selected_platforms,
                                "category": selected_categories,
                            }
                            st.session_state.current_step = 1
                            st.rerun()
                        else:
                            st.sidebar.caption("No data selected")
                else:
                    st.sidebar.success("Filters Locked")
                    # _sb_br(1)
                    if st.sidebar.button("Reset Filters", use_container_width=True):
                        st.session_state.filters_locked = False
                        st.rerun()

    return uploaded_file, app_mode

```

## FILE: ui\styles.py

```python
import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
            /* Force Sidebar to be visible and distinct */
            section[data-testid="stSidebar"] {
                background-color: #111 !important;
                min-width: 300px !important;
            }
            /* Fix the 'Ghost Text' visibility */
            .stMarkdown, p, h1, h2, h3, label {
                color: #FFFFFF !important;
            }
            /* Make the sidebar toggle button visible */
            button[kind="header"] {
                background-color: #FF4B4B !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

def hero_block(status: bool, message: str):
    """Renders the Green or Red status block."""
    if status:
        st.markdown(f'<div class="hero-valid">🟢 {message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="hero-invalid">🔴 {message}</div>', unsafe_allow_html=True)

def step_indicator(step_num: int, total_steps: int, step_name: str, subtitle: str):
    """Renders the Step Tracker at the top of the screen."""
    st.markdown(f'''
        <div class="step-header">
            Step <b>{step_num}</b> of {total_steps} — <b>{step_name}</b><br>
            <small style="color:#888">{subtitle}</small>
        </div>
    ''', unsafe_allow_html=True)
```

## FILE: ui\__init__.py

```python

```

## FILE: ui\components\charts.py

```python
import streamlit as st
import plotly.express as px
import pandas as pd


def render_semantic_map(coords_df, color_by=None):
    if coords_df is None:
        st.warning("No coordinate data available for the semantic map.")
        return

    color_col = color_by if color_by in coords_df.columns else None
    fig = px.scatter(
        coords_df,
        # x='x', y='y',
        color=color_col,
        title="UrbanPulse: 2D Semantic Vector Space",
        labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
        template="plotly_dark",
        opacity=0.8,
        height=600
    )
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(fig, use_container_width=True)


def render_bar_chart(data, x_label="x", y_label="y", title=""):
    if not data:
        st.info("No data available")
        return
    try:
        df = pd.DataFrame(data, columns=[x_label, y_label])
        fig = px.bar(
            df, x=x_label, y=y_label,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=["#00C87E"]
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            height=220,
            title_font=dict(size=13, color="#ffffff"),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#2a2a2a"),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Unable to render chart")


def render_pie_chart(data, names="label", values="value", title=""):
    if not data:
        st.info("No data available")
        return
    try:
        df = pd.DataFrame(data, columns=[names, values])
        fig = px.pie(
            df, names=names, values=values,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            height=220,
            title_font=dict(size=13, color="#ffffff"),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Unable to render chart")


def render_line_chart(data, x_label="x", y_label="y", title=""):
    if not data:
        st.info("No data available")
        return
    try:
        df = pd.DataFrame(data, columns=[x_label, y_label])
        fig = px.line(
            df, x=x_label, y=y_label,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=["#00C87E"]
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            height=220,
            title_font=dict(size=13, color="#ffffff"),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#2a2a2a"),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        print("chart error:", e)
        st.info("Unable to render chart")
```

## FILE: ui\components\reasoning_view.py

```python
import streamlit as st

def render_reasoning_panel(step_name, reasoning_text):
    """
    Renders the monospaced 'Thought Trace' for an agent.
    """
    with st.expander(f"System Trace: {step_name}"):
        st.markdown(f"""
            <div class="reasoning-box">
                {reasoning_text}
            </div>
        """, unsafe_allow_html=True)

def render_status_indicators(checks_dict):
    """
    Renders a simple grid of success/fail indicators.
    """
    cols = st.columns(len(checks_dict))
    for i, (check, status) in enumerate(checks_dict.items()):
        with cols[i]:
            symbol = "PASS" if status else "FAIL"
            color = "#00ff7f" if status else "#ff4b4b"
            st.markdown(f"<p style='color:{color}; font-weight:bold;'>{check}: {symbol}</p>", unsafe_allow_html=True)
```

## FILE: ui\views\landing_page.py

```python
import streamlit as st


def render_landing_page():
    """Clean landing page (UI improved, no logic change)"""

    raw_df = st.session_state.raw_df
    is_locked = st.session_state.filters_locked
    run_complete = st.session_state.pipeline_run_complete

    st.markdown(
        """
<style>
  .up-section { margin-bottom: 3.25rem; }
  .up-section-title {
    font-size: 1.35rem; font-weight: 700; color: #fafafa !important;
    margin: 0 0 1.25rem 0; letter-spacing: -0.02em;
  }
  .up-hero-title {
    text-align: center; font-size: 2.15rem; font-weight: 800; color: #ffffff !important;
    margin: 0 0 0.65rem 0; line-height: 1.15; letter-spacing: -0.03em;
  }
  .up-hero-sub {
    text-align: center; color: #a3a3a3 !important; font-size: 1.05rem; margin: 0 0 0.5rem 0;
    line-height: 1.5;
  }
  .up-hero-hint {
    text-align: center; color: #737373 !important; font-size: 0.9rem; margin: 0 0 2rem 0;
  }
  .up-card {
    background: #111111;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 1.25rem 1.35rem;
    box-sizing: border-box;
  }
  .up-card-feature {
    min-height: 180px;
    height: 100%;
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  [data-testid="stHorizontalBlock"]:has(.up-card-feature) {
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
  }
  [data-testid="stHorizontalBlock"]:has(.up-card-feature) > [data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 !important;
    min-width: 0 !important;
  }
  [data-testid="stHorizontalBlock"]:has(.up-card-feature) > [data-testid="column"] > div {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  .up-card-icon { display: flex; align-items: center; margin-bottom: 0.75rem; }
  .up-card-icon svg { flex-shrink: 0; }
  .up-card-title {
    font-size: 1rem; font-weight: 700; color: #fafafa !important; margin: 0 0 0.4rem 0;
  }
  .up-card-desc { font-size: 0.875rem; color: #a3a3a3 !important; margin: 0; line-height: 1.45; }
  .up-flow {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: stretch;
    gap: 0.5rem;
    justify-content: flex-start;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
  }
  .up-step-card {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.65rem;
    background: #111111;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    box-sizing: border-box;
    width: 172px;
    min-width: 172px;
    max-width: 172px;
    flex: 0 0 172px;
    min-height: 76px;
    height: auto;
    align-self: stretch;
  }
  .up-step-card .up-step-label {
    font-size: 0.88rem; font-weight: 600; color: #f5f5f5 !important; margin: 0; line-height: 1.25;
  }
  .up-flow-arrow {
    color: #e5e5e5 !important;
    font-size: 1.1rem;
    align-self: center;
    flex: 0 0 auto;
    padding: 0 0.15rem;
    user-select: none;
  }
  .up-chips-row {
    display: flex; flex-wrap: wrap; gap: 0.65rem; align-items: center;
  }
  .up-chip {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid #404040;
    border-radius: 9999px;
    padding: 0.55rem 1.1rem;
    font-size: 0.875rem;
    color: #a3a3a3 !important;
  }
  @media (max-width: 900px) {
    .up-flow { flex-wrap: wrap; }
    .up-flow-arrow { display: none; }
    .up-step-card {
      width: 100%;
      min-width: 0;
      max-width: 100%;
      flex: 1 1 140px;
    }
  }
</style>
""",
        unsafe_allow_html=True,
    )

    accent = "#34d399"

    def _svg_wrap(path_d: str, size: int = 22) -> str:
        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="{path_d}" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

    # --- HERO ---
    st.markdown(
        f"""
<div class="up-section" style="max-width:1100px;margin-left:auto;margin-right:auto;">
  <h1 class="up-hero-title">Urban Pulse: Multi-Agent Intelligence System</h1>
  <p class="up-hero-sub">Turn customer reviews into actionable business insights using AI-powered agents</p>
  <p class="up-hero-hint">Upload your dataset from the sidebar to begin analysis</p>
</div>
""",
        unsafe_allow_html=True,
    )

    # --- WHAT THIS SYSTEM DOES ---
    st.markdown('<p class="up-section-title">What This System Does</p>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    features = [
        (
            f1,
            "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
            "Understand Reviews",
            "Extract meaning from raw customer feedback",
        ),
        (
            f2,
            "M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2",
            "Detect Patterns",
            "Group similar issues and behaviors",
        ),
        (
            f3,
            "M9 18h6 M10 22h4 M15 2H9a7 7 0 0 0-7 7c0 1.5.5 3 1.4 4.1L2 22l4.9-1.4A7 7 0 0 0 9 18h0a7 7 0 0 0 7-7V9a7 7 0 0 0-7-7z",
            "Generate Insights",
            "Identify platform, product, and city trends",
        ),
        (
            f4,
            "M5 8l6 6M4 14l6-6 2-3M2 5h12M7 2h1M22 22l-5-10-5 10M14 18h6",
            "Analyze Customer Language",
            "Understand slang and Gen Z expressions",
        ),
    ]
    for col, path, title, desc in features:
        with col:
            st.markdown(
                f"""
<div class="up-card up-card-feature">
  <div class="up-card-icon">{_svg_wrap(path)}</div>
  <p class="up-card-title">{title}</p>
  <p class="up-card-desc">{desc}</p>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="up-section"></div>', unsafe_allow_html=True)

    # --- HOW IT WORKS (horizontal step cards) ---
    st.markdown('<p class="up-section-title">How It Works</p>', unsafe_allow_html=True)
    steps = [
        ("M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12", "Upload Data"),
        ("M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4L12 14.01l-3-3", "Data Validation"),
        ("M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z", "Context Understanding"),
        ("M3 7V5a2 2 0 0 1 2-2h2M21 7V5a2 2 0 0 0-2-2h-2M3 17v2a2 2 0 0 0 2 2h2M21 17v2a2 2 0 0 1-2 2h-2M7 12h10", "Pattern Detection"),
        ("M3 3v18h18M7 16l4-4 4 4 4-8", "Business Insights"),
        ("M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936a2 2 0 0 0 1.437-1.437l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5a2 2 0 0 0 1.437 1.437l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0L9.937 15.5z", "Language Intelligence"),
        ("M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z", "Final Dashboard"),
    ]
    def _flow_html(step_slice, *, last):
        parts: list[str] = []
        for i, (path, label) in enumerate(step_slice):
            parts.append(
                f"""<div class="up-step-card"><div class="up-card-icon" style="margin-bottom:0;">{_svg_wrap(path, 20)}</div><p class="up-step-label">{label}</p></div>"""
            )
            if i < len(step_slice) - 1:
                parts.append('<span class="up-flow-arrow">→</span>')
        margin = "0.75rem auto 3.25rem auto" if last else "0 auto 0 auto"
        return f'<div class="up-flow" style="margin:{margin};">{"".join(parts)}</div>'

    st.markdown(_flow_html(steps[:5], last=False), unsafe_allow_html=True)
    st.markdown(_flow_html(steps[5:], last=True), unsafe_allow_html=True)

    # --- WHAT YOU CAN EXPLORE (2x2 cards) ---
    st.markdown('<p class="up-section-title">What You Can Explore</p>', unsafe_allow_html=True)
    r1a, r1b = st.columns(2)
    r2a, r2b = st.columns(2)
    explore = [
        (r1a, "Compare Zepto vs Blinkit performance"),
        (r1b, "Analyze product issues (Magnum, Lays, Dove)"),
        (r2a, "Explore city-specific trends"),
        (r2b, "Understand customer language patterns"),
    ]
    for col, text in explore:
        with col:
            st.markdown(
                f"""
<div class="up-card" style="margin-bottom:1rem;">
  <div class="up-card-icon"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{accent};"></span></div>
  <p class="up-card-desc" style="color:#e5e5e5 !important;font-size:0.95rem;">{text}</p>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="up-section"></div>', unsafe_allow_html=True)

    # --- TRY ASKING (chips) ---
#     st.markdown('<p class="up-section-title">Try Asking</p>', unsafe_allow_html=True)
#     st.markdown(
#         f"""
# <div class="up-chips-row" style="margin-bottom:2.5rem;">
#   <span class="up-chip">Mumbai monsoon insights</span>
#   <span class="up-chip">Ice cream issues</span>
#   <span class="up-chip">Compare Bangalore vs Delhi slang</span>
# </div>
# """,
#         unsafe_allow_html=True,
#     )

    # --- STATUS (unchanged logic) ---
    if raw_df is None:
        st.warning("No dataset loaded yet. Upload a CSV to begin.")
        return

    if not is_locked:
        st.info("Configure filters in the sidebar and lock to start the pipeline.")
    elif run_complete:
        st.success("Pipeline complete. Explore results.")
    else:
        st.info("Filters locked. Pipeline will run shortly.")

```

## FILE: ui\views\step_1_gatekeeper.py

```python
# ================================
# FILE: ui/views/step_1_gatekeeper.py
# ================================

import streamlit as st
from ui.components.charts import render_bar_chart, render_pie_chart, render_line_chart


def inject_styles():
    st.markdown("""
    <style>
    .up-wrapper {
        max-width: 1100px;
        margin: auto;
    }

    .up-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }

    .up-subtitle {
        color: #a3a3a3;
        font-size: 0.95rem;
        margin-bottom: 24px;
    }

    .up-status-card {
        border: 1px solid #2a2a2a;
        border-left: 3px solid #00C87E;
        border-radius: 12px;
        padding: 20px 24px;
        background-color: #111111;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 24px;
    }

    .up-status-card.invalid {
        border-left-color: #ef4444;
    }

    .up-status-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 2px solid #00C87E;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00C87E;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .up-status-icon.invalid {
        border-color: #ef4444;
        color: #ef4444;
    }

    .up-status-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: white;
    }

    .up-status-desc {
        font-size: 0.85rem;
        color: #a3a3a3;
        margin-top: 2px;
    }

    .up-metric-card {
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px;
        background-color: #111111;
    }

    .up-metric-label {
        font-size: 0.82rem;
        color: #a3a3a3;
        margin-bottom: 8px;
    }

    .up-metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }

    .up-chart-card {
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px;
        background-color: #111111;
        margin-bottom: 16px;
    }

    .up-chart-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
    }

    .up-quality-card {
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px 24px;
        background-color: #111111;
        margin-bottom: 16px;
    }

    .up-quality-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 16px;
    }

    .up-quality-item {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        color: #e5e5e5;
    }

    .up-quality-icon {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        border: 2px solid #00C87E;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00C87E;
        font-size: 0.7rem;
        flex-shrink: 0;
    }

    .up-quality-icon.fail {
        border-color: #ef4444;
        color: #ef4444;
    }

    .up-continue-btn button {
        background-color: #00C87E !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.75rem !important;
    }

    .up-continue-btn button:hover {
        background-color: #00e08f !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(is_valid):
    status_icon = "✓" if is_valid else "✕"
    status_title = "Dataset Ready" if is_valid else "Dataset Invalid"
    status_desc = "Your data is valid and ready for analysis" if is_valid else "Please fix dataset issues before continuing"
    invalid_class = "" if is_valid else "invalid"

    st.markdown(f"""
    <div class="up-wrapper">
        <div class="up-title">Step 1 — Data Readiness Check</div>
        <div class="up-subtitle">Validate and understand your dataset before analysis</div>
        <div class="up-status-card {invalid_class}">
            <div class="up-status-icon {invalid_class}">{status_icon}</div>
            <div>
                <div class="up-status-title">{status_title}</div>
                <div class="up-status-desc">{status_desc}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(metrics):
    cols = st.columns(4)
    items = [
        ("Total Reviews", f"{metrics.get('total_reviews') or 0:,}"),
        ("Cities", metrics.get("cities") or 0),
        ("Platforms", metrics.get("platforms") or 0),
        ("Categories", metrics.get("categories") or 0),
    ]

    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div class="up-metric-card">
                <div class="up-metric-label">{label}</div>
                <div class="up-metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)


def render_charts(charts, highlights):
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    with r1c1:
        with st.container(border=True):
            render_bar_chart(
                charts.get("platform_distribution") or [],
                x_label="x", y_label="y",
                title="Platform Distribution"
            )

    with r1c2:
        with st.container(border=True):
            render_pie_chart(
                charts.get("category_distribution") or [],
                title="Category Share"
            )

    with r2c1:
        with st.container(border=True):
            render_line_chart(
                charts.get("review_trend") or [],
                x_label="date", y_label="count",
                title="Review Trend"
            )

    with r2c2:
        with st.container(border=True):
            st.markdown("""
            <div style="padding: 8px 4px;">
                <div style="font-size:0.95rem;font-weight:700;color:#ffffff;margin-bottom:14px;">Key Highlights</div>
            """, unsafe_allow_html=True)
            st.markdown(f"- Top Platform: **{highlights.get('top_platform', 'N/A')}**")
            st.markdown(f"- Top Category: **{highlights.get('top_category', 'N/A')}**")
            st.markdown(f"- Peak Month: **{highlights.get('peak_month', 'N/A')}**")
            st.markdown('</div>', unsafe_allow_html=True)


def render_data_quality(quality):
    def icon(flag):
        cls = "up-quality-icon" if flag else "up-quality-icon fail"
        symbol = "✓" if flag else "✕"
        return f'<div class="{cls}">{symbol}</div>'

    st.markdown(f"""
    <div class="up-quality-card">
        <div class="up-quality-title">Data Quality</div>
        <div class="up-quality-item">{icon(quality.get('schema_valid'))} Required columns present</div>
        <div class="up-quality-item">{icon(quality.get('format_valid'))} Data format valid</div>
        <div class="up-quality-item">{icon(quality.get('missing_data_ok'))} No major missing values</div>
    </div>
    """, unsafe_allow_html=True)


def render_sample_data(df):
    with st.expander("Sample Data Preview", expanded=False):
        st.dataframe(df, use_container_width=True)


def render_action():
    st.markdown('<div class="up-continue-btn">', unsafe_allow_html=True)
    if st.button("Continue  →  Context Detection", use_container_width=True):
        st.session_state.current_step = 2
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render(state):
    inject_styles()
    render_header(state.get("A1_is_valid"))
    st.markdown("<br>", unsafe_allow_html=True)
    render_metrics(state.get("A1_metrics", {}))
    st.markdown("<br>", unsafe_allow_html=True)
    render_charts(state.get("A1_charts", {}), state.get("A1_highlights", {}))
    st.markdown("<br>", unsafe_allow_html=True)
    render_data_quality(state.get("A1_data_quality", {}))
    render_sample_data(state.get("A1_sample"))
    st.markdown("<br>", unsafe_allow_html=True)
    render_action()
```

## FILE: ui\views\step_2_context_detector.py

```python
# ================================
# FILE: ui/views/step_2_context_detector.py
# ================================

import streamlit as st


def inject_styles():
    st.markdown("""
    <style>
    .up-wrapper {
        max-width: 1100px;
        margin: auto;
    }

    .up-card {
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        background-color: #111111;
        min-height: 220px;
    }

    .up-banner {
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        background: linear-gradient(145deg, #111111, #1a1a1a);
    }

    .tag {
        border: 1px solid #10b981;
        padding: 6px 12px;
        border-radius: 20px;
        margin-right: 8px;
        display: inline-block;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)


def render(state):

    inject_styles()

    data = state.get("A2_output", {})

    sentiment = data.get("localized_sentiment", "")
    slang = data.get("slang_detected", [])
    themes = data.get("top_themes", [])
    context = data.get("operational_context", "")

    city = (state.get("active_filters", {}).get("city") or ["Bangalore"])[0]

    # -------------------------------
    # SENTIMENT LABEL
    # -------------------------------
    sentiment_label = "Mixed"
    if "positive" in sentiment.lower():
        sentiment_label = "Positive"
    elif "negative" in sentiment.lower():
        sentiment_label = "Negative"

    top_issue = themes[0] if themes else "N/A"

    # -------------------------------
    # HEADER
    # -------------------------------
    st.markdown('<div class="up-wrapper">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="up-banner">
        <p style="color:#10b981;">🔥 {city} Insight</p>
        <h2>{sentiment_label} Sentiment Detected</h2>
        <p style="color:#cccccc;">{sentiment}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------
    # QUICK STATS
    # -------------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"📍 **City**<br>{city}", unsafe_allow_html=True)
    col2.markdown(f"🙂 **Sentiment**<br>{sentiment_label}", unsafe_allow_html=True)
    col3.markdown(f"⚠️ **Risk**<br>Medium", unsafe_allow_html=True)
    col4.markdown(f"🚚 **Top Issue**<br>{top_issue}", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------
    # GRID
    # -------------------------------
    col1, col2 = st.columns(2)

    # LEFT
    with col1:
        st.markdown('<div class="up-card">', unsafe_allow_html=True)

        st.markdown("### Slang Signals")

        if slang:
            for s in slang:
                st.markdown(f'<span class="tag">{s}</span>', unsafe_allow_html=True)
        else:
            st.markdown("_No slang detected_")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### Top Themes")

        if themes:
            total = len(themes)
            for i, t in enumerate(themes):
                percent = int(100 * (total - i) / (total + 1))

                st.markdown(f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <span>{t}</span>
                        <span>{percent}%</span>
                    </div>
                    <div style="background:#2a2a2a;height:6px;border-radius:10px;">
                        <div style="width:{percent}%;background:#10b981;height:6px;border-radius:10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown("_No themes available_")

        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT
    with col2:
        st.markdown('<div class="up-card">', unsafe_allow_html=True)

        st.markdown("### What Needs Attention")

        st.markdown(context if context else "No context available")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------
    # BUTTON
    # -------------------------------
    if st.button("Continue → Step 3"):
        st.session_state.current_step = 3
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
```

## FILE: ui\views\step_3_semantic_shaper.py

```python
import streamlit as st
import plotly.express as px

def render(state):
    # 1. Update Header to reflect 2D logic
    st.header("A3: Semantic Mapping (2D)")
    
    coords_df = state.get("A3_vector_coords")
    
    if coords_df is not None:
        # FIX: Switched from px.scatter_3d to px.scatter (2D)
        # Removed z='z' to prevent the ValueError
        fig = px.scatter(
            coords_df, 
            x='x', 
            y='y', 
            title="2D Semantic Review Space",
            template="plotly_dark",
            labels={'x': 'Semantic Component 1', 'y': 'Semantic Component 2'}
        )
        
        # UI Polish: Standardize marker look
        fig.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='white')))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No vector coordinates found for visualization.")

    # 2. Mathematical Trace (Using .get for safety)
    reasoning = state.get("A3_reasoning", "No trace available.")
    with st.expander("View Mathematical Trace"):
        st.markdown(f'<div class="reasoning-box">{reasoning}</div>', unsafe_allow_html=True)

    # 3. Sequential Navigation Button
    st.divider()
    if st.button("Continue to Clustering Agent →", type="primary"):
        # Manually incrementing step as per your sequential design
        st.session_state.current_step += 1
        st.rerun()

```

## FILE: ui\views\step_4_cluster_agent.py

```python
import streamlit as st

def render(state):
    st.header("A4: Cluster Persona Analysis")
    
    # 1. Access the cluster statistics safely
    stats = state.get("A4_cluster_stats", {})
    
    # 2. Extract the LIST of personas from the 'personas' key
    # This prevents the TypeError by iterating over individual persona objects
    personas = stats.get("personas", [])
    
    if personas:
        # Create dynamic columns based on the number of personas identified
        cols = st.columns(len(personas))
        
        for i, persona in enumerate(personas):
            with cols[i]:
                # 3. Match the keys exactly as shown in your debug console (lowercase)
                name = persona.get("name", f"Persona {i+1}")
                pain_point = persona.get("core_pain_point", "N/A")
                impact = persona.get("business_impact", "N/A")
                
                # Render the persona details using metrics and subheaders
                st.subheader(name)
                st.metric(label="Retention Risk", value="High" if "high" in impact.lower() else "Medium")
                st.info(f"**Core Pain Point:** {pain_point}")
                st.caption(f"**Business Impact:** {impact}")
    else:
        st.info("Waiting for persona synthesis results...")

    st.divider()
    
    # 4. View Agent Reasoning Trace
    with st.expander("View Clustering Reasoning"):
        # Use .get to safely retrieve the trace
        reasoning = state.get("A4_reasoning", "No trace available.")
        st.markdown(f'<div class="reasoning-box">{reasoning}</div>', unsafe_allow_html=True)

    st.divider()
    
    # 5. Sequential Navigation Button
    if st.button("Continue to Next Step →", type="primary"):
        # Explicitly setting the step ensures a clean transition
        st.session_state.current_step = 5
        st.rerun()
```

## FILE: ui\views\step_5_category_escalation.py

```python
import streamlit as st

def render(state):
    st.header("A5: Category & Escalation Routing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Category Distribution")
        # Placeholder for category distribution chart
        st.json(state.get("A5_business_categories", {}))
        
    with col2:
        st.subheader("High-Priority Escalations")
        escalations = state.get("A5_escalation_list", [])
        if escalations:
            for item in escalations:
                st.error(f"Priority Alert: {item}")
        else:
            st.success("No high-priority escalations found in current filtered set.")

    with st.expander("View Escalation Logic"):
        st.markdown(f'<div class="reasoning-box">{state["A5_reasoning"]}</div>', unsafe_allow_html=True)
    st.divider()
    if st.button("Continue to Next Step →", type="primary"):
        st.session_state.current_step += 1
        st.rerun()
```

## FILE: ui\views\step_6_platform_signal.py

```python
import streamlit as st

def render(state):
    st.header("A6: Platform Signal Benchmarking")
    
    insights = state.get("A6_market_insights", {})
    
    st.subheader(f"Strategic Comparison: {insights.get('target_platform', 'Primary')}")
    st.write(f"Benchmarked against: {', '.join(insights.get('competitors', []))}")
    
    # Custom display blocks for competitive signals
    st.info("Competitive Signal: Faster delivery perception in core Bangalore zones compared to Blinkit.")
    
    with st.expander("View Market Analysis Trace"):
        st.markdown(f'<div class="reasoning-box">{state["A6_reasoning"]}</div>', unsafe_allow_html=True)
    st.divider()
    if st.button("Continue to Next Step →", type="primary"):
        st.session_state.current_step += 1
        st.rerun()
```

## FILE: ui\views\step_7_novelty_score.py

```python
import streamlit as st

def render(state):
    st.header("A7: Novelty & Emerging Trends")
    
    # 1. Safely extract the data generated by Agent 7
    novelty_data = state.get("A7_novelty_data", {})
    # Note: Using 'novelty_score' to match Agent 7 output keys
    score = novelty_data.get("novelty_score", 0.0) 
    is_anomaly = novelty_data.get("is_anomaly", False)
    patterns = novelty_data.get("anomalous_patterns", [])
    recommendation = novelty_data.get("strategic_recommendation", "No recommendation available.")
    
    # 2. Main Metric Display
    st.metric(
        "Global Novelty Index", 
        f"{score:.4f}", 
        delta="High Alert / Emerging" if is_anomaly else "Stable Trends"
    )
    
    st.divider()
    
    # 3. Dynamic Emerging Trend Analysis
    # This replaces the hardcoded "Late Night" placeholder with actual AI insights
    st.subheader("Emerging Trend Analysis")
    if patterns:
        for pattern in patterns:
            # Renders each pattern identified by the LLM
            st.warning(f"AI Detected Signal: {pattern}")
    else:
        st.info("No anomalous patterns detected in current dataset.")

    # 4. Strategic Recommendation Block
    if recommendation:
        st.success(f"**Strategic Pivot:** {recommendation}")

    # 5. Safe Reasoning Trace
    reasoning = state.get("A7_reasoning", "No trace available.")
    with st.expander("View Anomaly Detection Trace"):
        st.markdown(f'<div class="reasoning-box">{reasoning}</div>', unsafe_allow_html=True)

    st.divider()
    
    # 6. Final Navigation Button
    if st.button("Complete Analysis Flow →", type="primary"):
        st.session_state.current_step = 8
        st.success("Pipeline Analysis Complete. You can now reset filters in the sidebar.")
```

## FILE: ui\views\step_8_master_dashboard.py

```python
import streamlit as st

def render(state):
    st.title("🏆 Urban Pulse: Complete Intelligence Summary")
    
    # Dual-Track Layout: Technical (Left) vs. Strategic (Right)
    col_tech, col_biz = st.columns([1, 2], gap="large")

    # --- LEFT COLUMN: THE TECHNICAL BLUEPRINT ---
    with col_tech:
        st.subheader("⚙️ Technical Pipeline")
        
        # 1. Pipeline Integrity (Agent 1)
        a1_data = state.get("A1_validation_checks", {})
        conf = state.get("confidence", 0.0)
        st.markdown(f"**Data Integrity:** `{conf*100:.0f}% Confidence`")
        
        # 2. Semantic Logic (Agent 3)
        st.markdown("**Vector Space Logic:**")
        st.latex(r"f(x) = TruncatedSVD(X_{tfidf}) \rightarrow \mathbb{R}^2")
        
        # 3. Agent Execution Trace (Status Timeline)
        st.info("**Execution Status:**")
        steps = ["Gatekeeper", "Context", "Shaper", "Cluster", "Risk", "Signal", "Novelty"]
        completed = state.get("completed_steps", [])
        for i, name in enumerate(steps, 1):
            status = "🟢" if i in completed else "⚪"
            st.write(f"{status} Agent {i}: {name}")

    # --- RIGHT COLUMN: THE EXECUTIVE INTELLIGENCE ---
    with col_biz:
        st.subheader("🎯 Strategic Insights")

        # 1. Top Persona (Agent 4)
        personas = state.get("A4_cluster_stats", {}).get("personas", [])
        if personas:
            top_p = personas[0]
            st.success(f"**Primary Persona:** {top_p.get('name')}")
            st.caption(f"Impact: {top_p.get('business_impact')}")

        # 2. Market Signals (Agent 6)
        st.divider()
        market = state.get("A6_market_insights", {})
        st.markdown("### 📊 Market Position")
        st.write(market.get("analysis_summary", "Gathering benchmark data..."))

        # 3. The Strategy Pivot (Agent 7)
        st.divider()
        novelty = state.get("A7_novelty_data", {})
        st.warning(f"**Novelty Index: {novelty.get('novelty_score', 0.0):.2f}**")
        st.error(f"**Final Recommendation:** {novelty.get('strategic_recommendation')}")

    # --- FOOTER: SUPPORTING EVIDENCE ---
    st.divider()
    with st.expander("📂 View Supporting Evidence (Raw Signal Samples)"):
        df = state.get("filtered_df")
        if df is not None:
            st.dataframe(df[['raw_text', 'city', 'platform']].head(5))

    if st.button("Reset Analysis Pipeline"):
        st.session_state.current_step = 1
        st.rerun()
```

## FILE: ui\views\__init__.py

```python

```

## FILE: utils\data_handler.py

```python
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
        
        # Basic Cleaning: Remove rows where 'raw_text' is empty as LLMs can't process them
        if "raw_text" in df.columns:
            df = df.dropna(subset=["raw_text"])
            # Remove extremely short noise (e.g., "." or " ")
            df = df[df["raw_text"].str.len() > 2]
            
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
```

## FILE: utils\llm_client.py

```python
import time
import json
import re
from google import genai


def extract_json(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return {}
        return {}


def generate_response(prompt: str, state: dict, temperature: float = 0.2, parse_json: bool = False):
    """
    Central LLM wrapper using NEW Gemini SDK
    """
    api_key = state.get("api_key")
    model = state.get("model", "gemini-1.5-flash")

    if not api_key:
        raise ValueError("Missing API Key in state")

    client = genai.Client(api_key=api_key)

    retries = 2

    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "temperature": temperature,
                },
            )

            raw_text = response.text

            if parse_json:
                return extract_json(raw_text)
            return raw_text  # ← return plain text by default

        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                raise e
```

## FILE: utils\logger.py

```python

```

## FILE: utils\state_utils.py

```python
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
    
    pipeline_keys = [
        "raw_df", "filtered_df", "active_filters", "filters_locked",
        "A1_validation_checks", "A1_routing_decision", "A1_is_valid",
        "A3_vector_coords", "A3_reasoning",
        "A4_cluster_stats", "A4_reasoning", "A5_category_data", 
        "A6_market_insights", "A7_novelty_data", "A7_reasoning",
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
```

## FILE: utils\vector_utils.py

```python

```

## FILE: utils\__init__.py

```python

```

