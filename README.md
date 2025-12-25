# Billigaste Kvittot

A modern web application for comparing weekly grocery deals from Swedish supermarkets to find the best prices.

## Overview

Billigaste Kvittot ("The Cheapest Receipt") automatically collects promotional data from Sweden's largest grocery chains and presents them in an interactive web interface. Users can filter products, compare prices across stores, and create shopping lists to optimize their grocery shopping.

**Live:** (https://billigaste-project-app-21981.azurewebsites.net/)

## Features

- **Automatic data collection** - Fetches deals from 4 grocery chains every week
- **Smart filtering** - Filter by store, brand, and product name
- **Price comparison** - View promotional price, regular price, and savings
- **Shopping list** - Add products and see totals per store
- **Responsive design** - Works on desktop, tablet, and mobile

## Supported Stores

| Store | Status |
|-------|--------|
| City Gross | Active |
| Coop | Active |
| Hemköp | Active |
| Willys | Active |

## Technical Architecture

```
Store APIs  -->  dlt (extract)  -->  DuckDB (staging)  -->  dbt (transform)
                                                                   |
                                                                   v
                 Flask (frontend)  <--  DuckDB (marts)  <----------+
```

### Stack

**Data Pipeline**
- [dlt](https://dlthub.com/) - Data ingestion from store APIs
- [DuckDB](https://duckdb.org/) - Embedded OLAP database
- [dbt](https://www.getdbt.com/) - SQL transformations
- [Dagster](https://dagster.io/) - Orchestration and scheduling

**Frontend**
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- Jinja2 - Template engine
- Vanilla JavaScript - Interactivity

**Infrastructure**
- Docker - Containerization
- Terraform - Infrastructure as Code
- Azure - Cloud hosting

## Project Structure

```
billigaste_kvittot/
|-- stores/                    # API integrations per store
|   |-- willys/
|   |-- coop/
|   |-- hemkop/
|   +-- city_gross/
|-- orchestration/             # Dagster pipeline
|   +-- definitions.py
|-- dbt_billigaste_kvittot/    # dbt project
|   |-- models/
|   |   |-- src/               # Staging models
|   |   +-- mart/              # Final marts
|   |-- dbt_project.yml
|   +-- profiles.yml
|-- frontend/                  # Flask web app
|   |-- app.py
|   |-- templates/
|   +-- static/
|-- database/                  # DuckDB database files
|-- iac/                       # Terraform (Azure)
|-- pyproject.toml
+-- README.md
```

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Local Development

```bash
# Clone the repo
git clone https://github.com/HenrikSjoe/billigaste_kvittot.git
cd billigaste_kvittot

# Install dependencies
uv sync
# or
pip install -e .

# Create .env file
cat > .env << EOF
COOP_API_KEY="your-api-key"
DUCKDB_PATH="database/billigaste_kvittot_db.duckdb"
DBT_PROFILES_DIR="."
EOF
```

### Run Frontend Locally

```bash
cd frontend
uv run python app.py
# Open http://localhost:5000
```

### Run Dagster (Orchestrator)

```bash
cd orchestration
uv run dagster dev -f definitions.py -h 0.0.0.0 -p 3000
# Open http://localhost:3000
```

### Run dbt Manually

```bash
cd dbt_billigaste_kvittot
uv run dbt build
```

## Data Pipeline

### Scheduling

Data collection runs automatically every Monday:

| Time (UTC) | Job |
|------------|-----|
| 05:00 | City Gross |
| 05:05 | Coop |
| 05:10 | Hemköp |
| 05:15 | Willys |

After store jobs complete, dbt is triggered automatically to transform the data.

### Data Model

**Staging** (dlt to DuckDB)
- Raw data from each store's API
- Normalized to consistent structure

**Marts** (dbt)
- `marts_all_stores` - Union of all stores with standardized columns:
  - `promotion_id`, `store`, `week`
  - `brand`, `product_name`, `description`
  - `ordinary_price`, `promotion_price`
  - `unit`, `product_unit`
  - `end_date`, `image_url`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COOP_API_KEY` | API key for Coop | Yes (for Coop data) |
| `DUCKDB_PATH` | Path to DuckDB file | Yes |
| `DBT_PROFILES_DIR` | Path to dbt profiles | Yes (for pipeline) |

## Docker

### Build and Run Frontend

```bash
docker build -f dockerfile.webapp -t billigaste-kvittot-web .
docker run -p 5000:5000 billigaste-kvittot-web
```

### Build and Run Pipeline

```bash
docker build -f dockerfile.pipe -t billigaste-kvittot-pipe .
docker run -p 3000:3000 billigaste-kvittot-pipe
```

## Deployment

The project uses Terraform for deployment to Azure:

```bash
cd iac
terraform init
terraform plan
terraform apply
```

## Authors

- **Henrik Sjögren** - [HenrikSjoe](https://github.com/HenrikSjoe)
- **Hampus Donnersten** - [Donnersten](https://github.com/Donnersten)
- **Andreas Reinholdsson** - [REAndreas](https://github.com/REAndreas)
- **Thorbjörn Persson Steive** - [plyschbjorn](https://github.com/plyschbjorn)

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Contact

Create an [issue](https://github.com/HenrikSjoe/billigaste_kvittot/issues) for bugs or feature requests.
