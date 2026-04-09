import streamlit as st
import pandas as pd
import os
import plotly.express as px
import altair as alt

def render_landing_page():
    """Enhanced landing page with insights + charts"""

    st.title("Urban Pulse Multi-Agent Intelligence")
    st.caption("Transform raw consumer reviews into actionable business intelligence")

    raw_df = st.session_state.raw_df
    is_locked = st.session_state.filters_locked
    run_complete = st.session_state.pipeline_run_complete

    # st.divider()
    # --- SYSTEM DESCRIPTION ---
    with st.expander("ℹ️ About this system", expanded=False):
        st.markdown("""
        **Project Overview:** UrbanPulse is a production-grade, multi-agent AI system that processes Quick Commerce's consumer reviews. Built to demonstrate advanced GenAI orchestration, the application utilizes a directed graph architecture to pass data through multiple specialized LLM agents.

        **Core Capabilities:**

        * **Gatekeeper Validation** <span style="color: #2986cc;">[Pydantic, LLM Guardrails]</span>: Automatically audits incoming raw data for schema consistency and domain relevance before initiating expensive LLM calls.
        
        * **Semantic Mapping** <span style="color: #2986cc;">[Text Embeddings, Dimensionality Reduction]</span>: Converts unstructured text into spatial coordinates to cluster reviews by thematic similarity, completely bypassing rigid keyword matching.
        
        * **Multi-Agent Swarm** <span style="color: #2986cc;">[LangGraph, LLM Orchestration]</span>: Distinct AI personas independently analyze the data to extract targeted insights:
            * *Persona Agent* <span style="color: #2986cc;">[Few-Shot Prompting]</span>: Derives underlying behavioral profiles (e.g., "Late Night Dependent").
            * *Risk Agent* <span style="color: #2986cc;">[Caching, Batching]</span>: Flags severe operational bottlenecks and delivery failures.
            * *Trend Agent* <span style="color: #2986cc;">[Vector Search, Cosine Similarity]</span>: Calculates novelty scores to identify net-new consumer requests versus historic complaints.
            
        * **Stateful Caching (Demo Mode)** <span style="color: #2986cc;">[Object Serialization, Streamlit State]</span>: Implements binary snapshotting (Pickle) to serialize agent intelligence and raw data, allowing for instant, cost-free demonstration of complex LLM inferences.
        """, unsafe_allow_html=True)

    if raw_df is None:
        st.warning("No dataset loaded yet. Upload a CSV to begin.")
        return

    # --- BASIC CLEANING ---
    df = raw_df.copy()

    # Ensure date exists
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    st.markdown("### Data Insights:")

    # --- SMART INSIGHT LINE ---

    if df is not None and not df.empty:

        platform_counts = df['platform'].value_counts()
        category_counts = df['category'].value_counts()

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        trend = df.groupby(df['date'].dt.to_period("M")).size()

        top_platform = platform_counts.idxmax()
        top_category = category_counts.idxmax()
        peak_month = str(trend.idxmax())
        # peak_month = trend.idxmax().strftime("%b %Y")

        category_pct = (category_counts.max() / category_counts.sum()) * 100

        st.info(
            f"{top_category} dominates reviews ({category_pct:.0f}%), "
            f"primarily on {top_platform}, with peak activity in {peak_month}."
        )

    # --- DATA PREPARATION ---
    # Assuming 'df' is your loaded DataFrame
    if 'df' in locals() and not df.empty:
        # 1. Platform Counts for the Bar Chart
        platform_counts = df["platform"].value_counts()

        # 2. Category Counts for the Pie Chart
        category_counts = df["category"].value_counts()

        # 3. Trend for the Line Chart (Monthly)
        # Ensure your date column is in datetime format first
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            # Group by month and count reviews
            trend = df.set_index("date").resample("M").size()
        else:
            trend = pd.Series() # Fallback if no date column
    else:
        # Fallback/Dummy data so the app doesn't crash before upload
        platform_counts = pd.Series({"No Data": 0})
        category_counts = pd.Series({"No Data": 0})
        trend = pd.Series()
        
    platform_counts = df["platform"].value_counts()
    category_counts = df["category"].value_counts()
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        trend = df.set_index("date").resample("M").size()
    else:
        trend = pd.Series()
    
    # --- ROW 1: 2x2 GRID START ---
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        with st.container(border=True):
            st.markdown("**Platform Distribution**")
            # Logic: Shorten labels and plot
            platform_counts_short = platform_counts.copy()
            platform_counts_short.index = [str(x)[:6] for x in platform_counts_short.index]
            df_plot = platform_counts_short.reset_index()
            df_plot.columns = ['Platform', 'Count']

            chart = alt.Chart(df_plot).mark_bar(color='#0068c9').encode(
                x=alt.X('Platform', axis=alt.Axis(labelAngle=0), title=None),
                y=alt.Y('Count', title=None)
            ).properties(height=220) # Slightly shorter to ensure no scroll
            st.altair_chart(chart, use_container_width=True)

    with row1_col2:
        with st.container(border=True):
            st.markdown("**Category Share**")
            pie_df = category_counts.reset_index()
            pie_df.columns = ["Category", "Count"]

            fig_pie = px.pie(pie_df, names="Category", values="Count", hole=0.5)
            fig_pie.update_traces(textinfo="percent", textposition="inside") # inside to save space
            fig_pie.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=220,
                showlegend=True # Legend helps when space is tight
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- ROW 2: TREND & INSIGHTS ---
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        # Use border=True to match the right side
        with st.container(border=True):
            st.markdown("**Review Trend (Monthly)**")
            # Increase height to 285 to match the height of 4 metrics
            st.line_chart(trend, height=285)
            

    with row2_col2:
        with st.container(border=True):
            # 1. Use colored text (:blue[]) and an icon for the header
            st.markdown("### :blue[🎯 Key Insights]")
            # --- COMPACT DIVIDER ---
            st.markdown(
                """<hr style="height:1px; border:none; color:#e6e9ef; background-color:#e6e9ef; margin-top:-10px; margin-bottom:10px;" />""", 
                unsafe_allow_html=True
            )
            # (I removed the divider here to keep the height tight as we discussed)

            # Values (Logic kept exactly as is)
            total_reviews = len(df)
            top_platform = platform_counts.idxmax() if not platform_counts.empty else "N/A"
            top_category = category_counts.idxmax() if not category_counts.empty else "N/A"
            peak_month = trend.idxmax().strftime("%b %Y") if not trend.empty else "N/A"

            # 2. Create 2x2 grid with icons and 'delta' for a splash of color
            c1, c2 = st.columns(2)
            
            # Metric Row 1
            c1.metric(
                label="📊 Total", 
                value=f"{total_reviews:,}", 
                delta="Analyzed", # Adds native green color
                help="Total count of processed reviews."
            )
            c2.metric(
                label="🏆 Top Cat", 
                value=str(top_category)[:10], 
                delta="Winner",
                help="The category with the highest volume."
            )
            
            # Metric Row 2
            c1.metric(
                label="📱 Top Plat", 
                value=str(top_platform)[:10], 
                delta="Primary",
                help="The dominant platform in this dataset."
            )
            c2.metric(
                label="📅 Peak", 
                value=peak_month, 
                delta="High Vol",
                help="The month where activity spiked."
            )

            # --- FOOTER LINE TO CONSUME SPACE ---
            st.markdown(
                "<p style='font-size: 6px; color: #6b7280; margin-top: 5px; opacity: 0.8;'>"
                "<i>This metrics is based on selected data</i></p>", 
                unsafe_allow_html=True
            )

    # --- SAMPLE DATA ---
    st.markdown("### 📄 Sample Dataset")
    st.dataframe(df.head(15), use_container_width=True)

    # --- STATUS MESSAGES ---
    if not is_locked:
        st.info("Configure filters in the sidebar and lock to start the agent pipeline.")
    elif run_complete:
        st.success("Pipeline complete. Explore agent outputs.")
    else:
        st.info("Filters locked. Pipeline will run shortly.")