import subprocess
import time
import sys

class SwarmOrchestrator:
    def __init__(self):
        # The DAG (Directed Acyclic Graph) sequence
        self.pipeline = [
            ("Semantic Shaper", "urban_pulse.engine.semantic_shaper"),
            ("Cluster Analyst", "urban_pulse.engine.cluster_analyst"),
            ("Escalation Engine", "urban_pulse.engine.escalation_agent"),
            ("Category Intelligence", "urban_pulse.engine.category_agent"),
            ("Shadow Agent", "urban_pulse.engine.shadow_agent")
        ]

    def run_pipeline(self):
        print("Architect Status: Initiating Swarm Orchestration...")
        start_time = time.time()
        
        for name, module in self.pipeline:
            print(f"\n>>> Triggering Node: {name}...")
            # Spawning isolated processes prevents memory leaks from heavy ML models
            result = subprocess.run([sys.executable, "-m", module])
            
            if result.returncode != 0:
                print(f"CRITICAL FAILURE: {name} crashed. Halting pipeline.")
                return
                
        elapsed = time.time() - start_time
        print(f"\nSWARM EXECUTION COMPLETE. Total pipeline time: {elapsed:.2f} seconds.")
        print("Dashboard is now serving fresh data.")

if __name__ == "__main__":
    orchestrator = SwarmOrchestrator()
    orchestrator.run_pipeline()