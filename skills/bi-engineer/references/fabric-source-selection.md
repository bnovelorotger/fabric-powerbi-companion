# Fabric source selection

## Preferred order

1. Curated domain tables documented in `dictionary/tables.yml`
2. Technical catalog entries in `catalog/*.csv`
3. Live Fabric confirmation when MCP tooling is available
4. Local TMDL or model exports when no live connection is available

## Rules

- Prefer curated and documented sources over ad hoc copies.
- Prefer shared semantic logic over report-local reinvention.
- If a live Fabric object contradicts the local catalog, record the conflict and treat live Fabric as the technical truth until governance catches up.
- If no safe source can be confirmed, stay in `Supuestos` instead of inventing provenance.
