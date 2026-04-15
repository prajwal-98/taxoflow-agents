# ================================
# FILE: ui/views/step_2_context_detector.py
# ================================

import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    /* Base Wrapper & Headers (From Step 1) */
    .up-wrapper { max-width: 1100px; margin: auto; }
    .up-title { font-size: 2rem; font-weight: 700; color: white; margin-bottom: 4px; }
    .up-subtitle { color: #a3a3a3; font-size: 0.95rem; margin-bottom: 24px; }

    /* Button Styling (Identical to Step 1) */
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

    /* Primary Insight Card */
    .up-insight-card {
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 24px 32px;
        background-color: #151515;
        margin-bottom: 24px;
    }
    .up-insight-header {
        color: #00C87E;
        font-size: 1rem;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .up-insight-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 16px;
    }
    .up-insight-desc {
        font-size: 1.05rem;
        color: #cccccc;
        line-height: 1.6;
        margin: 0;
    }

    /* Quick Stats Row */
    .up-stat-block { margin-bottom: 32px; }
    .up-stat-label { font-size: 1.05rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .up-stat-val { font-size: 1rem; color: #ffffff; margin-left: 28px; }

    /* Section Headings */
    .up-section-heading { 
        font-size: 1.8rem; 
        font-weight: 700; 
        color: white; 
        margin: 40px 0 20px 0; 
    }

    /* Slang Tags */
    .up-tag {
        border: 1px solid #00C87E;
        color: #ffffff;
        padding: 8px 24px;
        border-radius: 30px;
        margin-right: 12px;
        margin-bottom: 12px;
        display: inline-block;
        font-size: 0.95rem;
        background: transparent;
    }

    /* Theme Progress Bars */
    .up-theme-row { margin-bottom: 24px; }
    .up-theme-labels { 
        display: flex; 
        justify-content: space-between; 
        color: #ffffff; 
        font-size: 1.05rem; 
        margin-bottom: 10px; 
    }
    .up-theme-track { 
        background-color: #2a2a2a; 
        height: 6px; 
        border-radius: 10px; 
        width: 100%; 
    }
    .up-theme-fill { 
        background-color: #00C87E; 
        height: 6px; 
        border-radius: 10px; 
    }

    /* Paragraph Text */
    .up-attention-text { 
        color: #cccccc; 
        font-size: 1.05rem; 
        line-height: 1.6; 
    }
    </style>
    """, unsafe_allow_html=True)


def render(state):

    inject_styles()

    # Extract Data Safely
    data = state.get("A2_output", {})

    sentiment = data.get("localized_sentiment", "")
    slang = data.get("slang_detected", [])
    themes = data.get("top_themes", [])
    context = data.get("operational_context", "")
    city = (state.get("active_filters", {}).get("city") or ["Bangalore"])[0]

    # Format Sentiment Label
    sentiment_label = "Mixed"
    if "positive" in sentiment.lower():
        sentiment_label = "Positive"
    elif "negative" in sentiment.lower():
        sentiment_label = "Negative"

    top_issue = themes[0] if themes else "N/A"

    # -------------------------------
    # 1. HEADER (Added Agent Name)
    # -------------------------------
    st.markdown('<div class="up-wrapper">', unsafe_allow_html=True)

    st.markdown("""
    <div class="up-title">Step 2 — Context Detection</div>
    <div class="up-subtitle">Analyze localized sentiment, slang, and operational context</div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 2. INSIGHT BANNER
    # -------------------------------
    st.markdown(f"""
    <div class="up-insight-card">
        <div class="up-insight-header">🔥 {city} Insight</div>
        <div class="up-insight-title">{sentiment_label} Sentiment Detected</div>
        <p class="up-insight-desc">{sentiment}</p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 3. STATS ROW
    # -------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f'<div class="up-stat-block"><div class="up-stat-label">📍 City</div><div class="up-stat-val">{city}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="up-stat-block"><div class="up-stat-label">🙂 Sentiment</div><div class="up-stat-val">{sentiment_label}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="up-stat-block"><div class="up-stat-label">⚠️ Risk</div><div class="up-stat-val">Medium</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="up-stat-block"><div class="up-stat-label">🚚 Top Issue</div><div class="up-stat-val">{top_issue}</div></div>', unsafe_allow_html=True)

    # -------------------------------
    # 4. SLANG SIGNALS (Stacked)
    # -------------------------------
    st.markdown('<div class="up-section-heading" style="margin-top: 10px;">Slang Signals</div>', unsafe_allow_html=True)
    
    if slang:
        tags_html = "".join([f'<span class="up-tag">{s}</span>' for s in slang])
        st.markdown(tags_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="up-attention-text">No localized slang detected in current segment.</div>', unsafe_allow_html=True)

    # -------------------------------
    # 5. TOP THEMES (Stacked)
    # -------------------------------
    st.markdown('<div class="up-section-heading">Top Themes</div>', unsafe_allow_html=True)
    
    if themes:
        themes_html = ""
        for i, t in enumerate(themes):
            # Dynamic percentage scaling to match UI design (80%, 60%, 40%, etc.)
            percent = max(20, 100 - (i * 20) - 20) 

            themes_html += f"""
            <div class="up-theme-row">
                <div class="up-theme-labels">
                    <span>{t}</span>
                    <span>{percent}%</span>
                </div>
                <div class="up-theme-track">
                    <div class="up-theme-fill" style="width: {percent}%;"></div>
                </div>
            </div>
            """
        st.markdown(themes_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="up-attention-text">No dominant themes identified.</div>', unsafe_allow_html=True)

    # -------------------------------
    # 6. WHAT NEEDS ATTENTION (Stacked)
    # -------------------------------
    st.markdown('<div class="up-section-heading">What Needs Attention</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="up-attention-text">{context if context else "No critical context flags available."}</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # -------------------------------
    # 7. CONTINUE BUTTON (Gatekeeper Style)
    # -------------------------------
    st.markdown('<div class="up-continue-btn">', unsafe_allow_html=True)
    if st.button("Continue  →  Step 3", use_container_width=True):
        st.session_state.current_step = 3
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)