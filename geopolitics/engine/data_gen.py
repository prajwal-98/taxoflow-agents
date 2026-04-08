import pandas as pd
import json
import time
import os
import random
from google import genai  # <--- CRITICAL FIX: The new 2026 import path
from core_utils.config import Config

DEFAULT_MODEL = os.getenv("GEMINI_MODEL") or "gemini-3.1-flash-lite-preview"

_CLIENT: genai.Client | None = None
_MODEL_NAMES_CACHE: set[str] | None = None


def _is_retryable_error(exc: Exception) -> bool:
    """
    Best-effort retry classifier across google-genai / transport errors.
    We treat quota/rate-limit and transient server/network issues as retryable.
    """
    msg = str(exc).lower()
    retry_markers = [
        "429",
        "resource_exhausted",
        "rate limit",
        "quota",
        "too many requests",
        "503",
        "service unavailable",
        "500",
        "internal",
        "timeout",
        "temporarily unavailable",
        "connection reset",
        "connection aborted",
        "ssl",
    ]
    return any(m in msg for m in retry_markers)


def _sleep_seconds_for_attempt(attempt: int, *, min_seconds: float = 30.0, max_seconds: float = 300.0) -> float:
    """
    Exponential backoff with jitter, with a hard minimum wait.
    attempt=0 is the first retry sleep (after first failure).
    """
    # Exponential backoff (30, 60, 120, 240, ...) capped, plus small jitter.
    backoff = min_seconds * (2 ** attempt)
    jitter = random.uniform(0.0, 3.0)
    return min(max_seconds, max(min_seconds, backoff + jitter))


def _get_client() -> genai.Client:
    # Ensure `.env` was loaded (Config imports dotenv.load_dotenv()) and the key exists.
    Config.validate_setup()

    # Also verify the env var is actually present at runtime (guards against import-order issues).
    api_key = os.getenv("GEMINI_API_KEY") or Config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("CRITICAL: GEMINI_API_KEY missing (dotenv load may have failed).")

    global _CLIENT
    if _CLIENT is None:
        _CLIENT = genai.Client(api_key=api_key)
    return _CLIENT


def _get_available_model_names(client: genai.Client) -> set[str]:
    global _MODEL_NAMES_CACHE
    if _MODEL_NAMES_CACHE is None:
        _MODEL_NAMES_CACHE = {m.name for m in client.models.list()}
    return _MODEL_NAMES_CACHE


def _resolve_model_name(client: genai.Client, requested: str) -> str:
    """
    Prefer the requested model, but fall back when it isn't available for this key/API.

    The google-genai SDK returns model names like 'models/gemini-2.0-flash' from list().
    Some endpoints accept short names too, but we keep fallbacks in the listed form.
    """
    requested = (requested or "").strip()
    if not requested:
        requested = "gemini-3.1-flash-lite-preview"

    names = _get_available_model_names(client)

    # Try both short and fully-qualified forms for the requested model.
    requested_candidates = [requested]
    if not requested.startswith("models/"):
        requested_candidates.append(f"models/{requested}")

    for cand in requested_candidates:
        if cand in names:
            return cand

    # Fall back to an available flash model (prefer "lite" to reduce cost/pressure).
    fallbacks = [
        "models/gemini-flash-lite-latest",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash-lite-001",
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
    ]
    for fb in fallbacks:
        if fb in names:
            print(f"Architect Note: Requested model '{requested}' unavailable; using fallback '{fb}'.")
            return fb

    # Last resort: pick the first model the API lists (stable but not ideal).
    if names:
        chosen = sorted(names)[0]
        print(f"Architect Note: No preferred flash models found; using '{chosen}'.")
        return chosen

    # If listModels fails or returns nothing, just try the requested value.
    return requested

def generate_synthetic_batch(country, scenario, *, model: str = DEFAULT_MODEL, max_retries: int = 6):
    """Generates grounded data using the new 2026 GenAI SDK."""
    prompt = f"""
    Act as a Geopolitical Data Scientist. Generate 20 unique social media/news data points 
    for the year {scenario['year']} in {country}.
    Context: {scenario['focus']}
    Narrative: {scenario['narrative']}
    Format: Return ONLY a JSON list with: 'event_year', 'country', 'source', 'raw_text'.
    """
    
    client = _get_client()
    model = _resolve_model_name(client, model)

    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(model=model, contents=prompt)

            # Clean the response to ensure it's valid JSON
            clean_json = (response.text or "").replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            if not isinstance(data, list):
                raise ValueError("Model returned non-list JSON; expected a JSON list.")
            return data
        except Exception as e:
            last_err = e
            retryable = _is_retryable_error(e)
            if attempt >= max_retries or not retryable:
                print(
                    f"Architect Alert: Batch failed for {country}. "
                    f"Retryable={retryable}. Attempts={attempt + 1}/{max_retries + 1}. Error: {e}"
                )
                return []

            sleep_s = _sleep_seconds_for_attempt(attempt, min_seconds=30.0, max_seconds=300.0)
            print(
                f"Architect Alert: Batch failed for {country}. "
                f"Retrying in {sleep_s:.1f}s (attempt {attempt + 1}/{max_retries})... Error: {e}"
            )
            time.sleep(sleep_s)

    print(f"Architect Alert: Batch failed for {country}. Error: {last_err}")
    return []

def run_firehose():
    all_data = []
    print(f"--- Starting 2026 SDK Firehose: TaxoFlow-Agents ---")
    
    for country, scenario in Config.TARGET_SCENARIOS.items():
        print(f"Generating data for {country}...")
        batch = generate_synthetic_batch(country, scenario)
        if batch:
            all_data.extend(batch)
            print(f"Batch complete. Rows gathered: {len(all_data)}")
        time.sleep(1)  # Small pacing between batches
            
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("geopolitics/data/synthetic_geopol_data.csv", index=False)
        print("--- Firehose complete. CSV saved! ---")
    else:
        print("--- Firehose Error: No rows generated. Check API Key. ---")

if __name__ == "__main__":
    run_firehose()