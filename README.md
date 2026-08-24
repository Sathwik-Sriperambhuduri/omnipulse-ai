# OmniPulse AI: Real-Time Data, ML, and GenAI Command Center

OmniPulse AI is a beginner-friendly, production-style portfolio project that will grow into an end-to-end platform for data engineering, analytics, machine learning, MLOps, and generative AI. The project is intentionally built in small phases so that every component can be learned, tested, and documented before the next one is introduced.

## Project goals

- Build a realistic data platform using clear, maintainable project conventions.
- Learn how data moves from ingestion through processing, storage, analytics, and APIs.
- Develop and evaluate machine-learning workflows on trusted, transformed data.
- Add production practices such as testing, reproducibility, monitoring, and deployment.
- Create an interactive command center that demonstrates the complete system to recruiters.
- Keep each phase approachable with focused documentation and beginner-friendly code.

## Planned architecture

The final system is planned as a layered pipeline:

```text
Data Sources
    |
    v
Batch and Real-Time Ingestion
    |
    v
Raw Storage / Lakehouse
    |
    v
Distributed Processing and Data Quality
    |
    v
Warehouse Models and Analytics
    |
    +------------------+
    |                  |
    v                  v
Dashboards        ML and MLOps
                       |
                       v
                 GenAI / RAG Assistant
    |                  |
    +--------+---------+
             v
        FastAPI Services
             |
             v
       Cloud Deployment
```

This is the target architecture, not the current implementation. Components will be added only in their corresponding phases.

## Planned tech stack

| Area | Technologies |
| --- | --- |
| Language and analysis | Python, pandas, NumPy, Jupyter |
| Visualization | Matplotlib, Seaborn, dashboard tooling to be selected later |
| Ingestion and orchestration | Requests, Kafka, Airflow |
| Storage | PostgreSQL, object storage, lakehouse technology |
| Processing and modeling | Spark, SQL, dbt |
| Machine learning | scikit-learn, MLflow |
| GenAI | Retrieval-augmented generation (RAG), provider and framework to be selected later |
| APIs | FastAPI, Uvicorn |
| Quality | pytest, Black, Ruff |
| Delivery | Docker and a cloud platform to be selected later |

Tools listed for later phases are architectural plans only; Phase 1 contains no Kafka, Spark, Airflow, dbt, MLflow, or GenAI implementation.

## Phase roadmap

1. Project setup
2. Synthetic data generation
3. Batch ingestion
4. PostgreSQL database
5. Data warehouse/lakehouse
6. Spark processing
7. dbt transformations
8. Dashboards
9. Machine learning
10. MLOps
11. GenAI/RAG assistant
12. Cloud deployment and recruiter demo

See [the detailed phase roadmap](docs/phase_roadmap.md) for the purpose and expected outcome of each phase.

## Repository layout

```text
data/          Local raw, processed, and sample datasets
src/           Reusable application and pipeline source code
notebooks/     Exploratory analysis and learning notebooks
dashboards/    Dashboard applications and assets
api/           API entry points and routes
tests/         Automated tests
docs/          Project documentation
docker/        Container-related files
architecture/  Architecture diagrams and decisions
```

## Getting started

Create and activate a virtual environment, then install the starter dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
py -3.12 -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the project checks:

```bash
pytest
ruff check .
black --check .
```

## Current status

**Phase 1: project setup.** The initial repository structure, development configuration, documentation, and project-structure test are in place. Data pipelines and platform services will begin in later phases.
