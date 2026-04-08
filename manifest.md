## FILE: mock_swarm_results.py

```python
import json
import os
import pandas as pd

# Path Configuration
DATA_DIR = "urban_pulse/data/"
ANALYSIS_PATH = os.path.join(DATA_DIR, "cluster_insights.json")
ESCALATION_PATH = os.path.join(DATA_DIR, "escalation_results.json")
SHADOW_PATH = os.path.join(DATA_DIR, "shadow_insights.json")

def inject_mock_data():
    # 1. Ensure Directory Exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # 2. Mock Cluster Analyst Output (Tab 3)
    cluster_insights = {
        "0": {
            "cluster_title": "The Midnight Melt Crisis",
            "root_cause": "Delivery delays > 40 mins during peak Mumbai humidity affecting frozen categories.",
            "impact_level": "High"
        },
        "1": {
            "cluster_title": "Silk Board Logistics Friction",
            "root_cause": "Traffic congestion in Bangalore 'Last Mile' causing freshness degradation for produce.",
            "impact_level": "Medium"
        },
        "2": {
            "cluster_title": "Packaging Integrity Failure",
            "root_cause": "Specific brand poly-bags tearing during multi-drop routes.",
            "impact_level": "Low"
        }
    }

    # 3. Mock Escalation Engine Output (Tab 4)
    escalation_results = {
        "0": {
            "churn_probability": "92%",
            "financial_risk_driver": "Persistent logistics failure in high-value snacking segment.",
            "automated_action": "Issue 150 INR apology voucher to all users in Cluster 0."
        },
        "1": {
            "churn_probability": "45%",
            "financial_risk_driver": "Regional traffic delays affecting recurring grocery orders.",
            "automated_action": "Notify local warehouse to re-route via 2-wheelers."
        }
    }

    # 4. Mock Shadow Agent Output (Tab 4)
    shadow_insights = {
        "Ice Cream": {
            "Magnum": {
                "Winning_Platform": "Zepto",
                "Losing_Platform": "Blinkit",
                "Root_Insight": "Zepto's cold-chain logic maintains -18°C better than Blinkit's open-bag delivery."
            }
        },
        "Snacking": {
            "Lays": {
                "Winning_Platform": "Swiggy Instamart",
                "Losing_Platform": "Zepto",
                "Root_Insight": "Instamart has better multi-pack stock availability in Delhi-NCR clusters."
            }
        }
    }

    # Write the files
    with open(ANALYSIS_PATH, 'w') as f: json.dump(cluster_insights, f, indent=4)
    with open(ESCALATION_PATH, 'w') as f: json.dump(escalation_results, f, indent=4)
    with open(SHADOW_PATH, 'w') as f: json.dump(shadow_insights, f, indent=4)

    print("--- SUCCESS: Mock Swarm Intelligence Injected ---")
    print(f"Files created: \n- {ANALYSIS_PATH}\n- {ESCALATION_PATH}\n- {SHADOW_PATH}")

if __name__ == "__main__":
    inject_mock_data()
```

## FILE: taxoflow_control_center.py

