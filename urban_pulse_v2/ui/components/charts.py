import streamlit as st
import plotly.express as px
import pandas as pd


def render_semantic_map(coords_df, color_by=None):
    if coords_df is None:
        st.warning("No coordinate data available for the semantic map.")
        return

    color_col = color_by if color_by in coords_df.columns else None
    fig = px.scatter(
        coords_df,
        # x='x', y='y',
        color=color_col,
        title="UrbanPulse: 2D Semantic Vector Space",
        labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
        template="plotly_dark",
        opacity=0.8,
        height=600
    )
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(fig, use_container_width=True)


def render_bar_chart(data, x_label="x", y_label="y", title=""):
    if not data:
        st.info("No data available")
        return
    try:
        df = pd.DataFrame(data, columns=[x_label, y_label])
        fig = px.bar(
            df, x=x_label, y=y_label,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=["#00C87E"]
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            height=220,
            title_font=dict(size=13, color="#ffffff"),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#2a2a2a"),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Unable to render chart")


def render_pie_chart(data, names="label", values="value", title=""):
    if not data:
        st.info("No data available")
        return
    try:
        df = pd.DataFrame(data, columns=[names, values])
        fig = px.pie(
            df, names=names, values=values,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            height=220,
            title_font=dict(size=13, color="#ffffff"),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info("Unable to render chart")


def render_line_chart(data, x_label="x", y_label="y", title=""):
    if not data:
        st.info("No data available")
        return
    try:
        df = pd.DataFrame(data, columns=[x_label, y_label])
        fig = px.line(
            df, x=x_label, y=y_label,
            title=title,
            template="plotly_dark",
            color_discrete_sequence=["#00C87E"]
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            height=220,
            title_font=dict(size=13, color="#ffffff"),
            paper_bgcolor="#111111",
            plot_bgcolor="#111111",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#2a2a2a"),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        print("chart error:", e)
        st.info("Unable to render chart")