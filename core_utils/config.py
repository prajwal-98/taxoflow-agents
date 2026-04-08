import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Dynamic Root Path Resolution
# Resolves the absolute path of this file, then steps up twice to the workspace root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Force load the .env from the master root directory
load_dotenv(dotenv_path=ENV_PATH)

class Config:
    # 1. API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # 2. Project Scope (Geopolitics Anchors - Legacy)
    COUNTRIES = ["India", "Australia"]
    YEAR_RANGE = (2016, 2026)
    
    TARGET_SCENARIOS = {
        "Australia": {
            "year": 2020,
            "focus": "14 Grievances, Trade Sanctions, Coal/Wine bans",
            "narrative": "Strategic pivot and supply chain diversification."
        },
        "India": {
            "year": 2025,
            "focus": "U.S. Reciprocal Tariffs (50%), Steel Friction, Russian Oil Ties",
            "narrative": "Sovereign autonomy vs. trade coercion and pivot to EU-India FTA."
        }
    }
    
    # 3. Processing Settings
    TOTAL_ROWS = 20000  # Total target for the "Firehose"
    BATCH_SIZE = 50     # How many rows generated per AI call
    
    # 4. Math & UI Settings
    UMAP_COMPONENTS = 3 # For 3D Plotting
    CLUSTER_MIN_SIZE = 15 # Minimum rows to form an "Island" (HDBSCAN)
    
    @staticmethod
    def validate_setup():
        """Expert Peer Check: Ensure keys are present."""
        if not Config.GEMINI_API_KEY:
            raise ValueError(f"CRITICAL: GEMINI_API_KEY not found. Looked at: {ENV_PATH}")
        print("Architect Status: Configuration Locked. Root .env connected successfully.")

if __name__ == "__main__":
    Config.validate_setup()