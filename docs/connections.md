# Connections

## Power BI Desktop

Supported in two ways:

1. Offline, from an exported TMDL folder
2. Live, when Power BI Desktop is open and Codex Power BI MCP tooling is available

Detect local Desktop instances:

```powershell
python .\scripts\workflow_cli.py detect-pbi
```

## Fabric

This repo ships a safe `connect-fabric` planning command:

```powershell
python .\scripts\workflow_cli.py connect-fabric --config .\config\workflow.example.yaml
```

The command validates the config and prints:

- the workspace / semantic model values it would use
- a recommended Codex MCP connection payload
- a fallback XMLA-style connection string shape

## Why the live connection stays documented

Direct live connections depend on the host environment:

- local Power BI Desktop instance availability
- Power BI / Fabric access rights
- Codex MCP tooling support in the active session

The public core therefore keeps the live path explicit and reproducible, but the offline TMDL path remains the default guaranteed workflow.
