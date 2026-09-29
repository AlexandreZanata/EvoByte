# Contributing to EvoByte

Thank you for contributing. EvoByte is 100% open source (MIT) and
research-first: every claim must be reproducible.

## Before you start

1. Read [docs/VISION.md](docs/VISION.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
2. Pick one phase in [docs/phases/](docs/phases/README.md) — do not mix phases.
3. Check [docs/DECISIONS.md](docs/DECISIONS.md) for prior rulings.

## Pull requests

- Small, reviewable scope; one phase per branch (`phase-NN-slug`), one
  commit per task.
- Update/add tests when there is code; update affected docs in the same set.
- State security, determinism, and rollback risks.
- Never include real credentials, private data, or large artifacts
  (`runs/`, `checkpoints/`, datasets stay git-ignored).
- Confirm generated content was reviewed by a responsible human.

## Commits

Follow [docs/COMMITS.md](docs/COMMITS.md): `type(scope): description`
(Conventional Commits). Example:

```text
docs(phases): add P02 CPU reference interpreter plan
```

Enable the local template:

```bash
git config commit.template .gitmessage
```

## Every phase ends with commit + push

Each phase file contains a **Commit & Push** block. The pattern is always:

```bash
git status --short
git add <only-files-of-this-phase>
git commit -m "type(scope): description"
git push -u origin phase-NN-slug
gh pr create --title "type(scope): description" --body "Closes #<issue> ..."
```

Never push directly to `main`. Never force-push.

## Security

For vulnerabilities, follow [SECURITY.md](SECURITY.md). Do not open a
public issue.
