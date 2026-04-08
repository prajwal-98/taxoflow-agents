import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class ShadowAgent:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"
        self.input_path = "urban_pulse/data/vector_mapped_data.csv"
        self.output_path = "urban_pulse/data/shadow_insights.json"

    def execute_competitive_analysis(self):
        if not os.path.exists(self.input_path):
            print(f"CRITICAL: {self.input_path} not found. Shadow Agent halting.")
            return

        # 1. Load the mapped data
        df_mapped = pd.read_csv(self.input_path)
        
        # 2. The Pivot: Aggregate SLA metrics by Category, Brand, and Platform
        print("Shadow Agent: Aggregating cross-platform SLA metrics...")
        platform_pivot = df_mapped.groupby(['category', 'brand', 'platform'])[['star_rating', 'delivery_time']].mean().round(2).reset_index()
        
        # Convert to a condensed string for the LLM payload
        payload_str = platform_pivot.to_csv(index=False)

        # 3. Construct the LLM Prompt
        shadow_prompt = f"""
        Act as a Competitive Intelligence Analyst for Unilever Q-Commerce.
        Analyze the following aggregated performance metrics across different delivery platforms:
        
        {payload_str}
        
        Determine the 'Winning Platform' and 'Losing Platform' for each Category/Brand combination based on Star Rating and Delivery Time.
        
        Return ONLY a strictly valid JSON object using this exact nested structure:
        {{
            "Category_Name": {{
                "Brand_Name": {{
                    "Winning_Platform": "Name of best platform",
                    "Losing_Platform": "Name of worst platform",
                    "Root_Insight": "One concise sentence explaining the variance (e.g., 'Zepto is 12 mins faster on average, preserving cold chain.')"
                }}
            }}
        }}
        """

        # 4. Execute the LLM Call
        try:
            print("Shadow Agent: Evaluating platform variances...")
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=shadow_prompt
            )
            
            # Clean JSON formatting
            raw_res = response.text.strip()
            if "```json" in raw_res:
                raw_res = raw_res.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_res:
                raw_res = raw_res.split("```")[1].strip()
                
            shadow_insights_dict = json.loads(raw_res)
            
            # 5. Save the Output Contract
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            with open(self.output_path, 'w') as f:
                json.dump(shadow_insights_dict, f, indent=4)
                
            print(f"SUCCESS: Competitive insights saved to {self.output_path}")

        except Exception as e:
            print(f"Shadow Agent Execution Failed: {e}")

if __name__ == "__main__":
    agent = ShadowAgent()
    agent.execute_competitive_analysis()