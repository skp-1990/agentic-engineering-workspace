# Discovery that informs experiments

Start with the user's intended decision: learn how the feature works, choose an approach, prove an integration, expose implementation risk, or reject an unsuitable design. Write the user's own understanding as falsifiable statements; do not silently treat it as fact.

## Sources and concepts

Use official specifications, versioned upstream docs, maintained implementations, and the selected repositories. Search for prior art before proposing custom code. Use available connectors or browsing; if offline, use local source and label external claims unverified. Jira access is optional: accept pasted context when no connector is available. Do not require an OpenShift mapping for an explicitly supplied project.

For each important concept, explain its role, inputs/outputs, trust or ownership boundary, lifecycle, and relationship to adjacent concepts. Follow one request through the system, including initialization and steady state. Draw a small topology or sequence diagram if it clarifies the mechanism. Track bootstrapping separately from ongoing reconciliation, renewal, recovery, and teardown.

Record sources as `S1`, `S2`, etc., with URL or local path, commit/tag/version, access date, relevant symbol/section, and the claim they support. Prefer commit permalinks for code. Record dirty working-tree changes when they affect behavior. A citation to `main` does not identify the version tested. When docs and code disagree, investigate the deployed version and state what remains uncertain.

## Feature-focused repository map

Resolve repositories independently and assign roles: target product, upstream implementation, controller/operator, API/schema, client/SDK, deployment charts, test harness. Follow dependencies only as far as they affect the question. An unresolved optional repository need not block independent work.

### Discover context the user did not supply

Treat the initial repository list as starting points. Do not make the user enumerate dependencies that the source can identify. Inspect the feature's README/docs links, dependency manifests and lockfiles, image/version pins, submodules, API imports, build/deployment configuration, relevant tests, and linked design proposals. Follow authoritative links to additional repositories, specifications, or issue/PR discussions when they resolve a concrete unknown. A dependency name alone is not proof of its canonical repository; confirm the URL using project/module metadata or official documentation.

For each addition, record the originating file/link, the question it helps answer, resolved source/ref, and whether it is needed for research, building, or live testing. Prefer the product's pinned dependency version for compatibility claims. If upstream default is newer, record it separately; do not silently use newer behavior to describe the product. An enhancement or unmerged PR describes intent, not shipped support.

Repeat this bounded discovery loop until the critical path from user-facing API through runtime dependencies to observable behavior has evidence, or a specific missing source/access blocks it. Fetch only the relevant files or a shallow checkout where possible. Do not recursively clone every dependency. Record relevant candidates left unfetched and why. Ask the user only when authoritative sources disagree, several plausible products/designs remain, access is missing, or a missing requirement changes the decision. Source discovery does not authorize deployment, credentials access, or running repository-provided installers.

Add a context-discovery table to `research.md`. It should let a reviewer distinguish user-provided context, automatically discovered context, unresolved questions, and prior notes used only as hypotheses.

Inspect applicable repository instructions, current commit and local changes, relevant APIs and validation, configuration generation, execution/reconciliation, persistence, external calls, ownership, tests, and release pins. Explain:

| Area | What exists today | Proposed interaction/change | Evidence | Validation gap |
| --- | --- | --- | --- | --- |
| Relevant path/symbol | Current mechanism | Feature's effect | Source ID and ref | Experiment needed |

Distinguish upstream support from what the product exposes or ships. A plugin existing upstream is insufficient if its binary, API, permissions, configuration, or lifecycle is unavailable in the selected product release.

## Alternatives and unknowns

Compare the smallest existing supported path, reuse of another upstream mechanism, and custom extension where they are plausible. Evaluate correctness, capability gaps, security/privilege requirements, portability, bootstrap dependencies, steady-state behavior, recovery, operational burden, performance, maintenance, and upstream acceptance risk. Mark estimates as estimates; do not fabricate timings or line counts.

For each approach, state what must be true, the hardest implementation step, what evidence would reject it, and the cheapest discriminating test. An approach may work technically but lose on deployment complexity or maintainability. Keep rejected approaches and their reasons in the report.

Research is ready for experiment planning when the agent can explain the mechanism and repository integration, identify the unresolved claims, and derive test prerequisites. It need not read the entire repository or exhaust every possible design. If uncertainty only a live experiment can resolve remains, carry it explicitly into the plan.
