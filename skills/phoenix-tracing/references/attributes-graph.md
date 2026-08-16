# Agent and workflow graph attributes

Represent a workflow graph primarily through trace structure: parent spans contain child spans for agents, chains, LLM calls, retrievers, and tools. Set the OpenInference span kind that matches the operation instead of encoding the entire graph as custom metadata.

## Model the execution

- Use an `AGENT` span for the agent reasoning or orchestration boundary.
- Use `CHAIN` for deterministic multi-step application logic.
- Use `LLM`, `TOOL`, and `RETRIEVER` spans for the corresponding operations.
- Preserve parent-child relationships and propagate the active context across asynchronous boundaries.
- Attach stable node or route identifiers as small custom attributes only when they help compare runs.

Do not attach full graph state, prompts, or retrieved corpora to every span. Record inputs and outputs at the operation that owns them, apply redaction, and keep large artifacts outside trace attributes.

Validate the resulting trace in Phoenix: the root-to-leaf path should explain the executed route, retries should be distinguishable from parallel branches, and failed operations should carry error status.

Authoritative references:

- [OpenInference repository and span kinds](https://github.com/Arize-ai/openinference)
- [Phoenix tracing tutorial](https://arize.com/docs/phoenix/tracing)
