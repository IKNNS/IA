# Reusable prompts

## Orient the repository

```text
Read AGENTS.md, GOALS.md, and PLANS.md. Inspect the repository read-only.
Report the current phase, relevant files, available tests, and missing information.
Do not modify files.
```

## Plan one change

```text
Read AGENTS.md, GOALS.md, PLANS.md, and the relevant skill under .agents/skills/.
Prepare a small implementation plan with scope, non-goals, risks, files, and acceptance criteria.
Do not modify files until the plan is approved.
```

## Execute one approved change

```text
Read AGENTS.md, GOALS.md, PLANS.md, and the approved task description.
Implement only the approved scope. Run relevant tests, inspect the diff, and report evidence.
Do not commit, push, deploy, or perform external writes. Stop when this phase is complete.
```

## Verify a job

```text
Review the latest run under runs/. Check status.json, stdout/stderr, changed files, and outputs.
Report what passed, failed, and still needs human review. Do not rerun or modify source files.
```

## Review a diff

```text
Review the current Git diff against GOALS.md and AGENTS.md.
Look for scope creep, unsafe external actions, missing tests, secret exposure, and misplaced outputs.
Return findings by severity and do not modify files.
```
