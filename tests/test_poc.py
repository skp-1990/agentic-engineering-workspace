"""Offline behavioral contracts for the helper; no real cluster access."""

from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("poc", ROOT / ".agents/skills/poc/scripts/poc.py")
poc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(poc)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        self.state = poc.init_run(self.run, "Test a local feature")
        (self.run / "evidence/result.txt").write_text("Consumer observed expected result.\n")

    def planned(self):
        (self.run / "plan.md").write_text("Run the isolated consumer verification with a ten-second timeout and stop the process.\n")
        state = copy.deepcopy(self.state)
        state["requirements"] = [{"id": "R1", "question": "Does it work?", "acceptance": "Expected consumer result", "required": True}]
        state["approaches"] = [{"id": "A1", "summary": "Existing mechanism"}]
        state["environments"] = [{"id": "L1", "kind": "local", "role": "test process", "ready": True,
                                  "identity": "isolated process", "baseline": "Python runtime recorded"}]
        state["experiments"] = [{"id": "E1", "approach_id": "A1", "requirement_ids": ["R1"], "environment_ids": ["L1"],
                                 "required": True, "hypothesis": "Mechanism works", "procedure": "Run local verification",
                                 "expected": "Consumer result", "cleanup": "Stop local process", "timeout_seconds": 10,
                                 "status": "planned", "attempts": []}]
        return state

    def complete(self):
        state = self.planned()
        state.update(phase="completed", verdict="supported", recommended_approach="A1")
        experiment = state["experiments"][0]
        experiment["status"] = "passed"
        experiment["attempts"] = [{"status": "passed", "started_at": "2026-01-01T00:00:00Z",
                                   "finished_at": "2026-01-01T00:00:01Z", "command": "python3 verify.py",
                                   "exit_code": 0, "observation": "Expected consumer result",
                                   "evidence": ["evidence/result.txt"]}]
        (self.run / "report.md").write_text("Observed consumer result; see evidence/result.txt.\n")
        (self.run / "runbook.md").write_text("Run the isolated local verification and stop it.\n")
        return state

    def test_initialization_and_private_directory(self):
        self.assertEqual(poc.validate(self.run, self.state), [])
        self.assertEqual((self.run.stat().st_mode & 0o777), 0o700)
        self.assertEqual(((self.run / "private").stat().st_mode & 0o777), 0o700)
        self.assertIn("private/", (self.run / ".gitignore").read_text())

    def test_reinitialization_never_overwrites(self):
        for existing in (self.run, self.root / "empty", self.root / "link"):
            if existing.name == "empty":
                existing.mkdir()
            if existing.name == "link":
                existing.symlink_to(self.run, target_is_directory=True)
            with self.assertRaises(FileExistsError):
                poc.init_run(existing, "New objective")
        self.assertEqual(json.loads((self.run / "run.json").read_text())["objective"], "Test a local feature")

    def test_empty_objective_does_not_create_a_run(self):
        target = self.root / "bad"
        with self.assertRaises(ValueError):
            poc.init_run(target, "  ")
        self.assertFalse(target.exists())

    def test_ready_requires_coverage_and_environment(self):
        self.assertTrue(poc.validate(self.run, self.state, "ready"))
        state = self.planned()
        self.assertEqual(poc.validate(self.run, state, "ready"), [])
        state["environments"][0]["ready"] = False
        self.assertTrue(any("not ready" in error for error in poc.validate(self.run, state, "ready")))
        state["experiments"][0]["requirement_ids"] = ["unknown"]
        self.assertTrue(any("lacks a required experiment" in error for error in poc.validate(self.run, state, "ready")))

    def test_success_requires_real_evidence_files(self):
        state = self.complete()
        self.assertEqual(poc.validate(self.run, state, "complete"), [])
        (self.run / "evidence/result.txt").unlink()
        self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_ready_rejects_empty_or_unchanged_plan(self):
        state = self.planned()
        for content in ("", "  \n", (poc.TEMPLATES / "plan.md").read_text()):
            (self.run / "plan.md").write_text(content)
            self.assertTrue(poc.validate(self.run, state, "ready"))

    def test_completion_rejects_empty_or_unchanged_reports(self):
        for name in ("report.md", "runbook.md"):
            for content in ("", "  \n", (poc.TEMPLATES / name).read_text()):
                state = self.complete()
                (self.run / name).write_text(content)
                self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_evidence_cannot_escape_or_reference_private_data(self):
        state = self.complete()
        (self.root / "outside.txt").write_text("outside")
        (self.run / "private/secret.txt").write_text("private")
        (self.run / "evidence/outside-link").symlink_to(self.root / "outside.txt")
        (self.run / "evidence/private-link").symlink_to(self.run / "private/secret.txt")
        for path in ("../outside.txt", str(self.root / "outside.txt"), "private/secret.txt",
                     "evidence/outside-link", "evidence/private-link"):
            with self.subTest(path=path):
                state["experiments"][0]["attempts"][0]["evidence"] = [path]
                self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_zero_exit_does_not_override_a_failed_observation(self):
        state = self.complete()
        state["experiments"][0]["status"] = "failed"
        state["experiments"][0]["attempts"][0]["status"] = "failed"
        self.assertTrue(poc.validate(self.run, state, "complete"))
        state["verdict"] = "not_supported"
        self.assertEqual(poc.validate(self.run, state, "complete"), [])

    def test_negative_control_can_pass_with_nonzero_exit(self):
        state = self.complete()
        state["experiments"][0]["attempts"][0]["exit_code"] = 1
        state["experiments"][0]["attempts"][0]["observation"] = "Invalid request rejected as expected; control succeeds"
        self.assertEqual(poc.validate(self.run, state, "complete"), [])

    def test_failed_alternative_preserved_without_invalidating_recommendation(self):
        state = self.complete()
        state["approaches"].append({"id": "A2", "summary": "Rejected mechanism"})
        alternative = copy.deepcopy(state["experiments"][0])
        alternative.update(id="E2", approach_id="A2", status="failed")
        alternative["attempts"][0]["status"] = "failed"
        state["experiments"].append(alternative)
        self.assertEqual(poc.validate(self.run, state, "complete"), [])

    def test_required_blocked_test_cannot_support_a_verdict(self):
        for status in ("blocked", "skipped", "inconclusive"):
            state = self.complete()
            state["experiments"][0]["status"] = status
            state["experiments"][0]["attempts"][0].update(status=status, reason="Missing prerequisite")
            self.assertTrue(poc.validate(self.run, state, "complete"))
            state["verdict"] = "inconclusive"
            if status == "inconclusive":
                self.assertEqual(poc.validate(self.run, state, "complete"), [])
            else:
                self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_lifecycle_failure_cannot_be_hidden_by_a_happy_path(self):
        state = self.complete()
        lifecycle = copy.deepcopy(state["experiments"][0])
        lifecycle.update(id="E2", status="failed")
        lifecycle["attempts"][0]["status"] = "failed"
        state["experiments"].append(lifecycle)
        self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_uncovered_requirement_and_unfinished_experiment_block_completion(self):
        state = self.complete()
        state["requirements"].append({"id": "R2", "question": "Restart?", "acceptance": "Survives", "required": True})
        self.assertTrue(poc.validate(self.run, state, "complete"))
        state = self.complete()
        state["experiments"][0]["status"] = "running"
        self.assertTrue(poc.validate(self.run, state, "complete"))

    def resource(self):
        return {"id": "X1", "environment_id": "L1", "locator": "test process", "action": "created",
                "identity": "recorded-process-id", "rollback": "Stop exact process", "cleanup_status": "pending",
                "evidence": ["evidence/result.txt"]}

    def test_cleanup_failure_and_pending_cleanup_block_completion(self):
        for status in ("pending", "failed"):
            state = self.complete()
            row = self.resource()
            row["cleanup_status"] = status
            state["resources"] = [row]
            self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_retention_requires_owner_reason_and_evidence(self):
        state = self.complete()
        row = self.resource()
        row["cleanup_status"] = "retained"
        state["resources"] = [row]
        self.assertTrue(poc.validate(self.run, state, "complete"))
        row.update(owner="requesting team", retention_reason="User requested demo retention until tomorrow")
        self.assertEqual(poc.validate(self.run, state, "complete"), [])

    def test_modified_existing_resource_requires_restore_not_delete(self):
        state = self.complete()
        row = self.resource()
        row.update(action="modified", cleanup_status="deleted")
        state["resources"] = [row]
        self.assertTrue(poc.validate(self.run, state, "complete"))
        row.update(cleanup_status="restored", baseline_ref="private/prior-fields.json")
        self.assertEqual(poc.validate(self.run, state, "complete"), [])

    def test_intentional_removal_requires_scope_baseline_and_evidence(self):
        state = self.complete()
        row = self.resource()
        row.update(action="removed", cleanup_status="deleted")
        state["resources"] = [row]
        self.assertTrue(poc.validate(self.run, state, "complete"))
        row["baseline_ref"] = "private/pre-uninstall-inventory.json"
        self.assertTrue(poc.validate(self.run, state, "complete"))
        row["removal_authorization"] = "User requested complete uninstall on the dedicated test environment"
        self.assertEqual(poc.validate(self.run, state, "complete"), [])
        row["evidence"] = []
        self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_intentional_removal_completion_requires_deleted_or_restored(self):
        state = self.complete()
        row = self.resource()
        row.update(action="removed", baseline_ref="private/prior.json",
                   removal_authorization="User requested removing prior test installation")
        state["resources"] = [row]
        for status in ("pending", "failed", "retained"):
            row.update(cleanup_status=status, owner="team", retention_reason="Not deleted")
            self.assertTrue(poc.validate(self.run, state, "complete"))
        for status in ("deleted", "restored"):
            row["cleanup_status"] = status
            self.assertEqual(poc.validate(self.run, state, "complete"), [])

    def test_malformed_records_return_errors_not_exceptions(self):
        for value in (None, [], "invalid"):
            self.assertTrue(poc.validate(self.run, value))
        for field in ("phase", "verdict", "requirements", "repositories"):
            state = self.complete()
            state[field] = {"malformed": True}
            self.assertTrue(poc.validate(self.run, state, "complete"))
        for field in ("status", "approach_id", "environment_ids", "attempts"):
            state = self.complete()
            state["experiments"][0][field] = {"malformed": True}
            self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_duplicate_ids_and_attempt_mismatch_are_rejected(self):
        state = self.complete()
        state["requirements"].append(copy.deepcopy(state["requirements"][0]))
        self.assertTrue(poc.validate(self.run, state, "complete"))
        state = self.complete()
        state["experiments"][0]["attempts"][0]["status"] = "failed"
        self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_timestamps_must_be_ordered_and_timezone_aware(self):
        for finish in ("2025-01-01T00:00:00Z", "2026-01-01T00:00:02", "bad"):
            state = self.complete()
            state["experiments"][0]["attempts"][0]["finished_at"] = finish
            self.assertTrue(poc.validate(self.run, state, "complete"))

    def test_cli_check_does_not_mutate_state(self):
        before = (self.run / "run.json").read_bytes()
        with redirect_stdout(io.StringIO()) as output:
            code = poc.main(["check", str(self.run)])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output.getvalue())["valid"])
        self.assertEqual(before, (self.run / "run.json").read_bytes())


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = Path(self.temp.name) / "config"
        self.config.write_text("not a real kubeconfig")
        self.which = patch.object(poc.shutil, "which", return_value="/fake/kubectl")
        self.which.start()
        self.addCleanup(self.which.stop)

    def success(self, args, **kwargs):
        if "version" in args:
            output = json.dumps({"serverVersion": {"gitVersion": "v1.31.0"}})
        elif "namespace" in args:
            output = "12345678-1234-1234-1234-123456789012"
        else:
            output = "yes"
        return subprocess.CompletedProcess(args, 0, output)

    def call(self):
        return poc.preflight(self.config, "explicit-context", "poc-test", ["get:pods", "create:deployments.apps"])

    def test_commands_are_targeted_bounded_and_read_only(self):
        with patch.object(poc.subprocess, "run", side_effect=self.success) as run:
            self.assertEqual(self.call()["status"], "passed")
        self.assertEqual(run.call_count, 4)
        for call in run.call_args_list:
            args = call.args[0]
            self.assertIn(f"--kubeconfig={self.config}", args)
            self.assertIn("--context=explicit-context", args)
            self.assertIn("--request-timeout=20s", args)
            self.assertEqual(call.kwargs["timeout"], 20)
            self.assertEqual(call.kwargs["stderr"], subprocess.DEVNULL)
            self.assertNotIn("shell", call.kwargs)
            self.assertTrue(any(command in args for command in ("version", "get", "auth")))
            self.assertFalse({"apply", "delete", "patch", "use-context", "--raw"}.intersection(args))
            if "auth" in args:
                self.assertIn("--namespace=poc-test", args)

    def test_failure_and_timeout_never_echo_raw_sensitive_output(self):
        failures = [subprocess.CompletedProcess([], 1, "token=SECRET"),
                    subprocess.TimeoutExpired("token=SECRET", 20, output="SECRET"),
                    OSError("token=SECRET")]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                kwargs = {"side_effect": failure} if isinstance(failure, Exception) else {"return_value": failure}
                with patch.object(poc.subprocess, "run", **kwargs):
                    report = self.call()
                self.assertEqual(report["status"], "blocked")
                self.assertNotIn("SECRET", json.dumps(report))

    def test_malformed_success_output_is_not_a_pass(self):
        with patch.object(poc.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "token=SECRET")):
            report = self.call()
        self.assertEqual(report["status"], "blocked")
        self.assertNotIn("SECRET", json.dumps(report))

    def test_permission_denial_blocks_readiness(self):
        def result(args, **kwargs):
            if "auth" in args:
                return subprocess.CompletedProcess(args, 0, "no")
            return self.success(args, **kwargs)
        with patch.object(poc.subprocess, "run", side_effect=result):
            self.assertEqual(self.call()["status"], "blocked")

    def test_missing_config_never_invokes_cli(self):
        self.config.unlink()
        with patch.object(poc.subprocess, "run") as run:
            self.assertEqual(self.call()["status"], "blocked")
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
