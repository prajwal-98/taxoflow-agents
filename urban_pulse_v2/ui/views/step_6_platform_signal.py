# ================================
# FILE: ui/views/step_6_platform_signal.py
# ================================

import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    /* Base Wrapper & Headers */
    .up-wrapper { max-width: 1100px; margin: auto; }
    .up-agent-label { 
        font-size: 0.75rem; 
        font-weight: 700; 
        color: #737373; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        margin-bottom: 6px; 
    }
    .up-title { font-size: 2.1rem; font-weight: 800; color: white; margin-bottom: 6px; }
    .up-subtitle { color: #a3a3a3; font-size: 0.95rem; margin-bottom: 24px; }
    
    /* Section Headings */
    .up-section-heading { 
        font-size: 1.25rem; 
        font-weight: 700; 
        color: white; 
        margin: 32px 0 16px 0; 
    }

    /* List Cards (Platform, Brand, Category, City) */
    .up-list-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #111111;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }
    .up-list-card.highlight {
        border: 1px solid #00C87E;
    }
    .up-list-card.standard {
        border: 1px solid #2a2a2a;
    }
    .up-list-title {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
    }
    .up-list-value {
        font-size: 1rem;
        font-weight: 700;
    }
    .up-list-value.highlight { color: #00C87E; }
    .up-list-value.standard { color: #a3a3a3; }

    /* Insight Subtext */
    .up-insight-subtext {
        font-size: 0.8rem;
        color: #737373;
        margin-top: -2px;
        margin-bottom: 24px;
    }

    /* Time Insight Card */
    .up-time-card {
        background: #111111;
        border: 1px solid #00C87E;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 10px;
    }
    .up-time-label {
        font-size: 0.8rem;
        color: #737373;
        margin-bottom: 8px;
    }
    .up-time-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00C87E;
        line-height: 1;
    }
    .up-time-desc {
        font-size: 0.85rem;
        color: #a3a3a3;
        margin-top: 16px;
    }

    /* Dominant Issue Card */
    .up-dom-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #111111;
        border: 1px solid #00C87E;
        border-radius: 10px;
        padding: 20px 24px;
    }
    .up-dom-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #00C87E;
    }
    .up-dom-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #00C87E;
    }

    /* Explanation Text */
    .up-expander-text { 
        color: #888888; 
        font-size: 0.9rem; 
        line-height: 1.5; 
        padding-top: 6px;
    }

    /* Button Styling (Right-Aligned) */
    .up-btn-container {
        display: flex;
        justify-content: flex-end;
        margin-top: 24px;
    }
    .up-btn-container button {
        background-color: #00C87E !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.65rem 1.5rem !important;
    }
    .up-btn-container button:hover {
        background-color: #00e08f !important;
    }
    </style>
    """, unsafe_allow_html=True)


def build_list_card(title, value, is_top=False):
    card_class = "highlight" if is_top else "standard"
    return f"""
    <div class="up-list-card {card_class}">
        <div class="up-list-title">{title}</div>
        <div class="up-list-value {card_class}">{value}</div>
    </div>
    """


def render(state):
    inject_styles()

    # --- EXTRACT PRE-CALCULATED DATA FROM BACKEND ---
    a6_output = state.get("A6_output", {})

    if not a6_output:
        st.warning("No data available for Signal Analysis.")
        if st.button("Go Back"):
            st.session_state.current_step = 5
            st.rerun()
        return

    # 1. Platforms
    platform_data = [(p.get("platform"), f"{p.get('share')}%") for p in a6_output.get("platform", [])]

    # 2. Brands
    brand_data = [(b.get("name"), f"{b.get('mentions')} mentions") for b in a6_output.get("brand", [])]

    # 3. Categories
    category_data = [(c.get("name"), f"{c.get('mentions')} mentions") for c in a6_output.get("category", [])]

    # 4. Cities
    city_data = [(c.get("city"), f"{c.get('mentions')} reviews") for c in a6_output.get("city", [])]

    # 5. Time
    time_info = a6_output.get("time", {})
    peak_hour = time_info.get("peak_hour")
    time_desc = time_info.get("insight", "Customer activity and complaints peak during evening hours")
    
    if peak_hour is not None:
        ampm = "AM" if peak_hour < 12 else "PM"
        display_hour = peak_hour if peak_hour <= 12 else peak_hour - 12
        display_hour = 12 if display_hour == 0 else display_hour
        peak_hour_str = f"{display_hour} {ampm}"
    else:
        peak_hour_str = "N/A"
        time_desc = "No time data available in current scope."

    # 6. Dominant Issue (Sourced from Agent 4's Clusters)
    dominant_issue = "General Feedback"
    clusters = state.get("A4_output", {}).get("clusters", [])
    if clusters:
        dominant_issue = clusters[0].get("name", "Delivery Issues")

    # --- UI RENDERING ---
    st.markdown('<div class="up-wrapper">', unsafe_allow_html=True)

    # HEADER
    st.markdown("""
    <div class="up-agent-label">AGENT 6 — SIGNAL AGENT</div>
    <div class="up-title">Step 6 — Business Insights</div>
    <div class="up-subtitle">Analyze patterns across platform, city, brand, and time</div>
    """, unsafe_allow_html=True)

    # PLATFORM INSIGHT
    if platform_data:
        st.markdown('<div class="up-section-heading">Platform Insight</div>', unsafe_allow_html=True)
        for i, (plat, val) in enumerate(platform_data):
            st.markdown(build_list_card(plat, val, is_top=(i==0)), unsafe_allow_html=True)
        
        if len(platform_data) >= 2:
            top_plat = platform_data[0][0]
            second_plat = platform_data[1][0]
            st.markdown(f'<div class="up-insight-subtext">{top_plat} shows higher complaint share compared to {second_plat}</div>', unsafe_allow_html=True)

    # BRAND INSIGHT
    if brand_data:
        st.markdown('<div class="up-section-heading">Brand Insight</div>', unsafe_allow_html=True)
        for i, (brand, val) in enumerate(brand_data):
            st.markdown(build_list_card(brand, val, is_top=(i==0)), unsafe_allow_html=True)

    # CATEGORY INSIGHT
    if category_data:
        st.markdown('<div class="up-section-heading">Category Insight</div>', unsafe_allow_html=True)
        for i, (cat, val) in enumerate(category_data):
            st.markdown(build_list_card(cat, val, is_top=(i==0)), unsafe_allow_html=True)

    # CITY INSIGHT
    if city_data:
        st.markdown('<div class="up-section-heading">City Insight</div>', unsafe_allow_html=True)
        for i, (city, val) in enumerate(city_data):
            st.markdown(build_list_card(city, val, is_top=(i==0)), unsafe_allow_html=True)

    # TIME INSIGHT
    st.markdown('<div class="up-section-heading">Time Insight</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="up-time-card">
        <div class="up-time-label">Peak Hour</div>
        <div class="up-time-value">{peak_hour_str}</div>
        <div class="up-time-desc">{time_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    # DOMINANT ISSUE
    st.markdown('<div class="up-section-heading">Dominant Issue</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="up-dom-card">
        <div class="up-dom-title">{dominant_issue}</div>
        <div class="up-dom-dot"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # HOW THIS WORKS
    with st.expander("How this works"):
        st.markdown("""
        <div class="up-expander-text">
        This agent acts as a competitive and operational intelligence tracker. It receives pre-calculated real-time distributions 
        across critical business dimensions (Platforms, Geographies, Brands, Categories, and Temporal patterns) to map where systemic 
        issues are heavily concentrated.
        </div>
        """, unsafe_allow_html=True)

    # CONTINUE BUTTON
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        st.markdown('<div class="up-continue-btn">', unsafe_allow_html=True)
        if st.button("Continue  →  Novelty Score Agent", use_container_width=True):
            st.session_state.current_step = 7
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)