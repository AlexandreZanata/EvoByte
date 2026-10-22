# P183 — Busca de anomalias em redes frustradas e estados fundamentais (Q10–Q13)

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** nenhuma fase anterior exigida (reativação de trilha legada); branch a partir de `main`.
**Owner:** agente executor; revisor de física (conservação de invariantes) nos gates de veredito.
**Branch:** `codex/p183-hamiltonian-ground-state-anomaly-search`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), `src/evobyte/quantum/{hamiltonians,ground,evolution_q,observables}.py` (ler as APIs reais antes de codar).

## Por que esta fase existe

O repositório já contém um pipeline quântico de muitos corpos (Q10–Q13): Hamiltonianos,
estados fundamentais, observáveis e evolução com conservação. Esta fase o reativa sob as
regras do programa — **busca estrita, sem seeds manuais** — para procurar estados
fundamentais anômalos e invariantes conservados em redes frustradas (J1-J2 e afins): ou um
invariante genuíno e verificável é encontrado, ou registra-se `NULL_RESULT` com a mesma
integridade das demais trilhas.

## Pergunta falsificável da fase

> Sob orçamento pré-registrado e sem seeds manuais, a busca encontra estado fundamental ou
> invariante conservado em rede frustrada que (a) reproduz invariantes conhecidos em instâncias
> de calibração e (b) revela estrutura não catalogada verificável por diagonalização exata
> independente em instância pequena?

## Fatos de partida (código real do repo; ler antes de estender)

| Fato | Fonte |
|---|---|
| `hamiltonians.py`, `ground.py`, `observables.py`, `evolution_q.py`, `hamdisc.py`, `fame.py` implementam o pipeline Q10–Q13 | `src/evobyte/quantum/` (ler as assinaturas reais; não presumir APIs) |
| Calibração honesta usa instâncias exatamente solúveis (diagonalização completa) como gabarito | Princípio desta fase (ver Passo 3) |
| Seeds manuais de soluções são proibidas (mesma regra da P182) | AGENTS.md + P182 |

## Escopo

**Arquivos que você pode criar:**
- `benchmarks/run_hamiltonian_anomaly_search.py` (protocolo com orçamento, checkpoint e gabaritos)
- `experiments/p183-hamiltonian-manifest.json` (pré-registro: redes, tamanhos, orçamentos, sementes, regra de veredito)
- `experiments/p183-hamiltonian-results.json` (resultado medido + hashes)
- `tests/test_hamiltonian_anomaly.py` (só lógica e micro-instâncias exatas; suíte < 3 s)
- `docs/research/p183-hamiltonian-anomaly-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P183-hamiltonian-ground-state-anomaly-search.md`: só a linha de Status e o bloco final de execução.
- `src/evobyte/quantum/*` existente: **apenas** correções mínimas de compatibilidade documentadas (sem mudar física implementada; qualquer mudança de comportamento é STOP + reporte).

**Proibido:**
- seeds manuais de estados/soluções em qualquer ponto;
- buscas, evoluções ou diagonalizações grandes dentro de `tests/`;
- afirmar "novo invariante" sem verificação independente em instância exatamente solúvel.

## Trabalho ordenado

### Passo 1 — Branch e leitura obrigatória

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p183-hamiltonian-ground-state-anomaly-search
grep -n "^def \|^class " src/evobyte/quantum/hamiltonians.py src/evobyte/quantum/ground.py src/evobyte/quantum/observables.py | head -40
```

Se as APIs reais divergirem do que esta especificação pressupõe, **adapte a especificação à
realidade do código** (documentando o desvio no PR) — nunca o contrário.

### Passo 2 — Manifesto `experiments/p183-hamiltonian-manifest.json` (congelar ANTES de rodar)

```json
{
  "phase": "P183",
  "calibration": "instâncias exatamente solúveis (diagonalização completa) com invariantes conhecidos",
  "lattices": ["<rede_frustrada_1>", "<rede_frustrada_2>"],
  "sizes": ["pequeno-exato", "alvo"],
  "budget_sec_per_seed": 120.0,
  "seeds": [42, 101, 202],
  "verdict_rule": {
    "ANOMALY_CONFIRMED": "invariante/estado reproduz gabarito exato E revela estrutura verificável não catalogada",
    "NULL_RESULT": "nada além do conhecido dentro do orçamento"
  }
}
```

Redes e tamanhos concretos saem da leitura do código + literatura (registrar fonte de cada
escolha no relatório; sem fonte = sem alvo).

### Passo 3 — `benchmarks/run_hamiltonian_anomaly_search.py`

Fase 1 = calibração (gabaritos exatos; o pipeline precisa reproduzir invariantes conhecidos
a partir de inicialização aleatória). Fase 2 = busca nos alvos (orçamento duplo tempo/avaliações,
checkpoint incremental). Todo invariante alegado é rechecado por diagonalização exata
independente em instância pequena antes de qualquer registro.

### Passo 4 — Testes `tests/test_hamiltonian_anomaly.py` (todos < 0,2 s; suíte < 3 s)

1. `test_calibration_reproduces_exact_invariant`: micro-instância exatamente solúvel
   (diagonalização direta no teste, tamanho mínimo) reproduz o invariante conhecido.
2. `test_no_manual_seeds_in_protocol`: manifesto e script rejeitam inicialização com
   estados publicados (checagem estática de ausência de vetores literais no caminho de init).
3. `test_conserved_quantity_verified_independently`: invariante alegado em fixture passa na
   verificação independente do teste (não na do próprio pipeline).
4. `test_null_when_nothing_found`: sem anomalia, o veredito é `NULL_RESULT` (fixture), nunca vazio/ambíguo.

### Passo 5 — Relatório `docs/research/p183-hamiltonian-anomaly-report.md`

Calibração (atingida ou não, com números), vereditos por rede/tamanho, integridade (hash do
manifesto, seeds, orçamentos), limitações (tamanhos alcançáveis, o que `NULL_RESULT` prova e
não prova) e a frase literal aplicável.

## Regras de parada (PARE, não commite, reporte)

- Calibração não reproduz invariante conhecido (pipeline quebrado ou gabarito errado).
- Qualquer invariante alegado falhar na verificação independente.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer busca/diagonalização grande em `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_hamiltonian_anomaly.py -q -m "not slow"   # FAST LOOP, ~1s
python3 benchmarks/run_hamiltonian_anomaly_search.py --manifest experiments/p183-hamiltonian-manifest.json --output experiments/p183-hamiltonian-results.json --checkpoint experiments/p183-hamiltonian-checkpoint.json
python3 -m pytest tests/test_hamiltonian_anomaly.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add benchmarks/run_hamiltonian_anomaly_search.py experiments/p183-hamiltonian-manifest.json \
  experiments/p183-hamiltonian-results.json experiments/p183-hamiltonian-checkpoint.json \
  tests/test_hamiltonian_anomaly.py docs/research/p183-hamiltonian-anomaly-report.md \
  docs/phases/P183-hamiltonian-ground-state-anomaly-search.md
git diff --cached --check
git commit -m "feat(quantum): implement p183 hamiltonian ground-state anomaly search"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(quantum): p183 hamiltonian anomaly search" \
  --body-file /tmp/evobyte-p183-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p183-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (calibração sim/não, vereditos), limitações e o link do relatório.
