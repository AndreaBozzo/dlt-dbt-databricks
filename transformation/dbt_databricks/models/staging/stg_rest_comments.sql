-- Staging: 1:1 cleanup of the dlt-landed raw.rest_comments table.
with source as (
    select * from {{ source('raw', 'rest_comments') }}
)

select
    cast(id as bigint)       as comment_id,
    cast(post_id as bigint)  as post_id,
    name                     as commenter_name,
    email                    as commenter_email,
    body,
    _dlt_load_id             as _dlt_load_id
from source
