import pandas as pd
import json
import time
import os
import random
from google import genai
from core_utils.config import Config

# --- MASTER CONFIGURATION ---
TARGET_ROWS = 1000  # Upping this to your 1k goal
BATCH_SIZE = 10
MODEL_ID = "gemini-3.1-flash-lite-preview"
OUTPUT_PATH = "urban_pulse/data/raw_qcomm_reviews.csv"

def get_client():
    Config.validate_setup()
    return genai.Client(api_key=Config.GEMINI_API_KEY)

def generate_qcomm_batch(client, batch_num):
    """Generates hyper-realistic Q-Commerce data with advanced linguistic rules."""
    
    # --- INTEGRATING YOUR RESEARCH-DRIVEN PROMPT HERE ---
    prompt = f"""
    Act as an Expert Data Engineer. Generate {BATCH_SIZE} unique Q-Commerce reviews for 2025.
    
    SCHEMA: [review_id (UUID), date (DD/MM/YYYY), city, platform, category, brand, delivery_time, order_context, raw_text (Hinglish/Slang), star_rating, cart_value_inr, surge_fee_paid]
    
    GEOGRAPHIC SLANG RULES (STRICT):
    - Bangalore: 'Silk Board scene', 'Macha', 'Sakkath', 'Adjust maadi'.
    - Mumbai: 'Fatafat', 'Full majja', 'Paisa vasool', 'Kachra'.
    - Delhi: 'Systumm hang', 'Challan kat gaya', 'Oye hoye swaad', 'Kalesh'.
    - Hyderabad: 'Baigan', 'Hau', 'Kirak', 'Zabardast'.
    - Pune: 'Kantaala', 'Bhaari', 'Vishesh', 'Naad khula'.

    LOGIC & CORRELATION RULES:
    1. If delivery_time > 40 AND surge_fee_paid = True: The raw_text MUST complain about the platform/delay.
    2. If order_context = 'Mumbai Monsoon' AND category = 'Ice cream': Mention melting/leakage.
    3. Scenarios: IPL Finals, Silk Board Jam, PG Food Crisis, Late Night Cravings, Hangover Recovery.
    4. Slang must stay city-accurate (No 'Macha' in Delhi).

    Return ONLY a JSON list of objects. No prose.
    """

    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Architect Alert: Batch {batch_num} failed. Error: {e}")
        return []

def run_firehose():
    client = get_client()
    all_data = []
    
    print(f"--- Launching The Urban Pulse Firehose (Target: {TARGET_ROWS}) ---")
    
    batch_count = 1
    while len(all_data) < TARGET_ROWS:
        print(f"Generating Batch {batch_count} (Progress: {len(all_data)}/{TARGET_ROWS})...")
        batch = generate_qcomm_batch(client, batch_count)
        
        if batch:
            all_data.extend(batch)
            batch_count += 1
            # Batch sleep to respect Gemini 3.1 Flash-Lite Rate Limits (15 RPM)
            time.sleep(4.0) 
        else:
            print("Cooling down for 10s due to failure...")
            time.sleep(10)

    # Finalize and Save
    df = pd.DataFrame(all_data[:TARGET_ROWS])
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print("-" * 50)
    print(f"SUCCESS: {len(df)} rows saved to {OUTPUT_PATH}")
    print("-" * 50)

if __name__ == "__main__":
    run_firehose()