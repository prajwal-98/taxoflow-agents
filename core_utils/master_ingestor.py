import pandas as pd
import os
from datetime import datetime
from core_utils.triage_gatekeeper import TriageGatekeeper

class MasterIngestor:
    def __init__(self):
        print("Architect Status: Initializing Master Ingestor...")
        # Initialize our AI router
        self.gatekeeper = TriageGatekeeper()
        
        # Define the centralized map of Domain -> CSV Path
        self.domain_map = {
            "geopolitics": "geopolitics/data/synthetic_geopol_data.csv",
            "urban_pulse": "urban_pulse/data/raw_qcomm_reviews.csv"
        }

    def get_timestamp(self):
        """Standardizes date format for all domains."""
        return datetime.now().strftime("%d/%m/%Y")

    def process_and_route(self, raw_input_text: str):
        """Processes text through AI and identifies the target path."""
        print(f"Ingesting: {raw_input_text[:50]}...")
        
        # 1. Ask the Gatekeeper where this belongs
        classification = self.gatekeeper.route_input(raw_input_text)
        domain = classification.get("domain", "unknown")
        
        # 2. Match domain to the correct file path
        target_path = self.domain_map.get(domain)
        
        if not target_path:
            print(f"Architect Alert: Domain '{domain}' not recognized. Routing to 'unknown' bucket.")
            return "unknown", None
            
        print(f"Decision: Route to -> {domain.upper()} (Path: {target_path})")
        return domain, target_path


    def _map_to_schema(self, domain, raw_text):
        """Standardizes data structure based on the target domain's CSV schema."""
        timestamp = self.get_timestamp()
        
        if domain == "urban_pulse":
            # Matching the 10-column Urban Pulse Master Schema
            return {
                "review_id": f"manual-{os.urandom(4).hex()}",
                "date": timestamp,
                "city": "Unknown", # Could be extracted via another agent later
                "platform": "Manual_Entry",
                "category": "Uncategorized",
                "brand": "General",
                "delivery_time": 0,
                "order_context": "Direct_Ingest",
                "raw_text": raw_text,
                "star_rating": 3
            }
            
        elif domain == "geopolitics":
            # Matching the Geopolitics Swarm Schema
            return {
                "event_date": timestamp,
                "location": "Global",
                "event_description": raw_text,
                "risk_level": "Medium",
                "impact_area": "Supply Chain",
                "audit_status": "Pending_Review"
            }
        
        return {"raw_data": raw_text, "timestamp": timestamp}

    def save_data(self, mapped_data, target_path):
        """Appends structured data safely with quote protection."""
        try:
            new_row_df = pd.DataFrame([mapped_data])
            file_exists = os.path.isfile(target_path)
            
            # THE CRITICAL FIX: Add quoting=csv.QUOTE_ALL
            new_row_df.to_csv(
                target_path, 
                mode='a', 
                index=False, 
                header=not file_exists,
                quoting=csv.QUOTE_ALL  # <--- Forces quotes around every field
            )
            print(f"✅ Success: Data committed to {target_path}")
            return True
        except Exception as e:
            print(f"❌ Append Error: {e}")
            return False

    def run_ingest(self, raw_text: str):
        """The complete E2E ingestion flow."""
        # 1. Triage & Route (Step 2)
        domain, target_path = self.process_and_route(raw_text)
        
        if not target_path:
            return "Failed: No route found."
            
        # 2. Map to Schema (Step 3)
        mapped_data = self._map_to_schema(domain, raw_text)
        
        # 3. Commit to Disk (Step 4)
        success = self.save_data(mapped_data, target_path)
        
        return "Success" if success else "Failed: Append Error."

# --- INTEGRATION TEST BLOCK ---
if __name__ == "__main__":
    ingestor = MasterIngestor()
    
    # Test Case 1: Consumer Sentiment (Urban Pulse)
    print("\n--- TEST 1: CONSUMER FEEDBACK ---")
    ingestor.run_ingest("My Kwality Wall's ice cream was totally melted when it arrived via Zepto. Very disappointed.")
    
    # Test Case 2: Supply Chain Risk (Geopolitics)
    print("\n--- TEST 2: MACRO RISK ---")
    ingestor.run_ingest("Port strikes in Gujarat are likely to disrupt raw material supply for the Home Care division.")