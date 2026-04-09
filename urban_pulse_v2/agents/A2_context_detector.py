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
    # FIX 1: Use the filtered_df so it respects the Global Lock!
    df = state.get("filtered_df")
    
    # FIX 2: Safely handle the multiselect list to get a string
    active_filters = state.get("active_filters", {})
    city_list = active_filters.get("city", ["Bangalore"])
    city = city_list[0] if isinstance(city_list, list) and len(city_list) > 0 else "Bangalore"
    
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
        print("clientclientclient", client)
        # We sample reviews to detect the 'vibe' and specific local issues
        # Using .get() for safety in case 'raw_text' somehow goes missing]
        print("dfdfdfdfdf", df)
        sample_reviews = df.get("raw_text", pd.Series()).head(10).tolist()
        print("sample_reviewssample_reviews",sample_reviews)
        prompt = f"""
        Act as a Local Cultural Analyst and Q-Commerce Specialist for the city of {city}.
        
        Contextual Grounding:
        The following slang/terms are common in {city} Q-Commerce feedback: {slang_reference}
        
        Task:
        Analyze the provided reviews. Identify if customers are using local nuances to 
        describe issues (e.g., delivery speed, product quality, or courier behavior).
        
        Reviews:
        {sample_reviews}
        
       Output a highly compressed summary covering:
        1. Localized Sentiment
        2. Slang Match
        3. Operational Context

        CRITICAL CONSTRAINT: The entire output MUST be strictly 2 to 3 lines maximum. Do not use bullet points or long explanations. Be brutally concise.
        """

        # Using Gemini 3.1 Flash Preview
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
            config={
            "max_output_tokens": 350,  # Limits output to ~75 words (approx 2-3 lines)
            "temperature": 0.1         # Lower temperature makes it more "to the point"
            }
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