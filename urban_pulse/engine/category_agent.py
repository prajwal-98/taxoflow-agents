import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class CategoryAgent:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"

    def generate_insights(self, input_csv):
        if not os.path.exists(input_csv):
            print(f"ERROR: {input_csv} not found.")
            return

        df = pd.read_csv(input_csv)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        categories = df['category'].dropna().unique()
        print(f"Category Engine targeting: {categories}")
        
        category_map = {}

        for cat in categories:
            cat_df = df[df['category'] == cat].sort_values(by='date').tail(30)
            
            samples = cat_df.apply(lambda row: f"[{row['date'].strftime('%Y-%m-%d') if pd.notnull(row['date']) else 'Unknown'}] {row['raw_text']}", axis=1).tolist()
            text_bundle = "\n- ".join(samples)

            prompt = f"""
            Act as an FMCG Category Director for Unilever.
            Analyze these chronological reviews for the '{cat}' category:
            {text_bundle}
            
            Identify temporal trends, what customers liked, and what they disliked.
            Return ONLY a valid JSON object in this exact format:
            {{
                "peak_period": "Month/Event with highest positive engagement",
                "drop_period": "Month/Event with lowest engagement or highest complaints",
                "top_likes": ["Point 1", "Point 2"],
                "top_dislikes": ["Point 1", "Point 2"],
                "strategy_move": "One line of business advice"
            }}
            """

            try:
                print(f"Agent 5: Analyzing Category '{cat}'...")
                response = self.client.models.generate_content(model=self.model_id, contents=prompt)
                
                raw_res = response.text.strip()
                if "```json" in raw_res:
                    raw_res = raw_res.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_res:
                    raw_res = raw_res.split("```")[1].strip()
                
                category_map[str(cat)] = json.loads(raw_res)
                print(f"Category '{cat}' insights generated.")
                
            except Exception as e:
                print(f"Category '{cat}' Failed: {e}")

        output_path = "urban_pulse/data/category_insights.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(category_map, f, indent=4)
        
        print(f"\nCATEGORY INSIGHTS SAVED: {output_path}")

if __name__ == "__main__":
    agent = CategoryAgent()
    agent.generate_insights("urban_pulse/data/vector_mapped_data.csv")