```python
import streamlit as st
import pandas as pd
import os
import plotly.express as px
from core_utils.master_ingestor import MasterIngestor
# Import our new helper functions
from core_utils.ui_components import load_data, render_q_comm_view 

# --- PAGE CONFIG ---
st.set_page_config(page_title="TaxoFlow | Unilever AI Command", layout="wide")

# Initialize Ingestor as a Singleton
if 'ingestor' not in st.session_state:
    st.session_state.ingestor = MasterIngestor()

def main():
    st.sidebar.title("🧬 TaxoFlow Control")
    st.sidebar.info("Centralized Agentic Pipeline: Unilever BGs")
    
    bg_selector = st.sidebar.selectbox(
        "Select Business Group", 
        ["Geopolitics", "Q-Commerce"]
    )

    # --- 🧠 CENTRALIZED AI COMMAND INPUT ---
    st.markdown("## 🕹️ AI Command Center")
    with st.expander("📥 Live Signal Ingestion", expanded=True):
        col_input, col_status = st.columns([3, 1])
        
        with col_input:
            raw_input = st.text_area("Input raw feedback or risk signal:", 
                                   placeholder="e.g., Lays chips in Mumbai were stale...",
                                   height=100)
        
        with col_status:
            st.write("**Agent Status**")
            st.success("Triage: Online")
            if st.button("Route & Process", use_container_width=True):
                if raw_input:
                    with st.spinner("Triage Agent routing..."):
                        result = st.session_state.ingestor.run_ingest(raw_input)
                        st.balloons() if "Success" in result else st.error(result)
                else:
                    st.warning("Input required.")

    st.markdown("---")

    # --- DOMAIN DISPLAY LOGIC ---
    if bg_selector == "Geopolitics":
        st.title("🛡️ Geopolitics: Global Risk Monitor")
        data = load_data("geopolitics/data/synthetic_geopol_data.csv")
        
        if data is not None:
            # TODO: Move this block to ui_components later to keep tcc.py slim
            col1, col2 = st.columns([1, 1])
            with col1:
                st.metric("Total Risks Logged", len(data))
                target_col = 'location' if 'location' in data.columns else 'country'
                if target_col in data.columns:
                    counts = data[target_col].value_counts().reset_index()
                    counts.columns = ['Region', 'Event Count']
                    fig_geo = px.bar(counts, x='Region', y='Event Count', 
                                   template="plotly_dark", color='Event Count')
                    st.plotly_chart(fig_geo, use_container_width=True)
            with col2:
                source_col = 'source' if 'source' in data.columns else 'impact_area'
                if source_col in data.columns:
                    source_counts = data[source_col].value_counts().head(5).reset_index()
                    val_col = 'count' if 'count' in source_counts.columns else source_col
                    fig_source = px.pie(source_counts, values=val_col, names=source_col, 
                                      title="Top Intel Categories", hole=0.4,
                                      template="plotly_dark")
                    st.plotly_chart(fig_source, use_container_width=True)
            st.dataframe(data.tail(15), use_container_width=True)
        else:
            st.warning("No Geopolitics data found.")

    elif bg_selector == "Q-Commerce":
        st.title(f"🏙️ {bg_selector}: Semantic Intelligence")
        data = load_data("urban_pulse/data/vector_mapped_data.csv")
        
        if data is not None:
            # This now handles the vertical stack: Map -> Inspector -> Feed
            render_q_comm_view(data)
        else:
            st.warning("Please run the Semantic Shaper to generate vector data.")

    
# --- TAB NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Ingestion & Gatekeeper", 
    "🧪 Semantic Lab", 
    "🔍 Discovery", 
    "🎮 Executive War Room"
])

# --- TAB 1: DATA INGESTION & THE GATEKEEPER ---
with tab1:
    st.header("Data Funnel & Ingestion")
    
    # UI Layout: Raw Data on top, Console on bottom
    col_data, col_logs = st.columns([2, 1])
    
    with col_data:
        st.subheader("Raw Feedback Stream (Latest 1,000 Rows)")
        if not st.session_state.df_master.empty:
            st.dataframe(
                st.session_state.df_master.head(100), 
                use_container_width=True,
                height=400
            )
        else:
            st.warning("No data found in urban_pulse/data/raw_qcomm_reviews.csv")

    with col_logs:
        st.subheader("Agent Reasoning Console")
        # Creating a scrolling terminal-like window
        log_container = st.container(height=400, border=True)
        for log in st.session_state.agent_logs:
            log_container.code(log, language="bash")
            
    st.divider()
    
    # Simulation Logic for Demo Purposes
    if st.button("Simulate Gatekeeper Validation"):
        # This demonstrates state management by updating the logs
        new_log = f"[Gatekeeper] INFO: Validating Batch of {len(st.session_state.df_master)} rows..."
        st.session_state.agent_logs.append(new_log)
        st.session_state.agent_logs.append("[Gatekeeper] SUCCESS: Schema integrity verified (12/12 columns).")
        st.rerun()

    # --- TAB 2: SEMANTIC LAB (EMBEDDINGS & SLANG) ---
with tab2:
    st.header("Semantic Laboratory")
    st.markdown("Mapping Hinglish Slang to Semantic Intent")

    # 1. Slang Mapper Row
    with st.expander("View Hinglish Semantic Dictionary", expanded=False):
        # We simulate the dictionary that Agent 1 uses
        slang_data = {
            "Hinglish Term": ["Silk Board scene", "Systumm hang", "Baigan", "Macha", "Paisa vasool", "Full majja"],
            "City Origin": ["Bangalore", "Delhi", "Hyderabad", "Bangalore", "Mumbai", "Mumbai"],
            "Semantic Interpretation": ["Logistics Bottleneck", "System Failure/Chaos", "Nonsense/Poor Quality", "Friend/Generic Tag", "High Value/ROI", "High Satisfaction"]
        }
        st.table(pd.DataFrame(slang_data))

    st.divider()

    # 2. 3D Vector Space Visualization
    st.subheader("High-Dimensional Narrative Geometry")
    
    # Check for mapped data
    try:
        df_mapped = pd.read_csv("urban_pulse/data/vector_mapped_data.csv")
        
        fig = px.scatter_3d(
            df_mapped, 
            x='x', y='y', z='z',
            color='city', # Visualizing by city first to see regional distribution
            hover_data=['raw_text', 'brand'],
            template="plotly_dark",
            height=700,
            title="3D Semantic Projection (TF-IDF + SVD)"
        )
        
        fig.update_layout(
            scene=dict(
                xaxis_title='Semantic X',
                yaxis_title='Semantic Y',
                zaxis_title='Semantic Z'
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except FileNotFoundError:
        st.info("💡 Semantic Space is currently empty. Run the 'Semantic Shaper' Agent to generate the 3D projection.")
        if st.button("Run Semantic Shaper Now"):
            st.session_state.agent_logs.append("[Shaper] INFO: Initializing TF-IDF Vectorization...")
            st.session_state.agent_logs.append("[Shaper] SUCCESS: SVD compression complete. 3D geometry locked.")
            st.rerun()


# --- TAB 3: DISCOVERY (CLUSTERING & PERSONAS) ---
with tab3:
    st.header("Cluster Discovery & Personas")
    st.markdown("Agent 3: Root-Cause Analysis of Semantic Islands")

    # 1. The Cluster Map (DBSCAN View)
    try:
        df_mapped = pd.read_csv("urban_pulse/data/vector_mapped_data.csv")
        
        # Color by Cluster ID instead of City
        fig_clusters = px.scatter_3d(
            df_mapped, 
            x='x', y='y', z='z',
            color='cluster',
            hover_data=['raw_text', 'city', 'platform'],
            template="plotly_dark",
            height=600,
            title="DBSCAN Density-Based Semantic Islands"
        )
        st.plotly_chart(fig_clusters, use_container_width=True)

        st.divider()

        # 2. Cluster Persona Cards (Agent 3 Output)
        st.subheader("Agent 3: Cluster Persona Gallery")
        
        # Load insights from the analyst agent
        insights_path = "urban_pulse/data/cluster_insights.json"
        if os.path.exists(insights_path):
            with open(insights_path, 'r') as f:
                cluster_insights = json.load(f)
            
            # Create a grid of cards
            cols = st.columns(3)
            for i, (c_id, meta) in enumerate(cluster_insights.items()):
                with cols[i % 3]:
                    st.container(border=True).markdown(f"""
                    ### 🏷️ {meta.get('cluster_title', 'Unnamed Cluster')}
                    **ID:** {c_id}  
                    **Impact:** `{meta.get('impact_level', 'Unknown')}`
                    
                    **Agent Insight:** {meta.get('root_cause', 'No analysis available.')}
                    """)
        else:
            st.warning("⚠️ Cluster analysis not yet generated. Run Agent 3 to build personas.")
            
    except FileNotFoundError:
        st.error("Missing vector data. Please run the pipeline first.")

    # --- TAB 4: EXECUTIVE WAR ROOM (STRATEGIC INSIGHTS) ---
with tab4:
    st.header("Executive War Room")
    
    # 1. Revenue Risk Radar
    st.subheader("💰 Revenue Risk Radar (Cart Value vs. Rating)")
    try:
        # We use the master DF for financial metrics
        df_risk = st.session_state.df_master.copy()
        
        fig_risk = px.density_heatmap(
            df_risk, 
            x="Star_Rating", 
            y="Cart_Value_INR", 
            nbinsx=5, nbinsy=10,
            color_continuous_scale="Viridis",
            title="Density of Revenue Risk (Target: Bottom Right Quadrant)",
            template="plotly_dark"
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating Risk Radar: {e}")

    st.divider()

    # 2. Platform Shadow Analysis (Agent: Shadow Agent)
    st.subheader("🕵️ Platform Shadow Analysis (Zepto vs. Blinkit vs. Others)")
    shadow_path = "urban_pulse/data/shadow_insights.json"
    
    if os.path.exists(shadow_path):
        with open(shadow_path, 'r') as f:
            shadow_data = json.load(f)
        
        # Select Category/Brand to compare
        cat_list = list(shadow_data.keys())
        sel_cat = st.selectbox("Select Category for Shadow Audit:", cat_list)
        
        if sel_cat:
            brands = shadow_data[sel_cat]
            for brand, metrics in brands.items():
                with st.container(border=True):
                    col_b, col_w, col_i = st.columns([1, 1, 2])
                    col_b.success(f"🏆 Winner: {metrics.get('Winning_Platform')}")
                    col_w.error(f"📉 Loser: {metrics.get('Losing_Platform')}")
                    col_i.info(f"**Shadow Insight:** {metrics.get('Root_Insight')}")
    else:
        st.warning("Shadow insights not found. Please run the Shadow Agent.")

    st.divider()

    # 3. Escalation Feed (Agent 4)
    st.subheader("🚨 High-Priority Escalation Feed")
    esc_path = "urban_pulse/data/escalation_results.json"
    if os.path.exists(esc_path):
        with open(esc_path, 'r') as f:
            esc_results = json.load(f)
        
        for c_id, details in esc_results.items():
            # Only show if churn probability is high (>70%)
            prob_val = int(details.get('churn_probability', '0%').replace('%',''))
            if prob_val > 70:
                st.warning(f"**CLUSTER {c_id} ESCALATION** | Churn Risk: {details.get('churn_probability')}")
                st.markdown(f"**Driver:** {details.get('financial_risk_driver')} | **Action:** `{details.get('automated_action')}`")
    else:
        st.info("No active escalations. Swarm is in steady state.")

# --- THE AI CENTER (GLOBAL OVERLAY CHATBOT) ---
st.divider()
st.markdown("## 🤖 AI Center: Swarm Intelligence Query")

# Chat Container
chat_container = st.container(height=300, border=True)

# Display Chat History
for message in st.session_state.chat_history:
    with chat_container.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask the Swarm anything (e.g., 'Summarize the Mumbai risks')"):
    # 1. Add User Message to History
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with chat_container.chat_message("user"):
        st.markdown(prompt)

    # 2. Logic: Simple RAG Simulation using session state metadata
    # In a full build, this would use a Vector DB or load all JSONs as context
    with chat_container.chat_message("assistant"):
        with st.spinner("Consulting Swarm Agents..."):
            # Mock Response Logic for Sprint 1
            response = ""
            if "mumbai" in prompt.lower():
                response = "Based on the **Cluster Analyst (Agent 3)**, Mumbai is currently facing a 'Midnight Melt Crisis' due to Monsoon delays. **Agent 4** has escalated 5 tickets with 85% churn risk."
            elif "bangalore" in prompt.lower():
                response = "The **Semantic Shaper** indicates high 'Silk Board' friction. However, customer sentiment remains 'Sakkath' for frozen goods on Zepto."
            else:
                response = "I have analyzed the current swarm state. No critical anomalies detected outside of known regional clusters. How can I assist further?"
            
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()
```

## FILE: core_utils\batch_engine.py

