-- Roll claim-line detail up to one row per claim. Header attributes (payer, member, state) are
-- constant within a claim; we take max() defensively. Money is summed across lines.
with lines as (
    select * from {{ ref('stg_claims') }}
)

select
    claim_id,
    max(hvid)                                        as hvid,
    max(claim_type)                                  as claim_type,
    max(payer_type)                                  as payer_type,
    max(patient_state)                               as patient_state,
    max(patient_gender)                              as patient_gender,
    min(service_date)                                as first_service_date,
    count(*)                                         as line_count,
    count(distinct diagnosis_code)                   as distinct_diagnoses,
    sum(line_charge)                                 as total_charge,
    sum(line_allowed)                                as total_allowed,
    -- Share of charged amount the payer allowed; 0 means fully denied/non-covered.
    round(sum(line_allowed) / nullif(sum(line_charge), 0), 4) as allowed_ratio
from lines
group by claim_id
