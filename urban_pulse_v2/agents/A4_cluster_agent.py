import os
import json
from google import genai
from core.schema import UrbanPulseState

def cluster_agent_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 4: Translates semantic clusters into actionable customer personas.
    Synthesizes feedback patterns into human-centric business segments.
    """
    df = state.get("filtered_df")
    coords = state.get("A3_vector_coords")
    reasoning_steps = []

    if df is None or df.empty:
        state["A4_reasoning"] = "Error: No data available for persona clustering."
        return state

    try:
        # Initialize the 2026 SDK Client
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        # We provide a diverse sample of reviews to the LLM
        # In a full-scale version, we would pass cluster centroids
        review_samples = df["Review Text"].sample(min(20, len(df))).tolist()
        
        prompt = f"""
        Act as a Consumer Insights Strategist for Q-Commerce.
        
        Task: 
        Analyze the following review samples and group them into 3 distinct 'Customer Personas'.
        
        Reviews:
        {review_samples}
        
        For each persona, provide:
        1. A catchy Name (e.g., 'The Weekend Host', 'The Office Snacker').
        2. Core Pain Point (What is their primary complaint?).
        3. Business Impact (Why does this segment matter for retention?).
        
        Output ONLY a JSON object with the key "personas" containing a list of these details.
        """

        # Using Gemini 3 Flash for synthesis
        response = client.models.generate_content(
            model="gemini-3-flash",
            contents=prompt
        )
        
        # Parse the JSON Persona data
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(raw_text)
        
        # Update State
        state["A4_cluster_stats"] = data
        
        reasoning_steps.append("Status: Persona Synthesis complete.")
        reasoning_steps.append("Method: Zero-shot clustering via LLM summarization.")
        reasoning_steps.append(f"Output: Identified {len(data.get('personas', []))} distinct customer segments.")

    except Exception as e:
        reasoning_steps.append(f"Warning: Cluster Agent Error: {str(e)}")

    # Update State Reasoning
    state["A4_reasoning"] = "\n".join(reasoning_steps)
    
    # Navigation Logic
    if 4 not in state["completed_steps"]:
        state["completed_steps"].append(4)
    
    # Move to Category & Escalation Agent (A5)
    state["current_step"] = 5
    
    return state