# Agentic-first

`fabric-powerbi-companion` is designed as an agentic-first repository.

## What that means

The primary user experience is:

1. a user expresses intent
2. the agent reads the governed context
3. the agent inspects model state
4. the agent proposes or applies safe technical work
5. the agent syncs governance context after changes

The repository is not designed as a script collection first and an agent wrapper second. The scripts exist to support the agent workflow, not to replace it.

## Primary interfaces

- `/comensemos`: intake and routing
- `BI_ENGINEER`: technical modeling workflow
- `BI_GOVERNANCE`: dictionary and changelog synchronization

## Supporting interfaces

- `scripts/workflow_cli.py`
- `scripts/model_factory/`
- `docs/`
- demo TMDL and starter dictionary

## Design principles

- Agent before checklist: start from intent and context, not from manual command sequences.
- Governed context first: use `dictionary/` before inventing semantics.
- Inspect before mutate: read PBIX, Fabric, or TMDL state before proposing changes.
- Safe degradation: if live MCP tooling is unavailable, fall back to offline TMDL.
- Public/private boundary: keep the public agent core separate from private operational state.
- Reproducible skills: package the skills with the repository so another engineer can clone and reuse the same agent behavior.

## Non-goals

- The public core is not a dump of private workspace artifacts.
- The CLI is not intended to become the only way to use the project.
- Live connectivity is not assumed to exist in every environment.
