-- Intermediate: aggregate comments per post. Reusable building block for the marts layer.
with comments as (
    select * from {{ ref('stg_rest_comments') }}
)

select
    post_id,
    count(*)                          as comment_count,
    count(distinct commenter_email)   as distinct_commenters
from comments
group by post_id
