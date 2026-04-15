# ================================
# FILE: ui/views/step_5_category_escalation.py
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
    
    /* Expandable Action Cards */
    details.up-action-card {
        background: #111111;
        border: 1px solid #00C87E;
        border-radius: 10px;
        margin-bottom: 16px;
    }
    details.up-action-card summary {
        padding: 20px 24px 16px 24px;
        cursor: pointer;
        list-style: none; 
        position: relative;
    }
    details.up-action-card summary::-webkit-details-marker { display: none; }
    details.up-action-card summary::after {
        content: '▼';
        position: absolute;
        right: 24px;
        top: 24px;
        color: #737373;
        font-size: 0.8rem;
    }
    details[open].up-action-card summary::after { content: '▲'; }
    
    /* Card Header Elements */
    .up-action-title { 
        font-size: 1.4rem; 
        font-weight: 700; 
        color: #ffffff; 
        margin-bottom: 12px; 
    }
    .up-action-meta-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }
    .up-meta-label { color: #737373; }
    .up-meta-value { color: #e5e5e5; font-weight: 600; }
    
    /* Priority Badges */
    .up-badge-high {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .up-badge-medium {
        background: rgba(245, 158, 11, 0.1);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .up-badge-low {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .up-card-divider {
        border-top: 1px solid #2a2a2a;
        margin: 16px 24px 0 24px;
    }

    /* Card Content Area */
    .up-action-content {
        padding: 20px 24px 24px 24px;
    }
    
    .up-section-head {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
        margin-top: 20px;
    }
    .up-section-head:first-child { margin-top: 0; }
    
    .up-reason-text {
        color: #a3a3a3;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Impact Summary Grid */
    .up-impact-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 12px;
    }
    .up-impact-box {
        background: #151515;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 16px;
    }
    .up-impact-label {
        color: #737373;
        font-size: 0.75rem;
        margin-bottom: 12px;
    }
    .up-impact-val {
        color: #00C87E;
        font-size: 1.1rem;
        font-weight: 700;
    }

    /* Supporting Reviews */
    .up-review-box {
        background: #151515;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 14px 16px;
        margin-top: 8px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        font-size: 0.85rem;
        color: #e5e5e5;
    }
    .up-review-icon {
        color: #737373;
        font-size: 1rem;
        margin-top: 2px;
    }

    /* Explanation Text */
    .up-expander-text { 
        color: #888888; 
        font-size: 0.9rem; 
        line-height: 1.5; 
        padding-top: 6px;
    }

    /* Button Styling */
    .up-continue-btn button {
        background-color: #00C87E !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.65rem !important;
        margin-top: 20px !important;
    }
    .up-continue-btn button:hover {
        background-color: #00e08f !important;
    }
    </style>
    """, unsafe_allow_html=True)


def get_priority_badge(priority):
    p = priority.lower()
    if "high" in p:
        return '<span class="up-badge-high">🔴 High</span>'
    elif "medium" in p:
        return '<span class="up-badge-medium">🟡 Medium</span>'
    else:
        return '<span class="up-badge-low">🟢 Low</span>'


def render(state):
    inject_styles()

    # Extract dynamic data directly from the A5 backend format
    a5_actions = state.get("A5_output", [])

    st.markdown('<div class="up-wrapper">', unsafe_allow_html=True)

    # -------------------------------
    # 1. HEADER
    # -------------------------------
    st.markdown("""
    <div class="up-agent-label">AGENT 5 — CATEGORY & ESCALATION</div>
    <div class="up-title">Step 5 — Business Action Mapping</div>
    <div class="up-subtitle">Convert patterns into actionable decisions</div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 2. ACTION CARDS
    # -------------------------------
    if a5_actions:
        for i, action in enumerate(a5_actions):
            category = action.get("issue_category", "Unknown Category")
            priority = action.get("priority", "Low")
            teams = ", ".join(action.get("escalation_teams", ["General Support"]))
            reason = action.get("reason", "No reason provided.")
            
            impact = action.get("impact", {})
            percent = impact.get("affected_reviews_percent", 0)
            cities = ", ".join(impact.get("cities", [])) if impact.get("cities") else "All"
            platforms = ", ".join(impact.get("platforms", [])) if impact.get("platforms") else "All"
            
            reviews = action.get("supporting_reviews", [])

            badge_html = get_priority_badge(priority)
            
            # Default to open for the first card, closed for the rest
            open_attr = "open" if i == 0 else ""

            # Build Reviews HTML
            reviews_html = ""
            if reviews:
                for rev in reviews:
                    reviews_html += f'<div class="up-review-box"><div class="up-review-icon">ⓘ</div><div>{rev}</div></div>'
            else:
                reviews_html = '<div class="up-reason-text">No supporting reviews available.</div>'

            # TIGHTENED HTML STRING (No blank lines between tags)
            html_block = f"""
            <details class="up-action-card" {open_attr}>
                <summary>
                    <div class="up-action-title">{category}</div>
                    <div class="up-action-meta-row">
                        <span class="up-meta-label">Priority:</span> {badge_html}
                    </div>
                    <div class="up-action-meta-row">
                        <span class="up-meta-label">Escalation Teams:</span> <span class="up-meta-value">{teams}</span>
                    </div>
                </summary>
                <div class="up-card-divider"></div>
                <div class="up-action-content">
                    <div class="up-section-head">Why this matters</div>
                    <div class="up-reason-text">{reason}</div>
                    <div class="up-section-head">Impact Summary</div>
                    <div class="up-impact-grid">
                        <div class="up-impact-box">
                            <div class="up-impact-label">Affected Reviews</div>
                            <div class="up-impact-val">{percent}%</div>
                        </div>
                        <div class="up-impact-box">
                            <div class="up-impact-label">Cities</div>
                            <div class="up-impact-val">{cities}</div>
                        </div>
                        <div class="up-impact-box">
                            <div class="up-impact-label">Platforms</div>
                            <div class="up-impact-val">{platforms}</div>
                        </div>
                    </div>
                    <div class="up-section-head">Supporting Reviews</div>
                    {reviews_html}
                </div>
            </details>
            """
            st.markdown(html_block, unsafe_allow_html=True)
    else:
        st.info("No business actions generated. Please check previous steps or logs.")

    # -------------------------------
    # 3. HOW THIS WORKS
    # -------------------------------
    with st.expander("How this works"):
        st.markdown("""
        <div class="up-expander-text">
        This agent evaluates the grouped patterns from the previous step and maps them to your operational domains. 
        It assesses the scale and severity of each cluster to dynamically assign a priority level and route the 
        issue to the appropriate internal escalation teams.
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------
    # 4. CONTINUE BUTTON
    # -------------------------------
    st.markdown('<div class="up-continue-btn">', unsafe_allow_html=True)
    if st.button("Continue  →  Platform Signal Benchmarking", use_container_width=True):
        st.session_state.current_step = 6
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)