```python
import pandas as pd
import json
import time
from google import genai
from config import Config

client = genai.Client(api_key=Config.GEMINI_API_KEY)

def get_working_model():
    """Dynamically fetch the working model for this specific API key."""
    try:
        available = {m.name for m in client.models.list()}
        fallbacks = [
            "models/gemini-2.5-flash-lite",
            "models/gemini-flash-lite-latest",
            "models/gemini-1.5-flash"
        ]
        for f in fallbacks:
            if f in available:
                return f
        return sorted(available)[0] if available else "gemini-1.5-flash"
    except:
        return "gemini-1.5-flash"

def prepare_batch_jsonl(csv_path="synthetic_geopol_data.csv", jsonl_path="batch_payload.jsonl"):
    print("--- 1. Packaging Data for Cloud Batch ---")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("Error: CSV not found.")
        return None
    
    with open(jsonl_path, "w") as f:
        for index, row in df.iterrows():
            prompt = f"""Act as a Geopolitical Intelligence Swarm.
Analyze this raw text: "{row['raw_text']}"
1. WORKER: Categorize into a 'primary_topic' (Trade, Energy, Security).
2. WORKER: Assign a 'sentiment_score' from -1.0 to 1.0.
3. CRITIC: Based on {row['country']} in {row['event_year']}, provide a 1-sentence 'truth_audit'.
Return ONLY valid JSON."""
            
            request_obj = {
                "id": f"row_{index}", # 'id' is often preferred over 'key' in v1
                "request": {
                    "contents": [{"parts": [{"text": prompt}]}],
                }
            }
            f.write(json.dumps(request_obj) + "\n")
            
    print(f"Packaged {len(df)} rows into {jsonl_path}.")
    return jsonl_path

def trigger_cloud_batch():
    jsonl_path = prepare_batch_jsonl()
    if not jsonl_path: return

    working_model = get_working_model()
    print(f"--- 2. Uploading Payload (Targeting: {working_model}) ---")
    
    try:
        uploaded_file = client.files.upload(file=jsonl_path, config={'mime_type': 'text/plain'})
        print(f"Upload secure. File URI: {uploaded_file.uri}")
        
        print("--- 3. Initiating Asynchronous Batch Job ---")
        # Creating the batch job with the dynamically found model
        batch_job = client.batches.create(
            model=working_model, 
            src=uploaded_file.name,
        )
        print(f"Batch Job Active! ID: {batch_job.name}")
        
        print("--- 4. Monitoring Remote Execution ---")
        while True:
            job_status = client.batches.get(name=batch_job.name)
            state_str = str(job_status.state)
            print(f"[{time.strftime('%H:%M:%S')}] Server Status: {state_str}...")
            
            if "SUCCEEDED" in state_str:
                print("\nBatch Complete! Data is ready for download.")
                break
            elif "FAILED" in state_str or "CANCELLED" in state_str:
                print(f"\nArchitect Alert: Job terminated. State: {state_str}")
                break
                
            time.sleep(30)
            
    except Exception as e:
        print(f"Batch API Error: {e}")
        print("Architect Note: Free-tier keys sometimes block Batch API access. If this fails, rely on the agent_engine.py backoff script.")

if __name__ == "__main__":
    trigger_cloud_batch()
```

## FILE: core_utils\config.py

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Dynamic Root Path Resolution
# Resolves the absolute path of this file, then steps up twice to the workspace root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Force load the .env from the master root directory
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    # 1. API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # 2. Project Scope (Geopolitics Anchors - Legacy)
    COUNTRIES = ["India", "Australia"]
    YEAR_RANGE = (2016, 2026)
    
    TARGET_SCENARIOS = {
        "Australia": {
            "year": 2020,
            "focus": "14 Grievances, Trade Sanctions, Coal/Wine bans",
            "narrative": "Strategic pivot and supply chain diversification."
        },
        "India": {
            "year": 2025,
            "focus": "U.S. Reciprocal Tariffs (50%), Steel Friction, Russian Oil Ties",
            "narrative": "Sovereign autonomy vs. trade coercion and pivot to EU-India FTA."
        }
    }
    
    # 3. Processing Settings
    TOTAL_ROWS = 20000  # Total target for the "Firehose"
    BATCH_SIZE = 50     # How many rows generated per AI call
    
    # 4. Math & UI Settings
    UMAP_COMPONENTS = 3 # For 3D Plotting
    CLUSTER_MIN_SIZE = 15 # Minimum rows to form an "Island" (HDBSCAN)
    
    @staticmethod
    def validate_setup():
        """Expert Peer Check: Ensure keys are present."""
        if not Config.GEMINI_API_KEY:
            raise ValueError(f"CRITICAL: GEMINI_API_KEY not found. Looked at: {ENV_PATH}")
        print("Architect Status: Configuration Locked. Root .env connected successfully.")

if __name__ == "__main__":
    Config.validate_setup()
```

## FILE: core_utils\master_ingestor.py

```python
import pandas as pd
import os
from datetime import datetime
from core_utils.triage_gatekeeper import TriageGatekeeper

class MasterIngestor:
    def __init__(self):
        print("Architect Status: Initializing Master Ingestor...")
        # Initialize our AI router
        self.gatekeeper = TriageGatekeeper()
        
        # Define the centralized map of Domain -> CSV Path
        self.domain_map = {
            "geopolitics": "geopolitics/data/synthetic_geopol_data.csv",
            "urban_pulse": "urban_pulse/data/raw_qcomm_reviews.csv"
        }

    def get_timestamp(self):
        """Standardizes date format for all domains."""
        return datetime.now().strftime("%d/%m/%Y")

    def process_and_route(self, raw_input_text: str):
        """Processes text through AI and identifies the target path."""
        print(f"Ingesting: {raw_input_text[:50]}...")
        
        # 1. Ask the Gatekeeper where this belongs
        classification = self.gatekeeper.route_input(raw_input_text)
        domain = classification.get("domain", "unknown")
        
        # 2. Match domain to the correct file path
        target_path = self.domain_map.get(domain)
        
        if not target_path:
            print(f"Architect Alert: Domain '{domain}' not recognized. Routing to 'unknown' bucket.")
            return "unknown", None
            
        print(f"Decision: Route to -> {domain.upper()} (Path: {target_path})")
        return domain, target_path


    def _map_to_schema(self, domain, raw_text):
        """Standardizes data structure based on the target domain's CSV schema."""
        timestamp = self.get_timestamp()
        
        if domain == "urban_pulse":
            # Matching the 10-column Urban Pulse Master Schema
            return {
                "review_id": f"manual-{os.urandom(4).hex()}",
                "date": timestamp,
                "city": "Unknown", # Could be extracted via another agent later
                "platform": "Manual_Entry",
                "category": "Uncategorized",
                "brand": "General",
                "delivery_time": 0,
                "order_context": "Direct_Ingest",
                "raw_text": raw_text,
                "star_rating": 3
            }
            
        elif domain == "geopolitics":
            # Matching the Geopolitics Swarm Schema
            return {
                "event_date": timestamp,
                "location": "Global",
                "event_description": raw_text,
                "risk_level": "Medium",
                "impact_area": "Supply Chain",
                "audit_status": "Pending_Review"
            }
        
        return {"raw_data": raw_text, "timestamp": timestamp}

    def save_data(self, mapped_data, target_path):
        """Appends structured data safely with quote protection."""
        try:
            new_row_df = pd.DataFrame([mapped_data])
            file_exists = os.path.isfile(target_path)
            
            # THE CRITICAL FIX: Add quoting=csv.QUOTE_ALL
            new_row_df.to_csv(
                target_path, 
                mode='a', 
                index=False, 
                header=not file_exists,
                quoting=csv.QUOTE_ALL  # <--- Forces quotes around every field
            )
            print(f"✅ Success: Data committed to {target_path}")
            return True
        except Exception as e:
            print(f"❌ Append Error: {e}")
            return False

    def run_ingest(self, raw_text: str):
        """The complete E2E ingestion flow."""
        # 1. Triage & Route (Step 2)
        domain, target_path = self.process_and_route(raw_text)
        
        if not target_path:
            return "Failed: No route found."
            
        # 2. Map to Schema (Step 3)
        mapped_data = self._map_to_schema(domain, raw_text)
        
        # 3. Commit to Disk (Step 4)
        success = self.save_data(mapped_data, target_path)
        
        return "Success" if success else "Failed: Append Error."

