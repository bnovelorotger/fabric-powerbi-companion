# Layering a Private Workspace

Use this repository as the public base layer.

Keep the following in a separate private repository:

- real Fabric exports
- client projects
- domain-specific business rules
- real dictionaries
- auth state
- local caches
- one-off operational scripts

Recommended shape:

```text
public-core/
private-workspace/
```

The private workspace can:

- import or copy selected scripts from the public core
- maintain its own `catalog/` and `dictionary/`
- add private skills or domain packs
- keep real project logs and snapshots
