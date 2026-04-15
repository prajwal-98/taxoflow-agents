import pandas as pd
from core.schema import UrbanPulseState


def platform_signal_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 6 — Signal Agent (A6)

    Generates business insights across:
    - Platform
    - Brand/Product
    - Category
    - City
    - Time
    """

    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A6_output"] = {}
        state["A6_reasoning"] = "No data available"
        return state

    try:
        df = df.copy()

        # -------------------------------
        # 1. PLATFORM INSIGHT
        # -------------------------------
        platform_counts = df["platform"].value_counts(normalize=True) * 100

        platform_insight = []
        for p, val in platform_counts.head(2).items():
            platform_insight.append({
                "platform": p,
                "share": round(val, 1)
            })

        # -------------------------------
        # 2. BRAND / PRODUCT INSIGHT
        # -------------------------------
        brand_insight = []
        if "brand" in df.columns:
            top_brands = df["brand"].value_counts().head(3)
            for b, count in top_brands.items():
                brand_insight.append({
                    "name": b,
                    "mentions": int(count)
                })

        # -------------------------------
        # 3. CATEGORY INSIGHT
        # -------------------------------
        category_insight = []
        if "category" in df.columns:
            top_categories = df["category"].value_counts().head(3)
            for c, count in top_categories.items():
                category_insight.append({
                    "name": c,
                    "mentions": int(count)
                })

        # -------------------------------
        # 4. CITY INSIGHT
        # -------------------------------
        city_counts = df["city"].value_counts().head(3)

        city_insight = []
        for city, count in city_counts.items():
            city_insight.append({
                "city": city,
                "mentions": int(count)
            })

        # -------------------------------
        # 5. TIME INSIGHT
        # -------------------------------
        time_insight = {
            "peak_hour": None,
            "label": "",
            "insight": ""
        }

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])

            if not df.empty:
                df["hour"] = df["date"].dt.hour
                peak_hour = int(df["hour"].value_counts().idxmax())

                # convert to readable label
                if peak_hour < 12:
                    label = "Morning"
                elif peak_hour < 17:
                    label = "Afternoon"
                elif peak_hour < 21:
                    label = "Evening"
                else:
                    label = "Night"

                time_insight = {
                    "peak_hour": peak_hour,
                    "label": label,
                    "insight": f"Peak activity observed during {label} hours"
                }

        # -------------------------------
        # FINAL OUTPUT (INSIGHT ONLY)
        # -------------------------------
        state["A6_output"] = {
            "platform": platform_insight,
            "brand": brand_insight,
            "category": category_insight,
            "city": city_insight,
            "time": time_insight
        }

        reasoning_steps.append("Generated platform, brand, category, city, and time insights")

    except Exception as e:
        state["A6_output"] = {}
        reasoning_steps.append(f"Error: {str(e)}")

    # -------------------------------
    # STATE UPDATE
    # -------------------------------
    state["A6_reasoning"] = "\n".join(reasoning_steps)

    steps = state.get("completed_steps", [])
    if 6 not in steps:
        steps.append(6)

    state["completed_steps"] = steps
    state["current_step"] = 7

    return state