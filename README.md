### 🚀 Engineering Highlights: The "Model Harvester"
During development, the pipeline encountered significant API rate-limiting challenges (429 Errors). To ensure 100% data integrity, I implemented:

- **Dynamic Model Failover:** A discovery pattern that probes the Gemini API to identify and lock onto healthy endpoints (e.g., pivoting from 2.0-Flash to 1.5-Flash-8B) when daily quotas are exhausted.
- **Surgical Checkpoint Recovery:** A recovery engine that performs a differential analysis of the dataset, "healing" only missing or corrupted rows while saving progress after every successful request.
- **Adaptive Pacing Logic:** A regex-based retry-parser that extracts server-side delay hints to adjust request frequency in real-time, maintaining a strict 15 RPM safety buffer.


# TaxoFlow-Agents: Geopolitical Intelligence Swarm

A resilient, multi-agent pipeline designed to extract, audit, and visualize geopolitical narratives in a 3D semantic space. Built for high-volume data recovery and production stability in constrained API environments.

## 🛠️ Tech Stack
- **Core Engine**: Google Gemini 2.0 / 1.5-Flash (LLM)
- **Geometry**: UMAP + HDBSCAN (3D Semantic Clustering)
- **Frontend**: Streamlit + Plotly (Interactive Audit Dashboard)
- **Infrastructure**: Resilient Model Harvester & Checkpoint Recovery

## 🚀 Engineering Highlights: The "Resilience" Layer
This project was engineered to solve real-world API instability and quota constraints:

- **Dynamic Model Harvester**: Implemented a "probe-and-lock" discovery pattern that automatically fails over to healthy API endpoints (e.g., pivoting from Gemini 2.5-Flash to 1.5-Flash-8B) when primary daily quotas are exhausted.
- **Surgical Checkpoint Recovery**: A state-aware recovery engine that identifies missing intelligence and "heals" specific data rows without re-processing the entire dataset, ensuring zero data loss during network failures.
- **Adaptive Pacing Logic**: Engineered a 7-second safety buffer and a regex-based "Retry-After" parser to stay strictly within free-tier RPM limits while maintaining high-throughput batching.

## 📂 Project Structure
- **/data**: Raw signals and processed semantic coordinates.
- **/engine**: The intelligence swarm and 3D vector math logic.
- **/ui**: The interactive dashboard and analytical visualization.
- **/utils**: Configuration management and API health checks.

## 🏃 How to Run
1. **Prepare Env**: Add your `GEMINI_API_KEY` to the `.env` file.
2. **Process Data**: `python -m engine.taxoflow_swarm`
3. **Generate Geometry**: `python -m engine.vector_memory`
4. **Launch Dashboard**: `streamlit run ui/dashboard.py`