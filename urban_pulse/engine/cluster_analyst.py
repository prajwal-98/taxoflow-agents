import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class ClusterAnalyst:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"
        self.input_path = "urban_pulse/data/vector_mapped_data.csv"
        self.output_path = "urban_pulse/data/cluster_insights.json"

    def execute_analysis(self):
        if not os.path.exists(self.input_path):
            print(f"CRITICAL: {self.input_path} not found. Analyst halting.")
            return

        # 1. Load Data with Normalization
        df = pd.read_csv(self.input_path, on_bad_lines='skip', engine='python')
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Extract Valid Clusters (ignoring noise cluster -1)
        valid_clusters = df[df['cluster'] != -1]['cluster'].unique()
        
        if len(valid_clusters) == 0:
            print("Architect Note: No meaningful clusters found to analyze.")
            return

        cluster_insights_dict = {}

        print(f"Cluster Analyst: Deep-diving into {len(valid_clusters)} semantic islands...")

        for c_id in valid_clusters:
            # Sample data from this specific cluster for LLM context
            cluster_data = df[df['cluster'] == c_id].head(15)
            sample_text = "\n".join(cluster_data['raw_text'].tolist())
            avg_rating = cluster_data['star_rating'].mean()

            # 3. Construct the LLM Analyst Prompt
            analysis_prompt = f"""
            Act as a Lead Product Strategist at Unilever. 
            Analyze this cluster of consumer feedback and determine the root cause.
            
            CLUSTER DATA SAMPLES:
            {sample_text}
            
            Average Star Rating for this Cluster: {avg_rating:.2f}
            
            Provide a strictly valid JSON response with these keys:
            - cluster_title: A punchy 3-4 word title (e.g., 'Late Night Delivery Friction')
            - root_cause: A one-sentence technical/operational explanation.
            - impact_level: 'High', 'Medium', or 'Low' based on rating and sentiment.
            """

            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=analysis_prompt
                )
                
                # Clean and Parse JSON
                res_text = response.text.strip()
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                
                cluster_insights_dict[str(c_id)] = json.loads(res_text)
                print(f"   > Successfully analyzed Cluster {c_id}: {cluster_insights_dict[str(c_id)]['cluster_title']}")

            except Exception as e:
                print(f"   > Error analyzing cluster {c_id}: {e}")

        # 4. Save the Final Contract
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(cluster_insights_dict, f, indent=4)
        
        print(f"SUCCESS: Analysis artifacts locked at {self.output_path}")

if __name__ == "__main__":
    analyst = ClusterAnalyst()
    analyst.execute_analysis()