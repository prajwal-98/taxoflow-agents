import streamlit as st
from ui.styles import hero_block

def render(state):
    st.header("A1: Gatekeeper Validation")
    
    # 1. Extract safe variables with defaults
    is_valid = state.get("A1_is_valid", False)
    routing = state.get("A1_routing_decision", "Pending...")
    checks = state.get("A1_validation_checks", {})
    reasoning = state.get("A1_reasoning", "No trace available.")

    # 2. Use the SAFE variables (no square brackets!)
    hero_block(is_valid, routing)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Validation Checks")
        if not checks:
            st.write("Waiting for agent results...")
        else:
            for check, passed in checks.items():
                status = "PASS" if passed else "FAIL"
                st.write(f"- {check}: {status}")
            
    with col2:
        st.subheader("Decision Logic")
        st.info(f"Routing Pipeline: {routing}")

    # 3. Reasoning Trace
    with st.expander("View Agent Reasoning Trace"):
        st.code(reasoning, language="text")