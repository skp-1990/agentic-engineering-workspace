# Why the PoC workflow is structured this way

The initial AEW repository provided useful planning and repository-resolution skills, but stopped before prototype implementation or live validation. This extension preserves discovery-only behavior and adds one end-to-end `poc` skill. It uses the host's existing agent/tool loop instead of introducing a second agent service or a host-specific subagent configuration.

## Changes to existing behavior

- `aew` routes an explicit execution/resume/cleanup request to `poc`; a planning request still stops at its report. Already-authorized PoC work no longer needs a second request simply because discovery ended.
- Repository resolution accepts multiple explicit repositories and local checkouts for any project. It records exact revisions and local changes, discovers remote default branches, keeps release pins, and can continue independent work while one source is unresolved.
- The original map contained keyword entries while the resolver required an absent “unambiguous” marker. Resolution now considers all defined matches and rejects actual ambiguity. The `ZTWIM` alias used by the original example is explicitly mapped, including release resolution. The canonical ZTWIM URL replaces its verified redirect.
- Codex installation uses the documented `.agents/skills/` discovery path. Installation preserves existing skills and includes all sibling dependencies.

## Lessons applied from prior investigations

Historical federation work included bootstrap, two/three-cluster topology, route profiles, workload trust, refresh, and removal. That argues for separate experiments per lifecycle and ownership boundary, with consumer-level proof and negative controls.

Nested identity experiments compared multiple attestors under similar topology. Restart behavior, persistent keys, metadata access, service readiness, and trust lifetime mattered beyond first startup. Later research explicitly separated calculated lifetime guidance and proposed scale targets from measured capacity. The new workflow requires those distinctions in its evidence and report.

VM integration materials contain earlier recommendations for a bridge and a custom attestor, followed by a later ADR choosing direct networking and a built-in attestor. Rather than copying either conclusion into generic instructions, the workflow requires comparison of existing capabilities, source versions, conflicting claims, and operational costs. Earlier notes are hypotheses and historical evidence, not authority over the tested version.

No source PoC scripts, credentials, cluster endpoints, or product-specific implementation assumptions are copied into the reusable workflow. The [experience patterns](../.agents/skills/poc/references/experience-patterns.md) explain the abstract lessons.

## What is deterministic and what remains agent work

The Python helper does only three things: initializes a resumable run, checks structural evidence/coverage/cleanup consistency, and performs bounded read-only Kubernetes preflight. It cannot certify that evidence is truthful, redact arbitrary secrets, infer authorization, choose a safe failure injection, or deploy any possible feature. Those decisions remain explicit responsibilities of the skill-driven agent and its host permission controls.

Research, environment selection, implementation and deployment are deliberately adaptive. An API experiment can run locally. A cross-cluster feature can require multiple real clusters. Environment details are requested after the plan establishes those needs. A shared platform change is identified and scoped even if the actual test workload is namespaced.

One run has one state writer. Versioned sources, append-only experiment attempts, a mutation ledger, and a next action make progress recoverable across sessions and hosts. Evidence is local by default. Supported verdicts require coverage for the recommended approach; a rejected alternative does not erase a successful comparison, and a blocked environment does not become proof of infeasibility.

## Validation scope

Offline tests cover deterministic behavior. Behavioral scenarios test whether an agent can follow the instructions and make appropriate decisions, including a real local feature experiment. Live cluster qualification must be a separate requested PoC with current environment access. These checks cannot promise universal success across arbitrary products or identical behavior across all host models.
