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