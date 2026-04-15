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
    A1_is_valid: bool
    A1_routing_decision: str
    A1_validation_checks: Dict[str, bool]
    A1_reasoning: str
    A1_metrics: Optional[Dict[str, Any]]        # total_reviews, cities, platforms, categories
    A1_charts: Optional[Dict[str, Any]]         # platform_distribution, category_distribution, review_trend
    A1_highlights: Optional[Dict[str, Any]]     # top_platform, top_category, peak_month
    A1_data_quality: Optional[Dict[str, Any]]   # schema_valid, missing_data_ok, format_valid
    A1_sample: Optional[Any]                    # df.head(10)
    
    # --- A2: CONTEXT DETECTOR ---
    A2_output: Dict[str, Any]               
    A2_context_signals: List[Dict[str, Any]]# Signals extracted per review
    A2_slang_map: Dict[str, str]            # Localized slang interpretations found
    A2_reasoning: str                       # Agent 2 reasoning trace
    
    # --- A3: SEMANTIC SHAPER ---
    A3_output: Dict[str, Any]               # Anchor review, similar reviews list, and semantic theme
    A3_reasoning: str                       # Agent 3 reasoning trace
    
    # --- A4: CLUSTER AGENT ---
    A4_output: Dict[str, Any]               # NEW: {'summary': str, 'clusters': List[Dict], 'meta_insight': str}
    A4_reasoning: str

    # --- A5: CATEGORY + ESCALATION AGENT ---
    A5_output: List[Dict[str, Any]]         # NEW: List of actionable business dictionaries
    A5_reasoning: str
    
    # --- A6: PLATFORM SIGNAL AGENT ---
    A6_output: Dict[str, Any]               # Platform, Brand, Category, City, and Time distributions
    A6_reasoning: str
    
    # --- A7: NOVELTY SCORE ---
    A7_output: Dict[str, Any]               # NEW: slang_intelligence, city_slang, sentiment_mapping, emerging_slang
    A7_reasoning: str

    # --- A8: DECISION DASHBOARD AGENT ---
    A8_output: Dict[str, Any]               # Final synthesized story, metrics, and action plans
    
    # --- SYSTEM & LOGGING ---
    system_logs: List[str]                  # Execution timestamps and internal error tracking

    api_key: Optional[str]
    model: Optional[str]