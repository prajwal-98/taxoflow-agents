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