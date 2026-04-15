from typing import Dict, Any
from langgraph.graph import StateGraph, END
from core.schema import UrbanPulseState


# Import Agents (These will be implemented in the /agents folder)
from agents.A1_gatekeeper import gatekeeper_node
from agents.A2_context_detector import context_detector_node
from agents.A3_semantic_shaper import semantic_shaper_node
from agents.A4_cluster_agent import cluster_agent_node
from agents.A5_category_escalation import category_escalation_node
from agents.A6_platform_signal import platform_signal_node
from agents.A7_novelty_score import novelty_score_node

def check_validation(state: UrbanPulseState):
    """
    Conditional logic for Agent 1.
    If the dataset is invalid, we stop the pipeline immediately.
    """
    if state.get("A1_is_valid", False):
        return "A2_context_detector"
    return "end"

def build_urban_pulse_graph():
    """
    Constructs the LangGraph for the UrbanPulse V2 Sequential Pipeline.
    """
    # 1. Initialize Graph with our Shared State Schema
    workflow = StateGraph(UrbanPulseState)

    # 2. Add Nodes for all 7 Agents
    workflow.add_node("A1_gatekeeper", gatekeeper_node)
    workflow.add_node("A2_context_detector", context_detector_node)
    workflow.add_node("A3_semantic_shaper", semantic_shaper_node)
    workflow.add_node("A4_cluster_agent", cluster_agent_node)
    workflow.add_node("A5_category_escalation", category_escalation_node)
    workflow.add_node("A6_platform_signal", platform_signal_node)
    workflow.add_node("A7_novelty_score", novelty_score_node)

    # 3. Define the Flow (Edges)
    
    # Entry Point: Always starts with Gatekeeper
    workflow.set_entry_point("A1_gatekeeper")

    # Conditional Routing from A1
    workflow.add_conditional_edges(
        "A1_gatekeeper",
        check_validation,
        {
            "A2_context_detector": "A2_context_detector",
            "end": END
        }
    )

    # Sequential Logic (A2 -> A7)
    workflow.add_edge("A2_context_detector", "A3_semantic_shaper")
    workflow.add_edge("A3_semantic_shaper", "A4_cluster_agent")
    workflow.add_edge("A4_cluster_agent", "A5_category_escalation")
    workflow.add_edge("A5_category_escalation", "A6_platform_signal")
    workflow.add_edge("A6_platform_signal", "A7_novelty_score")
    workflow.add_edge("A7_novelty_score", END)

    # 4. Compile the Graph
    return workflow.compile()

# This compiled graph can now be invoked in app.py or via a button click
urban_pulse_app = build_urban_pulse_graph()