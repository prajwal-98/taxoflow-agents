import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from core.schema import UrbanPulseState
from utils.llm_client import generate_response


def cluster_agent_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 4 — Pattern Detection (A4)

    Fully dynamic:
    - Clustering (TF-IDF + KMeans)
    - LLM-based cluster naming
    - LLM-based characteristics
    - Trend calculation (if date exists)
    """

    df = state.get("filtered_df")
    reasoning_steps = []

    # -------------------------------
    # 1. SAFETY CHECK
    # -------------------------------
    if df is None or df.empty:
        state["A4_output"] = {}
        state["A4_reasoning"] = "No data available"
        return state

    reviews = df["raw_text"].fillna("").astype(str).tolist()

    if len(reviews) < 5:
        state["A4_output"] = {}
        state["A4_reasoning"] = "Not enough data"
        return state

    try:
        # -------------------------------
        # 2. TF-IDF
        # -------------------------------
        tfidf = TfidfVectorizer(
            stop_words="english",
            max_features=1000,
            sublinear_tf=True,
            ngram_range=(1, 2)
        )

        X = tfidf.fit_transform(reviews)

        # -------------------------------
        # 3. KMEANS
        # -------------------------------
        k = 3
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        df_clustered = df.copy()
        df_clustered["cluster"] = labels

        total = len(df_clustered)
        clusters_output = []

        # -------------------------------
        # 4. PROCESS EACH CLUSTER
        # -------------------------------
        for cluster_id in sorted(df_clustered["cluster"].unique()):

            cluster_df = df_clustered[df_clustered["cluster"] == cluster_id]
            texts = cluster_df["raw_text"].astype(str).tolist()

            size = int((len(cluster_df) / total) * 100)

            # -------------------------------
            # SIGNALS (TOP WORDS)
            # -------------------------------
            signals = _extract_keywords(texts)

            # -------------------------------
            # LLM: NAME + DESCRIPTION + CHARACTERISTICS
            # -------------------------------
            llm_prompt = f"""
            You are a Q-Commerce business analyst.

            Based on these customer reviews:
            {texts[:15]}

            Generate STRICT JSON:

            {{
              "name": "2-3 word cluster name",
              "description": "1 line summary",
              "characteristics": {{
                "product_type": "...",
                "issue_type": "...",
                "context": "..."
              }}
            }}
            """

            try:
                llm_output = generate_response(llm_prompt, state)

                if not isinstance(llm_output, dict):
                    llm_output = {}

            except:
                llm_output = {}

            # fallback if LLM fails
            name = llm_output.get("name") or _fallback_name(signals)
            description = llm_output.get("description") or "Customer issues grouped by similarity"
            characteristics = llm_output.get("characteristics") or {
                "product_type": "General",
                "issue_type": "Multiple",
                "context": "General usage"
            }

            # -------------------------------
            # EXAMPLES
            # -------------------------------
            examples = texts[:5]

            # -------------------------------
            # TREND (IF DATE EXISTS)
            # -------------------------------
            trend = _calculate_trend(cluster_df)

            clusters_output.append({
                "cluster_id": int(cluster_id),
                "name": name,
                "size": size,
                "description": description,
                "signals": signals,
                "characteristics": characteristics,
                "examples": examples,
                "trend": trend
            })

        # -------------------------------
        # META INSIGHT (LLM)
        # -------------------------------
        meta_prompt = f"""
        Given these cluster summaries:
        {clusters_output}

        Provide one short business insight (1 line).
        """

        try:
            meta_insight = generate_response(meta_prompt, state)
            if not isinstance(meta_insight, str):
                meta_insight = str(meta_insight)
        except:
            meta_insight = "Key operational issues dominate customer complaints"

        # -------------------------------
        # FINAL OUTPUT
        # -------------------------------
        state["A4_output"] = {
            "summary": f"{len(clusters_output)} major issue clusters identified",
            "clusters": clusters_output,
            "meta_insight": meta_insight.strip()
        }

        reasoning_steps.append("Dynamic clustering + LLM enrichment complete")

    except Exception as e:
        state["A4_output"] = {}
        reasoning_steps.append(f"Error: {str(e)}")

    # -------------------------------
    # STATE UPDATE
    # -------------------------------
    state["A4_reasoning"] = "\n".join(reasoning_steps)

    steps = state.get("completed_steps", [])
    if 4 not in steps:
        steps.append(4)

    state["completed_steps"] = steps
    state["current_step"] = 5

    return state


# =========================================================
# HELPERS
# =========================================================

def _extract_keywords(texts):
    words = " ".join(texts).lower().split()
    freq = {}

    for w in words:
        if len(w) < 4:
            continue
        freq[w] = freq.get(w, 0) + 1

    return sorted(freq, key=freq.get, reverse=True)[:5]


def _fallback_name(signals):
    text = " ".join(signals)

    if any(w in text for w in ["delivery", "delay"]):
        return "Delivery Issues"

    if any(w in text for w in ["missing", "wrong", "damaged"]):
        return "Product Issues"

    return "Service Experience"


def _calculate_trend(cluster_df):
    """
    Simple trend:
    compares recent vs older data if 'date' column exists
    """

    if "date" not in cluster_df.columns:
        return "Stable"

    df = cluster_df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.dropna(subset=["date"])

    if df.empty:
        return "Stable"

    recent = df[df["date"] >= df["date"].max() - pd.Timedelta(days=7)]
    previous = df[df["date"] < df["date"].max() - pd.Timedelta(days=7)]

    if len(previous) == 0:
        return "Stable"

    if len(recent) > len(previous):
        return "Increasing"

    if len(recent) < len(previous):
        return "Decreasing"

    return "Stable"