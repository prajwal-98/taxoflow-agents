import os
import json
from google import genai
from core.schema import UrbanPulseState
from core.constants import BUSINESS_CATEGORIES

def category_escalation_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 5: Categorizes feedback into business domains and flags critical 
    issues for immediate human intervention.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A5_reasoning"] = "Error: No data available for categorization."
        return state

    try:
        # Initialize the 2026 SDK Client
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Batching 20 reviews for efficient triage
        review_batch = df["raw_text"].head(20).tolist()
        
        prompt = f"""
        Act as a Senior Operations Manager for Q-Commerce.
        
        Categories: {BUSINESS_CATEGORIES}
        
        Task:
        1. Categorize the following reviews into the provided categories.
        2. Identify 'High-Risk' escalations (e.g., product tampering, delivery partner 
           misbehavior, missing high-value items, or safety concerns).
        
        Reviews:
        {review_batch}
        
        Output ONLY a JSON object with:
        "category_distribution": dict (category name: percentage),
        "escalations": list (objects with "original_text" and "priority_reason"),
        "summary": str
        """

        # Using Gemini 3 Flash for rapid classification
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
            config={
                    "max_output_tokens": 350, 
                    "temperature": 0.1      
                } 
        )
        
        # Parse the Triage Data
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(raw_text)
        
        # Update State
        state["A5_business_categories"] = data.get("category_distribution", {})
        state["A5_escalation_list"] = data.get("escalations", [])
        
        reasoning_steps.append("Status: Operations Triage complete.")
        reasoning_steps.append(f"Metrics: Analyzed {len(review_batch)} items for categorical distribution.")
        reasoning_steps.append(f"Alerts: {len(data.get('escalations', []))} high-risk items identified for escalation.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Category/Escalation Agent Error: {str(e)}")

    # Update State Reasoning
    state["A5_reasoning"] = "\n".join(reasoning_steps)
    
    # Navigation Logic
    if 5 not in state["completed_steps"]:
        state["completed_steps"].append(5)
    
    # Move to Platform Signal Agent (A6)
    state["current_step"] = 6
    
    return state