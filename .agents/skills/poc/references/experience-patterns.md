# Patterns learned from prior PoCs

These are experiment-design lessons from a user's historical SPIRE/ZTWIM investigations, not current product documentation or freshly reproduced results. They generalize beyond those projects. Validate any product-specific claim against the selected version before using it.

| Historical investigation | Useful lesson | General experiment |
| --- | --- | --- |
| Federation setup, two/three-cluster verification, bundle refresh, and removal | Initial exchange, ongoing refresh, consumer access, and teardown are different capabilities | Verify bootstrap, actual cross-boundary consumer behavior, rotation, rejection of an untrusted peer, and removal independently |
| Route profile comparisons | Reachability can succeed while the protocol's identity/authentication assumptions are broken | Trace TLS termination, endpoint identity, SNI, and directionality; test the actual protocol rather than an unauthenticated curl |
| Operator configuration versus controller-managed relationships | Multiple layers may configure similar-looking state with different ownership | Trace API → generated config → runtime datastore → consumer; test reconciliation and avoid competing owners |
| Nested attestor comparisons | A successful first startup may hide inability to reattest after restart or key loss | Test initial join, persistent-state restart, permitted loss-of-state recovery, and dependency outage separately |
| Challenge-based bootstrap | Readiness can depend on the very endpoint hidden by readiness gating | Test cold-start ordering and endpoint availability before marking the workload Ready |
| Nested lifetime and topology analysis | Configured lifetime, actual remaining validity, planning guidance, and measured capacity are distinct | Inspect issued values across lifecycle boundaries; measure scale independently; label analytical limits and proposed qualification targets |
| VM integration alternatives and later ADR | Earlier designs favored a bridge/custom attestor; later reasoning selected simpler existing transport/attestation | Re-test assumptions against actual networking and built-in mechanisms before designing a custom plugin |
| Manual PoC patches under an operator | A demo can depend on disabled reconciliation or a non-product configuration | Record each bypass and the production integration work; test with normal ownership restored when feasible |

The local materials consulted when designing this workflow included `federation-setup/README.md`, federation Q&A and route guides, `nested-spire/cloud_attestor_comparison/README.md`, `nested-spire/research/nested-spire-limits.md`, VM working steps/Q&A and x509pop notes, and the later VM connectivity/attestation ADR. These files are not dependencies of AEW and no cluster details or credentials from them are included here.
