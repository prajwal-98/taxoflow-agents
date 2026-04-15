import pandas as pd
from core.schema import UrbanPulseState
from utils.llm_client import generate_response


def category_escalation_node(state: UrbanPulseState) -> UrbanPulseState:
    """
    Step 5 — Category & Escalation (A5)

    - Convert clusters into business actions
    - Assign category, priority, escalation teams
    - Provide reasoning and impact
    """

    clusters = state.get("A4_output", {}).get("clusters", [])
    df = state.get("filtered_df")

    reasoning_steps = []

    if not clusters or df is None or df.empty:
        state["A5_output"] = []
        state["A5_reasoning"] = "No cluster data available"
        return state

    actions_output = []

    try:
        for cluster in clusters:

            name = cluster.get("name", "")
            description = cluster.get("description", "")
            signals = cluster.get("signals", [])
            examples = cluster.get("examples", [])

            # -------------------------------
            # LLM: BUSINESS MAPPING
            # -------------------------------
            prompt = f"""
            You are a Q-Commerce Business Operations Expert.

            Cluster:
            Name: {name}
            Description: {description}
            Signals: {signals}

            Task:
            Convert this into a business action plan.

            Output STRICT JSON:

            {{
              "category": "Issue category (e.g., Delivery, Product, Service)",
              "priority": "High / Medium / Low",
              "escalation_teams": ["Team1", "Team2"],
              "reason": "Why this needs attention"
            }}
            """

            try:
                response = generate_response(prompt, state)

                if not isinstance(response, dict):
                    response = {}

            except:
                response = {}

            # -------------------------------
            # FALLBACK LOGIC
            # -------------------------------
            category = response.get("category") or _fallback_category(name)
            priority = response.get("priority") or _fallback_priority(cluster)
            escalation = response.get("escalation_teams") or _fallback_escalation(category)
            reason = response.get("reason") or f"Issues related to {name} impacting customer experience"

            # -------------------------------
            # IMPACT SUMMARY
            # -------------------------------
            affected_reviews = cluster.get("size", 0)

            cities = df.get("city", pd.Series()).dropna().unique().tolist()
            platforms = df.get("platform", pd.Series()).dropna().unique().tolist()

            # -------------------------------
            # FINAL OBJECT
            # -------------------------------
            actions_output.append({
                "issue_category": category,
                "priority": priority,
                "escalation_teams": escalation,
                "reason": reason,
                "impact": {
                    "affected_reviews_percent": affected_reviews,
                    "cities": cities[:3],
                    "platforms": platforms[:3]
                },
                "supporting_reviews": examples[:5]
            })

        state["A5_output"] = actions_output
        reasoning_steps.append(f"{len(actions_output)} business actions generated")

    except Exception as e:
        state["A5_output"] = []
        reasoning_steps.append(f"Error: {str(e)}")

    # -------------------------------
    # STATE UPDATE
    # -------------------------------
    state["A5_reasoning"] = "\n".join(reasoning_steps)

    steps = state.get("completed_steps", [])
    if 5 not in steps:
        steps.append(5)

    state["completed_steps"] = steps
    state["current_step"] = 6

    return state


# =========================================================
# FALLBACK HELPERS
# =========================================================

def _fallback_category(name):
    text = name.lower()

    if "delivery" in text:
        return "Delivery"

    if "product" in text:
        return "Product"

    return "Service"


def _fallback_priority(cluster):
    size = cluster.get("size", 0)

    if size >= 35:
        return "High"

    if size >= 20:
        return "Medium"

    return "Low"


def _fallback_escalation(category):
    if category == "Delivery":
        return ["Logistics Team", "Operations"]

    if category == "Product":
        return ["Inventory Team", "Warehouse"]

    return ["Customer Support"]