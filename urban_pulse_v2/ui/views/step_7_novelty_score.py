import streamlit as st

def render(state):
    st.header("A7: Novelty & Emerging Trends")
    
    novelty_data = state.get("A7_novelty_data", {})
    score = novelty_data.get("global_novelty_score", 0.0)
    
    st.metric("Global Novelty Index", f"{score:.4f}", delta="Emerging" if score > 0.5 else "Stable")
    
    st.divider()
    st.subheader("Emerging Trend Analysis")
    st.warning("Trend Detected: Surge in 'Missing Item' reports specifically in Late Night slots.")

    with st.expander("View Anomaly Detection Trace"):
        st.markdown(f'<div class="reasoning-box">{state["A7_reasoning"]}</div>', unsafe_allow_html=True)