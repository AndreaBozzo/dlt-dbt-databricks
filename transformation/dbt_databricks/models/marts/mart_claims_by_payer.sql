-- Insurance analytics mart: claim & cost metrics by payer, state, and claim type.
-- Answers "how much do we pay vs get charged, by payer segment?" — core to reserving/pricing.
with claims as (
    select * from {{ ref('int_claims') }}
)

select
    payer_type,
    patient_state,
    claim_type,
    count(*)                                         as claims,
    count(distinct hvid)                             as members,
    sum(total_charge)                                as total_charge,
    sum(total_allowed)                               as total_allowed,
    round(avg(total_allowed), 2)                     as avg_allowed_per_claim,
    round(sum(total_allowed) / nullif(sum(total_charge), 0), 4) as allowed_ratio
from claims
group by payer_type, patient_state, claim_type
