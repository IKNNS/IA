from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .memory import save_note


ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "jobs" / "inbox"
PROCESSING = ROOT / "jobs" / "processing"
DONE = ROOT / "jobs" / "done"
FAILED = ROOT / "jobs" / "failed"
RUNS = ROOT / "runs"
WORKTREES = ROOT / "worktrees"
LOCK_PATH = ROOT / ".worker.lock"
DEFAULT_TIMEOUT_SECONDS = 15 * 60
DEFAULT_RETRIES = 1
DEFAULT_INTERVAL_SECONDS = 60
NOTIFICATIONS = ROOT / "notifications.jsonl"


def now_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{os.getpid()}-{uuid.uuid4().hex[:6]}"


def ensure_dirs() -> None:
    for directory in (INBOX, PROCESSING, DONE, FAILED, RUNS, WORKTREES, ROOT / "workspace", ROOT / "outputs"):
        directory.mkdir(parents=True, exist_ok=True)


def find_job(requested: str | None) -> Path | None:
    if requested:
        path = Path(requested)
        if not path.is_absolute():
            path = ROOT / path
        return path if path.is_file() else None
    jobs = sorted(INBOX.glob("*.md"))
    return jobs[0] if jobs else None


def requires_approval(job_text: str) -> bool:
    return any(line.strip().lower() == "approval: required" for line in job_text.splitlines()[:10])


def build_prompt(job_text: str, job_id: str, worktree: Path | None = None) -> str:
    worktree = worktree or ROOT
    return f"""You are running as a bounded local worker.

Repository worktree: {worktree}
Job id: {job_id}
Allowed input directory: {ROOT / 'workspace'}
Allowed long-lived output directory: {ROOT / 'outputs'}
Run evidence directory: {RUNS / job_id}

Safety rules:
- Follow AGENTS.md.
- Do not access secrets, credentials, SSH keys, browser profiles, or unrelated home-directory files.
- Do not push, deploy, send messages, make purchases, delete data, or call external systems.
- If the job requests a risky action, stop and explain what needs human approval.
- Do not merge or push the worktree. A human reviews the diff after this run.
- Verify your work and write a concise final report to stdout.

User job:
---
{job_text}
---
"""


def write_status(run_dir: Path, **values: object) -> None:
    status_path = run_dir / "status.json"
    current: dict[str, object] = {}
    if status_path.exists():
        current = json.loads(status_path.read_text(encoding="utf-8"))
    current.update(values)
    status_path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def notify(job_id: str, state: str, message: str) -> None:
    event = {
        "at": datetime.now(timezone.utc).isoformat(),
        "job_id": job_id,
        "state": state,
        "message": message,
    }
    with NOTIFICATIONS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def claim_job(job: Path) -> Path:
    """Atomically move an inbox job to processing."""
    processing_job = PROCESSING / job.name
    if processing_job.exists():
        raise RuntimeError(f"job is already processing: {job.name}")
    shutil.move(str(job), str(processing_job))
    return processing_job


def finish_job(processing_job: Path, success: bool) -> None:
    if processing_job.parent != PROCESSING or not processing_job.exists():
        return
    destination = DONE if success else FAILED
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / processing_job.name
    if target.exists():
        target = destination / f"{processing_job.stem}-{now_id()}{processing_job.suffix}"
    shutil.move(str(processing_job), str(target))


def release_job(processing_job: Path) -> None:
    if processing_job.parent != PROCESSING or not processing_job.exists():
        return
    target = INBOX / processing_job.name
    if target.exists():
        target = INBOX / f"{processing_job.stem}-{now_id()}{processing_job.suffix}"
    shutil.move(str(processing_job), str(target))


def create_worktree(job_id: str, run_dir: Path) -> Path:
    worktree = WORKTREES / job_id
    result = subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    (run_dir / "worktree-create.stdout").write_text(result.stdout, encoding="utf-8")
    (run_dir / "worktree-create.stderr").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git worktree add failed")
    return worktree