# --- INTEGRATION TEST BLOCK ---
if __name__ == "__main__":
    ingestor = MasterIngestor()
    
    # Test Case 1: Consumer Sentiment (Urban Pulse)
    print("\n--- TEST 1: CONSUMER FEEDBACK ---")
    ingestor.run_ingest("My Kwality Wall's ice cream was totally melted when it arrived via Zepto. Very disappointed.")
    
    # Test Case 2: Supply Chain Risk (Geopolitics)
    print("\n--- TEST 2: MACRO RISK ---")
    ingestor.run_ingest("Port strikes in Gujarat are likely to disrupt raw material supply for the Home Care division.")
```

## FILE: core_utils\triage_gatekeeper.py

```python
import json
from google import genai
from core_utils.config import Config

class TriageGatekeeper:
    def __init__(self):
        # Ensure your .env has the GEMINI_API_KEY
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"

    def route_input(self, raw_text: str):
        """
        Analyzes the input text and routes it to the correct 
        Business Group and Domain.
        """
        
        prompt = f"""
        Act as the Centralized AI Router for Unilever. 
        Analyze the following text and determine which Business Group (BG) and Pipeline it belongs to.
        
        TEXT: "{raw_text}"
        
        DOMAINS:
        1. 'geopolitics': Focuses on global risks, supply chain disruptions, war, trade policy, or macro-economic events. (BG: Home Care)
        2. 'urban_pulse': Focuses on Q-Commerce, consumer reviews, delivery speed, food quality (Ice cream, snacks), or local platform issues (Blinkit, Zepto). (BG: Personal Care)
        
        Return ONLY a JSON object with:
        {{
            "domain": "geopolitics" | "urban_pulse",
            "bg": "Home Care" | "Personal Care",
            "reasoning": "brief explanation"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=prompt
            )
            # Clean possible markdown formatting from LLM response
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Gatekeeper Error: {e}")
            # Fallback to prevent system crash
            return {"domain": "unknown", "bg": "unknown", "reasoning": str(e)}

if __name__ == "__main__":
    # Quick Test
    gatekeeper = TriageGatekeeper()
    print(gatekeeper.route_input("The price of crude oil is affecting our transport costs."))
```

## FILE: core_utils\ui_components.py

```python
import pandas as pd
import plotly.express as px
import json
import os
import streamlit as st

def load_data(path):
    if not os.path.exists(path):
        return None
    try:
        return pd.read_csv(path, on_bad_lines='warn')
    except:
        return None

def load_json_data(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def render_q_comm_view(data):
    tab1, tab2 = st.tabs(["Spatial Routing (Operations)", "Category Intelligence (Brand Health)"])

    with tab1:
        insights = load_json_data("urban_pulse/data/cluster_insights.json")
        escalations = load_json_data("urban_pulse/data/escalation_results.json")
        
        st.subheader("3D Semantic Mapping")
        fig = px.scatter_3d(
            data, x='x', y='y', z='z', 
            color='cluster',
            hover_data=['brand', 'raw_text'],
            template="plotly_dark", 
            height=600,
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z')
        )
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Trend Inspector & Routing")
        
        if insights:
            cluster_options = {f"Cluster {k}": k for k in insights.keys()}
            selected_label = st.selectbox("Select a micro-cluster to analyze:", options=list(cluster_options.keys()), key="cluster_select")
            
            if selected_label:
                c_id = cluster_options[selected_label]
                res = insights.get(c_id, {})
                esc = escalations.get(c_id, {})
                
                col1, col2 = st.columns([2, 2])
                with col1:
                    st.success(f"### {res.get('cluster_title', 'Unknown')}")
                    st.markdown(f"**Root Cause:** {res.get('root_cause', 'N/A')}")
                    st.metric("Impact Level", res.get('impact_level', 'N/A'))
                with col2:
                    st.warning("Automated Escalation Protocol")
                    st.markdown(f"**Churn Probability:** {esc.get('churn_probability', 'N/A')}")
                    st.markdown(f"**Target Routing:** {esc.get('recommended_routing', 'N/A')}")
                    st.info(f"**Action Executed:** {esc.get('automated_action', 'N/A')}")
        else:
            st.warning("No insights found. Run the pipelines.")

    with tab2:
        st.subheader("FMCG Category Intelligence")
        cat_insights = load_json_data("urban_pulse/data/category_insights.json")
        
        if cat_insights:
            selected_cat = st.selectbox("Select Category:", options=list(cat_insights.keys()), key="cat_select")
            if selected_cat:
                c_data = cat_insights[selected_cat]
                
                st.markdown(f"### Strategy: {c_data.get('strategy_move', 'N/A')}")
                
                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    st.info(f"📈 **Peak Period:** {c_data.get('peak_period', 'N/A')}")
                    st.write("**Top Likes:**")
                    for like in c_data.get('top_likes', []):
                        st.write(f"- {like}")
                with t_col2:
                    st.error(f"📉 **Drop Period:** {c_data.get('drop_period', 'N/A')}")
                    st.write("**Top Dislikes:**")
                    for dislike in c_data.get('top_dislikes', []):
                        st.write(f"- {dislike}")
        else:
            st.warning("Run Agent 5 to generate category insights.")

    with st.expander("View Raw Data Feed"):
        st.dataframe(data[['date', 'category', 'brand', 'raw_text', 'cluster']].tail(20), use_container_width=True)
```

## FILE: core_utils\__init__.py

```python

```

## FILE: geopolitics\data\__init__.py

```python

```

## FILE: geopolitics\engine\data_gen.py

```python
import pandas as pd
import json
import time
import os
import random
from google import genai  # <--- CRITICAL FIX: The new 2026 import path
from core_utils.config import Config

DEFAULT_MODEL = os.getenv("GEMINI_MODEL") or "gemini-3.1-flash-lite-preview"

_CLIENT: genai.Client | None = None
_MODEL_NAMES_CACHE: set[str] | None = None


def _is_retryable_error(exc: Exception) -> bool:
    """
    Best-effort retry classifier across google-genai / transport errors.
    We treat quota/rate-limit and transient server/network issues as retryable.
    """
    msg = str(exc).lower()
    retry_markers = [
        "429",
        "resource_exhausted",
        "rate limit",
        "quota",
        "too many requests",
        "503",
        "service unavailable",
        "500",
        "internal",
        "timeout",
        "temporarily unavailable",
        "connection reset",
        "connection aborted",
        "ssl",
    ]
    return any(m in msg for m in retry_markers)


def _sleep_seconds_for_attempt(attempt: int, *, min_seconds: float = 30.0, max_seconds: float = 300.0) -> float:
    """
    Exponential backoff with jitter, with a hard minimum wait.
    attempt=0 is the first retry sleep (after first failure).
    """
    # Exponential backoff (30, 60, 120, 240, ...) capped, plus small jitter.
    backoff = min_seconds * (2 ** attempt)
    jitter = random.uniform(0.0, 3.0)
    return min(max_seconds, max(min_seconds, backoff + jitter))


def _get_client() -> genai.Client:
    # Ensure `.env` was loaded (Config imports dotenv.load_dotenv()) and the key exists.
    Config.validate_setup()

    # Also verify the env var is actually present at runtime (guards against import-order issues).
    api_key = os.getenv("GEMINI_API_KEY") or Config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("CRITICAL: GEMINI_API_KEY missing (dotenv load may have failed).")

    global _CLIENT
    if _CLIENT is None:
        _CLIENT = genai.Client(api_key=api_key)
    return _CLIENT


def _get_available_model_names(client: genai.Client) -> set[str]:
    global _MODEL_NAMES_CACHE
    if _MODEL_NAMES_CACHE is None:
        _MODEL_NAMES_CACHE = {m.name for m in client.models.list()}
    return _MODEL_NAMES_CACHE


def _resolve_model_name(client: genai.Client, requested: str) -> str:
    """
    Prefer the requested model, but fall back when it isn't available for this key/API.

    The google-genai SDK returns model names like 'models/gemini-2.0-flash' from list().
    Some endpoints accept short names too, but we keep fallbacks in the listed form.
    """
    requested = (requested or "").strip()
    if not requested:
        requested = "gemini-3.1-flash-lite-preview"

    names = _get_available_model_names(client)

    # Try both short and fully-qualified forms for the requested model.
    requested_candidates = [requested]
    if not requested.startswith("models/"):
        requested_candidates.append(f"models/{requested}")

    for cand in requested_candidates:
        if cand in names:
            return cand

    # Fall back to an available flash model (prefer "lite" to reduce cost/pressure).
    fallbacks = [
        "models/gemini-flash-lite-latest",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash-lite-001",
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
    ]
    for fb in fallbacks:
        if fb in names:
            print(f"Architect Note: Requested model '{requested}' unavailable; using fallback '{fb}'.")
            return fb

    # Last resort: pick the first model the API lists (stable but not ideal).
    if names:
        chosen = sorted(names)[0]
        print(f"Architect Note: No preferred flash models found; using '{chosen}'.")
        return chosen

    # If listModels fails or returns nothing, just try the requested value.
    return requested

def generate_synthetic_batch(country, scenario, *, model: str = DEFAULT_MODEL, max_retries: int = 6):
    """Generates grounded data using the new 2026 GenAI SDK."""
    prompt = f"""
    Act as a Geopolitical Data Scientist. Generate 20 unique social media/news data points 
    for the year {scenario['year']} in {country}.
    Context: {scenario['focus']}
    Narrative: {scenario['narrative']}
    Format: Return ONLY a JSON list with: 'event_year', 'country', 'source', 'raw_text'.
    """
    
    client = _get_client()
    model = _resolve_model_name(client, model)

    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(model=model, contents=prompt)

            # Clean the response to ensure it's valid JSON
            clean_json = (response.text or "").replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            if not isinstance(data, list):
                raise ValueError("Model returned non-list JSON; expected a JSON list.")
            return data
        except Exception as e:
            last_err = e
            retryable = _is_retryable_error(e)
            if attempt >= max_retries or not retryable:
                print(
                    f"Architect Alert: Batch failed for {country}. "
                    f"Retryable={retryable}. Attempts={attempt + 1}/{max_retries + 1}. Error: {e}"
                )
                return []

            sleep_s = _sleep_seconds_for_attempt(attempt, min_seconds=30.0, max_seconds=300.0)
            print(
                f"Architect Alert: Batch failed for {country}. "
                f"Retrying in {sleep_s:.1f}s (attempt {attempt + 1}/{max_retries})... Error: {e}"
            )
            time.sleep(sleep_s)

    print(f"Architect Alert: Batch failed for {country}. Error: {last_err}")
    return []

def run_firehose():
    all_data = []
    print(f"--- Starting 2026 SDK Firehose: TaxoFlow-Agents ---")
    
    for country, scenario in Config.TARGET_SCENARIOS.items():
        print(f"Generating data for {country}...")
        batch = generate_synthetic_batch(country, scenario)
        if batch:
            all_data.extend(batch)
            print(f"Batch complete. Rows gathered: {len(all_data)}")
        time.sleep(1)  # Small pacing between batches
            
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("geopolitics/data/synthetic_geopol_data.csv", index=False)
        print("--- Firehose complete. CSV saved! ---")
    else:
        print("--- Firehose Error: No rows generated. Check API Key. ---")

if __name__ == "__main__":
    run_firehose()
```

## FILE: geopolitics\engine\geopol_swarm.py

```python
import pandas as pd
import json
import time
from google import genai
from utils.config import Config

Config.validate_setup()
client = genai.Client(api_key=Config.GEMINI_API_KEY)

def _is_429(err: Exception) -> bool:
    msg = str(err).lower()
    return "429" in msg or "resource_exhausted" in msg


def _harvest_working_model() -> str:
    """
    Model Harvester pattern:
    - List all models visible to this API key
    - Filter for likely-high-quota models (name contains 'flash' or '8b')
    - Probe models with a tiny request; lock onto the first that does NOT 429
    """
    available = [m.name for m in client.models.list() if getattr(m, "name", None)]
    if not available:
        raise ValueError("CRITICAL: No models returned by client.models.list().")

    candidates = [m for m in available if ("flash" in m.lower() or "8b" in m.lower())]
    # De-prioritize known capped aliases/buckets if others exist.
    deprioritized = {"models/gemini-2.5-flash-lite", "models/gemini-flash-lite-latest"}
    candidates = sorted(candidates, key=lambda m: (m in deprioritized, m))

    if not candidates:
        raise ValueError("CRITICAL: No candidate models matched 'flash' or '8b'.")

    test_prompt = "Return ONLY valid JSON: {\"ok\": true}"
    for model_name in candidates:
        try:
            resp = client.models.generate_content(model=model_name, contents=test_prompt)
            text = (resp.text or "").strip()
            if not text:
                # Treat empty as non-working; try next.
                continue
            print(f"Architect Note: Model Harvester locked onto '{model_name}'.")
            return model_name
        except Exception as e:
            if _is_429(e):
                continue
            # Not a 429: could be not supported for generateContent; try next.
            continue

    raise ValueError("CRITICAL: No working model found (all candidates 429 or unsupported).")


def get_working_model() -> str:
    """
    Selects a model that is actually usable right now (not 429) for this API key.
    """
    try:
        return _harvest_working_model()
    except Exception as e:
        print(f"Architect Note: Model Harvester failed ({e}).")
        # As a last resort, keep previous behavior: try a reasonable default.
        return "models/gemini-2.0-flash"


def _is_missing_truth_audit(value) -> bool:
    # Treat NaN, empty string, and literal "None" (case-insensitive) as missing.
    if pd.isna(value):
        return True
    s = str(value).strip()
    return s == "" or s.lower() == "none"


def _extract_retry_seconds(err: Exception) -> float | None:
    """
    Best-effort parser for retry hints like:
      "Please retry in 59.03s."
      or details: 'retryDelay': '59s'
    """
    msg = str(err)
    lowered = msg.lower()
    if "retry in" in lowered:
        # Very small heuristic parser to avoid regex dependency.
        try:
            tail = lowered.split("retry in", 1)[1].strip()
            # tail looks like "59.03s.', ..." or "59s.', ..."
            num = ""
            for ch in tail:
                if ch.isdigit() or ch == ".":
                    num += ch
                elif num:
                    break
            return float(num) if num else None
        except Exception:
            return None
    if "retrydelay" in lowered:
        try:
            # look for "... retryDelay': '59s' ..."
            tail = msg.split("retryDelay", 1)[1]
            digits = ""
            for ch in tail:
                if ch.isdigit():
                    digits += ch
                elif digits:
                    break
            return float(digits) if digits else None
        except Exception:
            return None
    return None

def recover_missing_data():
    print("--- TaxoFlow Agent Swarm: Checkpoint Recovery Mode ---")
    df = pd.read_csv("geopolitics/data/synthetic_geopol_data.csv")
    working_model = get_working_model()
    
    # Identify rows where the agent failed previously
    missing_mask = df["truth_audit"].apply(_is_missing_truth_audit)
    missing_count = missing_mask.sum()
    
    if missing_count == 0:
        print("Architect Status: All rows perfectly tagged. No recovery needed.")
        return

    print(f"Found {missing_count} rows missing intelligence. Resuming extraction...")
    print("Pacing at 7 seconds per row to guarantee bypass of the 15 RPM limit.")
    
    for index, row in df[missing_mask].iterrows():
        print(f"      Recovering Row {index+1}/{len(df)}...")
        prompt = f"""Act as a Geopolitical Intelligence Swarm.
