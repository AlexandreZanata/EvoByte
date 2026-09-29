# Commit convention

This project uses [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).

## Format

```text
type(scope): short description

optional body explaining context and motivation

optional footer
```

`!` marks a breaking change and requires `BREAKING CHANGE:` in the footer.

## Allowed types

- `feat`: new user/research-visible capability.
- `fix`: correction of defective behavior.
- `docs`: documentation only.
- `refactor`: internal change, no intended behavior shift.
- `perf`: performance improvement (with measurement).
- `test`: test creation/correction.
- `build`: build, packaging, modules.
- `ci`: workflows and automation.
- `chore`: maintenance not fitting above.
- `revert`: explicit revert of an earlier commit.

## Recommended scopes

- `bytecode`, `vm`, `verifier`, `evolution`, `archive`, `islands`,
  `constants`, `generator`, `bench`, `metrics`, `dashboard`;
- `phases`, `docs`, `project`, `deps`, `security`, `infra`, `web`.

A new scope must name a durable area. Omit scope only when the change is
indivisibly cross-cutting.

## Rules

- Imperative, lowercase, no trailing period; first line <= 72 chars.
- One logical reversible change per commit; no broad refactor + behavior mix.
- Explain *why* in the body when the diff is not enough.
- Reference issues in the footer (`Closes #123`).
- Never put secrets, personal, or sensitive data in messages.
- Generated code ships with its source.

Messages are in **English**; `type` and `scope` stay standardized.

## Examples

```text
feat(vm): add deterministic CPU reference interpreter
fix(verifier): clamp exp domain to stop overflow
docs(phases): add P02 CPU reference interpreter plan
test(bytecode): cover invalid opcode rejection
ci(quick): add ruff and pytest smoke
```

Breaking change:

```text
feat(bytecode)!: widen instruction to 8 bytes

BREAKING CHANGE: OPCODE_VERSION 0 archives need migration note.
```

## Branches and pull requests

Branches: `<category>/NN-short-slug`, e.g. `phase-02-cpu-interpreter`,
`docs/roadmap-clarify`, `fix/verifier-clamp`.

PR titles follow the same commit pattern. With squash merge, the PR title
becomes the final message.

## Versioning (when releases begin)

- `fix` -> patch; `feat` -> minor; `BREAKING CHANGE` -> major.
- `docs`, `test`, `ci`, `build`, `refactor`, `perf`, `chore` do not version
  alone unless a future policy says so.

## Local config

The repo ships `.gitmessage`. Enable it with:

```bash
git config commit.template .gitmessage
```
