# P186 — Auditoria dupla de novidade contra literatura mundial (pré-anúncio)

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P176/P177/P182 (vereditos) e P185 (certificados, se houver) concluídas; branch a partir de `main`.
**Owner:** agente executor + revisor humano obrigatório (nenhum anúncio sem as duas assinaturas).
**Branch:** `codex/p186-world-literature-novelty-dual-audit`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), catálogo P171 + fontes P180 + vereditos P176/P177/P182.

## Por que esta fase existe

Antes de qualquer anúncio de novidade, cada `DISCOVERY_BEATEN` precisa sobreviver a uma
auditoria dupla e independente contra a literatura mundial (arXiv, OEIS, tabelas de Gordon e
Grassl): (1) o objeto é realmente estrito em relação à melhor cota **publicada** congelada?
(2) a cota congelada continua sendo a melhor no momento da auditoria (rechecagem com data)?
Se a resposta a (1) for não, o veredito é rebaixado para `DISCOVERY_TIED`/nulo com registro
público do erro. Sem essa fase, "recorde" é só auto-declaração.

## Pergunta falsificável da fase

> Para cada `DISCOVERY_BEATEN` registrado, existe evidência datada e snapshotada de que
> (a) o objeto certificado supera a cota publicada congelada e (b) nenhuma publicação
> posterior (até a data da auditoria) já a superava?

## Fatos de partida

| Fato | Fonte |
|---|---|
| Vereditos com certificados e hashes | `experiments/p176-covering-results.json`, `p177-...`, `p182-...` |
| Cotas congeladas e fontes | P171 (`frontier_targets_v2.json` + `frontier_sources_v2.json`), P180 (`qecc_*`) |
| Padrão de auditoria dual | P150/P186-conceito (duplo verificador independente do programa P161–P170) |
| Se nenhum `DISCOVERY_BEATEN` existir: a auditoria cobre os certificados de **empate** e os **quase-recordes** (melhores candidatos), para garantir que nenhum recorde foi perdido por erro de comparação | Regra desta fase |

## Escopo

**Arquivos que você pode criar:**
- `scripts/novelty_dual_audit.py` (checklist mecânica: objeto vs cota congelada vs rechecagem datada)
- `experiments/p186-novelty-audit.json` (resultado por alegação: CONFIRMED / DOWNGRADED / NOT_APPLICABLE)
- `tests/test_novelty_dual_audit.py` (só lógica e fixtures; suíte < 3 s)
- `docs/research/p186-novelty-audit-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P186-world-literature-novelty-dual-audit.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- declarar novidade sem as duas assinaturas (mecânica + humana) registradas;
- acessar rede dentro de `tests/`; testes usam snapshots/fixuras locais;
- rebaixar veredito sem registrar o motivo e a evidência (transparência total).

## Trabalho ordenado

### Passo 1 — Branch e inventário de alegações

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p186-world-literature-novelty-dual-audit
python3 - <<'PY'
import json, glob
for p in ["experiments/p176-covering-results.json", "experiments/p177-weak-schur-results.json", "experiments/p182-qecc-results.json"]:
    try:
        d = json.load(open(p))
        beats = [(t.get("target_id"), t.get("candidate_sha256", "")[:16]) for t in d.get("trials", []) if t.get("oracle_certified")]
        print(p, "certificados:", len(beats))
    except FileNotFoundError:
        print(p, "AUSENTE")
PY
```

### Passo 2 — `scripts/novelty_dual_audit.py`

Para cada certificado `DISCOVERY_BEATEN` (ou de empate/quase, conforme o caso):

1. **Auditoria A (contra o congelado):** o objeto satisfaz `propriedade > best_known_value` do
   catálogo? (re-executa o verificador independente sobre o objeto.)
2. **Auditoria B (rechecagem datada):** re-consulta as fontes (arXiv/OEIS/tabelas/curadores)
   **na data de hoje**, com snapshot novo em `data/raw/novelty/`; alguma publicação posterior
   ao snapshot congelado já supera ou iguala o objeto?
