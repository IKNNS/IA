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

Status: Done (adapters)

- [x] Add file-based local memory writer
- [x] Add optional speech-to-text adapter
- [x] Add optional text-to-speech adapter boundary
- [x] Keep voice dependencies optional and local

## Phase 6 — Evaluation and hardening

Status: Done (baseline)

- [x] Add quota-free project structure checks
- [x] Add inbox secret-pattern checks
- [x] Keep worker tests separate from Codex execution
- [ ] Add a larger fixture suite after real local usage
