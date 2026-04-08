import streamlit as st
import plotly.express as px
import pandas as pd

def render_semantic_map(coords_df, color_by=None):
    """
    Renders the 2D Scatter plot for semantic review space.
    """
    if coords_df is None:
        st.warning("No coordinate data available for the semantic map.")
        return

    color_col = color_by if color_by in coords_df.columns else None
    
    # CHANGED: px.scatter instead of px.scatter_3d
    fig = px.scatter(
        coords_df, 
        x='x', y='y',
        color=color_col,
        title="UrbanPulse: 2D Semantic Vector Space",
        labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
        template="plotly_dark",
        opacity=0.8,
        height=600
    )

    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(fig, use_container_width=True)