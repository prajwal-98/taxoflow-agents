import os
import numpy as np
import pandas as pd
import umap
from sklearn.cluster import DBSCAN
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

INPUT_PATH = "urban_pulse/data/raw_qcomm_reviews.csv"
OUTPUT_PATH = "urban_pulse/data/vector_mapped_data.csv"

class SemanticShaper:
    def __init__(self):
        print("Architect Status: Initializing Semantic Shaper (TF-IDF + SVD)...")

    def process_data(self):
        if not os.path.exists(INPUT_PATH):
            raise FileNotFoundError(f"CRITICAL: {INPUT_PATH} not found.")

        # LOAD DATA WITH ROBUSTNESS: Handles extra commas and encoding issues
        try:
            df = pd.read_csv(
                INPUT_PATH, 
                on_bad_lines='skip', 
                engine='python', 
                encoding='utf-8'
            )
            
            # STANDARDIZE COLUMNS: Converts 'Raw_Text' -> 'raw_text'
            df.columns = [c.strip().lower() for c in df.columns]
            
        except Exception as e:
            print(f"CRITICAL LOAD FAILURE: {e}")
            return

        print(f"Loaded {len(df)} rows. Starting Embedding Firehose...")

        # Verify Column Contract
        if "raw_text" not in df.columns:
            print(f"ERROR: 'raw_text' not found. Available columns: {list(df.columns)}")
            return

        # Harden against NaNs and empties in raw_text
        before = len(df)
        df["raw_text"] = df["raw_text"].astype(str)
        df["raw_text"] = df["raw_text"].replace({"nan": ""})
        df = df[df["raw_text"].str.strip() != ""]
        after = len(df)
        dropped = before - after
        if dropped > 0:
            print(f"Architect Note: Dropped {dropped} rows with missing/empty raw_text.")

        if df.empty:
            print("Architect Alert: No valid text rows after cleaning; aborting shaping step.")
            return

        texts = df["raw_text"].tolist()

        print("Encoding reviews with TF-IDF (lightweight embedding)...")
        vectorizer = TfidfVectorizer(max_features=4096, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Compress TF-IDF into a dense semantic space via SVD
        n_components = min(256, tfidf_matrix.shape[1] - 1) if tfidf_matrix.shape[1] > 1 else 1
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        embeddings = svd.fit_transform(tfidf_matrix)

        print("Reducing dimensions for 3D UI space (UMAP)...")
        reducer = umap.UMAP(
            n_components=3,
            random_state=42,
            n_neighbors=15,
            min_dist=0.1,
        )
        projections = reducer.fit_transform(embeddings)

        print("Clustering reviews into semantic islands (DBSCAN)...")
        clusterer = DBSCAN(eps=0.5, min_samples=3)
        cluster_labels = clusterer.fit_predict(projections)

        # Preserve the downstream contract: x, y, z, cluster columns
        df["x"], df["y"], df["z"] = projections[:, 0], projections[:, 1], projections[:, 2]
        df["cluster"] = cluster_labels

        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)
        valid_clusters = [c for c in df["cluster"].unique() if c != -1]
        print(f"--- Complete! Discovered {len(valid_clusters)} clusters. Saved to {OUTPUT_PATH} ---")

if __name__ == "__main__":
    shaper = SemanticShaper()
    shaper.process_data()