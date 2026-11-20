# Evaluation checks

These checks are deliberately local and cheap. They do not call Codex or consume quota.

Run them with:

```bash
python3 scripts/check_project.py
```

The checks verify that:

- required project context files exist;
- the worker has a dry-run path;
- approval markers are recognized;
- jobs cannot accidentally include obvious secret file names;
- tests are present and pass separately.
