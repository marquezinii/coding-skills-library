# Exception attributes

Record an exception on the span that owns the failed operation and set the span status to error. Use the OpenTelemetry SDK's exception-recording API when available so standard fields are emitted consistently.

## Standard data

- exception type;
- exception message after secret and personal-data review;
- stack trace when policy permits it;
- whether the exception escaped the span scope, when the SDK exposes that signal.

## Handling rules

- Preserve the original exception and traceback; do not replace them with a generic string before recording.
- Avoid duplicate exception events on every parent span.
- Redact tokens, credentials, request bodies, and sensitive local paths.
- Mark handled failures accurately; a caught exception can still be an error for the operation.
- Verify export and rendering with a controlled test exception, then remove the test path.

Authoritative references:

- [OpenInference semantic conventions](https://github.com/Arize-ai/openinference)
- [Phoenix tracing helpers](https://arize.com/docs/phoenix/tracing/how-to-tracing/setup-tracing/instrument)
