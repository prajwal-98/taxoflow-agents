import pandas as pd
import numpy as np
import time
from google import genai
import umap
from sklearn.cluster import HDBSCAN
from utils.config import Config

Config.validate_setup()
client = genai.Client(api_key=Config.GEMINI_API_KEY)

def get_working_embedding_model():
    """Discovers a working embedding model via API listing, then falls back to known candidates."""
    try:
        for m in client.models.list():
            name = getattr(m, "name", None) or str(m)
            if not name or "embed" not in name.lower():
                continue
            try:
                client.models.embed_content(model=name, contents="test")
                print(f"Architect Note: Using discovered embedding model: {name}")
                return name
            except Exception:
                continue
    except Exception as e:
        print(f"Architect Note: Model discovery skipped ({e}). Trying known candidates...")

    candidates = [
        "models/gemini-embedding-001",
        "gemini-embedding-001",
        "text-embedding-004",
        "models/text-embedding-004",
        "embedding-001",
        "models/embedding-001",
        "text-embedding-005",
    ]
    print("Architect Note: Testing embedding endpoints...")
    for model_name in candidates:
        try:
            client.models.embed_content(model=model_name, contents="test")
            print(f"Architect Note: Using candidate embedding model: {model_name}")
            return model_name
        except Exception:
            continue

    raise ValueError("CRITICAL: No working embedding model found on this API key.")

def generate_embeddings(batch_size=50):
    print("--- TaxoFlow Vector Engine: Building Narrative Geometry ---")
    try:
        df = pd.read_csv('data/processed_geopol_data.csv')
    except FileNotFoundError:
        print("Architect Alert: 'processed_geopol_data.csv' missing.")
        return

    embedding_model = get_working_embedding_model()
    print(f"Locked onto verified embedding model: {embedding_model}")
    print(f"Embedding {len(df)} signals...")
    
    all_embeddings = []
    embedding_dim = 3072

    for i in range(0, len(df), batch_size):
        batch_texts = df['raw_text'].iloc[i:i+batch_size].tolist()
        print(f"      Processing Chunk {i//batch_size + 1}...")
        
        try:
            response = client.models.embed_content(
                model=embedding_model,
                contents=batch_texts
            )
            batch_vectors = []
            for e in (response.embeddings or []):
                vals = getattr(e, "values", None)
                if vals is not None:
                    batch_vectors.append(vals)
                    embedding_dim = len(vals)
                else:
                    batch_vectors.append([0.0] * embedding_dim)
            if len(batch_vectors) < len(batch_texts):
                batch_vectors.extend([[0.0] * embedding_dim] * (len(batch_texts) - len(batch_vectors)))
            all_embeddings.extend(batch_vectors)
        except Exception as e:
            print(f"      [Embedding Error] Chunk {i}: {e}")
            all_embeddings.extend([[0.0] * embedding_dim] * len(batch_texts))
            
        time.sleep(1) 
        
    matrix = np.array(all_embeddings)

    print("Projecting into 3D space (UMAP)...")
    reducer = umap.UMAP(n_components=3, n_neighbors=15, min_dist=0.1, random_state=42)
    projections = reducer.fit_transform(matrix)
    
    df['x'], df['y'], df['z'] = projections[:, 0], projections[:, 1], projections[:, 2]

    print("Identifying Geopolitical Islands (HDBSCAN)...")
    clusterer = HDBSCAN(min_cluster_size=3) 
    df['cluster_id'] = clusterer.fit_predict(projections)

    df.to_csv('data/vector_mapped_data.csv', index=False)
    print(f"--- Vector Mapping Complete. {len(df)} points locked! ---")

if __name__ == "__main__":
    generate_embeddings()