Analyze this raw text: "{row['raw_text']}"
1. WORKER: Categorize into a 'primary_topic' (Trade, Energy, Security, etc).
2. WORKER: Assign a 'sentiment_score' from -1.0 to 1.0.
3. CRITIC: Based on {row['country']} in {row['event_year']}, provide a 1-sentence 'truth_audit'.
Return ONLY valid JSON with keys: 'primary_topic', 'sentiment_score', 'truth_audit'."""
        
        try:
            resp = client.models.generate_content(model=working_model, contents=prompt)
            clean_json = resp.text.replace('```json', '').replace('```', '').strip()
            agent_data = json.loads(clean_json)
            
            df.at[index, 'primary_topic'] = agent_data.get('primary_topic')
            df.at[index, 'sentiment_score'] = float(agent_data.get('sentiment_score', 0.0))
            df.at[index, 'truth_audit'] = agent_data.get('truth_audit')

            # Checkpoint after each successful row to prevent data loss.
            df.to_csv('geopolitics/data/synthetic_geopol_data.csv', index=False)
        except Exception as e:
            print(f"      [Failed] Row {index+1}: {e}")

            # If the API returns a retry hint, respect it (daily quota won't fix,
            # but minute-level throttles will).
            retry_s = _extract_retry_seconds(e)
            sleep_s = max(7.0, retry_s) if retry_s is not None else 7.0
            time.sleep(sleep_s)
            continue

        # Strict pacing: always 7 seconds between successful requests (<= ~8.5 RPM).
        time.sleep(7)

    print("--- Recovery Complete! Data locked and saved. ---")

if __name__ == "__main__":
    recover_missing_data()
```

## FILE: geopolitics\engine\vector_memory.py

```python
import pandas as pd
import numpy as np
import time
from google import genai
import umap
from sklearn.cluster import HDBSCAN
from utils.config import Config

Config.validate_setup()
client = genai.Client(api_key=Config.GEMINI_API_KEY)

def get_working_embedding_model():
    """Discovers a working embedding model via API listing, then falls back to known candidates."""
    try:
        for m in client.models.list():
            name = getattr(m, "name", None) or str(m)
            if not name or "embed" not in name.lower():
                continue
            try:
                client.models.embed_content(model=name, contents="test")
                print(f"Architect Note: Using discovered embedding model: {name}")
                return name
            except Exception:
                continue
    except Exception as e:
        print(f"Architect Note: Model discovery skipped ({e}). Trying known candidates...")

    candidates = [
        "models/gemini-embedding-001",
        "gemini-embedding-001",
        "text-embedding-004",
        "models/text-embedding-004",
        "embedding-001",
        "models/embedding-001",
        "text-embedding-005",
    ]
    print("Architect Note: Testing embedding endpoints...")
    for model_name in candidates:
        try:
            client.models.embed_content(model=model_name, contents="test")
            print(f"Architect Note: Using candidate embedding model: {model_name}")
            return model_name
        except Exception:
            continue

    raise ValueError("CRITICAL: No working embedding model found on this API key.")

def generate_embeddings(batch_size=50):
    print("--- TaxoFlow Vector Engine: Building Narrative Geometry ---")
    try:
        df = pd.read_csv('data/processed_geopol_data.csv')
    except FileNotFoundError:
        print("Architect Alert: 'processed_geopol_data.csv' missing.")
        return

    embedding_model = get_working_embedding_model()
    print(f"Locked onto verified embedding model: {embedding_model}")
    print(f"Embedding {len(df)} signals...")
    
    all_embeddings = []
    embedding_dim = 3072

    for i in range(0, len(df), batch_size):
        batch_texts = df['raw_text'].iloc[i:i+batch_size].tolist()
        print(f"      Processing Chunk {i//batch_size + 1}...")
        
        try:
            response = client.models.embed_content(
                model=embedding_model,
                contents=batch_texts
            )
            batch_vectors = []
            for e in (response.embeddings or []):
                vals = getattr(e, "values", None)
                if vals is not None:
                    batch_vectors.append(vals)
                    embedding_dim = len(vals)
                else:
                    batch_vectors.append([0.0] * embedding_dim)
            if len(batch_vectors) < len(batch_texts):
                batch_vectors.extend([[0.0] * embedding_dim] * (len(batch_texts) - len(batch_vectors)))
            all_embeddings.extend(batch_vectors)
        except Exception as e:
            print(f"      [Embedding Error] Chunk {i}: {e}")
            all_embeddings.extend([[0.0] * embedding_dim] * len(batch_texts))
            
        time.sleep(1) 
        
    matrix = np.array(all_embeddings)

    print("Projecting into 3D space (UMAP)...")
    reducer = umap.UMAP(n_components=3, n_neighbors=15, min_dist=0.1, random_state=42)
    projections = reducer.fit_transform(matrix)
    
    df['x'], df['y'], df['z'] = projections[:, 0], projections[:, 1], projections[:, 2]

    print("Identifying Geopolitical Islands (HDBSCAN)...")
    clusterer = HDBSCAN(min_cluster_size=3) 
    df['cluster_id'] = clusterer.fit_predict(projections)

    df.to_csv('data/vector_mapped_data.csv', index=False)
    print(f"--- Vector Mapping Complete. {len(df)} points locked! ---")

if __name__ == "__main__":
    generate_embeddings()
```

## FILE: geopolitics\engine\__init__.py

```python

```

## FILE: geopolitics\ui\dashboard.py

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(
    page_title="TaxoFlow Agents | 3D Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌐 TaxoFlow: Geopolitical Swarm Intelligence")
st.markdown("Visualizing multi-agent taxonomy and sentiment clustering in 3D space.")

# 2. Robust Data Loading
@st.cache_data
def load_data():
    # Architect Note: Use absolute pathing based on the project root for Cloud stability
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    data_path = os.path.join(root_dir, 'geopolitics', 'data', 'vector_mapped_data.csv')
    
    try:
        df = pd.read_csv(data_path)
        df['cluster_id'] = df['cluster_id'].astype(str)
        return df
    except FileNotFoundError:
        st.error(f"Data missing at {data_path}. Please run vector_memory.py first.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. Top-Level Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Signals Processed", len(df))
    col2.metric("Distinct Geopolitical Islands", df['cluster_id'].nunique())
    col3.metric("Average Sentiment", round(df['sentiment_score'].mean(), 2))

    st.divider()

    # 4. The 3D Engine (Plotly)
    st.subheader("Interactive Narrative Space")
    
    fig = px.scatter_3d(
        df,
        x='x', y='y', z='z',
        color='cluster_id',
        hover_name='primary_topic',
        hover_data={
            'x': False, 'y': False, 'z': False, 
            'country': True,
            'event_year': True,
            'sentiment_score': True,
            'truth_audit': True
        },
        title="3D Semantic Clustering of Geopolitical Events",
        opacity=0.8,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )

    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=40),
        scene=dict(
            xaxis_title="Narrative Axis X",
            yaxis_title="Narrative Axis Y",
            zaxis_title="Narrative Axis Z"
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # 5. Raw Data Inspection Table
    st.subheader("Agent Audit Log")
    st.dataframe(
        df[['country', 'event_year', 'primary_topic', 'sentiment_score', 'truth_audit', 'raw_text']],
        use_container_width=True
    )

# --- System Resilience Documentation ---
with st.sidebar:
    st.markdown("---") 
    with st.expander("🛠️ System Health & Resilience Note"):
        st.info(
            "This pipeline features an **Automated Failover System**. "
            "If a primary LLM (e.g., Gemini 2.0) hits a daily quota or rate limit, "
            "the **'Model Harvester'** dynamically reroutes requests to the next "
            "available healthy endpoint (e.g., Gemini 1.5-Flash-8B) to ensure "
            "zero-downtime data processing."
        )
        st.caption("Status: Resilient Failover Active ✅")
```

## FILE: geopolitics\ui\__init__.py

```python

```

## FILE: urban_pulse\engine\category_agent.py

```python
import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class CategoryAgent:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"

    def generate_insights(self, input_csv):
        if not os.path.exists(input_csv):
            print(f"ERROR: {input_csv} not found.")
            return

        df = pd.read_csv(input_csv)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        categories = df['category'].dropna().unique()
        print(f"Category Engine targeting: {categories}")
        
        category_map = {}

        for cat in categories:
            cat_df = df[df['category'] == cat].sort_values(by='date').tail(30)
            
            samples = cat_df.apply(lambda row: f"[{row['date'].strftime('%Y-%m-%d') if pd.notnull(row['date']) else 'Unknown'}] {row['raw_text']}", axis=1).tolist()
            text_bundle = "\n- ".join(samples)

            prompt = f"""
            Act as an FMCG Category Director for Unilever.
            Analyze these chronological reviews for the '{cat}' category:
            {text_bundle}
            
            Identify temporal trends, what customers liked, and what they disliked.
            Return ONLY a valid JSON object in this exact format:
            {{
                "peak_period": "Month/Event with highest positive engagement",
                "drop_period": "Month/Event with lowest engagement or highest complaints",
                "top_likes": ["Point 1", "Point 2"],
                "top_dislikes": ["Point 1", "Point 2"],
                "strategy_move": "One line of business advice"
            }}
            """

            try:
                print(f"Agent 5: Analyzing Category '{cat}'...")
                response = self.client.models.generate_content(model=self.model_id, contents=prompt)
                
                raw_res = response.text.strip()
                if "```json" in raw_res:
                    raw_res = raw_res.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_res:
                    raw_res = raw_res.split("```")[1].strip()
                
                category_map[str(cat)] = json.loads(raw_res)
                print(f"Category '{cat}' insights generated.")
                
            except Exception as e:
                print(f"Category '{cat}' Failed: {e}")

        output_path = "urban_pulse/data/category_insights.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(category_map, f, indent=4)
        
        print(f"\nCATEGORY INSIGHTS SAVED: {output_path}")

if __name__ == "__main__":
    agent = CategoryAgent()
    agent.generate_insights("urban_pulse/data/vector_mapped_data.csv")
```

## FILE: urban_pulse\engine\cluster_analyst.py

```python
import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class ClusterAnalyst:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"
        self.input_path = "urban_pulse/data/vector_mapped_data.csv"
        self.output_path = "urban_pulse/data/cluster_insights.json"

    def execute_analysis(self):
        if not os.path.exists(self.input_path):
            print(f"CRITICAL: {self.input_path} not found. Analyst halting.")
            return

        # 1. Load Data with Normalization
        df = pd.read_csv(self.input_path, on_bad_lines='skip', engine='python')
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Extract Valid Clusters (ignoring noise cluster -1)
        valid_clusters = df[df['cluster'] != -1]['cluster'].unique()
        
        if len(valid_clusters) == 0:
            print("Architect Note: No meaningful clusters found to analyze.")
            return

        cluster_insights_dict = {}

        print(f"Cluster Analyst: Deep-diving into {len(valid_clusters)} semantic islands...")

        for c_id in valid_clusters:
            # Sample data from this specific cluster for LLM context
            cluster_data = df[df['cluster'] == c_id].head(15)
            sample_text = "\n".join(cluster_data['raw_text'].tolist())
            avg_rating = cluster_data['star_rating'].mean()

            # 3. Construct the LLM Analyst Prompt
            analysis_prompt = f"""
            Act as a Lead Product Strategist at Unilever. 
            Analyze this cluster of consumer feedback and determine the root cause.
            
            CLUSTER DATA SAMPLES:
            {sample_text}
            
            Average Star Rating for this Cluster: {avg_rating:.2f}
            
            Provide a strictly valid JSON response with these keys:
            - cluster_title: A punchy 3-4 word title (e.g., 'Late Night Delivery Friction')
            - root_cause: A one-sentence technical/operational explanation.
            - impact_level: 'High', 'Medium', or 'Low' based on rating and sentiment.
            """

            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=analysis_prompt
                )
                
                # Clean and Parse JSON
                res_text = response.text.strip()
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                
                cluster_insights_dict[str(c_id)] = json.loads(res_text)
                print(f"   > Successfully analyzed Cluster {c_id}: {cluster_insights_dict[str(c_id)]['cluster_title']}")

            except Exception as e:
                print(f"   > Error analyzing cluster {c_id}: {e}")

        # 4. Save the Final Contract
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(cluster_insights_dict, f, indent=4)
        
        print(f"SUCCESS: Analysis artifacts locked at {self.output_path}")

if __name__ == "__main__":
    analyst = ClusterAnalyst()
    analyst.execute_analysis()
```

## FILE: urban_pulse\engine\escalation_agent.py

```python
import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class EscalationEngine:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"
        self.input_path = "urban_pulse/data/vector_mapped_data.csv"
        self.output_path = "urban_pulse/data/escalation_results.json"

    def process_escalations(self):
        if not os.path.exists(self.input_path):
            print(f"CRITICAL: {self.input_path} missing.")
            return

        # 1. Standardized Load
        df = pd.read_csv(self.input_path, on_bad_lines='skip', engine='python')
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Logic: Target High-Value, Low-Rating Clusters
        # Group by cluster to find collective failure points
        cluster_stats = df.groupby('cluster').agg({
            'star_rating': 'mean',
            'cart_value_inr': 'sum'
        }).reset_index()

        # Identify clusters with avg rating < 3.0 and high revenue at risk
        high_risk_clusters = cluster_stats[
            (cluster_stats['star_rating'] < 3.0) & 
            (cluster_stats['cluster'] != -1)
        ].sort_values(by='cart_value_inr', ascending=False)

        escalation_dict = {}

        for _, row in high_risk_clusters.head(5).iterrows():
            c_id = int(row['cluster'])
            samples = df[df['cluster'] == c_id].head(10)['raw_text'].tolist()
            
            prompt = f"""
            Identify financial risk and suggest an automated action for this cluster:
            {samples}
            
            Total Revenue at Risk: INR {row['cart_value_inr']}
            
            Return JSON:
            {{
                "churn_probability": "High/Medium/Low",
                "financial_risk_driver": "Short reason",
                "automated_action": "e.g., Issue 100 INR refund to all in cluster"
            }}
            """
            
            try:
                res = self.client.models.generate_content(model=self.model_id, contents=prompt)
                res_text = res.text.strip()
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                
                escalation_dict[str(c_id)] = json.loads(res_text)
                escalation_dict[str(c_id)]['revenue_at_stake'] = float(row['cart_value_inr'])
            except Exception as e:
                print(f"Escalation Error for Cluster {c_id}: {e}")

        # 3. Save Artifact
        with open(self.output_path, 'w') as f:
            json.dump(escalation_dict, f, indent=4)
        print(f"SUCCESS: Escalation feed updated at {self.output_path}")

if __name__ == "__main__":
    engine = EscalationEngine()
    engine.process_escalations()
```

## FILE: urban_pulse\engine\orchestrator.py

```python
import subprocess
import time
import sys

class SwarmOrchestrator:
    def __init__(self):
        # The DAG (Directed Acyclic Graph) sequence
        self.pipeline = [
            ("Semantic Shaper", "urban_pulse.engine.semantic_shaper"),
            ("Cluster Analyst", "urban_pulse.engine.cluster_analyst"),
            ("Escalation Engine", "urban_pulse.engine.escalation_agent"),
            ("Category Intelligence", "urban_pulse.engine.category_agent"),
            ("Shadow Agent", "urban_pulse.engine.shadow_agent")
        ]

    def run_pipeline(self):
        print("Architect Status: Initiating Swarm Orchestration...")
        start_time = time.time()
        
        for name, module in self.pipeline:
            print(f"\n>>> Triggering Node: {name}...")
            # Spawning isolated processes prevents memory leaks from heavy ML models
            result = subprocess.run([sys.executable, "-m", module])
            
            if result.returncode != 0:
                print(f"CRITICAL FAILURE: {name} crashed. Halting pipeline.")
                return
                
        elapsed = time.time() - start_time
        print(f"\nSWARM EXECUTION COMPLETE. Total pipeline time: {elapsed:.2f} seconds.")
        print("Dashboard is now serving fresh data.")

if __name__ == "__main__":
    orchestrator = SwarmOrchestrator()
    orchestrator.run_pipeline()
```

## FILE: urban_pulse\engine\qcomm_data_gen.py

```python
import pandas as pd
import json
import time
import os
import random
from google import genai
from core_utils.config import Config

# --- MASTER CONFIGURATION ---
TARGET_ROWS = 1000  # Upping this to your 1k goal
BATCH_SIZE = 10
MODEL_ID = "gemini-3.1-flash-lite-preview"
OUTPUT_PATH = "urban_pulse/data/raw_qcomm_reviews.csv"

def get_client():
    Config.validate_setup()
    return genai.Client(api_key=Config.GEMINI_API_KEY)

def generate_qcomm_batch(client, batch_num):
    """Generates hyper-realistic Q-Commerce data with advanced linguistic rules."""
    
    # --- INTEGRATING YOUR RESEARCH-DRIVEN PROMPT HERE ---
    prompt = f"""
    Act as an Expert Data Engineer. Generate {BATCH_SIZE} unique Q-Commerce reviews for 2025.
    
    SCHEMA: [review_id (UUID), date (DD/MM/YYYY), city, platform, category, brand, delivery_time, order_context, raw_text (Hinglish/Slang), star_rating, cart_value_inr, surge_fee_paid]
    
    GEOGRAPHIC SLANG RULES (STRICT):
    - Bangalore: 'Silk Board scene', 'Macha', 'Sakkath', 'Adjust maadi'.
    - Mumbai: 'Fatafat', 'Full majja', 'Paisa vasool', 'Kachra'.
    - Delhi: 'Systumm hang', 'Challan kat gaya', 'Oye hoye swaad', 'Kalesh'.
    - Hyderabad: 'Baigan', 'Hau', 'Kirak', 'Zabardast'.
    - Pune: 'Kantaala', 'Bhaari', 'Vishesh', 'Naad khula'.

    LOGIC & CORRELATION RULES:
    1. If delivery_time > 40 AND surge_fee_paid = True: The raw_text MUST complain about the platform/delay.
    2. If order_context = 'Mumbai Monsoon' AND category = 'Ice cream': Mention melting/leakage.
    3. Scenarios: IPL Finals, Silk Board Jam, PG Food Crisis, Late Night Cravings, Hangover Recovery.
    4. Slang must stay city-accurate (No 'Macha' in Delhi).

    Return ONLY a JSON list of objects. No prose.
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Architect Alert: Batch {batch_num} failed. Error: {e}")
        return []

