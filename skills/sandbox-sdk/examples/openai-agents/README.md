# OpenAI Agents integration

Expose Cloudflare Sandbox operations as tools while keeping sandbox identity scoped to the current user or session.

```ts
import { Shell, Editor } from "@cloudflare/sandbox/openai";

export const sandboxTools = {
  shell: new Shell({ sandboxId: "session-scoped-id" }),
  editor: new Editor({ sandboxId: "session-scoped-id" }),
};
```

Use a stable per-session identifier, validate command inputs, avoid logging secrets, and destroy temporary sandboxes when the workflow finishes. Consult the SDK version installed in the target project for exact constructor and tool-registration APIs.
