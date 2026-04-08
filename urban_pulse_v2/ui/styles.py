import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
            /* Force Sidebar to be visible and distinct */
            section[data-testid="stSidebar"] {
                background-color: #111 !important;
                min-width: 300px !important;
            }
            /* Fix the 'Ghost Text' visibility */
            .stMarkdown, p, h1, h2, h3, label {
                color: #FFFFFF !important;
            }
            /* Make the sidebar toggle button visible */
            button[kind="header"] {
                background-color: #FF4B4B !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

def hero_block(status: bool, message: str):
    """Renders the Green or Red status block."""
    if status:
        st.markdown(f'<div class="hero-valid">🟢 {message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="hero-invalid">🔴 {message}</div>', unsafe_allow_html=True)

def step_indicator(step_num: int, total_steps: int, step_name: str, subtitle: str):
    """Renders the Step Tracker at the top of the screen."""
    st.markdown(f'''
        <div class="step-header">
            Step <b>{step_num}</b> of {total_steps} — <b>{step_name}</b><br>
            <small style="color:#888">{subtitle}</small>
        </div>
    ''', unsafe_allow_html=True)