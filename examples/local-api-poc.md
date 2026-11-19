# Local API/library PoC

```text
Use poc to compare approaches for adding idempotent retries to this service.
Repository: <local path>. Investigate the request handling and persistence paths.
I need to know whether retrying after a lost response can duplicate a side effect,
and whether request keys or transactional storage can prevent it.
Run a local prototype and test process restarts and concurrent duplicate requests.
Use only temporary local files/processes; no cluster, external service, or new dependency.
```

Expected behavior: inspect the service, compare feasible approaches, derive a local harness, preserve a baseline duplicate-side-effect reproduction, test each strategy and the relevant concurrency/restart cases, then clean up local processes/state. The final report links actual observations to the implementation recommendation and states where a local simulation differs from the real deployment.
