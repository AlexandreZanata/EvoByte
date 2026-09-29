# Security policy

## Supported versions

Only the latest `main` is supported with security updates during the
research pre-release period (v0.x).

## Reporting a vulnerability

Email the maintainer listed on GitHub (`AlexandreZanata/EvoByte`) with:

- affected commit SHA and file paths;
- reproduction steps (no private data);
- impact assessment.

Do **not** open a public issue for vulnerabilities. Expect an initial
response within 7 days.

## Rules

- Never commit secrets, tokens, private keys, or personal data.
- Secret scanning should run in CI; large experiment artifacts
  (`runs/`, `checkpoints/`) are git-ignored and never reviewed for secrets.
- GPU kernels and dataset loaders must bounds-check indices and clamp
  floating-point domains (no NaN/Inf propagation by design — see
  `docs/VERIFIER.md`).
