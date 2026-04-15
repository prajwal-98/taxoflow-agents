# ================================
# FILE: ui/views/step_1_gatekeeper.py
# ================================

import streamlit as st
from ui.components.charts import render_bar_chart, render_pie_chart, render_line_chart


def inject_styles():
    st.markdown("""
    <style>
    .up-wrapper {
        max-width: 1100px;
        margin: auto;
    }

    .up-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 4px;
    }

    .up-subtitle {
        color: #a3a3a3;
        font-size: 0.95rem;
        margin-bottom: 24px;
    }

    .up-status-card {
        border: 1px solid #2a2a2a;
        border-left: 3px solid #00C87E;
        border-radius: 12px;
        padding: 20px 24px;
        background-color: #111111;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 24px;
    }

    .up-status-card.invalid {
        border-left-color: #ef4444;
    }

    .up-status-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 2px solid #00C87E;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00C87E;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .up-status-icon.invalid {
        border-color: #ef4444;
        color: #ef4444;
    }

    .up-status-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: white;
    }

    .up-status-desc {
        font-size: 0.85rem;
        color: #a3a3a3;
        margin-top: 2px;
    }

    .up-metric-card {
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px;
        background-color: #111111;
    }

    .up-metric-label {
        font-size: 0.82rem;
        color: #a3a3a3;
        margin-bottom: 8px;
    }

    .up-metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }

    .up-chart-card {
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px;
        background-color: #111111;
        margin-bottom: 16px;
    }

    .up-chart-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
    }

    .up-quality-card {
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px 24px;
        background-color: #111111;
        margin-bottom: 16px;
    }

    .up-quality-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 16px;
    }

    .up-quality-item {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        color: #e5e5e5;
    }

    .up-quality-icon {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        border: 2px solid #00C87E;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00C87E;
        font-size: 0.7rem;
        flex-shrink: 0;
    }

    .up-quality-icon.fail {
        border-color: #ef4444;
        color: #ef4444;
    }

    .up-continue-btn button {
        background-color: #00C87E !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.75rem !important;
    }

    .up-continue-btn button:hover {
        background-color: #00e08f !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header(is_valid):
    status_icon = "✓" if is_valid else "✕"
    status_title = "Dataset Ready" if is_valid else "Dataset Invalid"
    status_desc = "Your data is valid and ready for analysis" if is_valid else "Please fix dataset issues before continuing"
    invalid_class = "" if is_valid else "invalid"

    st.markdown(f"""
    <div class="up-wrapper">
        <div class="up-title">Step 1 — Data Readiness Check</div>
        <div class="up-subtitle">Validate and understand your dataset before analysis</div>
        <div class="up-status-card {invalid_class}">
            <div class="up-status-icon {invalid_class}">{status_icon}</div>
            <div>
                <div class="up-status-title">{status_title}</div>
                <div class="up-status-desc">{status_desc}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(metrics):
    cols = st.columns(4)
    items = [
        ("Total Reviews", f"{metrics.get('total_reviews') or 0:,}"),
        ("Cities", metrics.get("cities") or 0),
        ("Platforms", metrics.get("platforms") or 0),
        ("Categories", metrics.get("categories") or 0),
    ]

    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div class="up-metric-card">
                <div class="up-metric-label">{label}</div>
                <div class="up-metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)


def render_charts(charts, highlights):
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)

    with r1c1:
        with st.container(border=True):
            render_bar_chart(
                charts.get("platform_distribution") or [],
                x_label="x", y_label="y",
                title="Platform Distribution"
            )

    with r1c2:
        with st.container(border=True):
            render_pie_chart(
                charts.get("category_distribution") or [],
                title="Category Share"
            )

    with r2c1:
        with st.container(border=True):
            render_line_chart(
                charts.get("review_trend") or [],
                x_label="date", y_label="count",
                title="Review Trend"
            )

    with r2c2:
        with st.container(border=True):
            st.markdown("""
            <div style="padding: 8px 4px;">
                <div style="font-size:0.95rem;font-weight:700;color:#ffffff;margin-bottom:14px;">Key Highlights</div>
            """, unsafe_allow_html=True)
            st.markdown(f"- Top Platform: **{highlights.get('top_platform', 'N/A')}**")
            st.markdown(f"- Top Category: **{highlights.get('top_category', 'N/A')}**")
            st.markdown(f"- Peak Month: **{highlights.get('peak_month', 'N/A')}**")
            st.markdown('</div>', unsafe_allow_html=True)


def render_data_quality(quality):
    def icon(flag):
        cls = "up-quality-icon" if flag else "up-quality-icon fail"
        symbol = "✓" if flag else "✕"
        return f'<div class="{cls}">{symbol}</div>'

    st.markdown(f"""
    <div class="up-quality-card">
        <div class="up-quality-title">Data Quality</div>
        <div class="up-quality-item">{icon(quality.get('schema_valid'))} Required columns present</div>
        <div class="up-quality-item">{icon(quality.get('format_valid'))} Data format valid</div>
        <div class="up-quality-item">{icon(quality.get('missing_data_ok'))} No major missing values</div>
    </div>
    """, unsafe_allow_html=True)


def render_sample_data(df):
    with st.expander("Sample Data Preview", expanded=False):
        st.dataframe(df, use_container_width=True)


def render_action():
    st.markdown('<div class="up-continue-btn">', unsafe_allow_html=True)
    if st.button("Continue  →  Context Detection", use_container_width=True):
        st.session_state.current_step = 2
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render(state):
    inject_styles()
    render_header(state.get("A1_is_valid"))
    st.markdown("<br>", unsafe_allow_html=True)
    render_metrics(state.get("A1_metrics", {}))
    st.markdown("<br>", unsafe_allow_html=True)
    render_charts(state.get("A1_charts", {}), state.get("A1_highlights", {}))
    st.markdown("<br>", unsafe_allow_html=True)
    render_data_quality(state.get("A1_data_quality", {}))
    render_sample_data(state.get("A1_sample"))
    st.markdown("<br>", unsafe_allow_html=True)
    render_action()