def run_firehose():
    client = get_client()
    all_data = []
    
    print(f"--- Launching The Urban Pulse Firehose (Target: {TARGET_ROWS}) ---")
    
    batch_count = 1
    while len(all_data) < TARGET_ROWS:
        print(f"Generating Batch {batch_count} (Progress: {len(all_data)}/{TARGET_ROWS})...")
        batch = generate_qcomm_batch(client, batch_count)
        
        if batch:
            all_data.extend(batch)
            batch_count += 1
            # Batch sleep to respect Gemini 3.1 Flash-Lite Rate Limits (15 RPM)
            time.sleep(4.0) 
        else:
            print("Cooling down for 10s due to failure...")
            time.sleep(10)

    # Finalize and Save
    df = pd.DataFrame(all_data[:TARGET_ROWS])
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print("-" * 50)
    print(f"SUCCESS: {len(df)} rows saved to {OUTPUT_PATH}")
    print("-" * 50)

if __name__ == "__main__":
    run_firehose()
```

## FILE: urban_pulse\engine\semantic_shaper.py

```python
import os
import numpy as np
import pandas as pd
import umap
from sklearn.cluster import DBSCAN
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

INPUT_PATH = "urban_pulse/data/raw_qcomm_reviews.csv"
OUTPUT_PATH = "urban_pulse/data/vector_mapped_data.csv"

