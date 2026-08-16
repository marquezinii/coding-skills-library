# Advanced update example

When a repository is reorganized, update sections atomically and avoid listing generated files individually.

```diff
-## Packages
-- [Core package](src/core/README.md): Core implementation.
+## Architecture
+- [System overview](docs/architecture/overview.md): Boundaries and data flow.
+
+## Packages
+- [Package index](packages/README.md): Maintained packages and ownership.
```

After the edit, check for duplicates, dead links, empty sections, and documents that moved but retained the same purpose.
