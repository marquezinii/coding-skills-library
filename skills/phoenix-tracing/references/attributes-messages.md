# Message attributes

Use OpenInference message attributes when an LLM span needs a structured representation of chat input or output. Prefer the attribute builders exported by the installed Phoenix/OpenInference package over manually assembling flattened keys.

## Capture

- ordered input and output messages;
- each message role and user-visible content;
- tool-call identifiers, function names, and serialized arguments when present;
- multimodal content through the library's typed content structures.

Keep raw `input.value` or `output.value` only when it adds diagnostic value. Structured message attributes and raw payloads can overlap, so apply the production redaction policy before recording either form.

## Validate

- Preserve message order.
- Serialize objects deterministically as JSON.
- Do not record secrets, credentials, unrestricted user files, or hidden reasoning.
- Confirm the resulting span renders correctly in Phoenix after an SDK upgrade.

Authoritative references:

- [OpenInference repository and specification](https://github.com/Arize-ai/openinference)
- [Phoenix tracing concepts](https://arize.com/docs/phoenix/tracing/concepts-tracing/what-are-traces)
