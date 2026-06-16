# Shortcuts around uv + dlt + dbt. Run `make help` to list targets.
# On Windows, run these from Git Bash (the Makefile uses POSIX sh).
# .env is loaded automatically via `dotenv` for dlt scripts; for dbt targets we export vars here.

DBT_DIR := transformation/dbt_databricks
# dbt looks for profiles.yml in --profiles-dir; we keep it next to the project.
# --env-file loads .env so env_var('DATABRICKS_TOKEN') in profiles.yml resolves.
DBT := uv run --env-file .env dbt --project-dir $(DBT_DIR) --profiles-dir $(DBT_DIR)

.DEFAULT_GOAL := help

.PHONY: help setup lint fmt \
        dlt-rest dlt-sql dlt-merge dlt-iceberg dlt-contracts \
        dbt-deps dbt-parse dbt-build dbt-test e2e

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Create the venv and install all deps (incl. dev group)
	uv sync
	$(DBT) deps

lint: ## Ruff lint
	uv run ruff check .

fmt: ## Ruff format
	uv run ruff format .

# --- dlt ingestion ---
dlt-rest: ## Run the REST API -> Databricks example
	uv run python ingestion/pipelines/rest_api_to_databricks.py
dlt-sql: ## Run the SQL database -> Databricks example
	uv run python ingestion/pipelines/sql_database_to_databricks.py
dlt-merge: ## Run the merge/incremental advanced example
	uv run python ingestion/advanced/merge_incremental.py
dlt-iceberg: ## Run the Iceberg table_format advanced example
	uv run python ingestion/advanced/iceberg_table_format.py
dlt-contracts: ## Run the schema-contracts advanced example
	uv run python ingestion/advanced/data_contracts.py

# --- dbt transformation ---
dbt-deps: ## Install dbt packages
	$(DBT) deps
dbt-parse: ## Parse the dbt project (no warehouse writes)
	$(DBT) parse
dbt-build: ## Run + test all dbt models
	$(DBT) build
dbt-test: ## Run dbt tests only
	$(DBT) test

# --- end to end ---
e2e: ## Run dlt ingestion then dbt build in one process
	uv run python orchestration/run_e2e.py
