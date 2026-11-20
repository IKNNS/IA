from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("AGENTS.md", "GOALS.md", "PLANS.md", "PROMPTS.md", ".agents/skills/summarize/SKILL.md")
FORBIDDEN_JOB_PARTS = (".env", "id_rsa", "credentials", "password")


def main() -> int:
    failures = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            failures.append(f"missing required file: {relative}")
    for job in (ROOT / "jobs" / "inbox").glob("*.md"):
        lowered = job.read_text(encoding="utf-8").lower()
        for part in FORBIDDEN_JOB_PARTS:
            if part in lowered:
                failures.append(f"job mentions forbidden secret pattern: {job.name} -> {part}")
    if failures:
        print("FAIL")
        print("\n".join(failures))
        return 1
    print("PASS: project structure and inbox safety checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
