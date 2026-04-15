import pandas as pd
from core.schema import UrbanPulseState


def decision_dashboard_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 8 — Final Decision Dashboard (A8)

    Combines outputs from A1–A7 into:
    - Story
    - Metrics
    - Impact
    - Actions
    """

    df = state.get("filtered_df")
    a4 = state.get("A4_output", {}).get("clusters", [])
    a5 = state.get("A5_output", [])
    a6 = state.get("A6_output", {})
    a7 = state.get("A7_output", {})

    if df is None or df.empty:
        state["A8_output"] = {}
        return state

    try:
        # -------------------------------
        # 1. TOP CLUSTER
        # -------------------------------
        top_cluster = max(a4, key=lambda x: x.get("size", 0)) if a4 else {}

        issue = top_cluster.get("name", "General Issue")
        size = top_cluster.get("size", 0)

        # -------------------------------
        # 2. BASIC METRICS
        # -------------------------------
        total_reviews = len(df)

        negative_count = df["raw_text"].str.contains(
            "late|delay|bad|missing|slow|rude", case=False, regex=True
        ).sum()

        negative_pct = round((negative_count / total_reviews) * 100, 1) if total_reviews else 0

        top_brand = None
        if "brand" in df.columns:
            top_brand = df["brand"].value_counts().idxmax()

        # -------------------------------
        # 3. TIME CONTEXT
        # -------------------------------
        peak_time = a6.get("time", {}).get("label", "peak hours")

        # -------------------------------
        # 4. DYNAMIC STORY
        # -------------------------------
        city = df["city"].mode()[0] if "city" in df.columns else "selected region"
        category = df["category"].mode()[0] if "category" in df.columns else "key categories"

        story = f"During {peak_time} in {city}, {issue.lower()} are impacting {category.lower()} products."

        # -------------------------------
        # 5. AI CONFIDENCE
        # -------------------------------
        confidence = min(95, max(60, int((size / total_reviews) * 100)))

        drivers = [
            f"{negative_pct}% negative sentiment",
            f"{issue} is dominant pattern",
            f"Peak load during {peak_time}"
        ]

        # -------------------------------
        # 6. IMPACT
        # -------------------------------
        impact = {
            "revenue_risk": f"₹{size * 150}K approx",
            "affected_reviews": size,
            "churn_risk_percent": min(50, int(negative_pct * 0.6))
        }

        # -------------------------------
        # 7. ROOT CAUSE
        # -------------------------------
        root_cause = f"High demand during {peak_time} combined with operational inefficiencies is driving {issue.lower()}."

        # -------------------------------
        # 8. ACTIONS (FROM A5)
        # -------------------------------
        actions = []

        for item in a5[:3]:
            actions.append({
                "title": f"{item.get('issue_category')} Fix",
                "description": item.get("reason"),
                "priority": item.get("priority")
            })

        # fallback
        if not actions:
            actions = [
                {
                    "title": "Improve Operations",
                    "description": "Optimize delivery and inventory handling",
                    "priority": "High"
                }
            ]

        # -------------------------------
        # 9. EVIDENCE
        # -------------------------------
        evidence = df["raw_text"].dropna().head(5).tolist()

        # -------------------------------
        # 10. LANGUAGE HIGHLIGHTS
        # -------------------------------
        slang_data = a7.get("slang_intelligence", [])

        language_highlights = []
        for s in slang_data[:3]:
            language_highlights.append({
                "slang": s.get("slang"),
                "usage": s.get("total_usage"),
                "sentiment": max(s.get("sentiment", {}), key=s.get("sentiment", {}).get)
            })

        # -------------------------------
        # FINAL OUTPUT
        # -------------------------------
        state["A8_output"] = {
            "story": story,
            "confidence": confidence,
            "drivers": drivers,
            "metrics": {
                "total_reviews": total_reviews,
                "negative_percent": negative_pct,
                "top_issue": issue,
                "top_brand": top_brand
            },
            "impact": impact,
            "breakdown": a6,
            "root_cause": root_cause,
            "actions": actions,
            "evidence": evidence,
            "language": language_highlights
        }

    except Exception as e:
        state["A8_output"] = {"error": str(e)}

    # -------------------------------
    # STATE UPDATE
    # -------------------------------
    steps = state.get("completed_steps", [])
    if 8 not in steps:
        steps.append(8)

    state["completed_steps"] = steps
    state["current_step"] = 9

    return state