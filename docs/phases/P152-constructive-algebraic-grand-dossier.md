# P152 — Grande campanha formal de descoberta construtiva e dossiê de literatura

**Status:** Proposed.
**Dependência:** P151 concluída; branch a partir de `codex/p151-blind-confirmation-holm-fwer`.
**Owner:** agente executor; revisor formal/matemático nos gates indicados.
**Pré-requisito:** P151 concluída com confirmação estatística cega aprovada sob Holm FWER.
**Branch:** `codex/p152-constructive-algebraic-grand-dossier`.

## Hipótese, objetivo e escopo

Consolidar a biblioteca formal unificada de identidades algébricas de alta ordem e certificados construtivos em combinatória finita no Lean 4 com zero tokens `sorry`. Gerar o grande dossiê de literatura matemática em `docs/research/p152-constructive-algebraic-dossier.md` detalhando com precisão: quais classes foram estendidas além do conhecimento publicado na literatura, os limites explícitos de aplicabilidade, a ausência de alegações universais espúrias, a cadeia criptográfica SHA-256 de custódia formal e os artefatos prontos para arquivamento e escrutínio por matemáticos externos.

Alterações permitidas: `lean_proofs/`, `docs/research/p152-constructive-algebraic-dossier.md`, `benchmarks/science_matrix.py`, `tests/`, `experiments/p152-config.json`, `experiments/p152-run.sh`.
Fora do escopo: alegações de solução universal definitiva sem demonstração completa no kernel.

Uma microtarefa por ciclo; implementar e validar sob gates herméticos.

## Trabalho ordenado

1. Integrar todos os módulos formais gerados em P145–P149 na compilação do Lake com 0 `sorry`.
2. Elaborar o dossiê formal exaustivo em `docs/research/p152-constructive-algebraic-dossier.md` com análise comparativa de literatura (Erdős, Sierpiński, Schinzel, Bloom).
3. Calcular a cadeia criptográfica de custódia (SHA-256 Hash Chain) para todos os módulos e certificados.
4. Adicionar interface de auditoria final P152 em `benchmarks/science_matrix.py` (`run_p152_grand_campaign_audit`).

## Gate de saída

Compilação completa no Lean 4 com 0 `sorry`, hash chain imutável e auditoria final P152 aceita:

```bash
git diff --check
git status --short
lake -d lean_proofs build
python3 -m pytest tests -q
python3 benchmarks/science_matrix.py --acceptance-phase P152 --config experiments/p152-config.json --output /tmp/evobyte-p152-acceptance.json
```

## Commit & Push (obrigatório)

```bash
git diff --cached --check
git commit -m "feat(formal): implement p152 constructive algebraic grand dossier"
git push -u origin HEAD
gh pr create --base codex/p151-blind-confirmation-holm-fwer --title "feat(formal): implement p152 constructive algebraic grand dossier" --body-file /tmp/evobyte-p152-pr.md
```
