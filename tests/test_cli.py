import tempfile
import unittest
from pathlib import Path

from codex_worker import cli


class WorkerTests(unittest.TestCase):
    def test_prompt_contains_job_and_boundaries(self):
        prompt = cli.build_prompt("สรุปไฟล์", "job-1")
        self.assertIn("สรุปไฟล์", prompt)
        self.assertIn("Do not access secrets", prompt)
        self.assertIn("job-1", prompt)

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


if __name__ == "__main__":
    unittest.main()
