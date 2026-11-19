# Execute and preserve evidence

## Build and deploy

Use an isolated prototype path or a suitable branch/worktree; inspect local changes first. Keep research-only work read-only. The user requesting an executed PoC authorizes the necessary local prototype edits, but not unrelated production refactors, publishing images, or pushing to a remote. Use the relevant project build/test instructions and existing harnesses.

Save version-pinned manifests/configuration, setup, validation, and teardown in `artifacts/`, with a parameterized `runbook.md`. Verify syntax/rendered manifests before deploying; server-side dry-run can validate admission when authorized, but does not prove runtime behavior. Avoid unconditional apply/delete of directories that contain resources from several environments.

Before each mutation, record a resource-ledger entry with exact environment and object identity, intended action, existing ownership, and rollback. After it succeeds, update the entry with the observed UID/ID. For modifying an existing resource, capture the minimal prior values needed to reverse the change, including whether fields were absent. Put sensitive baselines in protected local storage. Record operator reconciliation bypasses, RBAC, routes, storage, and external services as well as workload resources.

If the user explicitly requests uninstalling a previous installation first, inventory its ownership, dependents, controllers/finalizers, storage, and shared resources before removal. Record this separately as authorized `removed` resources (see [records.md](records.md)); do not mislabel them as run-created resources or promise restoration from a metadata inventory. Remove consumers before their required controllers/storage interfaces and verify the requested clean baseline. Ordinary PoC cleanup still only deletes run-owned resources.

If an interrupted command may have succeeded, inspect the target before retrying. Use idempotent setup where possible, but do not overwrite another run's resources just because names match. Check resource ownership and actual state.

## Test and diagnose

For every attempt, record UTC time, exact safe command or runnable script reference, source/image versions, environment alias, exit code, bounded duration, expected result, actual observation, and sanitized evidence path. Inspect outputs before saving them; a successful process exit is only evidence, not an automatic pass.

Treat persisted state and consumer refresh as separate parts of a configuration change. A restarted process may keep old certificates, signing keys, cached credentials, or schema state; prove the newly configured path was exercised rather than accepting readiness or reuse as evidence. Distinguish a restart with retained state from a cold bootstrap, and test each when the requirement depends on recovery. For replicated trust or configuration, validate at a different consumer and include a bounded propagation observation before diagnosing failure.

Record attempts append-only in the experiment's `attempts` list. Give each attempt's evidence a distinct or content-addressed path; later probes must not overwrite earlier certificates, outputs or baselines. For a pass, explicitly show how the acceptance criterion was met. For expected failures/negative controls, a nonzero command exit may be correct. Classify unexpected failures as environment, setup, implementation, unsupported behavior, or unresolved, with evidence supporting the diagnosis. Use `inconclusive` if competing explanations remain.

Diagnose in dependency order: credentials/API access; installed capability/version; scheduling/storage/permissions; transport/DNS/TLS; configuration/reconciliation; identity/trust/authorization; application behavior. Correlate producer and consumer evidence across environments. Preserve the original failure before changing anything. Update the assumption and experiment plan when the hypothesis changes; do not retitle a failing test to make it pass.

Wait for explicit readiness/observations with timeouts, rather than arbitrary long sleeps. Stop a mutation loop on loss of access, unexpected shared-resource impact, scope changes, or exhausted retry/budget bounds. Continue useful independent tests where possible. A blocked environment does not prove the approach impossible.

## Cleanup and interruption

Clean up in reverse dependency order after evidence capture, including test registrations, RBAC, routes, cloud resources, temporary files, background processes, and storage the run created. Respect an existing user retention request without asking again. For each retained resource record its owner, reason, expiry/review date where applicable, and exact manual cleanup instructions.

Delete only objects proved to be run-owned, checking identity/UID and intervening changes. Do not delete a pre-existing namespace, shared CRD, or arbitrary object selected by a broad label. Restore only fields changed by this run; do not replay a stale full-object backup over other people's work. If drift makes rollback unsafe, stop that cleanup, record the conflict, and ask about the concrete restoration needed. Do not disable TLS or escalate RBAC to force cleanup.

Verify deletion/restoration and post-cleanup baseline health. Mark each ledger entry `deleted`, `restored`, `retained`, or `failed`, with evidence. Failed/pending cleanup prevents an execution run from being called complete. If a run is interrupted, its ledger and next action must allow the next session to inspect and safely resume or clean up.
