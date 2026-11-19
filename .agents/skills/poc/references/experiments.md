# Design experiments before deployment

Assign stable IDs to requirements (`R1`), approaches (`A1`), experiments (`E1`), and environments (`C1` or `L1`). Requirements include both user goals and critical assumptions discovered during research. Give each an observable acceptance criterion and mark whether it is required for the requested conclusion.

Each experiment needs: linked requirements and approach, hypothesis, target environment roles, prerequisites, exact procedure or script, expected observation, pass/fail rule, bounded duration, likely side effects, evidence to collect, and cleanup/rollback. Store concise machine-checkable fields in `run.json`; put detailed procedures in `plan.md` and `artifacts/`.

Choose relevant cases, not a universal checklist:

| Kind | What it can establish |
| --- | --- |
| Baseline/control | Existing behavior without the feature; distinguish environment failure from feature failure |
| Happy path | Actual consumer-visible result across every required boundary |
| Negative control | Wrong identity/input/config is rejected for the intended reason, while a valid control works |
| Lifecycle | Bootstrap, update, reconcile, restart, reattestation/renewal, rotation, disablement, removal |
| Failure/recovery | Unavailable peer, delayed dependency, bad config, partition, expiry, recovery after restoration |
| Compatibility | Selected versions, skew, network topology, platform restrictions, migration |
| Capacity | Measured load/fanout/latency under stated conditions, only when relevant and affordable |

Select the failure cases most likely to invalidate the recommendation. For an unsafe or unavailable test, record `skipped` or `blocked` with why and how it limits the conclusion. A failure injection requires scope for the affected resource and a verified recovery method. Prefer disposable test instances; do not interrupt shared infrastructure to simulate failure.

Separate connectivity, authenticated identity, authorization, configuration acceptance, controller reconciliation, and application behavior. An accepted CR, Ready pod, successful curl, or minted certificate proves only that layer. A negative test passes only when the expected rejection is demonstrated; a generic network timeout is not an authorization result.

Compare approaches under equivalent versions and inputs. Restore the baseline between variants and record carryover. Bound each experiment and the overall investigation with a reasonable time/resource budget, reporting the assumed budget when the user has not given one. After two unsuccessful fixes of the same failure, reassess the hypothesis and environment rather than repeating the command. Continue another viable approach when it can answer the question within scope; otherwise report the blocker.

Use realistic lifecycle intervals when practical. Shortened TTLs or synthetic load can help discriminate designs, but record how they differ from real operation. A brief test cannot establish long-term renewal, reliability, scale, or production readiness.

Plan only enough implementation to make the experiment meaningful. Mark manual patches, disabled reconciliation, insecure bootstrap, custom images, and other shortcuts explicitly; test their removal or explain the production work they defer. Do not label a shortcut as a product-supported feature.
