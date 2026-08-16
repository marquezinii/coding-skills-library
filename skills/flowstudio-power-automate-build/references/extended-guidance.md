<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## 5. Verify the Deployment

```python
check = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)

# Confirm state
print("State:", check["properties"]["state"])  # Should be "Started"
# If state is "Stopped", use set_live_flow_state — NOT update_live_flow
# mcp("set_live_flow_state", environmentName=ENV, flowName=FLOW_ID, state="Started")

# Confirm the action we added is there
acts = check["properties"]["definition"]["actions"]
print("Actions:", list(acts.keys()))
```

---

## 6. Test the Flow

> **MANDATORY**: Before triggering any test run, **ask the user for confirmation**.
> Running a flow has real side effects — it may send emails, post Teams messages,
> write to SharePoint, start approvals, or call external APIs. Explain what the
> flow will do and wait for explicit approval before calling `trigger_live_flow`
> or `resubmit_live_flow_run`.

### Updated flows (have prior runs) — ANY trigger type

> **Use `resubmit_live_flow_run` first.** It works for EVERY trigger type —
> Recurrence, SharePoint, connector webhooks, Button, and HTTP. It replays
> the original trigger payload. Do NOT ask the user to manually trigger the
> flow or wait for the next scheduled run.

```python
runs = mcp("get_live_flow_runs", environmentName=ENV, flowName=FLOW_ID, top=1)
if runs:
    # Works for Recurrence, SharePoint, connector triggers — not just HTTP
    result = mcp("resubmit_live_flow_run",
        environmentName=ENV, flowName=FLOW_ID, runName=runs[0]["name"])
    print(result)   # {"resubmitted": true, "triggerName": "..."}
```

### HTTP-triggered flows — custom test payload

Only use `trigger_live_flow` when you need to send a **different** payload
than the original run. For verifying a fix, `resubmit_live_flow_run` is
better because it uses the exact data that caused the failure.

```python
defn = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)
triggers = defn["properties"]["definition"]["triggers"]
manual = next(iter(triggers.values()))
print("Expected body:", manual.get("inputs", {}).get("schema"))

result = mcp("trigger_live_flow",
    environmentName=ENV, flowName=FLOW_ID,
    body={"name": "Test", "value": 1})
print(f"Status: {result['responseStatus']}")
```

### Brand-new non-HTTP flows (Recurrence, connector triggers, etc.)

A brand-new Recurrence or connector-triggered flow has **no prior runs** to
resubmit and no HTTP endpoint to call. This is the ONLY scenario where you
need the temporary HTTP trigger approach below. **Deploy with a temporary
HTTP trigger first, test the actions, then swap to the production trigger.**

Compact recipe:

```python
production_trigger = definition["triggers"]
definition["triggers"] = {
    "manual": {"type": "Request", "kind": "Http", "inputs": {"schema": {}}}
}

result = mcp("update_live_flow",
    environmentName=ENV,
    flowName=FLOW_ID,       # omit if creating new
    definition=definition,
    connectionReferences=connection_references,
    displayName="Overdue Invoice Notifications")
FLOW_ID = FLOW_ID or result["created"]

test = mcp("trigger_live_flow", environmentName=ENV, flowName=FLOW_ID,
           body={"sample": "payload"})
runs = mcp("get_live_flow_runs", environmentName=ENV, flowName=FLOW_ID, top=1)

if runs[0]["status"] == "Failed":
    err = mcp("get_live_flow_run_error",
        environmentName=ENV, flowName=FLOW_ID, runName=runs[0]["name"])
    raise Exception(err["failedActions"][-1])

definition["triggers"] = production_trigger
mcp("update_live_flow",
    environmentName=ENV,
    flowName=FLOW_ID,
    definition=definition,
    connectionReferences=connection_references)
```

The trigger is only the entry point; testing through HTTP still exercises the
same actions. If actions use `triggerBody()` or `triggerOutputs()`, pass a
representative `trigger_live_flow.body` shaped like the production trigger
payload.

---

## Gotchas

| Mistake | Consequence | Prevention |
|---|---|---|
| Missing `connectionReferences` in deploy | 400 "Supply connectionReferences" | Always call `list_live_connections` first |
| `"operationOptions"` missing on Foreach | Parallel execution, race conditions on writes | Always add `"Sequential"` |
| `union(old_data, new_data)` | Old values override new (first-wins) | Use `union(new_data, old_data)` |
| `split()` on potentially-null string | `InvalidTemplate` crash | Wrap with `coalesce(field, '')` |
| Checking `result["error"]` exists | Always present; true error is `!= null` | Use `result.get("error") is not None` |
| Flow deployed but state is "Stopped" | Flow won't run on schedule | Call `set_live_flow_state` with `state: "Started"` — do **not** use `update_live_flow` for state changes |
| Teams "Chat with Flow bot" recipient as object | 400 `GraphUserDetailNotFound` | Use plain string with trailing semicolon (see below) |
| Copilot/Skills flow not in a solution | Copilot Studio may not discover it as an agent tool | After deploy, call `add_live_flow_to_solution` with the target `solutionId` |
| Button/Skills trigger used for MCP testing | MCP cannot directly fire the production trigger | Test the same actions through a temporary HTTP twin, then swap the trigger back |
| Connector action missing `metadata.operationMetadataId` | Designer/run-only UI can behave inconsistently | Preserve existing IDs; add stable GUIDs for new connector actions |
| Placeholder Excel `scriptId` | Dynamic validation fails at save time | Resolve the real Office Script ID before deploying |
| SharePoint `PatchItem` omits required fields | Save can fail even if the field is not changing | Echo unchanged required fields such as `item/Title` |
| Copilot Studio connector calls a draft agent | Connector invocation can fail or hit stale behavior | Publish the agent before testing/resubmitting the flow |

### Teams `PostMessageToConversation` — Recipient Formats

The `body/recipient` parameter format depends on the `location` value:

| Location | `body/recipient` format | Example |
|---|---|---|
| **Chat with Flow bot** | Plain email string with **trailing semicolon** | `"user@contoso.com;"` |
| **Channel** | Object with `groupId` and `channelId` | `{"groupId": "...", "channelId": "..."}` |

> **Common mistake**: passing `{"to": "user@contoso.com"}` for "Chat with Flow bot"
> returns a 400 `GraphUserDetailNotFound` error. The API expects a plain string.

---

## Reference Files

- [flow-schema.md](../references/flow-schema.md) — Full flow definition JSON schema
- [trigger-types.md](../references/trigger-types.md) — Trigger type templates
- [action-patterns-core.md](../references/action-patterns-core.md) — Variables, control flow, expressions
- [action-patterns-data.md](../references/action-patterns-data.md) — Array transforms, HTTP, parsing
- [action-patterns-connectors.md](../references/action-patterns-connectors.md) — SharePoint, Outlook, Teams, Approvals
- [build-patterns.md](../references/build-patterns.md) — Complete flow definition templates (Recurrence+SP+Teams, HTTP trigger)

## Related Skills

- `flowstudio-power-automate-mcp` — Core connection setup and tool reference
- `flowstudio-power-automate-debug` — Debug failing flows after deployment
