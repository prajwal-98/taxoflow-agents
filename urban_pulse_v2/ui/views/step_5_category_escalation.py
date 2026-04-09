import streamlit as st

def render(state):
    st.header("A5: Category & Escalation Routing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Category Distribution")
        # Placeholder for category distribution chart
        st.json(state.get("A5_business_categories", {}))
        
    with col2:
        st.subheader("High-Priority Escalations")
        escalations = state.get("A5_escalation_list", [])
        if escalations:
            for item in escalations:
                st.error(f"Priority Alert: {item}")
        else:
            st.success("No high-priority escalations found in current filtered set.")

    with st.expander("View Escalation Logic"):
        st.markdown(f'<div class="reasoning-box">{state["A5_reasoning"]}</div>', unsafe_allow_html=True)
    st.divider()
    if st.button("Continue to Next Step →", type="primary"):
        st.session_state.current_step += 1
        st.rerun()