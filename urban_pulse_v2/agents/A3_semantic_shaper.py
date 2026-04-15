import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from core.schema import UrbanPulseState
from utils.llm_client import generate_response


def semantic_shaper_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 3 — Semantic Shaper (A3)

    - TF-IDF vectorization
    - Smart anchor selection
    - Cosine similarity scoring
    - Clean filtering
    - Hybrid theme detection (rule + LLM fallback)
    """

    df = state.get("filtered_df")

    # -------------------------------
    # 1. SAFETY CHECK
    # -------------------------------
    if df is None or df.empty:
        state["A3_output"] = _empty_output()
        state["A3_reasoning"] = "No data available"
        return state

    reviews = df["raw_text"].fillna("").astype(str).tolist()

    if len(reviews) < 3:
        state["A3_output"] = _empty_output()
        state["A3_reasoning"] = "Not enough reviews"
        return state

    # -------------------------------
    # 2. TF-IDF VECTORIZATION
    # -------------------------------
    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=1000,
        sublinear_tf=True,
        ngram_range=(1, 2)
    )

    tfidf_matrix = tfidf.fit_transform(reviews)

    # -------------------------------
    # 3. SMART ANCHOR SELECTION
    # -------------------------------
    row_sums = tfidf_matrix.sum(axis=1).A1
    anchor_idx = int(np.argmax(row_sums))

    anchor_review = reviews[anchor_idx]
    anchor_vector = tfidf_matrix[anchor_idx]

    # -------------------------------
    # 4. COSINE SIMILARITY
    # -------------------------------
    similarities = (tfidf_matrix @ anchor_vector.T).toarray().flatten()
    similarities[anchor_idx] = -1  # remove self

    sorted_idx = similarities.argsort()[::-1]

    # -------------------------------
    # 5. TOP SIMILAR REVIEWS (FILTERED)
    # -------------------------------
    similar_pairs = []
    seen = set()

    for i in sorted_idx:
        score = similarities[i]

        if score < 0.2:
            continue

        text = reviews[i].strip()

        if text and text not in seen and text != anchor_review:
            similar_pairs.append({
                "text": text,
                "score": round(float(score), 2)
            })
            seen.add(text)

        if len(similar_pairs) >= 5:
            break

    similar_reviews = [x["text"] for x in similar_pairs]

    # -------------------------------
    # 6. THEME DETECTION (RULE FIRST)
    # -------------------------------
    theme = _detect_theme(similar_reviews)

    # fallback to LLM if needed
    if not theme and similar_reviews:
        prompt = f"""
        Given these similar customer reviews:

        {similar_reviews}

        Provide a short 2-3 word theme.

        Example:
        "Delivery Delay Issue"
        """
        try:
            theme = generate_response(prompt, state)
            if not isinstance(theme, str):
                theme = str(theme)
        except:
            theme = "General Issue"

    if not theme:
        theme = "General Issue"

    # -------------------------------
    # 7. OUTPUT
    # -------------------------------
    state["A3_output"] = {
        "anchor_review": anchor_review,
        "similar_reviews": similar_pairs,
        "semantic_theme": theme.strip()
    }

    state["A3_reasoning"] = "TF-IDF + cosine similarity + hybrid theme detection applied"

    # -------------------------------
    # 8. STEP UPDATE
    # -------------------------------
    steps = state.get("completed_steps", [])
    if 3 not in steps:
        steps.append(3)

    state["completed_steps"] = steps
    state["current_step"] = 4

    return state


# -------------------------------
# HELPERS
# -------------------------------

def _empty_output():
    return {
        "anchor_review": "",
        "similar_reviews": [],
        "semantic_theme": ""
    }


def _detect_theme(reviews):
    """
    Rule-based theme detection (fast + domain aligned)
    """
    text = " ".join(reviews).lower()

    if any(w in text for w in ["delivery", "late", "delay"]):
        return "Delivery Issue"

    elif any(w in text for w in ["missing", "wrong", "damaged", "expired"]):
        return "Product Issue"

    elif any(w in text for w in ["rude", "support", "refund", "response"]):
        return "Service Experience"

    return None