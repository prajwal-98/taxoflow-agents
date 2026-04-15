import pandas as pd
from core.schema import UrbanPulseState


def gatekeeper_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 1 — Data Readiness (Gatekeeper)

    Responsibilities:
    - Validate dataset
    - Generate summary metrics for UI
    - Provide data quality signals
    """

    df = state.get("raw_df")

    # -------------------------------
    # 1. BASIC VALIDATION
    # -------------------------------
    if df is None or not hasattr(df, "columns") or df.empty:
        state["A1_is_valid"] = False
        state["A1_reasoning"] = "Dataset is empty or not loaded"
        state["current_step"] = 1
        return state

    required_columns = ["raw_text", "star_rating", "city", "platform"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        state["A1_is_valid"] = False
        state["A1_reasoning"] = f"Missing columns: {missing}"
        state["current_step"] = 1
        return state

    # API key check (only for Live mode)
    if state.get("mode") == "Live API" and not state.get("api_key"):
        state["A1_is_valid"] = False
        state["A1_reasoning"] = "Missing API Key"
        state["current_step"] = 1
        return state

    # -------------------------------
    # 2. METRICS (FOR UI CARDS)
    # -------------------------------
    total_reviews = len(df)
    total_cities = df["city"].nunique() if "city" in df.columns else 0
    total_platforms = df["platform"].nunique() if "platform" in df.columns else 0
    total_categories = df["category"].nunique() if "category" in df.columns else 0

    state["A1_metrics"] = {
        "total_reviews": total_reviews,
        "cities": total_cities,
        "platforms": total_platforms,
        "categories": total_categories,
    }

    # -------------------------------
    # 3. CHART DATA (FOR UI)
    # -------------------------------
    try:
        platform_dist = (
            df["platform"].value_counts().reset_index().values.tolist()
            if "platform" in df.columns else []
        )

        category_dist = (
            df["category"].value_counts().reset_index().values.tolist()
            if "category" in df.columns else []
        )

        trend = []
        if "date" in df.columns:
            temp_df = df.copy()
            temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
            temp_df = temp_df.dropna(subset=["date"])
            trend = (
                temp_df.groupby(temp_df["date"].dt.to_period("M"))
                .size()
                .reset_index(name="count")
                .values.tolist()
            )

        state["A1_charts"] = {
            "platform_distribution": platform_dist,
            "category_distribution": category_dist,
            "review_trend": trend,
        }

    except Exception:
        state["A1_charts"] = {}

    # -------------------------------
    # 4. KEY HIGHLIGHTS
    # -------------------------------
    try:
        top_platform = df["platform"].mode()[0] if "platform" in df.columns else None
        top_category = df["category"].mode()[0] if "category" in df.columns else None

        peak_month = None
        if "date" in df.columns:
            temp_df = df.copy()
            temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
            temp_df = temp_df.dropna(subset=["date"])
            if not temp_df.empty:
                peak_month = (
                    temp_df["date"]
                    .dt.to_period("M")
                    .value_counts()
                    .idxmax()
                    .strftime("%B")
                )

        state["A1_highlights"] = {
            "top_platform": top_platform,
            "top_category": top_category,
            "peak_month": peak_month,
        }

    except Exception:
        state["A1_highlights"] = {}

    # -------------------------------
    # 5. DATA QUALITY
    # -------------------------------
    missing_ratio = df.isnull().mean().mean()

    state["A1_data_quality"] = {
        "schema_valid": True,
        "missing_data_ok": missing_ratio < 0.2,
        "format_valid": True,
    }

    # -------------------------------
    # 6. SAMPLE DATA
    # -------------------------------
    state["A1_sample"] = df.head(10)

    # -------------------------------
    # 7. FINAL STATE
    # -------------------------------
    state["A1_is_valid"] = True
    state["A1_reasoning"] = "Dataset validated successfully"

    df = state.get("filtered_df")

    if df is not None and not df.empty:
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        state["A1_metrics"] = {
            "total_reviews": len(df),
            "cities": df["city"].nunique() if "city" in df.columns else 0,
            "platforms": df["platform"].nunique() if "platform" in df.columns else 0,
            "categories": df["category"].nunique() if "category" in df.columns else 0,
        }

        state["A1_charts"] = {
            "platform_distribution": df["platform"].value_counts().reset_index().values.tolist() if "platform" in df.columns else [],
            "category_distribution": df["category"].value_counts().reset_index().values.tolist() if "category" in df.columns else [],
            # "review_trend": df.groupby(df["date"].dt.to_period("M")).size().reset_index().values.tolist() if "date" in df.columns else [],
            # with this
            "review_trend": (
                df.groupby(df["date"].dt.to_period("M"))
                .size()
                .reset_index(name="count")
                .assign(date=lambda x: x["date"].astype(str))  # converts Period → string for plotly
                [["date", "count"]]
                .values.tolist()
            ) if "date" in df.columns else [],
        }

        state["A1_highlights"] = {
            "top_platform": df["platform"].mode()[0] if "platform" in df.columns else None,
            "top_category": df["category"].mode()[0] if "category" in df.columns else None,
            "peak_month": str(df["date"].dt.to_period("M").mode()[0]) if "date" in df.columns else None,
        }

        state["A1_data_quality"] = {
            "schema_valid": True,
            "missing_data_ok": not df.isnull().any().any(),
            "format_valid": True,
        }

        state["A1_sample"] = df.head(10)

    else:
        state["A1_metrics"] = {}
        state["A1_charts"] = {}
        state["A1_highlights"] = {}
        state["A1_data_quality"] = {}
        state["A1_sample"] = None

    steps = state.get("completed_steps", [])
    
    if 1 not in steps:
        steps.append(1)
    state["completed_steps"] = steps
    state["current_step"] = 2
    
    return state