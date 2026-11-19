# Cross-cluster federation PoC

```text
Use poc to investigate and execute federation for our workload identity product.
Repositories: <operator path/URL>, <identity server>, <controller manager>, <client>.
Target versions: <release or commits>.
I want to understand bootstrap, relationship configuration, endpoint authentication,
workload trust selection, rotation, and removing a peer. Compare available upstream
mechanisms and endpoint profiles, and explain the operator/controller integration.
Research first, then request the minimum live-cluster topology. No access is supplied yet.
```

Expected behavior: trace each configuration owner and the real consumer path; derive independent cluster roles; request explicit kubeconfig paths/contexts and allowed changes after research; check each direction of connectivity and trust. Plan positive/negative workload tests, refresh/rotation and removal. A third cluster is requested only if fanout/new-peer behavior is in scope. Preserve failed variants, reconcile baselines, and report what rotation/scale was actually observed.
