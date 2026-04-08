import streamlit as st
import plotly.express as px

def render(state):
    st.header("A3: Semantic Mapping (3D)")
    
    coords_df = state.get("A3_vector_coords")
    
    if coords_df is not None:
        fig = px.scatter_3d(
            coords_df, x='x', y='y', z='z',
            title="3D Semantic Review Space",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No vector coordinates found for visualization.")

    with st.expander("View Mathematical Trace"):
        st.markdown(f'<div class="reasoning-box">{state["A3_reasoning"]}</div>', unsafe_allow_html=True)