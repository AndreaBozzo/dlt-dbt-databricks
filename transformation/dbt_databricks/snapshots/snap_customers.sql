{#
  Example snapshot: track row changes over time (SCD type 2) on a dlt-loaded table.
  Disabled by default because it needs raw.customers (from the advanced merge example).
  Enable by removing `enabled=false` once that table exists.
#}
{% snapshot snap_customers %}
{{
    config(
        target_schema=env_var('DATABRICKS_SCHEMA', 'analytics') ~ '_snapshots',
        unique_key='id',
        strategy='timestamp',
        updated_at='updated_at',
        enabled=false,
    )
}}
select * from {{ source('raw', 'customers') }}
{% endsnapshot %}
