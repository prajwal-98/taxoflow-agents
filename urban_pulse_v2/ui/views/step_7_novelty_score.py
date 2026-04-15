# ================================
# FILE: ui/views/step_7_language_intelligence.py
# ================================

import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    /* Base Wrapper & Headers */
    .up-wrapper { max-width: 1000px; margin: auto; }
    .up-agent-label { 
        font-size: 0.7rem; 
        font-weight: 700; 
        color: #00C87E; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        margin-bottom: 4px; 
    }
    .up-title { font-size: 2rem; font-weight: 800; color: white; margin-bottom: 4px; }
    .up-subtitle { color: #a3a3a3; font-size: 0.9rem; margin-bottom: 32px; }
    
    /* Section Headings */
    .up-section-heading { 
        font-size: 1.15rem; 
        font-weight: 700; 
        color: white; 
        margin: 28px 0 16px 0; 
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Slang Intelligence Cards (Compact) */
    .up-slang-card {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .up-slang-header-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .up-meta-label { font-size: 0.65rem; color: #737373; margin-bottom: 2px; }
    .up-slang-term { font-size: 1rem; font-weight: 700; color: #00C87E; }
    .up-slang-total { font-size: 1.1rem; font-weight: 700; color: #ffffff; text-align: right; }

    /* Custom Sentiment Bar */
    .up-sentiment-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .up-bar-wrapper {
        flex-grow: 1;
        display: flex;
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
        background: #222222;
        gap: 2px;
    }
    .up-bar-pos { background: #00C87E; }
    .up-bar-neg { background: #ef4444; }
    .up-bar-neu { background: #6b7280; }
    .up-sentiment-numbers {
        font-size: 0.7rem;
        color: #888888;
        white-space: nowrap;
    }

    /* City-wise Grid */
    .up-city-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 12px;
    }
    .up-city-card {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .up-city-name { font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .up-slang-pill {
        background: rgba(0, 200, 126, 0.1);
        border: 1px solid rgba(0, 200, 126, 0.3);
        color: #00C87E;
        font-size: 0.75rem;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Sentiment Mapping Stack */
    .up-mapping-card {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .up-mapping-text { font-size: 0.9rem; font-weight: 700; color: #00C87E; }
    
    .up-badge-Positive { background: rgba(0, 200, 126, 0.1); border: 1px solid #00C87E; color: #00C87E; padding: 2px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;}
    .up-badge-Negative { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; padding: 2px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;}
    .up-badge-Neutral { background: rgba(107, 114, 128, 0.1); border: 1px solid #6b7280; color: #9ca3af; padding: 2px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;}

    /* Emerging Chips */
    .up-emerging-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .up-emerging-chip {
        background: #111111;
        border: 1px solid #2a2a2a;
        padding: 6px 14px;
        border-radius: 8px;
        display: flex;
        align-items: baseline;
        gap: 6px;
    }
    .up-em-slang { color: #00C87E; font-weight: 700; font-size: 0.9rem; }
    .up-em-count { color: #888888; font-size: 0.7rem; }

    /* Explanation Text */
    .up-expander-text { 
        color: #888888; 
        font-size: 0.85rem; 
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
        padding: 0.6rem 1.5rem !important;
    }
    .up-btn-container button:hover {
        background-color: #00e08f !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sentiment_bar(sentiment_dict):
    pos = sentiment_dict.get('positive', 0)
    neg = sentiment_dict.get('negative', 0)
    neu = sentiment_dict.get('neutral', 0)
    total = pos + neg + neu
    
    if total == 0:
        return ""
        
    p_pct = (pos / total) * 100
    n_pct = (neg / total) * 100
    u_pct = (neu / total) * 100
    
    # Flattened HTML to prevent markdown escaping
    return f'<div class="up-meta-label">Sentiment Breakdown</div><div class="up-sentiment-container"><div class="up-bar-wrapper"><div class="up-bar-pos" style="width: {p_pct}%"></div><div class="up-bar-neg" style="width: {n_pct}%"></div><div class="up-bar-neu" style="width: {u_pct}%"></div></div><div class="up-sentiment-numbers">{pos} | {neg} | {neu}</div></div>'


# ================================
# FILE: ui/views/step_7_language_intelligence.py
# ================================

import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    /* Base Wrapper & Headers */
    .up-wrapper { max-width: 1000px; margin: auto; }
    .up-agent-label { 
        font-size: 0.7rem; 
        font-weight: 700; 
        color: #00C87E; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        margin-bottom: 4px; 
    }
    .up-title { font-size: 2rem; font-weight: 800; color: white; margin-bottom: 4px; }
    .up-subtitle { color: #a3a3a3; font-size: 0.9rem; margin-bottom: 32px; }
    
    /* Section Headings */
    .up-section-heading { 
        font-size: 1.15rem; 
        font-weight: 700; 
        color: white; 
        margin: 28px 0 16px 0; 
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Slang Intelligence Cards */
    .up-slang-card {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .up-slang-header-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .up-meta-label { font-size: 0.65rem; color: #737373; margin-bottom: 2px; }
    .up-slang-term { font-size: 1rem; font-weight: 700; color: #00C87E; }
    .up-slang-total { font-size: 1.1rem; font-weight: 700; color: #ffffff; text-align: right; }

    /* Custom Sentiment Bar */
    .up-sentiment-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .up-bar-wrapper {
        flex-grow: 1;
        display: flex;
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
        background: #222222;
        gap: 2px;
    }
    .up-bar-pos { background: #00C87E; }
    .up-bar-neg { background: #ef4444; }
    .up-bar-neu { background: #6b7280; }
    .up-sentiment-numbers {
        font-size: 0.7rem;
        color: #888888;
        white-space: nowrap;
    }

    /* Grid Layout for City and Mapping Cards */
    .up-shared-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 12px;
    }

    .up-grid-card {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100px;
    }

    .up-card-title { font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .up-slang-pill {
        background: rgba(0, 200, 126, 0.1);
        border: 1px solid rgba(0, 200, 126, 0.3);
        color: #00C87E;
        font-size: 0.75rem;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Mapping Specific Text */
    .up-mapping-text { font-size: 0.95rem; font-weight: 700; color: #00C87E; margin-bottom: 8px; }
    
    .up-badge-Positive { background: rgba(0, 200, 126, 0.1); border: 1px solid #00C87E; color: #00C87E; padding: 2px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;}
    .up-badge-Negative { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; padding: 2px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;}
    .up-badge-Neutral { background: rgba(107, 114, 128, 0.1); border: 1px solid #6b7280; color: #9ca3af; padding: 2px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;}

    /* Emerging Chips */
    .up-emerging-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .up-emerging-chip {
        background: #111111;
        border: 1px solid #2a2a2a;
        padding: 6px 14px;
        border-radius: 8px;
        display: flex;
        align-items: baseline;
        gap: 6px;
    }
    .up-em-slang { color: #00C87E; font-weight: 700; font-size: 0.9rem; }
    .up-em-count { color: #888888; font-size: 0.7rem; }

    /* Button Styling */
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
        padding: 0.6rem 1.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sentiment_bar(sentiment_dict):
    pos, neg, neu = sentiment_dict.get('positive', 0), sentiment_dict.get('negative', 0), sentiment_dict.get('neutral', 0)
    total = pos + neg + neu
    if total == 0: return ""
    p_pct, n_pct, u_pct = (pos/total)*100, (neg/total)*100, (neu/total)*100
    return f'<div class="up-meta-label">Sentiment Breakdown</div><div class="up-sentiment-container"><div class="up-bar-wrapper"><div class="up-bar-pos" style="width: {p_pct}%"></div><div class="up-bar-neg" style="width: {n_pct}%"></div><div class="up-bar-neu" style="width: {u_pct}%"></div></div><div class="up-sentiment-numbers">{pos} | {neg} | {neu}</div></div>'


def render(state):
    inject_styles()
    output = state.get("A7_output", {})

    st.markdown('<div class="up-wrapper">', unsafe_allow_html=True)

    # HEADER
    st.markdown("""
    <div class="up-agent-label">AGENT 7 — LANGUAGE INTELLIGENCE</div>
    <div class="up-title">Step 7 — Language Intelligence</div>
    <div class="up-subtitle">Analyze slang and customer expression patterns</div>
    <hr style="border-color:#2a2a2a; margin-bottom: 24px;">
    """, unsafe_allow_html=True)

    # 1. SLANG INTELLIGENCE
    st.markdown('<div class="up-section-heading">Slang Intelligence</div>', unsafe_allow_html=True)
    slang_data = output.get("slang_intelligence", [])
    if not slang_data:
        slang_data = [{"slang": "macha", "total_usage": 45, "sentiment": {"positive": 20, "negative": 15, "neutral": 10}}, {"slang": "bhai", "total_usage": 38, "sentiment": {"positive": 15, "negative": 15, "neutral": 8}}, {"slang": "scene", "total_usage": 32, "sentiment": {"positive": 10, "negative": 18, "neutral": 4}}, {"slang": "dude", "total_usage": 28, "sentiment": {"positive": 16, "negative": 5, "neutral": 7}}, {"slang": "yaar", "total_usage": 24, "sentiment": {"positive": 12, "negative": 4, "neutral": 8}}]

    for item in slang_data:
        st.markdown(f'<div class="up-slang-card"><div class="up-slang-header-row"><div><div class="up-meta-label">Slang Term</div><div class="up-slang-term">{item["slang"]}</div></div><div><div class="up-meta-label" style="text-align: right;">Total Usage</div><div class="up-slang-total">{item["total_usage"]}</div></div></div>{render_sentiment_bar(item["sentiment"])}</div>', unsafe_allow_html=True)

    # 2. CITY-WISE SLANG USAGE (Grid)
    st.markdown('<div class="up-section-heading" style="margin-top: 40px;">City-wise Slang Usage</div>', unsafe_allow_html=True)
    city_slang = output.get("city_slang", [])
    if not city_slang:
        city_slang = [{"city": "Bangalore", "slang": "macha"}, {"city": "Delhi", "slang": "bhai"}, {"city": "Mumbai", "slang": "scene"}, {"city": "Pune", "slang": "yaar"}, {"city": "Hyderabad", "slang": "dude"}]

    grid_html = '<div class="up-shared-grid">'
    for item in city_slang:
        grid_html += f'<div class="up-grid-card"><div class="up-meta-label">City</div><div class="up-card-title">{item["city"]}</div><div class="up-slang-pill">{item["slang"]}</div></div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # 3. SLANG MEANING (Now using the same Grid as City)
    st.markdown('<div class="up-section-heading" style="margin-top: 40px;">Slang Meaning (Sentiment Mapping)</div>', unsafe_allow_html=True)
    sentiment_mapping = output.get("sentiment_mapping", [])
    if not sentiment_mapping:
        sentiment_mapping = [{"slang": "macha", "dominant_sentiment": "Positive"}, {"slang": "bhai", "dominant_sentiment": "Neutral"}, {"slang": "scene", "dominant_sentiment": "Negative"}, {"slang": "dude", "dominant_sentiment": "Positive"}, {"slang": "yaar", "dominant_sentiment": "Neutral"}]

    mapping_grid_html = '<div class="up-shared-grid">'
    for item in sentiment_mapping:
        dom = str(item['dominant_sentiment']).capitalize()
        badge_class = f"up-badge-{dom}" if dom in ["Positive", "Negative", "Neutral"] else "up-badge-Neutral"
        mapping_grid_html += f'<div class="up-grid-card"><div class="up-mapping-text">{item["slang"]} &rarr;</div><div class="{badge_class}">{dom}</div></div>'
    mapping_grid_html += '</div>'
    st.markdown(mapping_grid_html, unsafe_allow_html=True)

    # 4. EMERGING EXPRESSIONS
    st.markdown('<div class="up-section-heading" style="margin-top: 40px;">📈 Emerging Expressions</div>', unsafe_allow_html=True)
    emerging = output.get("emerging_slang", [])
    if not emerging:
        emerging = [{"slang": "lit", "usage": 2}, {"slang": "OP", "usage": 3}, {"slang": "vibe", "usage": 2}, {"slang": "flex", "usage": 4}]

    em_html = '<div class="up-emerging-container">'
    for item in emerging:
        em_html += f'<div class="up-emerging-chip"><span class="up-em-slang">{item["slang"]}</span> <span class="up-em-count">{item["usage"]} usages</span></div>'
    em_html += '</div>'
    st.markdown(em_html, unsafe_allow_html=True)

    # FOOTER
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("How this works"):
        st.markdown('<div style="color: #888; font-size: 0.85rem; line-height: 1.5;">This agent uses regional dictionaries to track local slang and cross-references them with sentiment keyword density to determine context.</div>', unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#2a2a2a; margin-top: 24px;">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        st.markdown('<div class="up-btn-container">', unsafe_allow_html=True)
        if st.button("Continue  →", use_container_width=True):
            st.session_state.current_step = 8 
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# def mark(at the one  "the simulator")