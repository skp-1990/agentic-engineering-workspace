# Validation record

Validated on 19 November 2026 (Asia/Kolkata). This records development validation of the skills and helper, not qualification of a live product or cluster.

## Automated checks

`python3 -m unittest discover -s tests -v` passed **31 tests** on local Python 3.14.7. The earlier 29-test suite also passed on Python 3.12. The tests cover record initialization, missing/escaping evidence, requirement coverage, recommended versus rejected approaches, blocked required tests, cleanup/retention, explicitly authorized removal of pre-existing installations, malformed inputs, explicit cluster targeting, bounded preflight, suppressed raw errors, skill metadata, relative links, and local symlink installation.

All three skills passed the skill-creator frontmatter validator. Python syntax, mapping/workflow YAML parsing, and `git diff --check` passed. CI is configured to run the offline suite on Python 3.10 and 3.14; hosted CI and Python 3.10 were not run during this local validation.

## Independent local PoC

A fresh agent context received the [Counter fixture](../tests/behavioral/fixtures/counter/README.md), the `poc` skill, and the local-execution request in the [behavioral scenarios](../tests/behavioral/README.md). It was not given the evaluator's rubric or an intended implementation. It used local Python/SQLite, without network, cluster access, external dependencies, or changes to the fixture.

The agent researched the code, recorded requirements and alternatives, produced runnable prototypes, executed 11 experiments, preserved observations, cleaned up runtime resources, and wrote an implementation recommendation:

| Approach/case | Observed result |
| --- | --- |
| Existing behavior | Retrying a lost +5 response produced total 10; baseline defect reproduced |
| Memory cache | Same-process retry worked; fresh-process retry duplicated the increment |
| Separately committed receipt | A synchronized race and a crash between effect and receipt both duplicated the increment |
| Atomic effect and receipt | Six required experiments passed, including replay/conflict handling, concurrent processes, postcommit/precommit process death, existing-data initialization, and lock-timeout recovery |

Eight experiment assertions passed and three failed, providing evidence to reject alternatives. Twelve concurrent duplicate processes produced one increment under the recommended approach. All 13 resource-ledger entries were resolved: runtime resources deleted and the review artifacts explicitly retained. The original fixture's hashes were unchanged. The final report limited its recommendation to the tested local behavior and identified API, retention, and production integration work.

The forward-test found a real defect: `--ready` accepted an empty `plan.md` despite the documented requirement. The helper now rejects blank/unchanged plans and blank/unchanged report/runbook files; regression tests cover these cases. A separate consistency fix rejects completion when required experiments were blocked or skipped. The helper was updated during evaluation; its hash changes and the historical failing probe were retained. Counter experiment code was run-local and unaffected. The finished run passed both readiness and completion checks against the final helper.

The local review copy of the full run is under `.work/validation/poc-forward-test/` in the development checkout (ignored by Git). Its historical commands refer to the original temporary run location. The scenario and fixture are committed so another reviewer can run a fresh evaluation with their chosen agent host.

## Live nested SPIRE pilot

The next evaluation used the user-provided target ZTWIM `main` and three upstream repositories, then two explicitly authorized dedicated OpenShift clusters. The workflow found additional authoritative context and product release pins before environment access. The [case study](../examples/nested-spire-live-validation.md) records exact versions, topology, observations and limitations; the complete local run is retained under `.work/pocs/nested-spire-main/` (ignored by Git).

The pilot exercised source research, local build/tests, actual cluster preflight, an explicitly requested prior-installation uninstall, exact-main local controllers with real operands, manual nested configuration, CSI-backed consumers, bidirectional mutual TLS, child JWT verification through a parent agent, authorization negatives, persistent versus fresh bootstrap, expiry/outage recovery, operator reconciliation, and teardown. The source phase was performed in a separate agent context; the coordinating agent then owned the live run and resource ledger. This is a practical workflow evaluation with fixes during the run, not an untouched blind benchmark.

Observed failures are retained alongside successful retries. They include the required OLM OperatorCondition name for local startup, pre-nesting JWT keys absent from the parent bundle, delayed consumer refresh, and expiry of a join-token bridge credential during an accelerated outage test. A consumed token did not support reattestation. Pod readiness alone was insufficient evidence for these behaviors. The final bounded configuration recovered, normal reconciliation reproduced the product gap, and teardown verified 118 new cluster resource identities and eight local operator processes absent. Both clusters were available without degraded cluster operators, and the run passed `poc.py check --complete`.

The uninstall requirement exposed a record-schema gap: pre-existing objects deliberately removed with user authorization could not be represented correctly as created or modified. The ledger now supports `removed`, requires baseline and authorization references, rejects retention of a removed object, and still blocks unresolved cleanup. Two regression tests cover it. Additional execution guidance addresses persisted state, cold bootstrap and propagation to another consumer.

## Remaining qualification

The pilot demonstrates one feature investigation on two clusters. It does not validate arbitrary features, production reliability, performance/capacity, OLM packaging of the exact-main local controller, or remote PSAT bootstrap. No host picker integration or end-to-end execution was tested in Claude Code, Cursor, or Copilot; documented discovery paths and portable instructions remain compatibility guidance. Hosted CI and the configured Python 3.10 job were not executed locally. Cleanup drift and conflicting-evidence scenarios remain available for further behavioral evaluation.
