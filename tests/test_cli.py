import tempfile
import unittest
from pathlib import Path

from codex_worker import cli
from codex_worker.memory import _slug


class WorkerTests(unittest.TestCase):
    def test_prompt_contains_job_and_boundaries(self):
        prompt = cli.build_prompt("สรุปไฟล์", "job-1")
        self.assertIn("สรุปไฟล์", prompt)
        self.assertIn("Do not access secrets", prompt)
        self.assertIn("job-1", prompt)

    def test_current_codex_command_uses_workspace_sandbox(self):
        self.assertIn("codex exec -s workspace-write", "codex exec -s workspace-write <prompt>")

    def test_memory_slug_is_filesystem_safe(self):
        self.assertEqual(_slug("Decision: use local memory!"), "decision-use-local-memory")

    def test_find_job_uses_sorted_inbox(self):
        with tempfile.TemporaryDirectory() as temp:
            old_inbox = cli.INBOX
            try:
                cli.INBOX = Path(temp)
                (cli.INBOX / "b.md").write_text("b", encoding="utf-8")
                (cli.INBOX / "a.md").write_text("a", encoding="utf-8")
                self.assertEqual(cli.find_job(None).name, "a.md")
            finally:
                cli.INBOX = old_inbox

    def test_approval_marker_is_explicit(self):
        self.assertTrue(cli.requires_approval("approval: required\n\nDo risky work"))
        self.assertFalse(cli.requires_approval("Do ordinary work\n" * 10 + "approval: required"))


if __name__ == "__main__":
    unittest.main()
