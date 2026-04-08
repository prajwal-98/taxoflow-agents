import os
import json
import pandas as pd
from google import genai
from core.schema import UrbanPulseState

# System Instruction to ground the LLM's domain expertise
SYSTEM_INSTRUCTION = """
You are a Lead Data Auditor for a Quick-Commerce (Q-Commerce) Intelligence platform. 
Your task is to determine if customer reviews are relevant to the Q-Commerce ecosystem 
in India (e.g., Zepto, Blinkit, Swiggy Instamart, BigBasket Now).

Q-Commerce signals: Ultra-fast delivery (10-20 mins), grocery items, delivery partner behavior, 
platform-specific features like memberships.

If the data is generic e-commerce, food delivery (Zomato/Swiggy Food), or unrelated, 
it must be flagged as False.
"""

def gatekeeper_node(state: UrbanPulseState) -> UrbanPulseState:
    df = state.get("raw_df")
    checks = {"Schema": False, "Domain": False, "Required Fields": False}
    reasoning_steps = []

    # 1. Structural Validation (Early Exit if no data)
    if df is None or not hasattr(df, "columns") or df.empty:
        state["A1_is_valid"] = False
        state["A1_reasoning"] = "Critical: Dataframe not found or empty."
        state["A1_routing_decision"] = "Error"
        state["current_step"] = 1
        return state

    # 2. Schema Check
    required_columns = ["raw_text", "star_rating", "city", "platform"]
    missing = [col for col in required_columns if col not in df.columns]
    
    if not missing:
        checks["Schema"] = True
        checks["Required Fields"] = True
        reasoning_steps.append("Status: Schema Verified. All required columns present.")
    else:
        reasoning_steps.append(f"Error: Schema Failed. Missing columns: {missing}")

    # 3. Domain Triage (Agentic Reasoning)
    if checks["Schema"]:
        sample_reviews = df["raw_text"].head(5).tolist()
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        prompt = f"""
        {SYSTEM_INSTRUCTION}
        
        Analyze these samples for Q-Commerce domain alignment:
        {sample_reviews}
        
        Output ONLY a valid JSON object with:
        "is_qcommerce": bool,
        "confidence": float,
        "detected_signals": list,
        "justification": str
        """
       
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
                contents=prompt
            )
            
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(raw_text)
            
            # Robust JSON handling
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            
            if not isinstance(data, dict):
                reasoning_steps.append("Error: LLM returned invalid JSON structure.")
            elif data.get("is_qcommerce") is True:
                checks["Domain"] = True
                reasoning_steps.append(f"Status: Domain Confirmed. Justification: {data.get('justification')}")
                reasoning_steps.append(f"Detected Signals: {', '.join(data.get('detected_signals', []))}")
            else:
                reasoning_steps.append("Status: Domain Mismatch.")
                
        except Exception as e:
            reasoning_steps.append(f"Warning: LLM Triage Exception: {str(e)}")

    # 4. State Update & Routing
    is_valid = all(checks.values())
    state["A1_is_valid"] = is_valid
    state["A1_routing_decision"] = "Q-Commerce Intelligence" if is_valid else "Rejected"
    state["A1_validation_checks"] = checks
    state["A1_reasoning"] = "\n".join(reasoning_steps)
    
    if is_valid:
        # Safe list update
        steps = state.get("completed_steps", [])
        if 1 not in steps:
            steps.append(1)
        state["completed_steps"] = steps
        state["current_step"] = 2
    else:
        state["current_step"] = 1

    return state