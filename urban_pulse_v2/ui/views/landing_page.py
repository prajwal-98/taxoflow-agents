import streamlit as st


def render_landing_page():
    """Clean landing page (UI improved, no logic change)"""

    raw_df = st.session_state.raw_df
    is_locked = st.session_state.filters_locked
    run_complete = st.session_state.pipeline_run_complete

    st.markdown(
        """
<style>
  .up-section { margin-bottom: 3.25rem; }
  .up-section-title {
    font-size: 1.35rem; font-weight: 700; color: #fafafa !important;
    margin: 0 0 1.25rem 0; letter-spacing: -0.02em;
  }
  .up-hero-title {
    text-align: center; font-size: 2.15rem; font-weight: 800; color: #ffffff !important;
    margin: 0 0 0.65rem 0; line-height: 1.15; letter-spacing: -0.03em;
  }
  .up-hero-sub {
    text-align: center; color: #a3a3a3 !important; font-size: 1.05rem; margin: 0 0 0.5rem 0;
    line-height: 1.5;
  }
  .up-hero-hint {
    text-align: center; color: #737373 !important; font-size: 0.9rem; margin: 0 0 2rem 0;
  }
  .up-card {
    background: #111111;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 1.25rem 1.35rem;
    box-sizing: border-box;
  }
  .up-card-feature {
    min-height: 180px;
    height: 100%;
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  [data-testid="stHorizontalBlock"]:has(.up-card-feature) {
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
  }
  [data-testid="stHorizontalBlock"]:has(.up-card-feature) > [data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 !important;
    min-width: 0 !important;
  }
  [data-testid="stHorizontalBlock"]:has(.up-card-feature) > [data-testid="column"] > div {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  .up-card-icon { display: flex; align-items: center; margin-bottom: 0.75rem; }
  .up-card-icon svg { flex-shrink: 0; }
  .up-card-title {
    font-size: 1rem; font-weight: 700; color: #fafafa !important; margin: 0 0 0.4rem 0;
  }
  .up-card-desc { font-size: 0.875rem; color: #a3a3a3 !important; margin: 0; line-height: 1.45; }
  .up-flow {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: stretch;
    gap: 0.5rem;
    justify-content: flex-start;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
  }
  .up-step-card {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.65rem;
    background: #111111;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    box-sizing: border-box;
    width: 172px;
    min-width: 172px;
    max-width: 172px;
    flex: 0 0 172px;
    min-height: 76px;
    height: auto;
    align-self: stretch;
  }
  .up-step-card .up-step-label {
    font-size: 0.88rem; font-weight: 600; color: #f5f5f5 !important; margin: 0; line-height: 1.25;
  }
  .up-flow-arrow {
    color: #e5e5e5 !important;
    font-size: 1.1rem;
    align-self: center;
    flex: 0 0 auto;
    padding: 0 0.15rem;
    user-select: none;
  }
  .up-chips-row {
    display: flex; flex-wrap: wrap; gap: 0.65rem; align-items: center;
  }
  .up-chip {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid #404040;
    border-radius: 9999px;
    padding: 0.55rem 1.1rem;
    font-size: 0.875rem;
    color: #a3a3a3 !important;
  }
  @media (max-width: 900px) {
    .up-flow { flex-wrap: wrap; }
    .up-flow-arrow { display: none; }
    .up-step-card {
      width: 100%;
      min-width: 0;
      max-width: 100%;
      flex: 1 1 140px;
    }
  }
</style>
""",
        unsafe_allow_html=True,
    )

    accent = "#34d399"

    def _svg_wrap(path_d: str, size: int = 22) -> str:
        return f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="{path_d}" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

    # --- HERO ---
    st.markdown(
        f"""
<div class="up-section" style="max-width:1100px;margin-left:auto;margin-right:auto;">
  <h1 class="up-hero-title">Urban Pulse: Multi-Agent Intelligence System</h1>
  <p class="up-hero-sub">Turn customer reviews into actionable business insights using AI-powered agents</p>
  <p class="up-hero-hint">Upload your dataset from the sidebar to begin analysis</p>
</div>
""",
        unsafe_allow_html=True,
    )

    # --- WHAT THIS SYSTEM DOES ---
    st.markdown('<p class="up-section-title">What This System Does</p>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    features = [
        (
            f1,
            "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",
            "Understand Reviews",
            "Extract meaning from raw customer feedback",
        ),
        (
            f2,
            "M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2",
            "Detect Patterns",
            "Group similar issues and behaviors",
        ),
        (
            f3,
            "M9 18h6 M10 22h4 M15 2H9a7 7 0 0 0-7 7c0 1.5.5 3 1.4 4.1L2 22l4.9-1.4A7 7 0 0 0 9 18h0a7 7 0 0 0 7-7V9a7 7 0 0 0-7-7z",
            "Generate Insights",
            "Identify platform, product, and city trends",
        ),
        (
            f4,
            "M5 8l6 6M4 14l6-6 2-3M2 5h12M7 2h1M22 22l-5-10-5 10M14 18h6",
            "Analyze Customer Language",
            "Understand slang and Gen Z expressions",
        ),
    ]
    for col, path, title, desc in features:
        with col:
            st.markdown(
                f"""
<div class="up-card up-card-feature">
  <div class="up-card-icon">{_svg_wrap(path)}</div>
  <p class="up-card-title">{title}</p>
  <p class="up-card-desc">{desc}</p>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="up-section"></div>', unsafe_allow_html=True)

    # --- HOW IT WORKS (horizontal step cards) ---
    st.markdown('<p class="up-section-title">How It Works</p>', unsafe_allow_html=True)
    steps = [
        ("M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12", "Upload Data"),
        ("M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4L12 14.01l-3-3", "Data Validation"),
        ("M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z", "Context Understanding"),
        ("M3 7V5a2 2 0 0 1 2-2h2M21 7V5a2 2 0 0 0-2-2h-2M3 17v2a2 2 0 0 0 2 2h2M21 17v2a2 2 0 0 1-2 2h-2M7 12h10", "Pattern Detection"),
        ("M3 3v18h18M7 16l4-4 4 4 4-8", "Business Insights"),
        ("M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936a2 2 0 0 0 1.437-1.437l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5a2 2 0 0 0 1.437 1.437l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0L9.937 15.5z", "Language Intelligence"),
        ("M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z", "Final Dashboard"),
    ]
    def _flow_html(step_slice, *, last):
        parts: list[str] = []
        for i, (path, label) in enumerate(step_slice):
            parts.append(
                f"""<div class="up-step-card"><div class="up-card-icon" style="margin-bottom:0;">{_svg_wrap(path, 20)}</div><p class="up-step-label">{label}</p></div>"""
            )
            if i < len(step_slice) - 1:
                parts.append('<span class="up-flow-arrow">→</span>')
        margin = "0.75rem auto 3.25rem auto" if last else "0 auto 0 auto"
        return f'<div class="up-flow" style="margin:{margin};">{"".join(parts)}</div>'

    st.markdown(_flow_html(steps[:5], last=False), unsafe_allow_html=True)
    st.markdown(_flow_html(steps[5:], last=True), unsafe_allow_html=True)

    # --- WHAT YOU CAN EXPLORE (2x2 cards) ---
    st.markdown('<p class="up-section-title">What You Can Explore</p>', unsafe_allow_html=True)
    r1a, r1b = st.columns(2)
    r2a, r2b = st.columns(2)
    explore = [
        (r1a, "Compare Zepto vs Blinkit performance"),
        (r1b, "Analyze product issues (Magnum, Lays, Dove)"),
        (r2a, "Explore city-specific trends"),
        (r2b, "Understand customer language patterns"),
    ]
    for col, text in explore:
        with col:
            st.markdown(
                f"""
<div class="up-card" style="margin-bottom:1rem;">
  <div class="up-card-icon"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{accent};"></span></div>
  <p class="up-card-desc" style="color:#e5e5e5 !important;font-size:0.95rem;">{text}</p>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="up-section"></div>', unsafe_allow_html=True)

    # --- TRY ASKING (chips) ---
#     st.markdown('<p class="up-section-title">Try Asking</p>', unsafe_allow_html=True)
#     st.markdown(
#         f"""
# <div class="up-chips-row" style="margin-bottom:2.5rem;">
#   <span class="up-chip">Mumbai monsoon insights</span>
#   <span class="up-chip">Ice cream issues</span>
#   <span class="up-chip">Compare Bangalore vs Delhi slang</span>
# </div>
# """,
#         unsafe_allow_html=True,
#     )

    # --- STATUS (unchanged logic) ---
    if raw_df is None:
        st.warning("No dataset loaded yet. Upload a CSV to begin.")
        return

    if not is_locked:
        st.info("Configure filters in the sidebar and lock to start the pipeline.")
    elif run_complete:
        st.success("Pipeline complete. Explore results.")
    else:
        st.info("Filters locked. Pipeline will run shortly.")
