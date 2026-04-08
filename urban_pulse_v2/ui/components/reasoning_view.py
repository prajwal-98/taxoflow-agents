import streamlit as st

def render_reasoning_panel(step_name, reasoning_text):
    """
    Renders the monospaced 'Thought Trace' for an agent.
    """
    with st.expander(f"System Trace: {step_name}"):
        st.markdown(f"""
            <div class="reasoning-box">
                {reasoning_text}
            </div>
        """, unsafe_allow_html=True)

def render_status_indicators(checks_dict):
    """
    Renders a simple grid of success/fail indicators.
    """
    cols = st.columns(len(checks_dict))
    for i, (check, status) in enumerate(checks_dict.items()):
        with cols[i]:
            symbol = "PASS" if status else "FAIL"
            color = "#00ff7f" if status else "#ff4b4b"
            st.markdown(f"<p style='color:{color}; font-weight:bold;'>{check}: {symbol}</p>", unsafe_allow_html=True)