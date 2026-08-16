# Advanced `llms.txt` example

For a larger repository, group links by decision value and keep generated or volatile material out of the primary index.

```text
# Example Platform

> Services, SDKs, and operational documentation for the Example Platform.

## Architecture

- [System overview](docs/architecture/overview.md): Boundaries and data flow.
- [Architecture decisions](docs/adr/README.md): Durable technical decisions.

## APIs and SDKs

- [API reference](docs/api/index.md): Public contracts and authentication.
- [TypeScript SDK](packages/typescript/README.md): Installation and examples.

## Operations

- [Runbooks](docs/runbooks/README.md): Diagnosis, recovery, and escalation.

## Optional

- [Examples](examples/README.md): End-to-end sample applications.
```

Prefer one canonical link for each topic, verify links, and describe why each target matters.
