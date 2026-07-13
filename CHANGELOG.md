# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-13

### Added

- Agentic-first workflow for Microsoft Fabric and Power BI projects.
- Packaged Codex skills for project intake, BI engineering, governance, and executive report delivery.
- TMDL-first offline workflow with a sanitized demo project and governed starter dictionary.
- Environment validation, project bootstrap, Power BI Desktop detection, Fabric connection payloads, model snapshots, dictionary comparison, and synchronization commands.
- Local skill installer and public-repository bootstrap for Windows.
- HTML and PDF executive report pack generation with validation and self-tests.
- Publication audit, strict ignore rules, safe public/private workspace guidance, and an operational runbook.

### Security

- Public artifacts are separated from private workspaces, authentication state, Fabric exports, and generated executive report packs.
- Example configuration uses placeholders instead of tenant, workspace, endpoint, identity, or model values.

### Known limitations

- Live Power BI Desktop and Fabric inspection requires compatible MCP tooling in the active Codex session.
- `connect-fabric` prepares a connection payload but does not establish the live connection by itself.
- Private domain packs and complex live-model mutations are outside the scope of this initial release.

[0.1.0]: https://github.com/bnovelorotger/fabric-powerbi-companion/releases/tag/v0.1.0
