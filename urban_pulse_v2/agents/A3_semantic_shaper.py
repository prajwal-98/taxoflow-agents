import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from core.schema import UrbanPulseState

def semantic_shaper_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 3: Transforms unstructured review text into a 2D semantic space.
    This allows for visual clustering and pattern identification.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A3_reasoning"] = "Error: No data available for semantic mapping."
        return state

    try:
        # 1. Text Vectorization
        # Using sublinear_tf to scale the impact of high-frequency words
        tfidf = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            sublinear_tf=True,
            ngram_range=(1, 2)
        )
        
        # We fill NaNs to prevent the vectorizer from crashing
        review_corpus = df["raw_text"].fillna("").tolist()
        tfidf_matrix = tfidf.fit_transform(review_corpus)
        
        # 2. Dimensionality Reduction (SVD)
        # We project the sparse matrix into a dense 2D space for the UI
        svd = TruncatedSVD(n_components=2, random_state=42)
        vectors_2d = svd.fit_transform(tfidf_matrix)
        
        # 3. Coordinate Assignment
        # Creating a dataframe of (x, y) points mapped to the original index
        coords_df = pd.DataFrame(
            vectors_2d, 
            columns=['x', 'y'], 
            index=df.index
        )
        
        state["A3_vector_coords"] = coords_df
        
        reasoning_steps.append("Status: Semantic Shaper initialized.")
        reasoning_steps.append("Technique: TF-IDF Vectorization followed by Truncated SVD Projection.")
        reasoning_steps.append("Result: Multi-dimensional text space compressed to 2D coordinates for UI visualization.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Semantic Shaper Error: {str(e)}")

    # Update State Reasoning
    state["A3_reasoning"] = "\n".join(reasoning_steps)
    
    # Navigation Logic
    if 3 not in state["completed_steps"]:
        state["completed_steps"].append(3)
    
    # Move to Cluster Agent (A4)
    state["current_step"] = 4
    
    return state