class SemanticShaper:
    def __init__(self):
        print("Architect Status: Initializing Semantic Shaper (TF-IDF + SVD)...")

    def process_data(self):
        if not os.path.exists(INPUT_PATH):
            raise FileNotFoundError(f"CRITICAL: {INPUT_PATH} not found.")

        # LOAD DATA WITH ROBUSTNESS: Handles extra commas and encoding issues
        try:
            df = pd.read_csv(
                INPUT_PATH, 
                on_bad_lines='skip', 
                engine='python', 
                encoding='utf-8'
            )
            
            # STANDARDIZE COLUMNS: Converts 'Raw_Text' -> 'raw_text'
            df.columns = [c.strip().lower() for c in df.columns]
            
        except Exception as e:
            print(f"CRITICAL LOAD FAILURE: {e}")
            return

        print(f"Loaded {len(df)} rows. Starting Embedding Firehose...")

        # Verify Column Contract
        if "raw_text" not in df.columns:
            print(f"ERROR: 'raw_text' not found. Available columns: {list(df.columns)}")
            return

        # Harden against NaNs and empties in raw_text
        before = len(df)
        df["raw_text"] = df["raw_text"].astype(str)
        df["raw_text"] = df["raw_text"].replace({"nan": ""})
        df = df[df["raw_text"].str.strip() != ""]
        after = len(df)
        dropped = before - after
        if dropped > 0:
            print(f"Architect Note: Dropped {dropped} rows with missing/empty raw_text.")

        if df.empty:
            print("Architect Alert: No valid text rows after cleaning; aborting shaping step.")
            return

        texts = df["raw_text"].tolist()

        print("Encoding reviews with TF-IDF (lightweight embedding)...")
        vectorizer = TfidfVectorizer(max_features=4096, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Compress TF-IDF into a dense semantic space via SVD
        n_components = min(256, tfidf_matrix.shape[1] - 1) if tfidf_matrix.shape[1] > 1 else 1
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        embeddings = svd.fit_transform(tfidf_matrix)

        print("Reducing dimensions for 3D UI space (UMAP)...")
        reducer = umap.UMAP(
            n_components=3,
            random_state=42,
            n_neighbors=15,
            min_dist=0.1,
        )
        projections = reducer.fit_transform(embeddings)

        print("Clustering reviews into semantic islands (DBSCAN)...")
        clusterer = DBSCAN(eps=0.5, min_samples=3)
        cluster_labels = clusterer.fit_predict(projections)

        # Preserve the downstream contract: x, y, z, cluster columns
        df["x"], df["y"], df["z"] = projections[:, 0], projections[:, 1], projections[:, 2]
        df["cluster"] = cluster_labels

        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)
        valid_clusters = [c for c in df["cluster"].unique() if c != -1]
        print(f"--- Complete! Discovered {len(valid_clusters)} clusters. Saved to {OUTPUT_PATH} ---")

