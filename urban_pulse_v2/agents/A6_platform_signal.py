import os
import json
from google import genai
from core.schema import UrbanPulseState

def platform_signal_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 6: Extracts competitive intelligence and market positioning signals.
    Identifies mentions of rival platforms and relative performance benchmarks.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A6_reasoning"] = "Error: No data available for platform signal analysis."
        return state

    try:
        # Initialize the 2026 SDK Client
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        # Sampling data to identify comparative language
        review_samples = df["Review Text"].sample(min(20, len(df))).tolist()
        
        prompt = f"""
        Act as a Competitive Intelligence Analyst for the Indian Q-Commerce market.
        
        Competitors to track: Zepto, Blinkit, Swiggy Instamart, BigBasket (BB Now), Dunzo.
        
        Task:
        1. Identify any reviews that explicitly or implicitly compare the current platform 
           to a competitor.
        2. Determine the 'Market Sentiment': Is the current platform winning or losing 
           in these specific comparisons?
        3. Extract 'Feature Gaps': What does the competitor have that the customer misses here?
        
        Reviews:
        {review_samples}
        
        Output ONLY a valid JSON object with:
        "competitor_mentions": list of strings,
        "sentiment_bias": str (Winning/Neutral/Losing),
        "key_benchmarks": list of strings (e.g., "Better delivery tracking", "Fresher vegetables"),
        "analysis_summary": str
        """

        # Using Gemini 3 Flash for competitive pattern recognition
        response = client.models.generate_content(
            model="gemini-3-flash",
            contents=prompt
        )
        
        # Parse the Competitive Intelligence Data
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(raw_text)
        
        # Update State
        state["A6_market_insights"] = data
        
        reasoning_steps.append("Status: Competitive Benchmarking complete.")
        reasoning_steps.append(f"Competitors Detected: {', '.join(data.get('competitor_mentions', ['None']))}")
        reasoning_steps.append(f"Market Positioning: Currently {data.get('sentiment_bias')} in comparative feedback.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Platform Signal Agent Error: {str(e)}")

    # Update State Reasoning
    state["A6_reasoning"] = "\n".join(reasoning_steps)
    
    # Navigation Logic
    if 6 not in state["completed_steps"]:
        state["completed_steps"].append(6)
    
    # Move to the final Novelty Score Agent (A7)
    state["current_step"] = 7
    
    return state