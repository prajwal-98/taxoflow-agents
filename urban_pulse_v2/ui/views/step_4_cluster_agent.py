# ================================
# FILE: ui/views/step_4_cluster_agent.py
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
        color: #00C87E; 
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
        margin: 24px 0 12px 0; 
    }

    /* Top Summary Banner (More Compact) */
    .up-summary-banner {
        background: linear-gradient(145deg, #0a1f16, #111111);
        border: 1px solid rgba(0, 200, 126, 0.2);
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .up-summary-title {
        color: #00C87E;
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0 0 4px 0;
    }
    .up-summary-desc {
        color: #e5e5e5;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Expandable Cluster Cards (Tighter Padding) */
    details.up-cluster-card {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    details.up-cluster-card summary {
        padding: 16px 20px;
        cursor: pointer;
        list-style: none; 
        position: relative;
    }
    details.up-cluster-card summary::-webkit-details-marker { display: none; }
    details.up-cluster-card summary::after {
        content: '▼';
        position: absolute;
        right: 20px;
        top: 24px;
        color: #737373;
        font-size: 0.75rem;
    }
    details[open].up-cluster-card summary::after { content: '▲'; }
    
    .up-cluster-header-title { 
        font-size: 1.2rem; 
        font-weight: 700; 
        color: #ffffff; 
        margin-bottom: 4px; 
        display: flex; 
        align-items: center; 
        gap: 10px; 
    }
    .up-cluster-header-desc { 
        font-size: 0.9rem; 
        color: #a3a3a3; 
        margin-left: 34px;
    }
    
    .up-cluster-stats { 
        display: flex; 
        gap: 32px; 
        margin-top: 16px; 
        margin-left: 34px;
    }
    .up-stat-box { display: flex; flex-direction: column; }
    .up-stat-label { font-size: 0.75rem; color: #737373; margin-bottom: 2px; }
    .up-stat-value { font-size: 1.1rem; font-weight: 700; }
    .up-val-green { color: #00C87E; }
    .up-val-red { color: #ef4444; }
    .up-val-blue { color: #3b82f6; }
    
    .up-cluster-content {
        padding: 0 20px 16px 54px;
        color: #cccccc;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Distribution Cards (Smaller Height and Padding) */
    .up-dist-card {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 20px 16px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    .up-dist-icon { font-size: 1.6rem; margin-bottom: 6px; }
    .up-dist-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .up-dist-value { font-size: 1.8rem; font-weight: 800; color: #00C87E; line-height: 1; }

    /* Key Insight Card (Slimmer) */
    .up-insight-banner {
        background: #111111;
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 16px 24px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin: 28px 0 20px 0;
    }
    .up-insight-icon { color: #00C87E; font-size: 1.2rem; margin-top: 2px; }
    .up-insight-title { color: #ffffff; font-weight: 700; margin-bottom: 4px; font-size: 0.95rem; }
    .up-insight-text { color: #cccccc; font-size: 0.9rem; line-height: 1.5; }
    .up-highlight { color: #00C87E; font-weight: 600; }

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


def get_ui_icon(name):
    name_lower = name.lower()
    if any(w in name_lower for w in ["deliver", "speed", "late", "logistics", "time"]):
        return "🚚"
    elif any(w in name_lower for w in ["product", "item", "quality", "damage", "missing"]):
        return "📦"
    elif any(w in name_lower for w in ["service", "support", "app", "price", "experience"]):
        return "👥"
    return "📌"


def render(state):
    inject_styles()

    a4_output = state.get("A4_output", {})
    summary_text = a4_output.get("summary", "Pattern detection complete")
    clusters = a4_output.get("clusters", [])
    meta_insight = a4_output.get("meta_insight", "Review the clusters for operational bottlenecks.")

    st.markdown('<div class="up-wrapper">', unsafe_allow_html=True)

    # -------------------------------
    # 1. HEADER
    # -------------------------------
    st.markdown("""
    <div class="up-agent-label">AGENT 4 — CLUSTER AGENT</div>
    <div class="up-title">Step 4 — Pattern Detection</div>
    <div class="up-subtitle">Group similar reviews into meaningful patterns</div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 2. TOP BANNER
    # -------------------------------
    st.markdown(f"""
    <div class="up-summary-banner">
        <h2 class="up-summary-title">{summary_text}</h2>
        <p class="up-summary-desc">Across customer feedback analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 3. IDENTIFIED CLUSTERS (Expandable)
    # -------------------------------
    st.markdown('<div class="up-section-heading">Identified Clusters</div>', unsafe_allow_html=True)

    if clusters:
        for cluster in clusters:
            name = cluster.get("name", "Unknown Cluster")
            desc = cluster.get("description", "No description available.")
            size = cluster.get("size", 0)
            trend = cluster.get("trend", "Stable")
            chars = cluster.get("characteristics", {})
            
            icon = get_ui_icon(name)
            trend_class = "up-val-blue"
            if trend == "Increasing":
                trend_class = "up-val-red"
            elif trend == "Decreasing":
                trend_class = "up-val-green"

            chars_html = f"<strong>Product Type:</strong> {chars.get('product_type', 'N/A')}<br>" \
                         f"<strong>Issue Type:</strong> {chars.get('issue_type', 'N/A')}<br>" \
                         f"<strong>Context:</strong> {chars.get('context', 'N/A')}"

            st.markdown(f"""
            <details class="up-cluster-card">
                <summary>
                    <div class="up-cluster-header-title"><span>{icon}</span> {name}</div>
                    <div class="up-cluster-header-desc">{desc}</div>
                    <div class="up-cluster-stats">
                        <div class="up-stat-box">
                            <span class="up-stat-label">Size</span>
                            <span class="up-stat-value up-val-green">{size}%</span>
                        </div>
                        <div class="up-stat-box">
                            <span class="up-stat-label">Trend</span>
                            <span class="up-stat-value {trend_class}">{trend}</span>
                        </div>
                    </div>
                </summary>
                <div class="up-cluster-content">
                    {chars_html}
                </div>
            </details>
            """, unsafe_allow_html=True)
    else:
        st.info("No clusters were generated. Check dataset size or agent logs.")

    # -------------------------------
    # 4. CLUSTER DISTRIBUTION
    # -------------------------------
    if clusters:
        st.markdown('<div class="up-section-heading" style="margin-top: 32px;">Cluster Distribution</div>', unsafe_allow_html=True)
        cols = st.columns(len(clusters))
        for i, col in enumerate(cols):
            with col:
                name = clusters[i].get("name", "Unknown")
                icon = get_ui_icon(name)
                size = clusters[i].get("size", 0)
                
                st.markdown(f"""
                <div class="up-dist-card">
                    <div class="up-dist-icon">{icon}</div>
                    <div class="up-dist-name">{name}</div>
                    <div class="up-dist-value">{size}%</div>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------
    # 5. KEY INSIGHT
    # -------------------------------
    st.markdown(f"""
    <div class="up-insight-banner">
        <div class="up-insight-icon">💡</div>
        <div>
            <div class="up-insight-title">Key Insight</div>
            <div class="up-insight-text">
                {meta_insight}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # 6. HOW THIS AGENT WORKS
    # -------------------------------
    with st.expander("How this agent works"):
        st.markdown("""
        <div class="up-expander-text">
        This agent utilizes a hybrid ML approach. First, it vectorizes reviews using TF-IDF and applies KMeans clustering 
        to group text mathematically. Then, an LLM analyzes the dominant signals in each cluster to generate human-readable 
        names, descriptions, and operational characteristics, while Pandas calculates the temporal trend.
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------
    # 7. CONTINUE BUTTON
    # -------------------------------
    st.markdown('<div class="up-continue-btn">', unsafe_allow_html=True)
    if st.button("Continue  →  Category & Escalation Analysis", use_container_width=True):
        st.session_state.current_step = 5
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)