-- Staging: 1:1 cleanup of the dlt-landed raw.rest_posts table.
-- Rename/cast only; no business logic. dlt normalized camelCase -> snake_case for us.
with source as (
    select * from {{ source('raw', 'rest_posts') }}
)

select
    cast(id as bigint)       as post_id,
    cast(user_id as bigint)  as user_id,
    title,
    body,
    _dlt_load_id             as _dlt_load_id
from source
