import streamlit as st

def render(state):
    st.header("A4: Cluster Persona Analysis")
    
    stats = state.get("A4_cluster_stats", {})
    
    if stats:
        cols = st.columns(len(stats))
        for i, (cluster_id, data) in enumerate(stats.items()):
            with cols[i]:
                st.metric(label=f"Cluster {cluster_id}", value=f"{data['size']} Reviews")
                st.write(f"Sample: {data['representative_text'][:100]}...")
    
    st.divider()
    with st.expander("View Clustering Reasoning"):
        st.markdown(f'<div class="reasoning-box">{state["A4_reasoning"]}</div>', unsafe_allow_html=True)