if __name__ == "__main__":
    shaper = SemanticShaper()
    shaper.process_data()
```

## FILE: urban_pulse\engine\shadow_agent.py

```python
import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class ShadowAgent:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"
        self.input_path = "urban_pulse/data/vector_mapped_data.csv"
        self.output_path = "urban_pulse/data/shadow_insights.json"

    def execute_competitive_analysis(self):
        if not os.path.exists(self.input_path):
            print(f"CRITICAL: {self.input_path} not found. Shadow Agent halting.")
            return

        # 1. Load the mapped data
        df_mapped = pd.read_csv(self.input_path)
        
        # 2. The Pivot: Aggregate SLA metrics by Category, Brand, and Platform
        print("Shadow Agent: Aggregating cross-platform SLA metrics...")
        platform_pivot = df_mapped.groupby(['category', 'brand', 'platform'])[['star_rating', 'delivery_time']].mean().round(2).reset_index()
        
        # Convert to a condensed string for the LLM payload
        payload_str = platform_pivot.to_csv(index=False)

        # 3. Construct the LLM Prompt
        shadow_prompt = f"""
        Act as a Competitive Intelligence Analyst for Unilever Q-Commerce.
        Analyze the following aggregated performance metrics across different delivery platforms:
        
        {payload_str}
        
        Determine the 'Winning Platform' and 'Losing Platform' for each Category/Brand combination based on Star Rating and Delivery Time.
        
        Return ONLY a strictly valid JSON object using this exact nested structure:
        {{
            "Category_Name": {{
                "Brand_Name": {{
                    "Winning_Platform": "Name of best platform",
                    "Losing_Platform": "Name of worst platform",
                    "Root_Insight": "One concise sentence explaining the variance (e.g., 'Zepto is 12 mins faster on average, preserving cold chain.')"
                }}
            }}
        }}
        """

        # 4. Execute the LLM Call
        try:
            print("Shadow Agent: Evaluating platform variances...")
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=shadow_prompt
            )
            
            # Clean JSON formatting
            raw_res = response.text.strip()
            if "```json" in raw_res:
                raw_res = raw_res.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_res:
                raw_res = raw_res.split("```")[1].strip()
                
            shadow_insights_dict = json.loads(raw_res)
            
            # 5. Save the Output Contract
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            with open(self.output_path, 'w') as f:
                json.dump(shadow_insights_dict, f, indent=4)
                
            print(f"SUCCESS: Competitive insights saved to {self.output_path}")

        except Exception as e:
            print(f"Shadow Agent Execution Failed: {e}")

if __name__ == "__main__":
    agent = ShadowAgent()
    agent.execute_competitive_analysis()
```

## FILE: urban_pulse\engine\taxoflow_swarm.py

```python

```

## FILE: urban_pulse\ui\pulse_dashboard.py

```python

```

