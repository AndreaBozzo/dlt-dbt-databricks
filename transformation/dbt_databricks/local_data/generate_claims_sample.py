"""Generate the checked-in sample CSV that stands in for samples.healthverity on DuckDB.

The real source (`samples.healthverity.claims_sample_synthetic`, ~410k rows) only exists inside a
Databricks workspace. The DuckDB lane resolves the same dbt source from this CSV instead (see the
`external_location` meta in models/sources.yml), so the claims models and their tests run in CI.

The output mirrors the real table's raw contract: claim-line-detail grain, all-string columns,
~45% NULL line_charge, and a small share of negative charges (claim reversals) so the
warn-severity dbt_expectations tests fire — that is what the agentic quality gate classifies as
"expected claims warnings".

Deterministic (fixed seed): rerunning produces the identical CSV.

Run:  uv run python transformation/dbt_databricks/local_data/generate_claims_sample.py
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUTPUT = Path(__file__).with_name("claims_sample_synthetic.csv")

N_CLAIMS = 600
N_MEMBERS = 220

PAYER_TYPES = ["MEDICAID", "COMMERCIAL", "MEDICARE", "UNSPECIFIED", "MEDICARE SUPPLEMENT", ""]
PAYER_WEIGHTS = [25, 35, 20, 8, 7, 5]
STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA"]
DIAGNOSES = ["E11.9", "I10", "J45.909", "M54.5", "Z00.00", "F41.1", "K21.9", ""]
PROCEDURES = ["99213", "99214", "80053", "36415", "71046", "93000", ""]
REVENUE_CODES = ["0250", "0300", "0450", "0730", ""]

COLUMNS = [
    "claim_id",
    "hvid",
    "service_line_number",
    "claim_type",
    "date_service",
    "payer_type",
    "diagnosis_code",
    "procedure_code",
    "revenue_code",
    "patient_gender",
    "patient_year_of_birth",
    "patient_state",
    "patient_zip3",
    "line_charge",
    "line_allowed",
    "prov_billing_npi",
    "prov_rendering_npi",
]


def main() -> None:
    rng = random.Random(20260704)
    members = [
        {
            "hvid": f"HV{i:06d}",
            "gender": rng.choice(["M", "F", "U"]),
            "yob": str(rng.randint(1940, 2005)),
            "state": rng.choice(STATES),
            "zip3": f"{rng.randint(100, 999)}",
        }
        for i in range(N_MEMBERS)
    ]

    rows: list[dict[str, str]] = []
    for claim_no in range(N_CLAIMS):
        member = rng.choice(members)
        claim_type = rng.choices(["P", "I", "U"], weights=[70, 27, 3])[0]
        payer = rng.choices(PAYER_TYPES, weights=PAYER_WEIGHTS)[0]
        service_date = date(2025, 1, 1) + timedelta(days=rng.randint(0, 330))
        billing_npi = f"1{rng.randint(100000000, 999999999)}"
        for line_no in range(1, rng.randint(1, 4) + 1):
            if rng.random() < 0.45:
                charge, allowed = "", ""  # not reported — like ~57% of the real table
            else:
                amount = round(rng.uniform(50, 5000), 2)
                if rng.random() < 0.02:
                    amount = -round(rng.uniform(50, 500), 2)  # claim reversal/adjustment
                charge = f"{amount}"
                allowed = f"{round(amount * rng.uniform(0.30, 0.95), 2)}"
            rows.append(
                {
                    "claim_id": f"CLM{claim_no:07d}",
                    "hvid": member["hvid"],
                    "service_line_number": str(line_no),
                    "claim_type": claim_type,
                    "date_service": service_date.isoformat(),
                    "payer_type": payer,
                    "diagnosis_code": rng.choice(DIAGNOSES),
                    "procedure_code": rng.choice(PROCEDURES),
                    "revenue_code": rng.choice(REVENUE_CODES) if claim_type == "I" else "",
                    "patient_gender": member["gender"],
                    "patient_year_of_birth": member["yob"],
                    "patient_state": member["state"],
                    "patient_zip3": member["zip3"],
                    "line_charge": charge,
                    "line_allowed": allowed,
                    "prov_billing_npi": billing_npi,
                    "prov_rendering_npi": f"1{rng.randint(100000000, 999999999)}",
                }
            )

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    reversals = sum(1 for row in rows if row["line_charge"].startswith("-"))
    print(f"Wrote {len(rows)} claim lines ({reversals} reversals) to {OUTPUT}")


if __name__ == "__main__":
    main()
