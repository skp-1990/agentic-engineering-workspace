# Nested identity and attestation PoC

```text
Use poc to compare available upstream attestation methods for a nested identity deployment.
Repositories: <product operator>, <upstream identity server>, <registration controller>.
Target versions: <refs>. The parent and child are in independent clusters.
Investigate bootstrap, reattestation, persistence, CA lifetime, trust propagation,
operator integration, and recovery when the parent is unavailable.
Explain implementation complexity and operational tradeoffs, then test viable approaches.
Ask for the environment roles and permissions you need after researching them.
```

Expected behavior: distinguish first startup from restart/reattestation, compare approaches against common requirements, detect cloud-specific and privilege prerequisites, inspect actual issued lifetime, and make outage tests bounded and reversible. Do not turn a planning formula into a measured nesting/fanout limit or introduce a cloud service without an account/cost scope. Clearly identify temporary manual patches and restoration of normal reconciliation.

A recorded two-cluster trial using this workflow is summarized in the [nested SPIRE live case study](nested-spire-live-validation.md). Its manual patches and tested limits are specific to the pinned versions; use it as evidence and an experiment example, not a universal installer.
