# Metadata attributes

Use metadata for application-specific context that does not already have a standard OpenInference attribute. Use the Phoenix context helpers for session ID, user ID, tags, prompt-template data, and metadata so child spans inherit the intended values.

## Guidance

- Prefer semantic attributes when the specification already defines the concept.
- Keep metadata keys stable across deployments so queries and evaluations remain comparable.
- Use small JSON-serializable values; store large documents elsewhere and attach an identifier.
- Avoid secrets and unnecessary personal data.
- Define retention and access controls before recording tenant, user, or business context.

For Python, use the context managers exported by `phoenix.otel` when supported by the installed version. For TypeScript, use the context setters exported by `@arizeai/phoenix-otel`. Check the installed package API rather than copying a version-specific import blindly.

Authoritative references:

- [Add attributes, metadata, and users](https://arize.com/docs/phoenix/tracing/how-to-tracing/add-metadata/customize-spans)
- [Extract data and query spans](https://arize.com/docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/extract-data-from-spans)
