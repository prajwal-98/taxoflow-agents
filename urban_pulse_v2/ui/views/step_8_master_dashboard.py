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