def capture_diff(worktree: Path, run_dir: Path) -> None:
    status = subprocess.run(["git", "status", "--short"], cwd=worktree, text=True, capture_output=True, check=False)
    stat = subprocess.run(["git", "diff", "--stat"], cwd=worktree, text=True, capture_output=True, check=False)
    names = subprocess.run(["git", "diff", "--name-status"], cwd=worktree, text=True, capture_output=True, check=False)
    summary = "[git status --short]\n" + status.stdout
    summary += "\n[git diff --stat]\n" + stat.stdout
    summary += "\n[git diff --name-status]\n" + names.stdout
    (run_dir / "diff-summary.txt").write_text(summary, encoding="utf-8")
    changed = [line for line in status.stdout.splitlines() if line.strip()]
    write_status(run_dir, changed_files=changed, diff_summary=str(run_dir / "diff-summary.txt"))


def run_job(job: Path, execute: bool, timeout_seconds: int, retries: int, approve: bool) -> int:
    job_id = f"{now_id()}-{job.stem}"
    run_dir = RUNS / job_id
    run_dir.mkdir(parents=True, exist_ok=True)
    processing_job = job

    print(f"job: {job_id}")
    print(f"input: {job}")
    print(f"run: {run_dir}")

    job_text = job.read_text(encoding="utf-8")
    needs_approval = requires_approval(job_text)
    write_status(run_dir, job_id=job_id, job=str(job), state="created", approval="approved" if approve else ("pending" if needs_approval else "not-required"), created_at=datetime.now(timezone.utc).isoformat())

    if not execute:
        print("mode: dry-run")
        print("command: codex exec -s workspace-write <prompt from prompt.txt> in an isolated worktree")
        return 0

    git_check = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if git_check.returncode != 0:
        message = "project is not a Git repository; run git init or clone the project first"
        write_status(run_dir, state="blocked", finished_at=datetime.now(timezone.utc).isoformat(), error=message, returncode=78)
        print(f"error: {message}", file=sys.stderr)
        return 78

    if job.parent == INBOX:
        processing_job = claim_job(job)
        write_status(run_dir, state="claimed", claimed_at=datetime.now(timezone.utc).isoformat(), claimed_job=str(processing_job))

    if needs_approval and not approve:
        release_job(processing_job)
        write_status(run_dir, state="awaiting-approval", finished_at=datetime.now(timezone.utc).isoformat())
        notify(job_id, "awaiting-approval", "job requires explicit approval; rerun with --approve")
        print("status: awaiting approval; rerun with --approve", file=sys.stderr)
        return 3

    try:
        worktree = create_worktree(job_id, run_dir)
    except (OSError, RuntimeError) as error:
        finish_job(processing_job, success=False)
        write_status(run_dir, state="worktree-failed", finished_at=datetime.now(timezone.utc).isoformat(), error=str(error), returncode=78)
        notify(job_id, "worktree-failed", str(error))
        print(f"error: could not create worktree: {error}", file=sys.stderr)
        return 78

    prompt = build_prompt(job_text, job_id, worktree)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    write_status(run_dir, worktree=str(worktree), state="worktree-ready")

    codex_bin = os.environ.get("CODEX_BIN", "codex")
    command = [codex_bin, "exec", "-s", "workspace-write", prompt]
    env = os.environ.copy()
    write_status(run_dir, state="running", started_at=datetime.now(timezone.utc).isoformat(), timeout_seconds=timeout_seconds, retries=retries)
    last_returncode = 1

    for attempt in range(1, retries + 2):
        attempt_dir = run_dir / f"attempt-{attempt}"
        attempt_dir.mkdir(exist_ok=True)
        try:
            result = subprocess.run(
                command,
                cwd=worktree,
                env=env,
                text=True,
                capture_output=True,
                stdin=subprocess.DEVNULL,
                timeout=timeout_seconds,
                check=False,
            )
            (attempt_dir / "stdout.txt").write_text(result.stdout, encoding="utf-8")
            (attempt_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8")
            last_returncode = result.returncode
            write_status(run_dir, state="attempt-finished", attempt=attempt, returncode=result.returncode)
            if result.returncode == 0:
                capture_diff(worktree, run_dir)
                finish_job(processing_job, success=True)
                write_status(run_dir, state="succeeded", finished_at=datetime.now(timezone.utc).isoformat(), returncode=0)
                notify(job_id, "succeeded", f"artifacts available at {run_dir}")
                print(f"status: succeeded (attempt {attempt})")
                print(f"artifacts: {run_dir}")
                return 0
        except subprocess.TimeoutExpired as error:
            last_returncode = 124
            (attempt_dir / "timeout.txt").write_text(str(error), encoding="utf-8")
            capture_diff(worktree, run_dir)
            write_status(run_dir, state="timeout", attempt=attempt)
        except OSError as error:
            (attempt_dir / "error.txt").write_text(str(error), encoding="utf-8")
            capture_diff(worktree, run_dir)
            finish_job(processing_job, success=False)
            write_status(run_dir, state="failed-to-start", finished_at=datetime.now(timezone.utc).isoformat(), error=str(error), returncode=127)
            notify(job_id, "failed-to-start", str(error))
            print(f"error: could not start Codex: {error}", file=sys.stderr)
            return 127

        if attempt <= retries:
            write_status(run_dir, state="retrying", next_attempt=attempt + 1)

    capture_diff(worktree, run_dir)
    finish_job(processing_job, success=False)
    write_status(run_dir, state="failed", finished_at=datetime.now(timezone.utc).isoformat(), returncode=last_returncode)
    notify(job_id, "failed", f"failed after {retries + 1} attempt(s)")
    print(f"status: failed after {retries + 1} attempt(s)")
    print(f"artifacts: {run_dir}")
    return last_returncode


def with_worker_lock():
    LOCK_PATH.touch(exist_ok=True)
    handle = LOCK_PATH.open("r+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("another worker is already running")
    handle.seek(0)
    handle.truncate()
    handle.write(f"pid={os.getpid()}\nstarted={datetime.now(timezone.utc).isoformat()}\n")
    handle.flush()
    return handle


def list_jobs() -> None:
    for label, directory in (("inbox", INBOX), ("processing", PROCESSING), ("done", DONE), ("failed", FAILED)):
        jobs = sorted(directory.glob("*.md"))
        print(f"{label}: {len(jobs)}")
        for job in jobs:
            print(f"  - {job.name}")


def run_once(args: argparse.Namespace) -> int:
    if args.pause_file.exists():
        print(f"paused: remove {args.pause_file} to resume")
        return 4
    job = find_job(args.job)
    if job is None:
        print("No job found. Add a Markdown file to jobs/inbox/.")
        return 1
    try:
        lock = with_worker_lock()
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    try:
        return run_job(job, execute=args.execute and not args.dry_run, timeout_seconds=args.timeout, retries=args.retries, approve=args.approve)
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one local Codex job from jobs/inbox.")
    parser.add_argument("job", nargs="?", help="Job Markdown path; defaults to the oldest inbox job")
    parser.add_argument("--execute", action="store_true", help="Actually invoke codex exec")
    parser.add_argument("--dry-run", action="store_true", help="Show the planned run without invoking Codex")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="Seconds allowed per attempt")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES, help="Additional attempts after failure")
    parser.add_argument("--list", action="store_true", help="List jobs without running one")
    parser.add_argument("--approve", action="store_true", help="Approve a job explicitly marked approval: required")
    parser.add_argument("--watch", action="store_true", help="Keep polling the inbox for new jobs")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS, help="Seconds between watch polls")
    parser.add_argument("--max-jobs", type=int, default=0, help="Stop watch mode after this many jobs; 0 means unlimited")
    parser.add_argument("--pause-file", type=Path, default=ROOT / ".pause", help="File that pauses execution when present")
    parser.add_argument("--remember", metavar="TEXT", help="Save a short local memory note and exit")
    parser.add_argument("--memory-kind", choices=("raw", "wiki", "outputs"), default="raw")
    parser.add_argument("--memory-title", default="note")
    args = parser.parse_args()
    ensure_dirs()
    if args.remember is not None:
        path = save_note(args.remember, kind=args.memory_kind, title=args.memory_title)
        print(f"saved memory: {path}")
        return
    if args.timeout <= 0 or args.retries < 0 or args.interval <= 0 or args.max_jobs < 0:
        parser.error("timeout/interval must be positive; retries/max-jobs cannot be negative")
    if args.list:
        list_jobs()
        return
    if not args.watch:
        raise SystemExit(run_once(args))

    completed = 0
    try:
        while args.max_jobs == 0 or completed < args.max_jobs:
            if args.pause_file.exists():
                print(f"paused: remove {args.pause_file} to resume")
                break
            if find_job(args.job) is not None:
                run_once(args)
                completed += 1
                if args.job:
                    args.job = None
            else:
                print(f"watching: no jobs; next check in {args.interval}s")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("watch stopped")
