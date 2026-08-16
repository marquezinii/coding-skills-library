<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Workflow B: Create an evaluator for an experiment

Use this when the user says something like *"create an evaluator for my experiment"* or *"evaluate my dataset runs"*.

**If the user says "dataset" but doesn't have an experiment:** A task must target an experiment (not a bare dataset). Ask:
> "Evaluation tasks run against experiment runs, not datasets directly. Would you like help creating an experiment on that dataset first?"

If yes, use the **arize-experiment** skill to create one, then return here.

### Step 1: Find the dataset and experiment names

```bash
ax datasets list --space SPACE
ax experiments list --dataset DATASET_NAME --space SPACE -o json
```

Note the dataset name and the experiment name(s) to score. These accept names or IDs in subsequent commands — names are preferred.

### Step 2: Understand what to evaluate

If the user specified the evaluator type → skip to Step 3.

If not, inspect a recent experiment run to base the evaluator on actual data:

```bash
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | python3 -c "import sys,json; runs=json.load(sys.stdin); print(json.dumps(runs[0], indent=2))"
```

Look at the `output`, `input`, `evaluations`, and `metadata` fields. Identify gaps (metrics the user cares about but doesn't have yet) and propose **1–3 evaluator ideas**. Each suggestion must include: the evaluator name (bold), a one-sentence description, and the binary label pair in parentheses — same format as Workflow A, Step 2.

### Step 3: Confirm or create an AI integration

Same as Workflow A, Step 3.

### Step 4: Create the evaluator

Same as Workflow A, Step 4. Keep variables generic.

### Step 5: Determine column mappings from real run data

Run data shape differs from span data. Inspect:

```bash
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | python3 -c "import sys,json; runs=json.load(sys.stdin); print(json.dumps(runs[0], indent=2))"
```

Common mapping for experiment runs:
- `output` → `"output"` (top-level field on each run)
- `input` → check if it's on the run or embedded in the linked dataset examples

If `input` is not on the run JSON, export dataset examples to find the path:
```bash
ax datasets export DATASET_NAME --space SPACE --stdout | python3 -c "import sys,json; ex=json.load(sys.stdin); print(json.dumps(ex[0], indent=2))"
```

### Step 6: Create the task

```bash
ax tasks create \
  --name "Experiment Correctness" \
  --task-type template_evaluation \
  --dataset DATASET_NAME --space SPACE \
  --experiment-ids "EXP_ID" \   # base64 ID from `ax experiments list --space SPACE -o json`
  --evaluators '[{"evaluator_id": "EVAL_ID", "column_mappings": {"output": "output"}}]' \
  --no-continuous
```

### Step 7: Trigger and monitor

```bash
ax tasks trigger-run TASK_ID \
  --experiment-ids "EXP_ID" \   # base64 ID from `ax experiments list --space SPACE -o json`
  --wait

ax tasks list-runs TASK_ID
ax tasks get-run RUN_ID
```

---

## Best Practices for Template Design

### 1. Use generic, portable variable names

Use `{input}`, `{output}`, and `{context}` — not names tied to a specific project or span attribute (e.g. do not use `{attributes_input_value}`). The evaluator itself stays abstract; the **task's `column_mappings`** is where you wire it to the actual fields in a specific project or experiment. This lets the same evaluator run across multiple projects and experiments without modification.

### 2. Default to binary labels

Use exactly two clear string labels (e.g. `hallucinated` / `factual`, `correct` / `incorrect`, `pass` / `fail`). Binary labels are:
- Easiest for the judge model to produce consistently
- Most common in the industry
- Simplest to interpret in dashboards

If the user insists on more than two choices, that's fine — but recommend binary first and explain the tradeoff (more labels → more ambiguity → lower inter-rater reliability).

### 3. Be explicit about what the model must return

The template must tell the judge model to respond with **only** the label string — nothing else. The label strings in the prompt must **exactly match** the labels in `--classification-choices` (same spelling, same casing).

Good:
```
Respond with exactly one of these labels: hallucinated, factual
```

Bad (too open-ended):
```
Is this hallucinated? Answer yes or no.
```

### 4. Keep temperature low

Pass `--invocation-params '{"temperature": 0}'` for reproducible scoring. Higher temperatures introduce noise into evaluation results.

### 5. Use `--include-explanations` for debugging

During initial setup, always include explanations so you can verify the judge is reasoning correctly before trusting the labels at scale.

### 6. Pass the template in single quotes in bash

Single quotes prevent the shell from interpolating `{variable}` placeholders. Double quotes will cause issues:

```bash
# Correct
--template 'Judge this: {input} → {output}'

# Wrong — shell may interpret { } or fail
--template "Judge this: {input} → {output}"
```

### 7. Always set `--classification-choices` to match your template labels

The labels in `--classification-choices` must exactly match the labels referenced in `--template` (same spelling, same casing). Omitting `--classification-choices` causes task runs to fail with "missing rails and classification choices."

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ax: command not found` | See references/ax-setup.md |
| `401 Unauthorized` | API key may not have access to this space. Verify at https://app.arize.com/admin > API Keys |
| `Evaluator not found` | `ax evaluators list --space SPACE` |
| `Integration not found` | `ax ai-integrations list --space SPACE` |
| `Task not found` | `ax tasks list --space SPACE` |
| `project and dataset-id are mutually exclusive` | Use only one when creating a task |
| `experiment-ids required for dataset tasks` | Add `--experiment-ids` to `create` and `trigger-run` |
| `sampling-rate only valid for project tasks` | Remove `--sampling-rate` from dataset tasks |
| Validation error on `ax spans export` | Project name usually works; if you still get a validation error, look up the base64 project ID via `ax projects list --space SPACE -o json` and use the `id` field instead |
| Template validation errors | Use single-quoted `--template '...'` in bash; single braces `{var}`, not double `{{var}}` |
| Run stuck in `pending` | `ax tasks get-run RUN_ID`; then `ax tasks cancel-run RUN_ID` |
| Run `cancelled` ~1s | Integration credentials invalid — check AI integration |
| Run `cancelled` ~3min | Found spans but LLM call failed — wrong model name or bad key |
| Run `completed`, 0 spans | Widen time window; eval index may not cover older data |
| No scores in UI | Fix `column_mappings` to match real paths on your spans/runs |
| Scores look wrong | Add `--include-explanations` and inspect judge reasoning on a few samples |
| Evaluator cancels on wrong span kind | Match `query_filter` and `column_mappings` to LLM vs CHAIN spans |
| Time format error on `trigger-run` | Use `2026-03-21T09:00:00` — no trailing `Z` |
| Run failed: "missing rails and classification choices" | Add `--classification-choices '{"label_a": 1, "label_b": 0}'` to `ax evaluators create` — labels must match the template |
| Run `completed`, all spans skipped | Query filter matched spans but column mappings are wrong or template variables don't resolve — export a sample span and verify paths |
| `query_filter` set but 0 spans scored | The filter attribute may not be indexed in the eval index. `attributes.metadata.*` and custom attributes are often not indexed. Use `span_kind` or `attributes.llm.model_name` instead, or remove the filter to confirm spans exist in the window. |

### Diagnosing cancelled runs

When a task run is cancelled (status `cancelled`), follow this checklist in order:

**1. Check integration credentials**
```bash
ax ai-integrations list --space SPACE -o json
```
Verify the integration ID used by the evaluator exists and has valid credentials. If the integration was deleted or the API key expired, the run cancels within ~1 second.

**2. Verify the model name**
```bash
ax evaluators get EVALUATOR_NAME --space SPACE -o json
```
Check the `model_name` field. A typo or deprecated model causes the LLM call to fail and the run to cancel after ~3 minutes.

**3. Export a sample span/run and compare paths to column_mappings**

For project tasks:
```bash
ax spans export PROJECT --space SPACE -l 1 --days 7 --stdout | python3 -m json.tool
```

For experiment tasks:
```bash
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | python3 -c "import sys,json; runs=json.load(sys.stdin); print(json.dumps(runs[0], indent=2)) if runs else print('No runs')"
```

Compare the exported JSON paths against the task's `column_mappings`. For each template variable, confirm the mapped path actually exists. Common mismatches:
- Mapping `output` to `attributes.output.value` on an experiment run (should be just `output`)
- Mapping `input` to `attributes.input.value` on a CHAIN span when the actual path is `attributes.llm.input_messages`
- Mapping `context` to a path that doesn't exist on the span kind being filtered

**4. Check that `data_start_time` is not epoch**

If `trigger-run` used a start time of `0`, `1970-01-01`, or an empty string, the time window is invalid. Always derive from real span timestamps:
```bash
ax spans export PROJECT --space SPACE -l 5 --days 30 --stdout | python3 -c "
import sys, json
spans = json.load(sys.stdin)
for s in spans:
    print(s.get('start_time', 'N/A'), s.get('end_time', 'N/A'))
"
```

**5. Verify span kind matches evaluator scope**

If the evaluator was created with `--data-granularity trace` but the task's `query_filter` is `span_kind = 'LLM'`, the run may find no qualifying data and cancel. Ensure the granularity and filter are consistent.

**6. Check that all template variables resolve**

Every `{variable}` in the evaluator template must have a corresponding `column_mappings` entry that resolves to a non-null value. Test resolution against a real span:
```bash
ax spans export PROJECT --space SPACE -l 3 --days 7 --stdout | python3 -c "
import sys, json
spans = json.load(sys.stdin)
# Replace these paths with your actual column_mappings values
mappings = {'input': 'attributes.input.value', 'output': 'attributes.output.value'}
for i, span in enumerate(spans):
    print(f'--- Span {i} ---')
    for var, path in mappings.items():
        parts = path.split('.')
        val = span
        for p in parts:
            val = val.get(p) if isinstance(val, dict) else None
        status = 'FOUND' if val else 'MISSING'
        print(f'  {var} ({path}): {status} — {str(val)[:80] if val else \"null\"}')
"
```
If any variable shows MISSING on all spans, fix the column mapping or adjust `query_filter` to target a different span kind.

---

## Related Skills

- **arize-ai-provider-integration**: Full CRUD for LLM provider integrations (create, update, delete credentials)
- **arize-trace**: Export spans to discover column paths and time ranges
- **arize-experiment**: Create experiments and export runs for experiment column mappings
- **arize-dataset**: Export dataset examples to find input fields when runs omit them
- **arize-link**: Deep links to evaluators and tasks in the Arize UI

---

## Save Credentials for Future Use

See references/ax-profiles.md § Save Credentials for Future Use.
