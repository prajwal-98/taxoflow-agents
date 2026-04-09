import streamlit as st
import plotly.express as px

def render(state):
    # 1. Update Header to reflect 2D logic
    st.header("A3: Semantic Mapping (2D)")
    
    coords_df = state.get("A3_vector_coords")
    
    if coords_df is not None:
        # FIX: Switched from px.scatter_3d to px.scatter (2D)
        # Removed z='z' to prevent the ValueError
        fig = px.scatter(
            coords_df, 
            x='x', 
            y='y', 
            title="2D Semantic Review Space",
            template="plotly_dark",
            labels={'x': 'Semantic Component 1', 'y': 'Semantic Component 2'}
        )
        
        # UI Polish: Standardize marker look
        fig.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='white')))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No vector coordinates found for visualization.")

    # 2. Mathematical Trace (Using .get for safety)
    reasoning = state.get("A3_reasoning", "No trace available.")
    with st.expander("View Mathematical Trace"):
        st.markdown(f'<div class="reasoning-box">{reasoning}</div>', unsafe_allow_html=True)

    # 3. Sequential Navigation Button
    st.divider()
    if st.button("Continue to Clustering Agent →", type="primary"):
        # Manually incrementing step as per your sequential design
        st.session_state.current_step += 1
        st.rerun()
