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