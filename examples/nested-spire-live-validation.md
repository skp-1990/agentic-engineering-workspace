# Nested SPIRE: live workflow evaluation

This case study records a real run of the portable PoC workflow on 19 November 2026 (Asia/Kolkata). It is an example of the investigation process, not a feature installer or production qualification. The full local run is retained in `.work/pocs/nested-spire-main/` in the development checkout; that directory is ignored by Git. No credentials or cluster addresses belong in this shareable case study.

## Question and source discovery

Can independent parent and child ZTWIM installations issue usable identities in one SPIFFE trust domain, and what would native product support require?

The user supplied the target and three related repositories. The workflow additionally followed dependency pins and relevant source links to the SPIFFE specifications and SPIRE examples. SPIFFE Helper was added for an actual CSI-backed consumer. Research distinguished upstream default branches from the product's deployed release pins.

| Component | Tested/source revision |
| --- | --- |
| ZTWIM target `main` | `02a35f5fd6c7358b031c61c38168f5d639dd22d0` |
| SPIRE | `v1.15.5`, source `f62d747d56e9caa6a38ad4bcbc32dbcc3dc1399a` |
| SPIRE Controller Manager | `v0.7.1`, source `40c1a27565f5228b9170d5611afe119b00d94e1a` |
| SPIFFE CSI | `v0.2.13`, source `75b55d200dc1f1c82e05e2ab3e98f36d9ad52995` |
| SPIFFE Helper consumer | `v0.8.0`, source `dbfe5a62b2018e39a3c0fb6cf1bc976af6ecba17` |
| Live environment | Two independent OpenShift 4.20.8 / Kubernetes v1.33.6 clusters, amd64, standard-csi |

The user explicitly requested complete removal of the prior ZTWIM installations and authorized bounded deployment, tests and cleanup on dedicated clusters. Ownership inventories and UID-preconditioned deletion established clean baselines. A separate cert-manager installation was preserved.

## Approaches and implementation

The target API supports upstream cert-manager/Vault authorities but does not expose the SPIRE upstream authority and bridge configuration. Two product-managed servers need separate clusters because the operator CRs are cluster-scoped singletons.

The selected proof ran a locally compiled exact-main operator against each explicit cluster context, with pinned operand images. It did not publish a new image. The child operator used `CREATE_ONLY_MODE=true` to allow manual ConfigMap/StatefulSet changes. The parent remained normally reconciled except during the bounded outage.

A parent-attested bridge agent shared a Workload API socket and process namespace with the child server. Its keys and SVID persisted on the child server PVC. A parent registration granted the child-server identity downstream authority; a TLS-passthrough Route carried the real SPIRE protocol. CSI-backed consumers used SPIFFE Helper and Python TLS probes with certificate validation and explicit peer SPIFFE-ID checks.

| Approach | Benefit | Cost / qualification |
| --- | --- | --- |
| Existing ZTWIM API alone | Normal product lifecycle | Selected main lacks the required nested configuration |
| Manual create-only configuration | Proves upstream mechanism with actual product operands | Bypasses reconciliation; dedicated installations; product integration remains |
| Separate upstream-only deployment | Isolates SPIRE mechanism | Would not prove product integration; local container attempt was blocked by user-namespace restrictions |
| Remote PSAT bootstrap | Candidate for automatic fresh attestation | Needs parent access to the child API, scoped credentials and policy; not executed in this pilot |

## Observed results

- All 13 source checks and focused existing Go tests passed; the exact-main binary built and both baseline installations became healthy.
- Local startup initially failed without `OPERATOR_CONDITION_NAME`. Providing the run-owned OperatorCondition and environment resolved it.
- The child obtained a parent-signed CA. Its workload chain validated against the parent root, and cross-cluster mutual TLS succeeded in both directions.
- JWT validation initially failed because a pre-nesting child signing key was missing in the parent bundle. After explicit rotation, restart and consumer refresh, validation through a parent agent succeeded. The wrong audience was rejected. This sequence does not isolate a propagation latency measurement.
- With the only matching downstream registration changed to false, a fresh CA request failed with `PermissionDenied` on `NewDownstreamX509CA`, while the mTLS control still worked. Restoring the flag restored issuance.
- A persisted child/bridge restart loaded its existing SVID and recovered mTLS. An isolated bridge with empty state failed to reuse the consumed token.
- During parent unavailability the child continued issuing new workload certificates from its existing CA, while requests for a new CA failed. The original 60-second parent default also shortened node/bridge credentials; the bridge expired and could not reattest using its consumed token. Recovery required a fresh token and CA preparation. The later configuration separated the parent node credential lifetime from the 60-second workload test lifetime.

- With the longer bridge credential, the repeated short outage recovered after gRPC reconnect and consumer refresh: CA issuance, mTLS, chain verification and JWT validation passed. Immediate Ready-pod probes had still failed and are retained.
- Normal reconciliation removed the manual bridge/upstream settings and returned the child to self-signed authority. Cross-cluster chain verification and TLS then failed, confirming the product integration gap.
- Cleanup verified all 118 newly recorded cluster resource identities absent, including dynamic PVs, and all eight local operator processes stopped. The two clusters had no unavailable/degraded cluster operators. The prior authorized uninstall separately resolved 138 old-installation entries; unrelated cert-manager remained. The run passed the helper's completion check.

The full local run report links each result to evidence and retains failures, configuration changes and limitations. These observations do not establish native ZTWIM nested support.

## Work the product would need

Expose and validate nested authority settings; reconcile the bridge and its lifecycle; choose bootstrap policy and credential recovery; protect parent bundle distribution; manage process/socket access and workload selectors; migrate persisted CA/JWT state; model credential lifetimes and outage budgets separately; handle rotation/readiness; and test upgrades and teardown.

The same-UID unix selector and shared process namespace are PoC shortcuts. Join tokens simplify the initial network topology, but do not provide automatic cold reattestation. Shortened certificates make lifecycle behavior observable quickly; they do not measure production reliability, scale, fanout or long-term rotation. The pilot also does not qualify OLM packaging of the new main build or all four host integrations.

## What the evaluation improved in the skills

The workflow now explicitly discovers missing related context with provenance and a bounded relevance rule. Its ledger also represents authorized removal of pre-existing installations, with separate baseline and authorization fields; an inventory is not described as a recoverable backup. Regression tests cover that distinction. Execution guidance now distinguishes persisted state, cold bootstrap and propagation to another consumer.
