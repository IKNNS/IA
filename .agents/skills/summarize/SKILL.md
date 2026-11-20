---
name: summarize
description: Summarize approved local text or Markdown files into a concise Markdown report without changing source files.
---

# Summarize local files

## When to use

Use when a job asks for a summary, brief, executive overview, or key points from files under `workspace/`.

## Boundaries

- Read only files named by the job or files under `workspace/`.
- Never read secrets, credentials, browser profiles, SSH keys, or unrelated home-directory files.
- Do not modify source files.
- Write only under `outputs/` or the current run directory.
- Do not send, publish, commit, push, or deploy anything.

## Procedure

1. Identify input files and report missing files before proceeding.
2. Read the smallest relevant set of files.
3. Extract the main claim, decisions, facts, risks, and open questions.
4. Write a Markdown report with a short title and clear sections.
5. Check that important claims are traceable to the input.
6. Report the output path and validation performed.

## Definition of done

- Source files are unchanged.
- The report exists at the requested path.
- Facts are distinguished from assumptions.
- The final response names files read and output written.
