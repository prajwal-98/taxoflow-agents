# ================================
# FILE: ui/views/step_3_semantic_shaper.py
# ================================

import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    /* Base Wrapper & Headers */
    .up-wrapper { max-width: 1100px; margin: auto; }
    .up-agent-label { 
        font-size: 0.8rem; 
        font-weight: 700; 
        color: #737373; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        margin-bottom: 8px; 
    }
    .up-title { font-size: 2.4rem; font-weight: 800; color: white; margin-bottom: 8px; }
    .up-subtitle { color: #a3a3a3; font-size: 1.05rem; margin-bottom: 24px; }
    .up-divider { border-top: 1px solid #2a2a2a; margin-top: 8px; margin-bottom: 32px; }
    
    /* Section Labels */
    .up-section-label { 
        font-size: 0.75rem; 
        font-weight: 700; 
        color: #737373; 
        text-transform: uppercase; 
        letter-spacing: 0.08em; 
        margin-bottom: 12px; 
        margin-top: 24px; 
    }
    
    /* Review Cards */
    .up-card { 
        border: 1px solid #2a2a2a; 
        border-radius: 10px; 
        padding: 20px 24px; 
        margin-bottom: 12px; 
    }
    .up-card-selected { 
        background-color: #151515; 
        font-size: 1.15rem; 
        font-weight: 600; 
        color: #ffffff; 
    }
    .up-card-similar { 
        background-color: #0d0d0d; 
        font-size: 1rem; 
        color: #cccccc; 
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .up-similarity-score {
        font-size: 0.85rem;
        color: #00C87E;
        font-weight: 600;
        background: rgba(0, 200, 126, 0.1);
        padding: 4px 8px;
        border-radius: 6px;
    }
    
    /* Semantic Theme Card */
    .up-theme-card { 
        background-color: #111111; 
        border-top: 1px solid #2a2a2a; 
        border-right: 1px solid #2a2a2a; 
        border-bottom: 1px solid #2a2a2a; 
        border-left: 4px solid #00C87E; 
        padding: 24px 28px; 
        border-radius: 12px; 
    }
    .up-pattern-label { 
        font-size: 0.75rem; 
        font-weight: 700; 
        color: #a3a3a3; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        margin-bottom: 8px; 
    }
    .up-pattern-value { 
        font-size: 2rem; 
        font-weight: 700; 
        color: #ffffff; 
    }

    /* Explanation Text */
    .up-expander-text { 
        color: #888888; 
        font-size: 0.95rem; 
        line-height: 1.6; 
        padding-top: 8px;
    }

    /* Button Styling */
    .up-continue-btn button {
        background-color: #00C87E !important;
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.75rem !important;
        margin-top: 24px !important;
    }
    .up-continue-btn button:hover {
        background-color: #00e08f !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render(state):
    inject_styles()

    # --- DYNAMIC DATA EXTRACTION ---
    # Pulling directly from the output of agents/A3_semantic_shaper.py
    a3_data = state.get("A3_output", {})
    
    selected_review = a3_data.get("anchor_review", "No anchor review identified.")
    similar_reviews_data = a3_data.get("similar_reviews", [])
    identified_pattern = a3_data.get("semantic_theme", "No pattern detected.")

    st.markdown('<div class="up-wrapper">', unsafe_allow_html=True)

    # -------------------------------
    # 1. HEADER
    # -------------------------------
    st.markdown("""
    <div class="up-agent-label">AGENT 3 — SEMANTIC SHAPER</div>
    <div class="up-title">Step 3 — Similarity Mapping</div>
    <div class="up-subtitle">Identify similar behavior patterns in customer feedback</div>
    <div class="up-divider"></div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 2. SELECTED REVIEW (ANCHOR)
    # -------------------------------
    st.markdown('<div class="up-section-label">SELECTED REVIEW</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="up-card up-card-selected">{selected_review}</div>', unsafe_allow_html=True)

    # -------------------------------
    # 3. SIMILAR REVIEWS
    # -------------------------------
    st.markdown('<div class="up-section-label">SIMILAR REVIEWS</div>', unsafe_allow_html=True)
    
    if similar_reviews_data:
        for item in similar_reviews_data:
            text = item.get("text", "")
            score = item.get("score", 0.0)
            
            # Rendering text alongside the cosine similarity score
            st.markdown(f"""
            <div class="up-card up-card-similar">
                <span>{text}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="up-card up-card-similar" style="color: #666;">No similar reviews detected above the threshold.</div>', unsafe_allow_html=True)

    # -------------------------------
    # 4. SEMANTIC THEME
    # -------------------------------
    st.markdown('<div class="up-section-label">SEMANTIC THEME</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="up-theme-card">
        <div class="up-pattern-label">IDENTIFIED PATTERN</div>
        <div class="up-pattern-value">{identified_pattern}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------
    # 5. HOW THIS WORKS (Expander)
    # -------------------------------
    with st.expander("How this works"):
        st.markdown("""
        <div class="up-expander-text">
        This agent converts each review into a semantic representation (TF-IDF vector). It then calculates the cosine similarity 
        to find reviews with similar meaning and groups them together. Finally, a hybrid rule-based and LLM system extracts the core theme.
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------
    # 6. CONTINUE BUTTON
    # -------------------------------
    st.markdown('<div class="up-continue-btn">', unsafe_allow_html=True)
    if st.button("Continue  →  Step 4", use_container_width=True):
        st.session_state.current_step = 4
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)