import pandas as pd
import json
import time
from google import genai
from utils.config import Config

Config.validate_setup()
client = genai.Client(api_key=Config.GEMINI_API_KEY)

def _is_429(err: Exception) -> bool:
    msg = str(err).lower()
    return "429" in msg or "resource_exhausted" in msg


def _harvest_working_model() -> str:
    """
    Model Harvester pattern:
    - List all models visible to this API key
    - Filter for likely-high-quota models (name contains 'flash' or '8b')
    - Probe models with a tiny request; lock onto the first that does NOT 429
    """
    available = [m.name for m in client.models.list() if getattr(m, "name", None)]
    if not available:
        raise ValueError("CRITICAL: No models returned by client.models.list().")

    candidates = [m for m in available if ("flash" in m.lower() or "8b" in m.lower())]
    # De-prioritize known capped aliases/buckets if others exist.
    deprioritized = {"models/gemini-2.5-flash-lite", "models/gemini-flash-lite-latest"}
    candidates = sorted(candidates, key=lambda m: (m in deprioritized, m))

    if not candidates:
        raise ValueError("CRITICAL: No candidate models matched 'flash' or '8b'.")

    test_prompt = "Return ONLY valid JSON: {\"ok\": true}"
    for model_name in candidates:
        try:
            resp = client.models.generate_content(model=model_name, contents=test_prompt)
            text = (resp.text or "").strip()
            if not text:
                # Treat empty as non-working; try next.
                continue
            print(f"Architect Note: Model Harvester locked onto '{model_name}'.")
            return model_name
        except Exception as e:
            if _is_429(e):
                continue
            # Not a 429: could be not supported for generateContent; try next.
            continue

    raise ValueError("CRITICAL: No working model found (all candidates 429 or unsupported).")


def get_working_model() -> str:
    """
    Selects a model that is actually usable right now (not 429) for this API key.
    """
    try:
        return _harvest_working_model()
    except Exception as e:
        print(f"Architect Note: Model Harvester failed ({e}).")
        # As a last resort, keep previous behavior: try a reasonable default.
        return "models/gemini-2.0-flash"


def _is_missing_truth_audit(value) -> bool:
    # Treat NaN, empty string, and literal "None" (case-insensitive) as missing.
    if pd.isna(value):
        return True
    s = str(value).strip()
    return s == "" or s.lower() == "none"


def _extract_retry_seconds(err: Exception) -> float | None:
    """
    Best-effort parser for retry hints like:
      "Please retry in 59.03s."
      or details: 'retryDelay': '59s'
    """
    msg = str(err)
    lowered = msg.lower()
    if "retry in" in lowered:
        # Very small heuristic parser to avoid regex dependency.
        try:
            tail = lowered.split("retry in", 1)[1].strip()
            # tail looks like "59.03s.', ..." or "59s.', ..."
            num = ""
            for ch in tail:
                if ch.isdigit() or ch == ".":
                    num += ch
                elif num:
                    break
            return float(num) if num else None
        except Exception:
            return None
    if "retrydelay" in lowered:
        try:
            # look for "... retryDelay': '59s' ..."
            tail = msg.split("retryDelay", 1)[1]
            digits = ""
            for ch in tail:
                if ch.isdigit():
                    digits += ch
                elif digits:
                    break
            return float(digits) if digits else None
        except Exception:
            return None
    return None

def recover_missing_data():
    print("--- TaxoFlow Agent Swarm: Checkpoint Recovery Mode ---")
    df = pd.read_csv('data/processed_geopol_data.csv')
    working_model = get_working_model()
    
    # Identify rows where the agent failed previously
    missing_mask = df["truth_audit"].apply(_is_missing_truth_audit)
    missing_count = missing_mask.sum()
    
    if missing_count == 0:
        print("Architect Status: All rows perfectly tagged. No recovery needed.")
        return

    print(f"Found {missing_count} rows missing intelligence. Resuming extraction...")
    print("Pacing at 7 seconds per row to guarantee bypass of the 15 RPM limit.")
    
    for index, row in df[missing_mask].iterrows():
        print(f"      Recovering Row {index+1}/{len(df)}...")
        prompt = f"""Act as a Geopolitical Intelligence Swarm.
Analyze this raw text: "{row['raw_text']}"
1. WORKER: Categorize into a 'primary_topic' (Trade, Energy, Security, etc).
2. WORKER: Assign a 'sentiment_score' from -1.0 to 1.0.
3. CRITIC: Based on {row['country']} in {row['event_year']}, provide a 1-sentence 'truth_audit'.
Return ONLY valid JSON with keys: 'primary_topic', 'sentiment_score', 'truth_audit'."""
        
        try:
            resp = client.models.generate_content(model=working_model, contents=prompt)
            clean_json = resp.text.replace('```json', '').replace('```', '').strip()
            agent_data = json.loads(clean_json)
            
            df.at[index, 'primary_topic'] = agent_data.get('primary_topic')
            df.at[index, 'sentiment_score'] = float(agent_data.get('sentiment_score', 0.0))
            df.at[index, 'truth_audit'] = agent_data.get('truth_audit')

            # Checkpoint after each successful row to prevent data loss.
            df.to_csv('data/processed_geopol_data.csv', index=False)
        except Exception as e:
            print(f"      [Failed] Row {index+1}: {e}")

            # If the API returns a retry hint, respect it (daily quota won't fix,
            # but minute-level throttles will).
            retry_s = _extract_retry_seconds(e)
            sleep_s = max(7.0, retry_s) if retry_s is not None else 7.0
            time.sleep(sleep_s)
            continue

        # Strict pacing: always 7 seconds between successful requests (<= ~8.5 RPM).
        time.sleep(7)

    print("--- Recovery Complete! Data locked and saved. ---")

if __name__ == "__main__":
    recover_missing_data()