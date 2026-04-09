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