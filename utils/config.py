import os
from dotenv import load_dotenv

# Load Environment Variables (API Keys)
load_dotenv()

class Config:
    # 1. API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # 2. Project Scope (Narrative Anchors)
    COUNTRIES = ["India", "Australia"]
    YEAR_RANGE = (2016, 2026)
    
    # Target Events for Grounding (The "Truth" we tell the AI)
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
            raise ValueError("CRITICAL: GEMINI_API_KEY not found in .env file.")
        print("Architect Status: Configuration Locked and Validated.")

if __name__ == "__main__":
    Config.validate_setup()# config.py
