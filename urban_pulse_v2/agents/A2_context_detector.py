import pandas as pd
import json
from core.schema import UrbanPulseState
from core.constants import CITY_SLANG_MAP
from utils.llm_client import generate_response


def context_detector_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 2 — Context Detection (A2)
    """

    df = state.get("filtered_df")

    # -------------------------------
    # 1. SAFETY CHECK
    # -------------------------------
    if df is None or df.empty:
        state["A2_output"] = _empty_output("No data available")
        state["A2_reasoning"] = "No data available"
        state["current_step"] = 2
        return state

    # -------------------------------
    # 2. CITY CONTEXT
    # -------------------------------
    active_filters = state.get("active_filters", {})
    city = (active_filters.get("city") or ["Bangalore"])[0]

    slang_reference = CITY_SLANG_MAP.get(city, [])

    # -------------------------------
    # 3. SAMPLE REVIEWS
    # -------------------------------
    sample_reviews = (
        df.get("raw_text", pd.Series())
        .dropna()
        .astype(str)
        .head(10)
        .tolist()
    )

    # -------------------------------
    # 4. PROMPT
    # -------------------------------
    prompt = f"""
    You are a Local Market Analyst for Q-Commerce in {city}.

    Slang Reference: {slang_reference}

    Reviews:
    {sample_reviews}

    Return STRICT JSON:

    {{
        "localized_sentiment": "short summary",
        "slang_detected": ["list"],
        "operational_context": "what is going wrong",
        "top_themes": ["3-5 issues"]
    }}
    """

    # -------------------------------
    # 5. LLM CALL
    # -------------------------------
    try:
        raw_response = generate_response(prompt, state)

    except Exception as e:
        state["A2_output"] = _empty_output("LLM failed")
        state["A2_reasoning"] = str(e)
        state["current_step"] = 2
        return state

    # -------------------------------
    # 6. SAFE PARSE (IMPORTANT FIX)
    # -------------------------------
    parsed = _safe_parse(raw_response)

    # -------------------------------
    # 7. STORE OUTPUT
    # -------------------------------
    state["A2_output"] = {
        "localized_sentiment": parsed.get("localized_sentiment", ""),
        "slang_detected": parsed.get("slang_detected", []),
        "operational_context": parsed.get("operational_context", ""),
        "top_themes": parsed.get("top_themes", [])
    }

    state["A2_reasoning"] = "Success"

    # -------------------------------
    # 8. STEP UPDATE
    # -------------------------------
    steps = state.get("completed_steps", [])
    if 2 not in steps:
        steps.append(2)

    state["completed_steps"] = steps
    state["current_step"] = 3

    return state


# -------------------------------
# HELPERS
# -------------------------------

def _empty_output(msg):
    return {
        "localized_sentiment": msg,
        "slang_detected": [],
        "operational_context": msg,
        "top_themes": []
    }


import json

def _safe_parse(raw):
    if isinstance(raw, dict):
        return raw

    if isinstance(raw, str):
        # 1. Clean whitespace and Markdown wrappers
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:-3].strip()  # Remove ```json and trailing ```
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:-3].strip()  # Remove ``` and trailing ```
        
        try:
            return json.loads(cleaned)
        except Exception:
            # 2. If it still fails, it might be a partial string or badly formatted
            return {}

    return {}