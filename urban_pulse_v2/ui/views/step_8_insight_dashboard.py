# ================================
# FILE: ui/views/step_8_insight_dashboard.py
# ================================

import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
        /* ─── Global Reset (Scoped to Step 8) ─────────────────────────────── */
        * { font-family: 'Inter', 'Segoe UI', sans-serif; }

        /* ─── Selectbox overrides ─────────────────────────────────── */
        .stSelectbox > div > div {
            background-color: #1a1a1a !important; border: 1px solid #333333 !important;
            border-radius: 8px !important; color: #e5e5e5 !important;
        }
        .stSelectbox label { color: #9ca3af !important; font-size: 0.75rem !important; }

        /* ─── Text Input overrides ────────────────────────────────── */
        .stTextInput > div > div > input {
            background-color: #1a1a1a !important; border: 1px solid #333333 !important;
            border-radius: 10px !important; color: #ffffff !important;
            padding: 0.75rem 1rem !important; font-size: 0.95rem !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #10b981 !important; box-shadow: 0 0 0 2px rgba(16,185,129,0.15) !important;
        }

        /* ─── Progress bar overrides ──────────────────────────────── */
        .stProgress > div > div > div > div { background-color: #10b981 !important; }
        .stProgress > div > div { background-color: #222222 !important; border-radius: 99px !important; }

        /* ─── Button overrides ────────────────────────────────────── */
        .stButton > button {
            background-color: #1a1a1a !important; border: 1px solid #333333 !important;
            border-radius: 8px !important; color: #9ca3af !important; font-size: 0.8rem !important;
            padding: 0.4rem 1.2rem !important; transition: all 0.2s ease;
        }
        .stButton > button:hover { border-color: #10b981 !important; color: #10b981 !important; }
    </style>
    """, unsafe_allow_html=True)


def render(state):
    inject_styles()
    
    a8 = state.get("A8_output", {})
    if not a8 or "error" in a8:
        st.warning("Dashboard generation failed. Missing data.")
        return

    # Extract dynamic data strictly from backend schema
    story = a8.get("story", "Analysis complete.")
    conf = a8.get("confidence", 87)
    drivers = a8.get("drivers", [])
    metrics = a8.get("metrics", {})
    impact = a8.get("impact", {})
    breakdown = a8.get("breakdown", {})
    actions = a8.get("actions", [])
    evidence = a8.get("evidence", [])
    language = a8.get("language", [])
    root_cause = a8.get("root_cause", "No distinct root cause identified.")

    # ════════════════════════════════════════════════════
    #  1. HEADER & FILTER BAR
    # ════════════════════════════════════════════════════
    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:space-between; padding: 0.5rem 0 1.5rem 0; border-bottom: 1px solid #222222; margin-bottom: 2rem;">
        <div>
            <div style="display:flex; align-items:center; gap: 10px; margin-bottom: 6px;">
                <div style="width:8px; height:8px; border-radius:50%; background:#10b981; box-shadow: 0 0 8px #10b981;"></div>
                <span style="font-size:0.75rem; color:#10b981; letter-spacing:0.12em; text-transform:uppercase; font-weight:600;">UrbanPulse · Live</span>
            </div>
            <h1 style="font-size:2rem; font-weight:700; color:#ffffff; margin:0; letter-spacing:-0.02em;">Intelligence Dashboard</h1>
            <p style="color:#6b7280; margin:4px 0 0 0; font-size:0.9rem; font-weight:400;">Explore insights and make decisions</p>
        </div>
        <div style="display:flex; gap:12px; align-items:center;">
            <div style="background:#1a1a1a; border:1px solid #333333; border-radius:8px; padding: 6px 14px; font-size:0.75rem; color:#6b7280;">Last synced: Just now</div>
            <div style="background:#10b981; border-radius:8px; padding: 6px 18px; font-size:0.78rem; font-weight:600; color:#000000; cursor:pointer;">Export Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.72rem; color:#6b7280; letter-spacing:0.1em; text-transform:uppercase; font-weight:600; margin-bottom:10px;">FILTERS</p>', unsafe_allow_html=True)
    f1, f2, f3, f4, f5, f6 = st.columns(6)
    with f1: st.selectbox("City", ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad"])
    with f2: st.selectbox("Platform", ["All Platforms", "Swiggy", "Zomato", "Blinkit", "Dunzo"])
    with f3: st.selectbox("Category", ["All Categories", "Ice Cream", "Beverages", "Snacks"])
    with f4: st.selectbox("Brand", ["All Brands", "Amul", "Mother Dairy", "Kwality Wall's"])
    with f5: st.selectbox("Context", ["All Contexts", "Delivery", "Quality", "Pricing"])
    with f6: st.selectbox("Time Range", ["Last 7 Days", "Last 30 Days", "Custom"])

    st.markdown("""
    <div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding: 1.5rem; margin-top: 2rem; margin-bottom: 2rem;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom: 1rem;">
            <div style="background:#10b981; width:20px; height:20px; border-radius:5px; display:flex; align-items:center; justify-content:center; font-size:11px; color:#000;">✦</div>
            <span style="font-size:0.8rem; color:#10b981; font-weight:600; letter-spacing:0.05em;">AI ASSISTANT</span>
        </div>
    """, unsafe_allow_html=True)
    st.text_input("", placeholder="Ask anything about your data...", label_visibility="collapsed")
    st.markdown("""
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top: 0.75rem;">
            <span style="background:#222222; border:1px solid #333333; border-radius:20px; padding:5px 14px; font-size:0.75rem; color:#9ca3af; cursor:pointer;">Summarize main issues</span>
            <span style="background:#222222; border:1px solid #333333; border-radius:20px; padding:5px 14px; font-size:0.75rem; color:#9ca3af; cursor:pointer;">What is the sentiment trend?</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  2. HERO STORY & CONFIDENCE
    # ════════════════════════════════════════════════════
    hero_col, conf_col = st.columns([3, 2])
    with hero_col:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0f2b1f 0%, #1a1a1a 60%); border: 1px solid #1a4731; border-radius: 14px; padding: 2rem; height: 100%; position: relative; overflow: hidden;">
            <div style="position:absolute; top:-30px; right:-30px; width:150px; height:150px; background: radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%); border-radius:50%;"></div>
            <div style="margin-bottom:1rem;"><span style="background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); color:#10b981; font-size:0.7rem; font-weight:600; padding:4px 10px; border-radius:20px; letter-spacing:0.08em;">DYNAMIC STORY</span></div>
            <p style="font-size:1.35rem; font-weight:500; color:#ffffff; line-height:1.65; margin:0; letter-spacing:-0.01em;">{story}</p>
            <div style="margin-top:1.5rem; display:flex; gap:16px;">
                <div style="font-size:0.75rem; color:#6b7280;"><span style="color:#10b981; font-weight:700;">{metrics.get('total_reviews', 0):,}</span> reviews analyzed</div>
                <div style="font-size:0.75rem; color:#6b7280;"><span style="color:#10b981; font-weight:700;">Live</span> window</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with conf_col:
        drivers_html = ""
        for i, d in enumerate(drivers):
            icon = "!" if i==0 else "↑" if i==1 else "●"
            color = "#ef4444" if i==0 else "#f59e0b" if i==1 else "#10b981"
            bg = f"rgba({('239,68,68' if i==0 else '245,158,11' if i==1 else '16,185,129')},0.1)"
            drivers_html += f'<div style="display:flex; align-items:center; gap:10px;"><div style="width:28px; height:28px; background:{bg}; border:1px solid {bg}; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:10px; color:{color}; font-weight:700;">{icon}</div><span style="font-size:0.82rem; color:#d1d5db;">{d}</span></div>'

        st.markdown(f"""
        <div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding: 1.5rem 1.5rem 1rem 1.5rem;">
            <div style="font-size:0.7rem; color:#6b7280; letter-spacing:0.1em; text-transform:uppercase; font-weight:600; margin-bottom:1rem;">AI CONFIDENCE</div>
            <div style="display:flex; align-items:baseline; gap:6px; margin-bottom:0.75rem;">
                <span style="font-size:3rem; font-weight:700; color:#10b981; letter-spacing:-0.04em;">{conf}</span><span style="font-size:1.2rem; color:#10b981; font-weight:600;">%</span>
            </div>
        """, unsafe_allow_html=True)
        st.progress(conf)
        st.markdown(f'<div style="margin-top:1.25rem;"><div style="font-size:0.7rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.75rem;">KEY DRIVERS</div><div style="display:flex; flex-direction:column; gap:0.6rem;">{drivers_html}</div></div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:2rem;'></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  3. METRICS & IMPACT
    # ════════════════════════════════════════════════════
    st.markdown('<p style="font-size:0.72rem; color:#6b7280; letter-spacing:0.1em; text-transform:uppercase; font-weight:600; margin-bottom:10px;">PERFORMANCE METRICS</p>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem 1.25rem 1rem 1.25rem;"><div style="font-size:0.7rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.5rem;">Total Reviews</div><div style="font-size:2.2rem; font-weight:700; color:#ffffff; letter-spacing:-0.03em; line-height:1.1;">{metrics.get("total_reviews", 0):,}</div><div style="font-size:0.75rem; color:#6b7280; margin-top:6px;">Filtered cohort</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem 1.25rem 1rem 1.25rem;"><div style="font-size:0.7rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.5rem;">Negative %</div><div style="font-size:2.2rem; font-weight:700; color:#ef4444; letter-spacing:-0.03em; line-height:1.1;">{metrics.get("negative_percent", 0)}%</div><div style="font-size:0.75rem; color:#6b7280; margin-top:6px;">Of all sentiment signals</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem 1.25rem 1rem 1.25rem;"><div style="font-size:0.7rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.5rem;">Top Issue</div><div style="font-size:2.2rem; font-weight:700; color:#f59e0b; letter-spacing:-0.03em; line-height:1.1;">{metrics.get("top_issue", "N/A")}</div><div style="font-size:0.75rem; color:#6b7280; margin-top:6px;">Dominant pattern</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem 1.25rem 1rem 1.25rem;"><div style="font-size:0.7rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.5rem;">Top Brand</div><div style="font-size:2.2rem; font-weight:700; color:#10b981; letter-spacing:-0.03em; line-height:1.1;">{metrics.get("top_brand", "N/A")}</div><div style="font-size:0.75rem; color:#6b7280; margin-top:6px;">Most discussed</div></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a0f0f 0%, #1a1a1a 70%); border: 1px solid #4b1c1c; border-radius: 14px; padding: 1.5rem 2rem; margin: 2rem 0;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:1.25rem;">
            <div style="width:6px; height:6px; background:#ef4444; border-radius:50%; box-shadow: 0 0 6px #ef4444;"></div>
            <span style="font-size:0.7rem; color:#ef4444; letter-spacing:0.1em; text-transform:uppercase; font-weight:600;">BUSINESS IMPACT SUMMARY</span>
        </div>
        <div style="display:flex; gap:3rem; flex-wrap:wrap;">
            <div><div style="font-size:0.72rem; color:#9ca3af; margin-bottom:4px;">Revenue Risk</div><div style="font-size:2rem; font-weight:700; color:#ef4444; letter-spacing:-0.02em;">{impact.get('revenue_risk', 'N/A')}</div></div>
            <div style="border-left:1px solid #333333; margin: 0 0.5rem;"></div>
            <div><div style="font-size:0.72rem; color:#9ca3af; margin-bottom:4px;">Affected Reviews</div><div style="font-size:2rem; font-weight:700; color:#f59e0b; letter-spacing:-0.02em;">{impact.get('affected_reviews', 0):,}</div></div>
            <div style="border-left:1px solid #333333; margin: 0 0.5rem;"></div>
            <div><div style="font-size:0.72rem; color:#9ca3af; margin-bottom:4px;">Churn Risk</div><div style="font-size:2rem; font-weight:700; color:#ef4444; letter-spacing:-0.02em;">{impact.get('churn_risk_percent', 0)}%</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  4. INSIGHT BREAKDOWN 
    # ════════════════════════════════════════════════════
    st.markdown('<p style="font-size:0.72rem; color:#6b7280; letter-spacing:0.1em; text-transform:uppercase; font-weight:600; margin-bottom:10px;">INSIGHT BREAKDOWN</p>', unsafe_allow_html=True)
    bg1, bg2 = st.columns(2)
    
    plat_html = "".join([f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-size:0.85rem; color:#d1d5db;">{p.get("platform")}</span><div style="display:flex; align-items:center; gap:8px;"><div style="width:80px; height:4px; background:#222; border-radius:2px; overflow:hidden;"><div style="width:{p.get("share")}%; height:100%; background:#10b981; border-radius:2px;"></div></div><span style="font-size:0.75rem; color:#6b7280;">{p.get("share")}%</span></div></div>' for p in breakdown.get("platform", [])])
    brand_html = "".join([f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-size:0.85rem; color:#d1d5db;">{b.get("name")}</span><span style="font-size:0.75rem; background:#222; color:#d1d5db; border-radius:4px; padding:2px 8px; border:1px solid #333;">{b.get("mentions")} mentions</span></div>' for b in breakdown.get("brand", [])])
    cat_html = "".join([f'<span style="background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.25); font-size:0.75rem; padding:4px 12px; border-radius:20px;">{c.get("name")}</span>' for c in breakdown.get("category", [])])
    time_info = breakdown.get("time", {})
    
    with bg1: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem; margin-bottom:1rem;"><div style="font-size:0.7rem; color:#10b981; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:1rem;">PLATFORM INSIGHT</div><div style="display:flex; flex-direction:column; gap:0.6rem;">{plat_html if plat_html else "<span style=color:#888>No platform data</span>"}</div></div>', unsafe_allow_html=True)
    with bg2: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem; margin-bottom:1rem;"><div style="font-size:0.7rem; color:#10b981; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:1rem;">BRAND INSIGHT</div><div style="display:flex; flex-direction:column; gap:0.6rem;">{brand_html if brand_html else "<span style=color:#888>No brand data</span>"}</div></div>', unsafe_allow_html=True)
    bg3, bg4 = st.columns(2)
    with bg3: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem; margin-bottom:2rem;"><div style="font-size:0.7rem; color:#10b981; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:1rem;">CATEGORY INSIGHT</div><div style="display:flex; flex-wrap:wrap; gap:8px;">{cat_html if cat_html else "<span style=color:#888>No category data</span>"}</div></div>', unsafe_allow_html=True)
    with bg4: st.markdown(f'<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem; margin-bottom:2rem;"><div style="font-size:0.7rem; color:#10b981; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:1rem;">TIME INSIGHT</div><div style="display:flex; flex-direction:column; gap:0.5rem;"><div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-size:0.8rem; color:#9ca3af;">{time_info.get("label", "Peak Hour")}</span><span style="font-size:0.8rem; font-weight:600; color:#ef4444;">{time_info.get("insight", "Activity Peak")}</span></div></div></div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  5. ROOT CAUSE
    # ════════════════════════════════════════════════════
    st.markdown(f"""
    <div style="background:#1a1a1a; border:1px solid #333333; border-left: 3px solid #10b981; border-radius:14px; padding:1.5rem; margin-bottom:2rem;">
        <div style="font-size:0.7rem; color:#10b981; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; margin-bottom:0.75rem;">ROOT CAUSE ANALYSIS</div>
        <p style="font-size:1rem; color:#d1d5db; line-height:1.7; margin:0;">{root_cause}</p>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  6. RECOMMENDED ACTIONS
    # ════════════════════════════════════════════════════
    st.markdown('<p style="font-size:0.72rem; color:#6b7280; letter-spacing:0.1em; text-transform:uppercase; font-weight:600; margin-bottom:10px;">RECOMMENDED ACTIONS</p>', unsafe_allow_html=True)
    if actions:
        cols = st.columns(len(actions[:3]))
        for i, act in enumerate(actions[:3]):
            priority = act.get("priority", "Medium")
            pr_col = "#ef4444" if priority == "High" else "#f59e0b" if priority == "Medium" else "#10b981"
            bg_col = "239,68,68" if priority == "High" else "245,158,11" if priority == "Medium" else "16,185,129"
            with cols[i]:
                st.markdown(f"""
                <div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem; height:100%;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
                        <div style="background:#222; border:1px solid #333; border-radius:8px; width:32px; height:32px; display:flex; align-items:center; justify-content:center; font-size:0.8rem; font-weight:700; color:#ffffff;">0{i+1}</div>
                        <span style="font-size:0.68rem; background:rgba({bg_col},0.1); color:{pr_col}; padding:3px 8px; border-radius:4px; border:1px solid rgba({bg_col},0.2); font-weight:600;">{priority}</span>
                    </div>
                    <div style="font-size:0.95rem; font-weight:600; color:#ffffff; margin-bottom:0.4rem;">{act.get("title", "Action")}</div>
                    <div style="font-size:0.8rem; color:#6b7280; margin-bottom:1rem; line-height:1.5;">{act.get("description", "")}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No actionable recommendations generated.")
    st.markdown("<div style='margin-bottom:2rem;'></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    #  7. EVIDENCE & LANGUAGE (DYNAMIC SENTIMENT)
    # ════════════════════════════════════════════════════
    ev_col, lang_col = st.columns([3, 2])
    with ev_col:
        st.markdown('<p style="font-size:0.72rem; color:#6b7280; letter-spacing:0.1em; text-transform:uppercase; font-weight:600; margin-bottom:10px;">CUSTOMER EVIDENCE</p>', unsafe_allow_html=True)
        if evidence:
            for i, text in enumerate(evidence[:4]):
                st.markdown(f"""
                <div style="background:#1a1a1a; border:1px solid #333333; border-radius:12px; padding:1rem 1.25rem; margin-bottom:0.75rem;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.5rem;">
                        <div style="width:26px; height:26px; background:#222; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:0.65rem; color:#9ca3af; font-weight:600;">R{i+1}</div>
                    </div>
                    <p style="font-size:0.85rem; color:#d1d5db; margin:0; line-height:1.6;">{text}</p>
                </div>
                """, unsafe_allow_html=True)

    with lang_col:
        st.markdown('<p style="font-size:0.72rem; color:#6b7280; letter-spacing:0.1em; text-transform:uppercase; font-weight:600; margin-bottom:10px;">LANGUAGE INSIGHTS</p>', unsafe_allow_html=True)
        lang_html = '<div style="background:#1a1a1a; border:1px solid #333333; border-radius:14px; padding:1.25rem;"><div style="font-size:0.72rem; color:#10b981; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:0.75rem;">SLANG FREQUENCY</div><div style="display:flex; flex-direction:column; gap:0.5rem; margin-bottom:1.25rem;">'
        
        sent_html = '<div style="border-top:1px solid #222; padding-top:1rem;"><div style="font-size:0.72rem; color:#10b981; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:0.75rem;">SENTIMENT MAPPING</div><div style="display:flex; flex-direction:column; gap:0.45rem;">'

        if language:
            for l in language[:4]:
                # Dynamic Frequency List
                lang_html += f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="background:#222; border:1px solid #333; border-radius:6px; padding:3px 10px; font-size:0.78rem; color:#d1d5db; font-family:monospace;">{l.get("slang")}</span><span style="font-size:0.78rem; color:#10b981; font-weight:600;">{l.get("usage")} mentions</span></div>'
                
                # Dynamic Sentiment Mapping
                dom = str(l.get("sentiment", "neutral")).capitalize()
                s_col = "#10b981" if dom == "Positive" else "#ef4444" if dom == "Negative" else "#f59e0b"
                bg_col = "16,185,129" if dom == "Positive" else "239,68,68" if dom == "Negative" else "245,158,11"
                sent_html += f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-size:0.8rem; color:#d1d5db; font-family:monospace;">{l.get("slang")}</span><span style="background:rgba({bg_col},0.1); color:{s_col}; font-size:0.7rem; padding:2px 8px; border-radius:4px; border:1px solid rgba({bg_col},0.2);">{dom}</span></div>'
        else:
            lang_html += "<span style='color:#6b7280; font-size: 0.8rem;'>No slang detected.</span>"
        
        lang_html += "</div>" + sent_html + "</div></div>"
        st.markdown(lang_html, unsafe_allow_html=True)


    # ════════════════════════════════════════════════════
    #  8. HOW IT WORKS & FOOTER
    # ════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("How this works"):
        st.markdown("""
        <div style="padding:0.5rem 0; color:#9ca3af; font-size:0.88rem; line-height:1.8;">
            <p>This dashboard combines multiple AI agents to analyze customer feedback, detect patterns, and recommend business actions in real time.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="border-top:1px solid #222222; margin-top:2rem; padding-top:1.5rem; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:0.72rem; color:#4b5563;">UrbanPulse Intelligence · Powered by multi-agent AI</span>
        <div style="display:flex; gap:16px;">
            <span style="font-size:0.72rem; color:#10b981;">● Live Synthesis Complete</span>
        </div>
    </div>
    """, unsafe_allow_html=True)