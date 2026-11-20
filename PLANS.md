# Project plan

## Phase 1 — Local worker safety

Status: Done

- local `codex exec` runner
- dry-run mode
- single-worker lock
- timeout and retry
- per-run status and logs
- Git repository preflight

## Phase 2 — Context and reusable workflows

Status: Done

- [x] Define goals and non-goals
- [x] Define phase roadmap
- [x] Add reusable prompt entry points
- [x] Add first repository skill
- [x] Add validation checklist

## Phase 3 — Isolation and review

Status: Done

- [x] Run implementation jobs in separate Git worktrees
- [x] Produce a diff summary before merge
- [x] Add explicit approval state before external writes
- [x] Preserve run evidence for recovery after interruption

## Phase 4 — Scheduling and notifications

Status: Done

- [x] Add local watch mode
- [x] Notify only on completion, failure, or approval needed
- [x] Add manual pause behavior for quota or maintenance
- [x] Add launchd template without installing it automatically

## Phase 5 — Voice and memory

Status: Not started

- add local speech-to-text
- add optional text-to-speech
- connect curated notes to `workspace/` or an Obsidian vault
