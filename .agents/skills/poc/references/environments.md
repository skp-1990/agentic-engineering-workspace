# Environment request and preflight

Derive environments from the experiment graph after research. Do not always demand two clusters, and do not collapse independent-cluster behavior into namespaces without explaining the loss of fidelity. A language/library/API PoC may be entirely local.

Request missing information together, adapting this form:

> The planned experiments need **[count and roles]** because **[cross-boundary behavior]**. I will create/change **[resources and scope]**, test **[behavior and bounded failures]**, and **[clean up/retain]** afterward. Please provide **[local kubeconfig paths and explicit contexts, or service/VM connection references]**, the allowed namespaces/projects, relevant installed versions/capabilities, and any restrictions on shared resources, cost, disruption, or retention.

Reuse supplied details and authorization. Do not ask for secret values in chat. Store connection references in `private/environments.local.json`, never kubeconfig contents. Keep the shareable state limited to environment aliases, roles, versions, and a sanitized identity marker. Use the host's secret facility or files outside the repository for actual credentials. Do not inspect unrelated credential directories to discover access.

## Kubernetes / OpenShift

1. Confirm the file exists and the user-selected context is present. Kubeconfig auth plugins can execute local programs; use configurations from the user/trusted setup, not an arbitrary downloaded example. Do not print `config view --raw`, Secrets, or full environment dumps.
2. Use explicit `--kubeconfig` and `--context` on **every** command, including reads, exec/logs, Helm, and cleanup. Do not change the user's global current context. In scripts use per-role functions/argument arrays, never a mutable global context switched between clusters.
3. Run the bounded, read-only helper if available:

   ```bash
   python3 <skill-dir>/scripts/poc.py preflight \
     --kubeconfig /local/path/config --context selected-context \
     --namespace poc-example --can-i get:pods --can-i create:deployments.apps
   ```

   It checks server version, a cluster identity marker (the `kube-system` namespace UID), and requested namespaced permissions. It never deploys or writes kubeconfig, and suppresses raw command output/errors. If identity lookup is forbidden, record the limitation and establish identity via another authorized method. An inaccessible server or denied permission is a blocker, not a prompt to weaken RBAC/TLS. A nonzero exit means preflight is incomplete.
4. Compare identity markers for roles requiring independent clusters; two paths/contexts may point to the same cluster. Check the feature's actual CRDs/operators, API versions, registry access, storage, architecture, VM capability, DNS, directional network reachability, TLS/SNI, and clock requirements. The helper's generic checks do not establish these. Check specific cluster-scoped privileges separately when the plan needs them; `auth can-i --list` or a cluster-admin grant is not a substitute for scoped requirements.
5. Capture a minimal baseline and identify shared/operator-owned resources. Confirm permissions for each intended write before deployment. Use a unique run namespace where feasible. Cluster-scoped resources, operator subscriptions, CRDs, webhooks, SCC/RBAC grants, and network/ingress changes must be explicitly accounted for even when the workload itself is namespaced.

For manifests and commands use parameters such as `CLUSTER_A_KUBECONFIG`, `CLUSTER_A_CONTEXT`, and `RUN_NAMESPACE`, with fail-fast checks that they are supplied. Do not embed real connection paths or endpoints in committed examples.

## Other environments

For local processes/containers, record runtime/dependency versions, ports, mounted paths, existing processes, and cleanup commands. For VMs, record the connection reference, OS, privilege boundary, snapshots/backups if needed, and installed components. For cloud/API services, verify account/project/region, service version, scoped permissions, quotas/cost constraints, and cleanup for every external resource. Use explicit account/endpoint targeting, analogous to explicit cluster contexts.

## Scope record

Write the user's authorization in `plan.md`: environments, permitted resources/actions, disruptions, bounds, cleanup/retention, and the message or other trusted basis. Existing authorization persists across phases and resumes until changed. Do not represent the JSON `ready` flag or a successful preflight as authorization. When a discovery needs broader scope, prepare the exact additional change and its rollback, then ask only about that change.
