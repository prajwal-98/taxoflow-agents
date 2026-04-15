import pandas as pd
from core.schema import UrbanPulseState
from core.constants import CITY_SLANG_MAP


def novelty_score_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 7 — Language Intelligence (A7)

    - Slang usage detection
    - City-wise slang mapping
    - Sentiment mapping (simple heuristic)
    - Emerging slang detection
    """

    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A7_output"] = {}
        state["A7_reasoning"] = "No data available"
        return state

    try:
        df = df.copy()
        df["raw_text"] = df["raw_text"].fillna("").astype(str)

        # -------------------------------
        # 1. SLANG DETECTION
        # -------------------------------
        slang_usage = {}

        for city, slang_list in CITY_SLANG_MAP.items():
            for slang in slang_list:
                count = df["raw_text"].str.lower().str.contains(slang).sum()

                if count > 0:
                    slang_usage[slang] = slang_usage.get(slang, 0) + int(count)

        # -------------------------------
        # 2. SENTIMENT BREAKDOWN (heuristic)
        # -------------------------------
        slang_sentiment = []

        for slang, count in slang_usage.items():

            subset = df[df["raw_text"].str.lower().str.contains(slang)]

            pos = subset["raw_text"].str.contains(
                "good|fast|great|awesome|quick", case=False, regex=True
            ).sum()

            neg = subset["raw_text"].str.contains(
                "late|delay|bad|missing|slow|rude", case=False, regex=True
            ).sum()

            neutral = count - (pos + neg)

            slang_sentiment.append({
                "slang": slang,
                "total_usage": count,
                "sentiment": {
                    "positive": int(pos),
                    "negative": int(neg),
                    "neutral": int(max(neutral, 0))
                }
            })

        # -------------------------------
        # 3. CITY-WISE SLANG
        # -------------------------------
        city_slang = []

        for city, slang_list in CITY_SLANG_MAP.items():
            for slang in slang_list:
                count = df[
                    (df["city"] == city) &
                    (df["raw_text"].str.lower().str.contains(slang))
                ].shape[0]

                if count > 0:
                    city_slang.append({
                        "city": city,
                        "slang": slang,
                        "usage": int(count)
                    })

        # -------------------------------
        # 4. SENTIMENT MAPPING (MEANING)
        # -------------------------------
        sentiment_mapping = []

        for item in slang_sentiment:
            slang = item["slang"]
            sentiment = item["sentiment"]

            dominant = max(sentiment, key=sentiment.get)

            sentiment_mapping.append({
                "slang": slang,
                "dominant_sentiment": dominant
            })

        # -------------------------------
        # 5. EMERGING SLANG (RARE BUT PRESENT)
        # -------------------------------
        emerging_slang = []

        for slang, count in slang_usage.items():
            if 1 <= count <= 3:
                emerging_slang.append({
                    "slang": slang,
                    "usage": count
                })

        # -------------------------------
        # FINAL OUTPUT
        # -------------------------------
        state["A7_output"] = {
            "slang_intelligence": slang_sentiment,
            "city_slang": city_slang,
            "sentiment_mapping": sentiment_mapping,
            "emerging_slang": emerging_slang
        }

        reasoning_steps.append("Slang and language patterns analyzed successfully")

    except Exception as e:
        state["A7_output"] = {}
        reasoning_steps.append(f"Error: {str(e)}")

    # -------------------------------
    # STATE UPDATE
    # -------------------------------
    state["A7_reasoning"] = "\n".join(reasoning_steps)

    steps = state.get("completed_steps", [])
    if 7 not in steps:
        steps.append(7)

    state["completed_steps"] = steps
    state["current_step"] = 8

    return state