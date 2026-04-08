import os
import pandas as pd
from google import genai
from core.schema import UrbanPulseState
from core.constants import CITY_SLANG_MAP

def context_detector_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 2: Injects hyper-local context and slang signals into the analysis.
    Uses the Gemini 3 Flash model to decode regional nuances.
    """
    df = state.get("raw_df")
    active_filters = state.get("active_filters", {})
    city = active_filters.get("city", "Bangalore")
    
    # Retrieve local slang from our constants
    slang_reference = CITY_SLANG_MAP.get(city, [])
    reasoning_steps = []
    
    # 2. SAFETY GUARD FIRST (Before any prints or head() calls)
    if df is None or not hasattr(df, "columns") or df.empty:
        state["A2_reasoning"] = "Error: No data available for context detection."
        return state

    try:
        # Initialize the 2026 SDK Client
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # We sample reviews to detect the 'vibe' and specific local issues
        sample_reviews = df["raw_text"].head(15).tolist()
        
        prompt = f"""
        Act as a Local Cultural Analyst and Q-Commerce Specialist for the city of {city}.
        
        Contextual Grounding:
        The following slang/terms are common in {city} Q-Commerce feedback: {slang_reference}
        
        Task:
        Analyze the provided reviews. Identify if customers are using local nuances to 
        describe issues (e.g., delivery speed, product quality, or courier behavior).
        
        Reviews:
        {sample_reviews}
        
        Output a brief summary of:
        1. Localized Sentiment (How the specific city vibe affects the feedback).
        2. Slang Match (Which local terms from the list were identified or implied).
        3. Operational Context (Specific local hurdles like weather, traffic, or festive surges).
        """

        # Using Gemini 3 Flash for contextual pattern matching
        response = client.models.generate_content(
            model="gemini-3-flash",
            contents=prompt
        )
        
        # Update State with detected signals
        state["A2_context_signals"] = [
            {"city": city, "signal_analysis": response.text}
        ]
        
        state["A2_slang_map"] = {
            "city": city,
            "applied_slang": slang_reference
        }
        
        reasoning_steps.append(f"Status: Contextual grounding applied for {city}.")
        reasoning_steps.append(f"Reference: Utilized {len(slang_reference)} local slang signals for mapping.")
        reasoning_steps.append("Analysis: Localized sentiment patterns isolated from review samples.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Context Detector Node Error: {str(e)}")

    # Update Reasoning and Step Logic
    state["A2_reasoning"] = "\n".join(reasoning_steps)
    
    if 2 not in state["completed_steps"]:
        state["completed_steps"].append(2)
    
    # Move to the Semantic Shaper (A3)
    state["current_step"] = 3
    
    return state