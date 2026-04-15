import os
from core.schema import UrbanPulseState
from utils.llm_client import generate_response


def novelty_score_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 7: Calculates the 'Novelty Index' of current feedback.
    Determines if detected issues are recurring known problems or 
    emerging anomalies that require a strategic pivot.
    """
    df = state.get("filtered_df")
    reasoning_steps = []

    if df is None or df.empty:
        state["A7_reasoning"] = "Error: No data available for novelty scoring."
        return state

    try:
        context_summary = state.get("A2_context_signals", [{}])[0].get("signal_analysis", "N/A")
        persona_summary = state.get("A4_cluster_stats", {}).get("persona_summary", "N/A")
        market_intel = state.get("A6_market_insights", {}).get("analysis_summary", "N/A")

        prompt = f"""
        Act as a Strategic Innovation Lead for a Q-Commerce firm.
        
        Baseline Knowledge:
        Standard issues include: Late delivery, crushed bread, missing items, and high delivery fees.
        
        Current Pipeline Findings:
        - Local Context: {context_summary}
        - Detected Personas: {persona_summary}
        - Market Signals: {market_intel}
        
        Task:
        1. Assign a 'Novelty Score' from 0.0 to 1.0. 
           (0.0 = Business as usual/Legacy issues, 1.0 = Highly anomalous/New market shift).
        2. Identify 'Emerging Anomalies': Are there new patterns not mentioned in the baseline?
        3. Strategic Recommendation: What is the single most important action for the COO?
        
        Output ONLY a valid JSON object with:
        "novelty_score": float,
        "is_anomaly": bool,
        "anomalous_patterns": list of strings,
        "strategic_recommendation": str
        """

        response_text = generate_response(prompt, state, temperature=0.1, parse_json=True)

        state["A7_novelty_data"] = response_text

        reasoning_steps.append("Status: Final Novelty Assessment finalized.")
        reasoning_steps.append(f"Novelty Index: {response_text.get('novelty_score')} ({'High Alert' if response_text.get('is_anomaly') else 'Stable Patterns'})")
        
        recommendation = response_text.get('strategic_recommendation', '')
        reasoning_steps.append(f"Strategic Recommendation: {recommendation[:100]}...")

    except Exception as e:
        reasoning_steps.append(f"Warning: Novelty Score Agent Error: {str(e)}")

    state["A7_reasoning"] = "\n".join(reasoning_steps)

    if 7 not in state["completed_steps"]:
        state["completed_steps"].append(7)

    return state