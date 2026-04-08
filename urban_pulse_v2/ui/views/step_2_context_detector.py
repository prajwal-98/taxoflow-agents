import streamlit as st

def render(state):
    st.header("Step 2: Hyper-Local Context Detection")
    
    # Extract data from Agent 2's output in the state
    signals = state.get("A2_context_signals", [])
    slang_data = state.get("A2_slang_map", {})
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Localized Parameters")
        st.write(f"**Target City:** {slang_data.get('city', 'N/A')}")
        st.write("**Slang Dictionary Applied:**")
        st.json(slang_data.get('signals', []))
        
    with col2:
        st.subheader("Agentic Analysis")
        if signals:
            st.write(signals[0].get("signal_analysis", "No analysis generated."))
        else:
            st.warning("No contextual signals detected for this batch.")

    st.subheader("Agent Reasoning Trace")
    st.code(state.get("A2_reasoning", "No trace available."), language="text")