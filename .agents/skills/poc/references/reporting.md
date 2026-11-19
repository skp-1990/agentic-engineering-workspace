# Report for a decision

Lead with what was learned and whether the evidence supports the requested feature under the tested conditions. Use `supported`, `supported_with_constraints`, `not_supported`, or `inconclusive` as the experiment verdict. `completed` is the workflow phase, not a claim that the approach worked.

Use `assets/report.md` as a starting structure and remove irrelevant sections. Include:

- The user's objective, corrected assumptions, concepts, and end-to-end mechanism in language suitable for the team.
- Repositories/commits, deployed images/versions, topology, environment aliases, and scope. Explicitly identify local simulation versus live testing.
- Results by requirement and experiment: pass/fail/blocked/skipped/inconclusive, expected versus observed, and evidence links. Preserve failed attempts and distinguish environment blockers from design failures.
- Approach comparison: what worked, what did not, tradeoffs, custom code/dependencies/privileges, deployment and recovery complexity, ongoing operations, and conditions under which another approach wins. Explain changes to an earlier recommendation.
- Hard implementation work: affected APIs/components, bootstrap and lifecycle integration, reconciliation/ownership, compatibility, security/trust, failure recovery, tests, and upstream gaps.
- Reproduction commands, setup parameters, negative controls, cleanup outcome, retained resources, and the next resumable action.
- Limitations: what was not tested, how shortcuts narrow confidence, and what evidence is still needed before product support or production use. Do not invent performance, scale, reliability, or security guarantees from a demo.

Every material conclusion must link to an experiment observation or versioned source; label deductions and untested hypotheses. A supported verdict requires passing evidence for every required experiment of the recommended approach and coverage of every required requirement. Failed alternatives remain part of the comparison. Required tests of the recommended approach that fail, are blocked/skipped, or remain inconclusive cannot be hidden behind a supported verdict; narrow the declared scope transparently with the user's agreement or report `inconclusive`/`not_supported`. Blocked/skipped required experiments leave the investigation partial, even with an inconclusive verdict.

For `not_supported`, show evidence that the approach fails a requirement and separate that from mere lack of access. For a partial run, report completed work now, list exact blockers and cleanup status, and leave phase `blocked` or `reporting` with `next_action`. A scaffold, static check, or dry run must never be reported as a live PoC result.

Reports are local by default. Inspect all artifacts for secrets and environment-specific details before a user-requested export or commit. Do not copy raw kubeconfigs, private keys, token-bearing commands, full Secrets, or unredacted logs into a PR or shared report.
