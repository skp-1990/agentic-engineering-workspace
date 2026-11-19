# Run records and helper commands

`poc.py` uses Python 3.10+ and the standard library. It initializes local files, validates records, and performs optional read-only Kubernetes preflight. It is not an autonomous deployment engine, secret scrubber, authorization mechanism, or semantic judge of test results. The agent performs research and implementation with host tools and must evaluate the actual evidence.

```bash
python3 <skill-dir>/scripts/poc.py init .work/pocs/example --objective 'Compare approaches for the requested feature'
python3 <skill-dir>/scripts/poc.py check .work/pocs/example
python3 <skill-dir>/scripts/poc.py check .work/pocs/example --ready
python3 <skill-dir>/scripts/poc.py check .work/pocs/example --complete
```

Initialization refuses an existing directory, including an empty directory or symlink. To resume, read it rather than initialize again. `check` never changes state. Exit code 0 means the requested consistency checks passed, 1 means invalid/incomplete records, and 2 means CLI usage error. Keep one writer for a run; do not edit `run.json` concurrently.

## Files

| File | Purpose |
| --- | --- |
| `brief.md` | User intent, scope, requirements and acceptance |
| `research.md` | Concepts, versioned sources, repository map, competing approaches |
| `plan.md` | Topology, authorization, preflight, matrix, budgets, rollback |
| `run.json` | Machine-checkable progress, experiments, attempts, resource ledger |
| `runbook.md` | Parameterized reproduction and cleanup instructions |
| `report.md` | Decision, results, tradeoffs, implementation work, limitations |
| `artifacts/` | Prototype, manifests, setup/verify/cleanup scripts |
| `evidence/` | Inspected and sanitized observations, with timestamps and provenance |
| `private/` | Ignored local connection references and sensitive rollback data; never export |

The whole `.work/` tree is ignored by this repository. Other output locations are not automatically ignored; check the destination's Git rules. Local privacy permissions and ignore files do not make a file safe to share. Manually inspect/redact reports, commands and evidence; do not store actual secret values in any shareable field. Evidence paths must be relative files inside the run and cannot point into `private/` or escape through a symlink.

## State contract (schema version 1)

Top-level fields are initialized for you. `phase` is one of `discovery`, `planning`, `awaiting_environment`, `ready`, `experimenting`, `reporting`, `blocked`, `completed`. Set `next_action` after each meaningful step, including how to resume a blocked run. `verdict` is `inconclusive` until evidence justifies `supported`, `supported_with_constraints`, or `not_supported`. Failed approaches can still lead to a completed investigation. For a supported verdict, set `recommended_approach` to the ID validated by passing required experiments.

Edit the arrays as research and experiments progress. This is an **illustrative local experiment**, not evidence that any real feature was tested:

```json
{
  "repositories": [{"role": "target", "location": "https://example.org/team/project", "revision": "exact-commit-and-any-local-diff"}],
  "requirements": [{"id": "R1", "question": "Does the public API preserve the requested value?", "acceptance": "Consumer reads back the same value", "required": true}],
  "approaches": [{"id": "A1", "summary": "Use the existing public API"}],
  "environments": [{"id": "L1", "kind": "local", "role": "test process", "ready": true, "identity": "isolated-local-process", "baseline": "Runtime/version and baseline recorded in plan.md"}],
  "experiments": [{
    "id": "E1", "approach_id": "A1", "requirement_ids": ["R1"], "environment_ids": ["L1"], "required": true,
    "hypothesis": "The existing API suffices", "procedure": "artifacts/verify.py", "expected": "Read-back equals the submitted value",
    "timeout_seconds": 30, "cleanup": "Stop the local test process", "status": "planned", "attempts": []
  }],
  "resources": []
}
```

`required` on an experiment means required to judge **its approach**. Set it before execution; do not downgrade a failing test after the fact. All required requirements need required experiment coverage. Multiple approaches can share requirements, so a rejected alternative's failures do not invalidate a successful recommended approach.

Experiment statuses are `planned`, `running`, `passed`, `failed`, `blocked`, `skipped`, `inconclusive`. Append a completed attempt and set the experiment status to the last attempt's status. Keep earlier attempts. While an attempt is running, use `status: running` and append its record when it finishes; interrupted work must be inspected and recorded before retrying.

An attempt contains:

```json
{
  "status": "passed",
  "started_at": "2026-01-01T10:00:00Z", "finished_at": "2026-01-01T10:00:01Z",
  "command": "python3 artifacts/verify.py", "exit_code": 0,
  "observation": "Actual consumer read-back matched the submitted value",
  "evidence": ["evidence/E1-attempt-1.txt"],
  "change": "Initial attempt"
}
```

Timestamps must include timezones. `passed`, `failed`, and `inconclusive` require a safe command/script reference, integer exit code, and existing evidence file(s). `blocked`, `skipped`, and `inconclusive` need a `reason`; a skipped/blocked attempt can omit command/exit code and evidence when no command ran. Passing a negative test may have a nonzero exit code; the observation must explain the expected rejection.

Before mutation, add a resource entry; update its observed identity afterward:

```json
{
  "id": "X1", "environment_id": "C1", "locator": "Deployment/poc-example/demo",
  "action": "created", "identity": "observed-resource-uid",
  "rollback": "Delete only this run-owned UID, then verify absence",
  "cleanup_status": "pending", "evidence": []
}
```

For `action: modified`, include `baseline_ref` pointing to protected prior field values and later mark `restored`, never `deleted`. Created resources must become `deleted` or explicitly `retained`. Retention requires `owner` and `retention_reason`. Final cleanup states (`deleted`, `restored`, `retained`) require identity and evidence. `pending` or `failed` cleanup prevents completion. This includes local processes/files needing cleanup and external resources, not just Kubernetes objects.

Use `action: removed` only when the user explicitly requests removal of pre-existing resources, such as uninstalling a previous test installation before the new PoC. Include `baseline_ref` for the prior identity/ownership inventory and `removal_authorization` describing the user's instruction and its scope. Record whether rollback is possible; an inventory is not a data backup. Verified intentional removal ends with `cleanup_status: deleted`; a verified rollback ends with `restored`. This does not authorize removal or turn ordinary cleanup into permission to delete existing resources. The agent must check actual ownership and scope before acting.

`--ready` requires a nonempty, edited `plan.md`, linked requirements/approaches/environments, bounded experiments, and ready environments with identity/baseline. It does not check permissions or execute a plan. `--complete` requires terminal experiments, no blocked/skipped required experiments, resolved cleanup, nonempty edited report/runbook, and `phase: completed`. A supported verdict additionally requires all required experiments of the recommended approach to pass and cover every required requirement. An executed but inconclusive experiment can finish an investigation with an inconclusive verdict; a required experiment that could not run leaves a partial investigation. The agent must still read the evidence and verify the report's truth; passing this checker is not proof by itself.
