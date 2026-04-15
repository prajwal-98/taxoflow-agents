import time
import json
import re
from google import genai


def extract_json(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return {}
        return {}


def generate_response(prompt: str, state: dict, temperature: float = 0.2, parse_json: bool = False):
    """
    Central LLM wrapper using NEW Gemini SDK
    """
    api_key = state.get("api_key")
    model = state.get("model", "gemini-1.5-flash")

    if not api_key:
        raise ValueError("Missing API Key in state")

    client = genai.Client(api_key=api_key)

    retries = 2

    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "temperature": temperature,
                },
            )

            raw_text = response.text

            if parse_json:
                return extract_json(raw_text)
            return raw_text  # ← return plain text by default

        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                raise e