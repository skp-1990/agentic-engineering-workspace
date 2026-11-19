# Workload identity in virtual machines

```text
Use poc to investigate workload identity for applications inside our VMs.
Repositories: <operator>, <identity server/agent>, <virtualization integration>.
We have earlier notes suggesting a host-to-guest bridge and custom attestor.
Check whether built-in mechanisms and existing networking can meet our needs.
Compare transport, node attestation, workload identity and registration independently.
After research, request the needed VM/cluster environments and test the viable options.
```

Expected behavior: treat the earlier design as a hypothesis; map guest/host isolation and credential boundaries; compare direct networking and bridges where plausible, and built-in attestors against a custom plugin. Test authenticated joining, distinct workload identities, restart/renewal, rejection of wrong credentials, and registration lifecycle. Report separately what the PoC automates and what production integration still needs. Do not present metadata matching alone as proof of identity.
