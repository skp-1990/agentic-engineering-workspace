# Agentic Engineering Workspace

AEW is a portable collection of skills for investigating engineering requests and carrying feature proofs of concept from research through implementation, experiments, cleanup, and an evidence-backed recommendation.

Give it a feature/problem statement and the relevant repositories. It learns the concepts and current implementation, checks upstream options, compares approaches, and designs experiments around the questions you need answered. Only then does it request the necessary environment access: none for local experiments, or the appropriate number of clusters, VMs, or services. After execution it explains what worked, what failed, the tradeoffs, and the hard parts of product implementation.

The repository list need not be exhaustive. The skills follow relevant dependency/image pins, source links, tests, and design documents to find missing context, recording why each source matters. They distinguish the product's shipped versions from newer upstream behavior and ask only when the missing context cannot be resolved from evidence.

The agent runs in your existing agent host with its tools and permissions. This repository is not a standalone daemon or a universal deployment program. The agent writes and runs feature-specific prototypes; the included Python helper keeps run records consistent and performs optional read-only Kubernetes checks. A particular feature may remain blocked or infeasible, and the report must say so.

## Skills

| Skill | Purpose |
| --- | --- |
| `aew` | Entry point: discovery/feasibility by default; routes an explicit PoC execution request to `poc`. |
| `repository-resolution` | Resolve one or more explicit repos/local checkouts, exact revisions, or known OpenShift image/component mappings. |
| `poc` | Research, compare, implement, deploy, test, diagnose, report, resume, and clean up a bounded feature PoC. |

`.agents/skills/` is the canonical source. The `poc` skill has progressively loaded references, report/runbook templates, and `scripts/poc.py`. OpenShift-specific mappings and examples are optional; explicit repositories and local/non-Kubernetes experiments work without them.

## Use it

In a host with slash-command skills, invoke `/poc` (or `/aew` with an execution request). In Codex, use `$poc` / `$aew`. If your host lacks a skill picker, ask it to read `.agents/skills/poc/SKILL.md` and follow it. Send the request in the agent chat: `poc.py` is a record/preflight helper, not an agent launcher.

```text
Use the poc skill to investigate and execute a proof of concept for <feature>.
Problem/decision: <what we need to understand or choose>.
Repositories: <URLs or local paths, target refs/releases if relevant>.
My current understanding: <claims to verify>.
Constraints: <platform, versions, time/cost, required behavior>.
Research the concepts and upstream implementations first, compare approaches,
then tell me what environments you need. Build and test the PoC within the
agreed scope and explain the results, failures, tradeoffs, and implementation work.
```

Do not paste kubeconfig contents or credentials. When requested, provide local paths and explicit contexts plus allowed namespaces/resources. The agent reuses supplied authorization rather than repeatedly asking about each reversible step. It asks when the intended action exceeds that scope. Existing cluster files in your workspace are not automatically selected or used.

For discovery only:

```text
Use aew to assess <request>. Repositories: <paths/URLs>.
Planning only: do not modify application code or access a cluster.
```

Resume or clean up:

```text
Use poc to resume .work/pocs/<run-id>; read its state and evidence first.
```

```text
Use poc to clean up .work/pocs/<run-id> using its recorded resource ledger.
```

## Installation and host requirements

The host needs file/repository access, shell execution for experiments, and either browsing/connectors or local source material for research. Python 3.10+ enables the helper; it has no third-party dependencies. `kubectl` or `oc` is needed only for Kubernetes experiments. Missing connectors or a lack of delegation do not prevent using the workflow; the agent reports unavailable capabilities and can work sequentially.

| Host | Project skill location | Invocation |
| --- | --- | --- |
| Codex | `.agents/skills/` | `$poc`, `$aew` |
| Cursor | `.agents/skills/` | `/poc`, `/aew` |
| Claude Code (local) | `.claude/skills/` | `/poc`, `/aew` |
| GitHub Copilot (supported agent clients) | `.agents/skills/` | Ask to use `poc`; picker syntax depends on client |

