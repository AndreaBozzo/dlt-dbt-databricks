# Security

## No secrets in this repo

This repository is designed to keep credentials **out of version control**:

- `.env`, `**/secrets.toml`, and `transformation/dbt_databricks/profiles.yml` are gitignored.
- Only `*.example` templates are committed.
- Local dev auth uses the **Databricks CLI OAuth** token in `~/.databrickscfg` (run
  `databricks auth login`) — no PAT in files for dbt.

The one public credential-shaped value committed on purpose is EBI's **read-only** RNAcentral
Postgres connection string in `.env.example` (a widely published, intentionally-public dataset
endpoint). Secret scanners may still flag it because it looks like a password. Treat that as a
review item, not as proof that a private secret leaked.

### Before you push

- Never commit a real Databricks PAT, OAuth client secret, or a non-public database password.
- If you add a new source, put its secret in `.env` / `secrets.toml`, not in code.
- Consider enabling a secret scanner (e.g. `gitleaks`) in CI for extra safety.

## Reporting a vulnerability

If you find a security issue in this repository, please open a private report via GitHub Security
Advisories, or email the maintainer. Do not file a public issue for sensitive reports.
