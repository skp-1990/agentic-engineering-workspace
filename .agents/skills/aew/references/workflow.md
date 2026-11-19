# AEW Discovery Workflow

## Phase 1: normalise the request

Extract the objective, component names, scope, constraints, desired outcome, validation expectations, and live-cluster requirement. If the request is too broad to investigate, ask for a concise objective.

## Phase 2: resolve the repository

Run `repository-resolution` with all available repository URLs/local paths, component, image, Jira, and release evidence. Resolve each target and relevant dependency independently, with its role and exact revision.

- Continue investigation of resolved repositories and references.
- Request missing evidence when a necessary repository is `not_found` or `ambiguous`; continue independent research where possible.
- Do not infer a repository from generic keywords alone.

## Phase 3: inspect and assess

Inspect the resolved repositories before recommending an implementation. Find relevant APIs, controllers/services, configuration, tests, documentation, ownership, and release constraints. Explain the feature's concepts and follow its path through the existing product. Check versioned upstream implementations before proposing custom code. Separate current product support, upstream support, and proposed changes; label assumptions and conflicting evidence.

Follow the shared [missing-context discovery process](../../poc/references/discovery.md#discover-context-the-user-did-not-supply) even when the user requests discovery only. Use source links, dependency/image pins, tests, and design documents to identify relevant omitted sources. Record each source's origin, purpose, exact ref, and unresolved questions in the assessment (or `research.md` when continuing into a PoC). Keep expansion bounded to the feature's critical path; discovering a source does not authorize running its installers or accessing an environment.

Classify the result as one of:

- **feasible** — a bounded approach is supported by evidence;
- **feasible with constraints** — viable, with explicit dependencies or risks;
- **needs discovery** — insufficient evidence for a responsible recommendation.

## Phase 4: define validation

Propose the smallest proof that validates the objective: existing automated tests first, then local/integration validation, then a disposable live-cluster plan only when requested. State setup, expected observations, cleanup, and rollback boundaries for any live-cluster work.

## Phase 5: report

Provide:

1. executive summary and feasibility classification;
2. objective and scope;
3. supplied and discovered sources, URL, branch/commit, confidence, provenance, and unresolved context;
4. relevant implementation areas;
5. recommended approach and alternatives;
6. validation plan;
7. risks, limitations, and open questions;
8. recommended next action.

Planning-only requests end here. If the user already requested PoC execution, continue with the sibling `poc` workflow using the existing authorization and research; do not ask for a new request simply because discovery has finished. Request only missing environment details or additional scope. Publishing, Jira writes, and PR creation are separate actions unless included in the user's request.