Opening this repository is sufficient for hosts that discover `.agents/skills/`. To use it from another project, link **all three** sibling skills into the host's skill directory. For local Claude Code, link into `.claude/skills/`, including when opening this repository itself:

```bash
AEW_SOURCE=/absolute/path/to/agentic-engineering-workspace
AEW_DEST=.agents/skills  # use .claude/skills for local Claude Code
mkdir -p "$AEW_DEST"
for skill in aew repository-resolution poc; do
  if [ -e "$AEW_DEST/$skill" ] || [ -L "$AEW_DEST/$skill" ]; then
    printf 'Already exists; inspect before replacing: %s\n' "$AEW_DEST/$skill"
  else
    ln -s "$AEW_SOURCE/.agents/skills/$skill" "$AEW_DEST/$skill"
  fi
done
```

Start a new agent session or reload skills after installation. Symlinks outside a remote/cloud workspace will not travel with it: copy the three directories into that workspace's supported skill location instead. Verify discovery in the specific host/version; portable instructions do not imply identical tools or cloud filesystem access.

Discovery paths were checked against the official [Codex](https://developers.openai.com/codex/skills/), [Cursor](https://cursor.com/docs/skills), [Claude Code](https://code.claude.com/docs/en/skills), and [Copilot](https://docs.github.com/en/copilot/concepts/customizations/agent-skills) documentation. The old Codex `.codex/skills/` installation example has been replaced by the documented `.agents/skills/` path.

## What a run produces

By default, each run is under `.work/pocs/<run-id>/` (ignored by Git):

```text
brief.md        objective, assumptions, acceptance criteria
research.md     concepts, versioned sources, repo map, alternatives
plan.md         experiment matrix, environment roles, scope, rollback
run.json        progress, attempts, evidence links, resource ledger
runbook.md      reproducible setup / test / cleanup commands
report.md       findings, tradeoffs, hard parts, limitations, next steps
artifacts/      prototype code, parameterized manifests and scripts
evidence/       inspected and sanitized observations
private/        ignored local connection references and rollback data
```

Results distinguish observed behavior from documentation, inference, and untested claims. A report does not call a deployment production-ready because a happy-path demo succeeded. Experiments include relevant negative controls and lifecycle cases; a failed approach remains useful evidence. Failed cleanup is reported and blocks completion. Resources explicitly retained by the user have an owner and cleanup instructions.

See the [record contract and helper commands](.agents/skills/poc/references/records.md), [design rationale](docs/poc-design.md), and [behavioral evaluation scenarios](tests/behavioral/README.md).

For a short explanation, an example invocation, and a meeting demo, see the [manager briefing](docs/manager-brief.md).

## Examples

- [Planning: disable federation](examples/ztwim-federation-disable.md)
- [Federation across independent clusters](examples/federation-poc.md)
- [Nested attestation approaches](examples/nested-identity-poc.md)
- [Workload identity for VMs](examples/vm-identity-poc.md)
- [A local API/library experiment](examples/local-api-poc.md)

The examples above describe requests and expected investigation behavior. For executed results, see the [nested SPIRE pilot case study](examples/nested-spire-live-validation.md), including observed failures, recovery, product gaps, and cleanup.

## Development and validation

```bash
python3 -m unittest discover -s tests -v
```

Tests exercise run creation, evidence containment, completion/coverage rules, retained and restored resources, read-only preflight argument targeting, timeouts, and error redaction. They run offline and do not use a real kubeconfig or cluster. Behavioral evaluations complement these checks; read their instructions before running a new scenario. Passing these tests does not establish live feature behavior or verify every agent host.

See the [validation record](docs/validation.md) for executed checks, the independent local PoC, the defect it exposed and the fix, the executed two-cluster pilot, and remaining qualification across agent hosts and feature scenarios.

## Boundaries

Discovery requests remain read-only. Executed PoCs use the user's authorized environments and scope, explicit targeting, bounded experiments, and tracked cleanup. Shareable artifacts exclude credentials and raw secret-bearing dumps. Publishing code/images/reports, opening PRs, and updating Jira require a request for those actions. Add the team-approved license before publishing this repository externally.
