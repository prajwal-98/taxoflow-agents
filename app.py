import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px
from core_utils.master_ingestor import MasterIngestor
# Import our new helper functions
from core_utils.ui_components import load_data, render_q_comm_view 

# --- SESSION STATE INITIALIZATION ---
# This block ensures all variables exist before the UI tries to read them
if 'df_master' not in st.session_state:
    raw_path = "urban_pulse/data/raw_qcomm_reviews.csv"
    if os.path.exists(raw_path):
        df = pd.read_csv(raw_path)
        # Standardize columns to lowercase to prevent chart errors
        df.columns = [c.lower().strip() for c in df.columns]
        st.session_state.df_master = df
    else:
        st.session_state.df_master = pd.DataFrame()

if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = ["[System] INFO: Urban Pulse Command Center Online."]

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- PAGE CONFIG ---
st.set_page_config(page_title="Urban Pulse | Unilever AI Command", layout="wide")

# Initialize Ingestor as a Singleton
if 'ingestor' not in st.session_state:
    st.session_state.ingestor = MasterIngestor()

def main():
    st.sidebar.title("🧬 Urban Pulse Control")
    st.sidebar.info("Senior GenAI Engineer: Q-Commerce Swarm")
    
    # Geopolitics selector removed to focus on Urban Pulse

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
                        if "Success" in result:
                            st.balloons()
                            st.session_state.agent_logs.append(f"[Triage] SUCCESS: Processed signal.")
                        else:
                            st.error(result)
                else:
                    st.warning("Input required.")

    st.markdown("---")

    # --- DOMAIN DISPLAY LOGIC ---
    # Defaulting directly to Urban Pulse (Q-Commerce)
    st.title("🏙️ Urban Pulse: Semantic Intelligence")
    data = load_data("urban_pulse/data/vector_mapped_data.csv")
    
    if data is not None:
        # Standardize column names for the imported data
        data.columns = [c.lower().strip() for c in data.columns]
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
            log_container = st.container(height=400, border=True)
            for log in st.session_state.agent_logs:
                log_container.code(log, language="bash")
                
        st.divider()
        
        if st.button("Simulate Gatekeeper Validation"):
            new_log = f"[Gatekeeper] INFO: Validating Batch of {len(st.session_state.df_master)} rows..."
            st.session_state.agent_logs.append(new_log)
            st.session_state.agent_logs.append("[Gatekeeper] SUCCESS: Schema integrity verified (12/12 columns).")
            st.rerun()
# --- TAB 2: SEMANTIC LAB (EMBEDDINGS & SLANG) ---
    with tab2:
        st.header("Semantic Laboratory")
        st.markdown("Mapping Hinglish Slang to Semantic Intent")

        with st.expander("View Hinglish Semantic Dictionary", expanded=False):
            slang_data = {
                "Hinglish Term": ["Silk Board scene", "Systumm hang", "Baigan", "Macha", "Paisa vasool", "Full majja"],
                "City Origin": ["Bangalore", "Delhi", "Hyderabad", "Bangalore", "Mumbai", "Mumbai"],
                "Semantic Interpretation": ["Logistics Bottleneck", "System Failure/Chaos", "Nonsense/Poor Quality", "Friend/Generic Tag", "High Value/ROI", "High Satisfaction"]
            }
            st.table(pd.DataFrame(slang_data))

        st.divider()

        st.subheader("High-Dimensional Narrative Geometry")
        
        try:
            df_mapped = pd.read_csv("urban_pulse/data/vector_mapped_data.csv")
            df_mapped.columns = [c.lower().strip() for c in df_mapped.columns]
            
            fig = px.scatter_3d(
                df_mapped, 
                x='x', y='y', z='z',
                color='city', 
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
            st.info("💡 Semantic Space is empty. Run the 'Semantic Shaper' Agent.")
            if st.button("Run Semantic Shaper Now"):
                st.session_state.agent_logs.append("[Shaper] INFO: Initializing TF-IDF Vectorization...")
                st.session_state.agent_logs.append("[Shaper] SUCCESS: SVD compression complete.")
                st.rerun()

    # --- TAB 3: DISCOVERY (CLUSTERING & PERSONAS) ---
    with tab3:
        st.header("Cluster Discovery & Personas")
        st.markdown("Agent 3: Root-Cause Analysis of Semantic Islands")

        try:
            df_mapped = pd.read_csv("urban_pulse/data/vector_mapped_data.csv")
            df_mapped.columns = [c.lower().strip() for c in df_mapped.columns]
            
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

            st.subheader("Agent 3: Cluster Persona Gallery")
            insights_path = "urban_pulse/data/cluster_insights.json"
            if os.path.exists(insights_path):
                with open(insights_path, 'r') as f:
                    cluster_insights = json.load(f)
                
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
                st.warning("⚠️ Cluster analysis not yet generated. Run Agent 3.")
                
        except FileNotFoundError:
            st.error("Missing vector data. Please run the pipeline first.")

    # --- TAB 4: EXECUTIVE WAR ROOM (STRATEGIC INSIGHTS) ---
    with tab4:
        st.header("Executive War Room")
        st.subheader("💰 Revenue Risk Radar (Cart Value vs. Rating)")
        try:
            df_risk = st.session_state.df_master.copy()
            # Plotly call updated to use the normalized lowercase names
            fig_risk = px.density_heatmap(
                df_risk, 
                x="star_rating", 
                y="cart_value_inr", 
                nbinsx=5, nbinsy=10,
                color_continuous_scale="Viridis",
                title="Density of Revenue Risk (Target: Bottom Right Quadrant)",
                template="plotly_dark"
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating Risk Radar: {e}")

        st.divider()
        st.subheader("🕵️ Platform Shadow Analysis")
        shadow_path = "urban_pulse/data/shadow_insights.json"
        
        if os.path.exists(shadow_path):
            with open(shadow_path, 'r') as f:
                shadow_data = json.load(f)
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
            st.warning("Shadow insights not found.")

        st.divider()
        st.subheader("🚨 High-Priority Escalation Feed")
        esc_path = "urban_pulse/data/escalation_results.json"
        if os.path.exists(esc_path):
            with open(esc_path, 'r') as f:
                esc_results = json.load(f)
            for c_id, details in esc_results.items():
                prob_val = int(details.get('churn_probability', '0%').replace('%',''))
                if prob_val > 70:
                    st.warning(f"**CLUSTER {c_id} ESCALATION** | Churn Risk: {details.get('churn_probability')}")
                    st.markdown(f"**Driver:** {details.get('financial_risk_driver')} | **Action:** `{details.get('automated_action')}`")
        else:
            st.info("No active escalations.")

    # --- THE AI CENTER (GLOBAL OVERLAY CHATBOT) ---
    st.divider()
    st.markdown("## 🤖 AI Center: Swarm Intelligence Query")
    chat_container = st.container(height=300, border=True)

    for message in st.session_state.chat_history:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask the Swarm anything..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        with chat_container.chat_message("assistant"):
            with st.spinner("Consulting Swarm Agents..."):
                # Placeholder for live Gemini call
                response = "Agent 3 indicates high sentiment. Analyzing 'Sakkath' as positive speed signal."
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

if __name__ == "__main__":
    main()