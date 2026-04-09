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

    st.markdown("---") # Visual separator line

    #  Agent 1 has actually finished its job
    if state.get("A1_is_valid") is True:
        col1, col2 = st.columns([3, 1]) 

        with col1:
            st.success("✅ Step 1 Complete. Data is ready for Context Detection.")
            
        with col2:
            # We change the step from 1 to 2
            st.divider()
            if st.button("Continue to Next Step →", type="primary"):
                st.session_state.current_step += 1
                st.rerun()
    else:
        # If the agent hasn't run or failed, show a disabled button or a hint
        st.info("Waiting for Gatekeeper validation to complete...")
        st.button("Continue to Next Agent →", disabled=True)