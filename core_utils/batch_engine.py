import pandas as pd
import json
import time
from google import genai
from config import Config

client = genai.Client(api_key=Config.GEMINI_API_KEY)

def get_working_model():
    """Dynamically fetch the working model for this specific API key."""
    try:
        available = {m.name for m in client.models.list()}
        fallbacks = [
            "models/gemini-2.5-flash-lite",
            "models/gemini-flash-lite-latest",
            "models/gemini-1.5-flash"
        ]
        for f in fallbacks:
            if f in available:
                return f
        return sorted(available)[0] if available else "gemini-1.5-flash"
    except:
        return "gemini-1.5-flash"

def prepare_batch_jsonl(csv_path="synthetic_geopol_data.csv", jsonl_path="batch_payload.jsonl"):
    print("--- 1. Packaging Data for Cloud Batch ---")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("Error: CSV not found.")
        return None
    
    with open(jsonl_path, "w") as f:
        for index, row in df.iterrows():
            prompt = f"""Act as a Geopolitical Intelligence Swarm.
Analyze this raw text: "{row['raw_text']}"
1. WORKER: Categorize into a 'primary_topic' (Trade, Energy, Security).
2. WORKER: Assign a 'sentiment_score' from -1.0 to 1.0.
3. CRITIC: Based on {row['country']} in {row['event_year']}, provide a 1-sentence 'truth_audit'.
Return ONLY valid JSON."""
            
            request_obj = {
                "id": f"row_{index}", # 'id' is often preferred over 'key' in v1
                "request": {
                    "contents": [{"parts": [{"text": prompt}]}],
                }
            }
            f.write(json.dumps(request_obj) + "\n")
            
    print(f"Packaged {len(df)} rows into {jsonl_path}.")
    return jsonl_path

def trigger_cloud_batch():
    jsonl_path = prepare_batch_jsonl()
    if not jsonl_path: return

    working_model = get_working_model()
    print(f"--- 2. Uploading Payload (Targeting: {working_model}) ---")
    
    try:
        uploaded_file = client.files.upload(file=jsonl_path, config={'mime_type': 'text/plain'})
        print(f"Upload secure. File URI: {uploaded_file.uri}")
        
        print("--- 3. Initiating Asynchronous Batch Job ---")
        # Creating the batch job with the dynamically found model
        batch_job = client.batches.create(
            model=working_model, 
            src=uploaded_file.name,
        )
        print(f"Batch Job Active! ID: {batch_job.name}")
        
        print("--- 4. Monitoring Remote Execution ---")
        while True:
            job_status = client.batches.get(name=batch_job.name)
            state_str = str(job_status.state)
            print(f"[{time.strftime('%H:%M:%S')}] Server Status: {state_str}...")
            
            if "SUCCEEDED" in state_str:
                print("\nBatch Complete! Data is ready for download.")
                break
            elif "FAILED" in state_str or "CANCELLED" in state_str:
                print(f"\nArchitect Alert: Job terminated. State: {state_str}")
                break
                
            time.sleep(30)
            
    except Exception as e:
        print(f"Batch API Error: {e}")
        print("Architect Note: Free-tier keys sometimes block Batch API access. If this fails, rely on the agent_engine.py backoff script.")

if __name__ == "__main__":
    trigger_cloud_batch()