import pandas as pd
import json
import os
from google import genai
from core_utils.config import Config

class EscalationEngine:
    def __init__(self):
        Config.validate_setup()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview"
        self.input_path = "urban_pulse/data/vector_mapped_data.csv"
        self.output_path = "urban_pulse/data/escalation_results.json"

    def process_escalations(self):
        if not os.path.exists(self.input_path):
            print(f"CRITICAL: {self.input_path} missing.")
            return

        # 1. Standardized Load
        df = pd.read_csv(self.input_path, on_bad_lines='skip', engine='python')
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Logic: Target High-Value, Low-Rating Clusters
        # Group by cluster to find collective failure points
        cluster_stats = df.groupby('cluster').agg({
            'star_rating': 'mean',
            'cart_value_inr': 'sum'
        }).reset_index()

        # Identify clusters with avg rating < 3.0 and high revenue at risk
        high_risk_clusters = cluster_stats[
            (cluster_stats['star_rating'] < 3.0) & 
            (cluster_stats['cluster'] != -1)
        ].sort_values(by='cart_value_inr', ascending=False)

        escalation_dict = {}

        for _, row in high_risk_clusters.head(5).iterrows():
            c_id = int(row['cluster'])
            samples = df[df['cluster'] == c_id].head(10)['raw_text'].tolist()
            
            prompt = f"""
            Identify financial risk and suggest an automated action for this cluster:
            {samples}
            
            Total Revenue at Risk: INR {row['cart_value_inr']}
            
            Return JSON:
            {{
                "churn_probability": "High/Medium/Low",
                "financial_risk_driver": "Short reason",
                "automated_action": "e.g., Issue 100 INR refund to all in cluster"
            }}
            """
            
            try:
                res = self.client.models.generate_content(model=self.model_id, contents=prompt)
                res_text = res.text.strip()
                if "```json" in res_text:
                    res_text = res_text.split("```json")[1].split("```")[0].strip()
                
                escalation_dict[str(c_id)] = json.loads(res_text)
                escalation_dict[str(c_id)]['revenue_at_stake'] = float(row['cart_value_inr'])
            except Exception as e:
                print(f"Escalation Error for Cluster {c_id}: {e}")

        # 3. Save Artifact
        with open(self.output_path, 'w') as f:
            json.dump(escalation_dict, f, indent=4)
        print(f"SUCCESS: Escalation feed updated at {self.output_path}")

if __name__ == "__main__":
    engine = EscalationEngine()
    engine.process_escalations()