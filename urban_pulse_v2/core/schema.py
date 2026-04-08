from typing import TypedDict, List, Dict, Optional, Any
import pandas as pd

class UrbanPulseState(TypedDict):
    """
    The Central State for UrbanPulse V2.
    Acts as the source of truth for all 7 Agents and the UI components.
    """
    # --- GLOBAL DATA & FILTERS ---
    raw_df: Optional[pd.DataFrame]          # Original uploaded dataset
    filtered_df: Optional[pd.DataFrame]     # Dataset after City/Platform/Date filters are locked
    active_filters: Dict[str, Any]          # {Date: ..., City: ..., Platform: ...}
    filters_locked: bool                    # UI State: True = filters applied and locked
    
    # --- NAVIGATION & PROGRESS ---
    current_step: int                       # 1 to 7 tracking the active module
    completed_steps: List[int]              # IDs of steps that have finished successfully
    
    # --- A1: GATEKEEPER ---
    A1_is_valid: bool                       # Hero Block: Valid/Invalid status
    A1_routing_decision: str                # e.g., "Q-Commerce Intelligence"
    A1_validation_checks: Dict[str, bool]   # Schema, Domain, and Required field statuses
    A1_reasoning: str                       # Markdown for the "Why this decision?" panel
    
    # --- A2: CONTEXT DETECTOR ---
    A2_context_signals: List[Dict[str, Any]]# Signals extracted per review
    A2_slang_map: Dict[str, str]            # Localized slang interpretations found
    A2_reasoning: str                       # Agent 2 reasoning trace
    
    # --- A3: SEMANTIC SHAPER ---
    A3_vector_coords: Optional[pd.DataFrame]# x, y, z coordinates for the 3D Plotly Map
    A3_reasoning: str                       # Agent 3 reasoning trace
    
    # --- A4: CLUSTER AGENT ---
    A4_cluster_stats: Dict[str, Any]        # Persona definitions and root cause stats
    A4_reasoning: str                       # Agent 4 reasoning trace
    
    # --- A5: CATEGORY + ESCALATION AGENT ---
    A5_business_categories: Dict[str, str]  # Review ID -> Category mapping
    A5_escalation_list: List[str]           # IDs flagged for high-priority action
    A5_reasoning: str                       # Agent 5 reasoning trace
    
    # --- A6: PLATFORM SIGNAL AGENT ---
    A6_market_insights: Dict[str, Any]      # Comparative metrics (Zepto vs Competitors)
    A6_reasoning: str                       # Agent 6 reasoning trace
    
    # --- A7: NOVELTY SCORE ---
    A7_novelty_data: Dict[str, float]       # Novelty scores and trend labels
    A7_reasoning: str                       # Agent 7 reasoning trace
    
    # --- SYSTEM & LOGGING ---
    system_logs: List[str]                  # Execution timestamps and internal error tracking