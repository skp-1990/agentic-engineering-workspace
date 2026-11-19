#!/usr/bin/env python3
"""Local PoC records and bounded read-only Kubernetes preflight (stdlib only)."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


PHASES = {"discovery", "planning", "awaiting_environment", "ready", "experimenting",
          "reporting", "blocked", "completed"}
VERDICTS = {"supported", "supported_with_constraints", "not_supported", "inconclusive"}
TERMINAL = {"passed", "failed", "blocked", "skipped", "inconclusive"}
TEMPLATES = Path(__file__).resolve().parents[1] / "assets"


def init_run(directory, objective):
    """Refuse reuse, including nonempty directories and symlinks."""
    if not objective.strip():
        raise ValueError("objective must not be empty")
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    for name in ("evidence", "artifacts", "private"):
        (directory / name).mkdir(mode=0o700)
    for template in TEMPLATES.glob("*.md"):
        shutil.copyfile(template, directory / template.name)
    (directory / ".gitignore").write_text("private/\n__pycache__/\n", encoding="utf-8")
    state = {
        "schema_version": 1, "run_id": directory.name, "objective": objective,
        "created_at": datetime.now(timezone.utc).isoformat(), "phase": "discovery",
        "verdict": "inconclusive", "recommended_approach": None,
        "repositories": [], "requirements": [], "approaches": [],
        "environments": [], "experiments": [], "resources": [],
        "next_action": "Research concepts, repositories, and competing approaches.",
    }
    (directory / "run.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state


def validate(directory, state, gate=None):
    """Validate records, not truth, authorization, redaction, or experiment safety."""
    errors = []

    def need(condition, message):
        if not condition:
            errors.append(message)

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def choice(value, options):
        return isinstance(value, str) and value in options

    def fields(row, names, label):
        for name in names:
            need(nonempty(row.get(name)), f"{label}: missing {name}")

    def rows(name):
        value = state.get(name)
        if not isinstance(value, list):
            errors.append(f"{name}: must be a list")
            return {}
        result = {}
        for index, row in enumerate(value):
            if not isinstance(row, dict):
                errors.append(f"{name}[{index}]: must be an object")
                continue
            key = row.get("id")
            if not nonempty(key):
                errors.append(f"{name}[{index}]: missing id")
                continue
            need(key not in result, f"{name}: duplicate id {key}")
            result[key] = row
        return result

    def links(row, name, known, label, required=True):
        values = row.get(name)
        if not isinstance(values, list):
            errors.append(f"{label}: {name} must be a list")
            return []
        if required:
            need(bool(values), f"{label}: empty {name}")
        for value in values:
            need(isinstance(value, str) and value in known,
                 f"{label}: unknown {name} reference")
        return [value for value in values if isinstance(value, str) and value in known]

    def evidence(row, label, required=False):
        paths = row.get("evidence", [])
        if not isinstance(paths, list):
            errors.append(f"{label}: evidence must be a list")
            return
        if required:
            need(bool(paths), f"{label}: evidence is required")
        root = directory.resolve()
        for value in paths:
            if not nonempty(value):
                errors.append(f"{label}: invalid evidence path")
                continue
            path = Path(value)
            target = (root / path).resolve()
            safe = (not path.is_absolute() and ".." not in path.parts
                    and target.is_relative_to(root) and target != root
                    and not target.is_relative_to(root / "private")
                    and "private" not in path.parts)
            need(safe and target.is_file(), f"{label}: evidence must be an existing shareable file inside the run")

    def timestamp(value):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return result if result.tzinfo is not None else None
        except (AttributeError, TypeError, ValueError):
            return None

    def written_document(name):
        path = directory / name
        if not path.is_file():
            return False
        content = path.read_text(encoding="utf-8").strip()
        return bool(content) and content != (TEMPLATES / name).read_text(encoding="utf-8").strip()

    if not isinstance(state, dict):
        return ["run.json must be an object"]
    need(type(state.get("schema_version")) is int and state["schema_version"] == 1,
         "unsupported schema_version")
    fields(state, ("run_id", "objective", "next_action"), "run")
    need(choice(state.get("phase"), PHASES), "invalid phase")
    need(choice(state.get("verdict"), VERDICTS), "invalid verdict")
    requirements = rows("requirements")
    approaches = rows("approaches")
    environments = rows("environments")
    experiments = rows("experiments")
    resources = rows("resources")
    repositories = state.get("repositories")
    need(isinstance(repositories, list), "repositories must be a list")
    if isinstance(repositories, list):
        for index, repo in enumerate(repositories):
            if not isinstance(repo, dict):
                errors.append(f"repositories[{index}]: must be an object")
                continue
            fields(repo, ("role", "location", "revision"), f"repositories[{index}]")

    for key, row in requirements.items():
        fields(row, ("question", "acceptance"), key)
        need(type(row.get("required")) is bool, f"{key}: required must be boolean")
    for key, row in approaches.items():
        fields(row, ("summary",), key)
    for key, row in environments.items():
        fields(row, ("kind", "role"), key)
        need(type(row.get("ready")) is bool, f"{key}: ready must be boolean")
        if row.get("ready") is True:
            fields(row, ("identity", "baseline"), key)

    for key, row in experiments.items():
        fields(row, ("hypothesis", "procedure", "expected", "cleanup"), key)
        links(row, "requirement_ids", requirements, key)
        targets = links(row, "environment_ids", environments, key)
        need(isinstance(row.get("approach_id"), str) and row["approach_id"] in approaches,
             f"{key}: unknown approach_id")
        need(type(row.get("required")) is bool, f"{key}: required must be boolean")
        need(type(row.get("timeout_seconds")) is int and row["timeout_seconds"] > 0,
             f"{key}: timeout_seconds must be a positive integer")
        status = row.get("status")
        need(choice(status, TERMINAL | {"planned", "running"}), f"{key}: invalid status")
        attempts = row.get("attempts")
        if not isinstance(attempts, list):
            errors.append(f"{key}: attempts must be a list")
            attempts = []
        for index, attempt in enumerate(attempts):
            label = f"{key} attempt {index + 1}"
            if not isinstance(attempt, dict):
                errors.append(f"{label}: must be an object")
                continue
            result = attempt.get("status")
            need(choice(result, TERMINAL), f"{label}: invalid status")
            fields(attempt, ("observation",), label)
            start, finish = timestamp(attempt.get("started_at")), timestamp(attempt.get("finished_at"))
            need(start is not None and finish is not None and finish >= start,
                 f"{label}: ordered timezone-aware timestamps required")
            if choice(result, {"passed", "failed", "inconclusive"}):
                fields(attempt, ("command",), label)
                need(type(attempt.get("exit_code")) is int, f"{label}: exit_code must be an integer")
            if choice(result, {"blocked", "skipped", "inconclusive"}):
                fields(attempt, ("reason",), label)
            evidence(attempt, label, required=choice(result, {"passed", "failed", "inconclusive"}))
        if choice(status, TERMINAL):
            need(bool(attempts) and isinstance(attempts[-1], dict) and attempts[-1].get("status") == status,
                 f"{key}: terminal status must match the last attempt")
        if gate == "ready":
            for target in targets:
                need(environments[target].get("ready") is True, f"{key}: environment {target} is not ready")
        if gate == "complete":
            need(choice(status, TERMINAL), f"{key}: experiment is unfinished")
            if row.get("required") is True:
                need(not choice(status, {"blocked", "skipped"}), f"{key}: required experiment was not executed")

    for key, row in resources.items():
        fields(row, ("locator", "rollback"), key)
        need(isinstance(row.get("environment_id"), str) and row["environment_id"] in environments,
             f"{key}: unknown environment_id")
        action, cleanup = row.get("action"), row.get("cleanup_status")
        need(choice(action, {"created", "modified", "removed"}), f"{key}: invalid action")
        need(choice(cleanup, {"pending", "deleted", "restored", "retained", "failed"}),
             f"{key}: invalid cleanup_status")
        if action == "modified":
            fields(row, ("baseline_ref",), key)
            need(cleanup != "deleted", f"{key}: cannot delete a pre-existing modified resource")
        if action == "created":
            need(cleanup != "restored", f"{key}: created resource must be deleted or retained")
        if action == "removed":
            fields(row, ("baseline_ref", "removal_authorization"), key)
            need(cleanup != "retained", f"{key}: removed resource must be deleted or restored")
        if cleanup == "retained":
            fields(row, ("owner", "retention_reason"), key)
        if choice(cleanup, {"deleted", "restored", "retained"}):
            fields(row, ("identity",), key)
            evidence(row, key, required=True)
        if gate == "complete":
            need(choice(cleanup, {"deleted", "restored", "retained"}), f"{key}: cleanup is unresolved")

    if gate:
        need(bool(requirements), "at least one requirement is needed")
        need(bool(approaches), "at least one approach is needed")
        need(bool(experiments), "at least one experiment is needed")
        for key, requirement in requirements.items():
            if requirement.get("required") is True:
                covered = any(isinstance(row.get("requirement_ids"), list)
                              and key in row["requirement_ids"] and row.get("required") is True
                              for row in experiments.values())
                need(covered, f"{key}: required requirement lacks a required experiment")
    if gate == "ready":
        need(written_document("plan.md"), "plan.md: replace the scaffold with an actual experiment plan")
    if gate == "complete":
        need(state.get("phase") == "completed", "phase must be completed for the completion check")
        for name in ("report.md", "runbook.md"):
            need(written_document(name),
                 f"{name}: replace the scaffold with actual findings/procedures")
        if choice(state.get("verdict"), {"supported", "supported_with_constraints"}):
            selected = state.get("recommended_approach")
            need(isinstance(selected, str) and selected in approaches, "supported verdict needs recommended_approach")
            selected_tests = [row for row in experiments.values()
                              if row.get("approach_id") == selected and row.get("required") is True]
            need(bool(selected_tests) and all(row.get("status") == "passed" for row in selected_tests),
                 "supported verdict requires all required experiments for the recommended approach to pass")
            for key, requirement in requirements.items():
                if requirement.get("required") is True:
                    need(any(isinstance(row.get("requirement_ids"), list) and key in row["requirement_ids"]
                             and row.get("status") == "passed" for row in selected_tests),
                         f"{key}: no passing evidence for recommended approach")
    return errors


def preflight(kubeconfig, context, namespace, permissions, cli="kubectl", timeout=20):
    """Never echo raw subprocess stdout/stderr, credentials, or kubeconfig content."""
    report = {"status": "blocked", "checks": []}
    executable = shutil.which(cli)
    if not executable or not kubeconfig.expanduser().is_file():
        report["checks"].append({"check": "local prerequisites", "status": "blocked"})
        return report
    base = [executable, f"--kubeconfig={kubeconfig.expanduser().resolve()}",
            f"--context={context}", f"--request-timeout={timeout}s"]

    def run(label, args):
        try:
            result = subprocess.run(base + args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    text=True, timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired, UnicodeError):
            report["checks"].append({"check": label, "status": "blocked"})
            return None
        if result.returncode:
            report["checks"].append({"check": label, "status": "blocked"})
            return None
        return result.stdout.strip()

    raw_version = run("server version", ["version", "-o", "json"])
    if raw_version is not None:
        try:
            version = json.loads(raw_version)["serverVersion"]["gitVersion"]
            valid = isinstance(version, str) and re.fullmatch(r"v[0-9][A-Za-z0-9.+_-]{0,80}", version)
        except (ValueError, KeyError, TypeError):
            version, valid = None, False
        report["checks"].append({"check": "server version", "status": "passed" if valid else "blocked"})
        if valid:
            report["server_version"] = version
    uid = run("cluster identity", ["get", "namespace", "kube-system", "-o", "jsonpath={.metadata.uid}"])
    if uid is not None:
        valid = re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", uid)
        report["checks"].append({"check": "cluster identity", "status": "passed" if valid else "blocked"})
        if valid:
            report["cluster_identity"] = uid
    for permission in permissions:
        verb, resource = permission.split(":", 1)
        label = f"permission {permission}"
        result = run(label, ["auth", "can-i", verb, resource, f"--namespace={namespace}"])
        if result is not None:
            report["checks"].append({"check": label, "status": "passed" if result == "yes" else "blocked"})
    if all(check["status"] == "passed" for check in report["checks"]):
        report["status"] = "passed"
    return report


def permission_arg(value):
    if not re.fullmatch(r"[a-z]+:[a-z0-9][a-z0-9./-]*", value):
        raise argparse.ArgumentTypeError("use verb:resource, e.g. create:deployments.apps")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create a new run; never overwrite an existing path")
    init.add_argument("directory", type=Path)
    init.add_argument("--objective", required=True)
    check = commands.add_parser("check", help="validate record consistency; does not authorize actions")
    check.add_argument("directory", type=Path)
    gate = check.add_mutually_exclusive_group()
    gate.add_argument("--ready", action="store_true")
    gate.add_argument("--complete", action="store_true")
    pre = commands.add_parser("preflight", help="bounded read-only Kubernetes checks")
    pre.add_argument("--kubeconfig", type=Path, required=True)
    pre.add_argument("--context", required=True)
    pre.add_argument("--namespace", required=True)
    pre.add_argument("--can-i", action="append", type=permission_arg, dest="permissions")
    pre.add_argument("--cli", choices=("kubectl", "oc"), default="kubectl")
    pre.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            state = init_run(args.directory, args.objective)
            print(json.dumps({"run_id": state["run_id"], "phase": state["phase"]}))
        elif args.command == "check":
            state = json.loads((args.directory / "run.json").read_text(encoding="utf-8"))
            gate_name = "ready" if args.ready else "complete" if args.complete else None
            errors = validate(args.directory, state, gate_name)
            print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
            return 1 if errors else 0
        else:
            if not args.context.strip() or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", args.namespace):
                parser.error("a nonempty explicit context and valid namespace are required")
            if not 1 <= args.timeout <= 300:
                parser.error("timeout must be between 1 and 300 seconds")
            result = preflight(args.kubeconfig, args.context, args.namespace,
                               args.permissions or ["get:pods"], args.cli, args.timeout)
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "passed" else 1
    except (OSError, ValueError) as error:
        # Avoid raw payloads/paths from malformed private files in error messages.
        print(json.dumps({"error": type(error).__name__, "message": "Unable to process local run files; check path, format, and permissions."}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
