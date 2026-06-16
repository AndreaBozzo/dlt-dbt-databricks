# Databricks notebook source
# MAGIC %md
# MAGIC # dlt zero-config + claims exploration
# MAGIC
# MAGIC Two things you can only really show *inside* Databricks:
# MAGIC
# MAGIC 1. **dlt runs zero-config in a Databricks notebook** — no credentials. dlt picks up the
# MAGIC    workspace context and loads straight into Unity Catalog.
# MAGIC 2. **Explore the dbt insurance marts** built on `samples.healthverity` claims.
# MAGIC
# MAGIC > Import this file into your workspace (Repos or Workspace import) and run on a cluster /
# MAGIC > serverless notebook. It is **not** meant to run locally.
# MAGIC
# MAGIC `dlt` here = the [dlthub](https://dlthub.com) library, not Databricks Delta Live Tables.

# COMMAND ----------

# MAGIC %pip install "dlt[databricks]>=1.6.0"
# MAGIC %restart_python

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Unity Catalog catalog")
dbutils.widgets.text("raw_schema", "raw", "dlt landing schema")
dbutils.widgets.text("analytics_schema", "analytics", "dbt models schema")

CATALOG = dbutils.widgets.get("catalog")
RAW_SCHEMA = dbutils.widgets.get("raw_schema")
ANALYTICS_SCHEMA = dbutils.widgets.get("analytics_schema")
print(f"catalog={CATALOG} raw={RAW_SCHEMA} analytics={ANALYTICS_SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. dlt zero-config ingestion
# MAGIC No `server_hostname` / `access_token` anywhere — inside Databricks, dlt resolves the
# MAGIC destination from the runtime. We load a tiny public REST API into `<catalog>.<raw>`.

# COMMAND ----------

import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source(
    {
        "client": {"base_url": "https://jsonplaceholder.typicode.com/", "paginator": "single_page"},
        "resources": [{"name": "nb_posts", "endpoint": {"path": "posts"}}],
    }
)

pipeline = dlt.pipeline(
    pipeline_name="nb_zero_config",
    destination="databricks",  # zero-config: credentials come from the Databricks runtime
    dataset_name=RAW_SCHEMA,
)
load_info = pipeline.run(source)
print(load_info)

# COMMAND ----------

display(spark.sql(f"SELECT count(*) AS posts FROM {CATALOG}.{RAW_SCHEMA}.nb_posts"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Explore the insurance claims marts
# MAGIC These were built by dbt (`transformation/dbt_databricks`) on `samples.healthverity`.
# MAGIC Run `make dbt-build` first if `mart_claims_by_payer` doesn't exist yet.

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT payer_type,
               sum(claims)                         AS claims,
               round(sum(total_allowed))           AS total_allowed,
               round(avg(allowed_ratio), 3)        AS avg_allowed_ratio
        FROM {CATALOG}.{ANALYTICS_SCHEMA}.mart_claims_by_payer
        GROUP BY payer_type
        ORDER BY claims DESC
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC Top states by allowed amount — the kind of slice a reserving/pricing analyst would start from.

# COMMAND ----------

display(
    spark.sql(
        f"""
        SELECT patient_state,
               sum(claims)               AS claims,
               round(sum(total_allowed)) AS total_allowed
        FROM {CATALOG}.{ANALYTICS_SCHEMA}.mart_claims_by_payer
        GROUP BY patient_state
        ORDER BY total_allowed DESC
        LIMIT 15
        """
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Recap
# MAGIC - dlt loaded into Unity Catalog with **zero credentials** (notebook-native).
# MAGIC - dbt marts on real claims data are queryable for insurance analytics.
# MAGIC - Same code runs locally (`make e2e`) or as a Databricks Job via `databricks.yml`.
