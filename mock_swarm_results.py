import json
import os
import pandas as pd

# Path Configuration
DATA_DIR = "urban_pulse/data/"
ANALYSIS_PATH = os.path.join(DATA_DIR, "cluster_insights.json")
ESCALATION_PATH = os.path.join(DATA_DIR, "escalation_results.json")
SHADOW_PATH = os.path.join(DATA_DIR, "shadow_insights.json")

def inject_mock_data():
    # 1. Ensure Directory Exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # 2. Mock Cluster Analyst Output (Tab 3)
    cluster_insights = {
        "0": {
            "cluster_title": "The Midnight Melt Crisis",
            "root_cause": "Delivery delays > 40 mins during peak Mumbai humidity affecting frozen categories.",
            "impact_level": "High"
        },
        "1": {
            "cluster_title": "Silk Board Logistics Friction",
            "root_cause": "Traffic congestion in Bangalore 'Last Mile' causing freshness degradation for produce.",
            "impact_level": "Medium"
        },
        "2": {
            "cluster_title": "Packaging Integrity Failure",
            "root_cause": "Specific brand poly-bags tearing during multi-drop routes.",
            "impact_level": "Low"
        }
    }

    # 3. Mock Escalation Engine Output (Tab 4)
    escalation_results = {
        "0": {
            "churn_probability": "92%",
            "financial_risk_driver": "Persistent logistics failure in high-value snacking segment.",
            "automated_action": "Issue 150 INR apology voucher to all users in Cluster 0."
        },
        "1": {
            "churn_probability": "45%",
            "financial_risk_driver": "Regional traffic delays affecting recurring grocery orders.",
            "automated_action": "Notify local warehouse to re-route via 2-wheelers."
        }
    }

    # 4. Mock Shadow Agent Output (Tab 4)
    shadow_insights = {
        "Ice Cream": {
            "Magnum": {
                "Winning_Platform": "Zepto",
                "Losing_Platform": "Blinkit",
                "Root_Insight": "Zepto's cold-chain logic maintains -18°C better than Blinkit's open-bag delivery."
            }
        },
        "Snacking": {
            "Lays": {
                "Winning_Platform": "Swiggy Instamart",
                "Losing_Platform": "Zepto",
                "Root_Insight": "Instamart has better multi-pack stock availability in Delhi-NCR clusters."
            }
        }
    }

    # Write the files
    with open(ANALYSIS_PATH, 'w') as f: json.dump(cluster_insights, f, indent=4)
    with open(ESCALATION_PATH, 'w') as f: json.dump(escalation_results, f, indent=4)
    with open(SHADOW_PATH, 'w') as f: json.dump(shadow_insights, f, indent=4)

    print("--- SUCCESS: Mock Swarm Intelligence Injected ---")
    print(f"Files created: \n- {ANALYSIS_PATH}\n- {ESCALATION_PATH}\n- {SHADOW_PATH}")

if __name__ == "__main__":
    inject_mock_data()