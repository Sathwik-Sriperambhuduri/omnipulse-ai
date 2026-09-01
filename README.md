# OmniPulse AI: Real-Time Data, ML, and GenAI Command Center

OmniPulse AI is a project that will grow into an end-to-end platform for data engineering, analytics, machine learning, MLOps, and generative AI. The project is intentionally built in small phases so that every component can be learned, tested, and documented before the next one is introduced.

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

Tools listed for later phases are architectural plans only. Phases 1 and 2 do
not start PostgreSQL, Kafka, Spark, Airflow, dbt, MLflow, dashboards, machine
learning, or GenAI.

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

## Generate the Phase 2 datasets

From the repository root, with the virtual environment active, run:

```powershell
python -m src.ingestion.generate_synthetic_data `
  --customers 1000 `
  --products 200 `
  --orders 5000 `
  --clickstream-sessions 3000 `
  --seed 42 `
  --output-dir data/raw
```

On macOS or Linux, replace PowerShell's backticks with backslashes, or put the
command on one line. Every argument is optional; the values above are the
defaults. Using the same sizes and seed reproduces the same data.

The command creates these related CSV files: customers, products, orders,
order items, payments, reviews, inventory, marketing campaigns, and clickstream
events. See the [data dictionary](docs/data_dictionary.md) for every column and
the [data model guide](docs/data_model.md) for relationship explanations.

- `data/raw/` contains locally generated working data. Its CSV files are ignored
  by Git because full runs may become large.
- `data/sample/` contains small recruiter-friendly CSVs with the same schemas.
  These examples are intentionally allowed in Git.

To make a separate small dataset for experimentation, choose another output
directory:

```powershell
python -m src.ingestion.generate_synthetic_data --customers 20 --products 10 --orders 30 --clickstream-sessions 15 --seed 42 --output-dir data/my_test_run
```

## Current status

- **Phase 1 — Complete:** repository structure, development configuration, and
  foundation documentation are in place.
- **Phase 2 — Complete:** the reproducible synthetic e-commerce generator,
  sample data, relationship tests, data dictionary, and data-model guide are in
  place.
- **Phase 3 and later — Not started:** no platform services or downstream data
  pipelines have been introduced yet.