3. Veredito por alegação: `CONFIRMED` (passa A e B), `DOWNGRADED` (falha A ou B, com motivo +
   evidência), `NOT_APPLICABLE` (sem alegação a auditar — ex: só nulos e empates já publicados).

Tudo offline exceto as re-consultas da Auditoria B, cujos snapshots vão para `data/raw/novelty/`
(ignorado pelo git) com URL+data+SHA registrados no JSON de saída.

### Passo 3 — Testes `tests/test_novelty_dual_audit.py` (todos < 0,2 s; suíte < 3 s)

1. `test_audit_confirms_clear_record`: certificado de Fano-com-6-blocos? Não — fixture:
   objeto que supera cota fictícia congelada em snapshot local → `CONFIRMED`.
2. `test_audit_downgrades_stale_claim`: snapshot "novo" com cota maior que o objeto → `DOWNGRADED` com motivo.
3. `test_null_when_no_beaten`: sem `DISCOVERY_BEATEN` nas entradas → todas `NOT_APPLICABLE`, nenhuma `CONFIRMED` inventada.
4. `test_every_claim_has_dated_evidence`: toda entrada `CONFIRMED`/`DOWNGRADED` referencia snapshot com URL+data+SHA (ou `not_obtained` com motivo).

### Passo 4 — Relatório `docs/research/p186-novelty-audit-report.md`

Tabela por alegação (objeto, cota congelada, rechecagem datada, veredito, evidência), fontes
reconsultadas com SHAs, e a frase literal aplicável: ou "NENHUMA ALEGAÇÃO DE NOVIDADE
SOBREVIVEU/DOWNGRADED..." ou a lista de `CONFIRMED` com dupla assinatura.

## Regras de parada (PARE, não commite, reporte)

- Qualquer `CONFIRMED` sem as duas evidências (A e B) snapshotadas.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer acesso à rede em `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_novelty_dual_audit.py -q -m "not slow"   # FAST LOOP, ~1s
python3 scripts/novelty_dual_audit.py --inputs <resumos> --out experiments/p186-novelty-audit.json --snapshots data/raw/novelty/
python3 -m pytest tests/test_novelty_dual_audit.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add scripts/novelty_dual_audit.py tests/test_novelty_dual_audit.py \
  experiments/p186-novelty-audit.json docs/research/p186-novelty-audit-report.md \
  docs/phases/P186-world-literature-novelty-dual-audit.md
git diff --cached --check
git commit -m "feat(research): implement p186 world literature novelty dual audit"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(research): p186 novelty audit" \
  --body-file /tmp/evobyte-p186-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p186-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (alegações auditadas e vereditos), limitações (o que não foi
reconsultável) e o link do relatório. Snapshots brutos ficam em `data/raw/novelty/` (ignorado).

## Registro de Execução

- **Script de Auditoria:** `scripts/novelty_dual_audit.py` (auditoria mecânica de validade e cotas congeladas + reconsultas datadas).
- **Resultados da Auditoria:** [`experiments/p186-novelty-audit.json`](../../experiments/p186-novelty-audit.json).
  - 50 metas auditadas (P176, P177, P182): 0 CONFIRMED, 0 DOWNGRADED, 50 NOT_APPLICABLE.
  - Veredito Geral: `NO_ACTIVE_DISCOVERY_CLAIMS`.
  - Assinaturas duplas: `machine_verifier: EvoByte-FrontierVerifier-v2`, `human_reviewer: human:Alexandre`.
- **Suíte de Testes:** [`tests/test_novelty_dual_audit.py`](../../tests/test_novelty_dual_audit.py) (7/7 testes aprovados em 0,24 s; zero acesso à rede).
- **Relatório de Pesquisa:** [`docs/research/p186-novelty-audit-report.md`](../research/p186-novelty-audit-report.md).
