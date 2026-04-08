import json
from google import genai
from core_utils.config import Config

class TriageGatekeeper:
    def __init__(self):
        # Ensure your .env has the GEMINI_API_KEY
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"

    def route_input(self, raw_text: str):
        """
        Analyzes the input text and routes it to the correct 
        Business Group and Domain.
        """
        
        prompt = f"""
        Act as the Centralized AI Router for Unilever. 
        Analyze the following text and determine which Business Group (BG) and Pipeline it belongs to.
        
        TEXT: "{raw_text}"
        
        DOMAINS:
        1. 'geopolitics': Focuses on global risks, supply chain disruptions, war, trade policy, or macro-economic events. (BG: Home Care)
        2. 'urban_pulse': Focuses on Q-Commerce, consumer reviews, delivery speed, food quality (Ice cream, snacks), or local platform issues (Blinkit, Zepto). (BG: Personal Care)
        
        Return ONLY a JSON object with:
        {{
            "domain": "geopolitics" | "urban_pulse",
            "bg": "Home Care" | "Personal Care",
            "reasoning": "brief explanation"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=prompt
            )
            # Clean possible markdown formatting from LLM response
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"Gatekeeper Error: {e}")
            # Fallback to prevent system crash
            return {"domain": "unknown", "bg": "unknown", "reasoning": str(e)}

if __name__ == "__main__":
    # Quick Test
    gatekeeper = TriageGatekeeper()
    print(gatekeeper.route_input("The price of crude oil is affecting our transport costs."))