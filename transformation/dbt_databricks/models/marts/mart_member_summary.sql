-- Member-level (hvid) utilization summary: one row per insured member.
-- Building block for risk scoring / high-cost-member identification.
with claims as (
    select * from {{ ref('int_claims') }}
)

select
    hvid,
    max(payer_type)                                  as primary_payer_type,
    max(patient_state)                               as patient_state,
    count(*)                                         as claim_count,
    -- Explicit cast: DuckDB widens sum(bigint) to hugeint; the contract pins bigint on every lane.
    cast(sum(line_count) as bigint)                  as total_service_lines,
    sum(total_charge)                                as total_charge,
    sum(total_allowed)                               as total_allowed,
    min(first_service_date)                          as first_claim_date,
    max(first_service_date)                          as last_claim_date
from claims
group by hvid
