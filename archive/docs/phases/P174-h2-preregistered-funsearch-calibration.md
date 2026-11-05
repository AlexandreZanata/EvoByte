# P174 — Calibração pré-registrada da hipótese H2 (bytecode vs FunSearch em cap sets)

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P173 concluída (motor de prioridade + ISA v1); branch a partir de `codex/p173-constructive-bytecode-priority-engine`.
**Owner:** agente executor; revisor estatístico nos gates de veredito.
**Branch:** `codex/p174-h2-preregistered-funsearch-calibration`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P173-constructive-bytecode-priority-engine.md`](P173-constructive-bytecode-priority-engine.md), catálogo v2 da P171 (`docs/research/targets/frontier_targets_v2.json`).

## Por que esta fase existe

A hipótese H2 afirma que **evolução em bytecode (sem LLM)** descobre programas construtores
no nível do FunSearch (DeepMind, *Nature* 2024) com frações do custo computacional. Antes de
atacar qualquer recorde, H2 precisa de calibração honesta e pré-registrada: evoluir prioridades
em bytecode para **reproduzir** o cap set de tamanho 512 em F₃⁸ — que é alvo de *calibração*
(`cap_set_8`, P171), não de recorde — e comparar o custo em avaliações de candidatos contra
Random Search, Simulated Annealing e o gasto publicado do FunSearch.

## Pergunta falsificável da fase

> Evolução de programas de prioridade em bytecode atinge um cap set de tamanho 512 em F₃⁸
> (o valor publicado) usando estritamente menos avaliações de candidatos que o número
> publicado pelo FunSearch, enquanto Random Search e SA, sob o mesmo orçamento, não atingem?

## Fatos de partida (todos re-verificados pelo executor; nada é copiado de memória)

| Fato | Fonte / como re-verificar |
|---|---|
| O alvo de reprodução é `cap_set_8` = 512, do paper do FunSearch (doi `10.1038/s41586-023-06924-6`) | P171 Passo 2 (snapshot do paper + repo público). O conjunto de 512 pontos **deve** vir do snapshot da P171 (`docs/research/targets/` + `frontier_sources_v2.json`); **nunca** digitado |
| Orçamento do FunSearch (avaliações/TPU-horas) | Extrair do paper/repo na execução; se indisponível, registrar `funsearch_budget: "not_obtained"` e a perna de eficiência do veredito vira `INCONCLUSIVE` (não chute) |
| Verificador `verify_cap_set` decide cap sets em F₃ⁿ | P171 (`frontier_catalogue.py`); calibre-o contra `{0,1}³` (válido) e `{(0,0),(1,1),(2,2)}` em F₃² (inválido) antes de qualquer campanha |
| Construtor guloso + `evaluate_priority` existem e são determinísticos | P173 (`src/evobyte/constructive.py`) |
| P171 declara `cap_set_8` como calibração, não recorde | `frontier_targets_v2.json` (`role = calibration`, `proven_optimal = false` para o 512? **não**: verificar no catálogo; reproduzir ≠ provar ótimo) |

> [!IMPORTANT]
> **Regra anti-alucinação.** Nenhum número do paper do FunSearch entra no manifesto sem URL+SHA
> ou citação verificável. O executor que não encontrar o orçamento publica `INCONCLUSIVE` na
> perna de eficiência — e isso é resultado válido, não falha.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/priority_evolution.py` (loop evolutivo de programas de prioridade: mutação/crossover em bytecode v1, fitness = tamanho do cap construído)
- `benchmarks/h2_capset_evolution.py` (campanha pré-registrada: BytecodeEvolution vs Random vs SA em F₃⁸)
- `experiments/p174-h2-manifest.json` (pré-registro: alvo, orçamento, sementes, regra de veredito, orçamento FunSearch pinado ou `not_obtained`)
- `experiments/p174-h2-results.json` (resultado medido)
- `tests/test_h2_calibration.py` (só componentes e micro-construções; suíte < 3 s)
- `docs/research/p174-h2-calibration-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P174-h2-preregistered-funsearch-calibration.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- digitar o conjunto de 512 pontos em qualquer arquivo (ele só entra via snapshot da P171);
- rodar evolução, buscas ou avaliações em F₃⁸ dentro de `tests/` (tudo > 0,2 s é proibido; campanhas ficam no script de `benchmarks/`);
- LLM em qualquer ponto do loop de busca;
- declarar eficiência sem o número pinado do FunSearch.

## Trabalho ordenado

### Passo 1 — Branch e pré-condições mecânicas

```bash
git status --short
git switch codex/p173-constructive-bytecode-priority-engine
git switch -c codex/p174-h2-preregistered-funsearch-calibration
test -f docs/research/targets/frontier_targets_v2.json || { echo "P171 NAO CONCLUIDA"; exit 1; }
python3 -c "from evobyte import constructive; print('p173 ok')"
```

### Passo 2 — `src/evobyte/priority_evolution.py`

Loop evolutivo honesto sobre programas de prioridade (bytecode v1, 64 bytes):

```python
"""Evolution of bytecode priority programs for constructive search (P174)."""

def evolve_priorities(objective_fn, budget_evals, pop_size, seed, ...):
    """População de programas v1; fitness = objective_fn(programa).
    `objective_fn` constrói o objeto via greedy_construct + evaluate_priority e
    retorna (score, is_valid). Conta TODAS as avaliações (construções). Sem LLM,
    sem rede, sem cache entre sementes. Retorna (melhor_programa, melhor_score, n_evals, elapsed_sec)."""
```

Regras: mutação pontual em bytes + crossover de ponto único (operadores sobre o vetor
`uint32`, respeitando `is_valid` da v1); população inicial aleatória (nada hardcoded);
toda avaliação conta; `elapsed_sec` por `time.perf_counter()`.

### Passo 3 — Manifesto `experiments/p174-h2-manifest.json` (congelar ANTES de rodar)

```json
{
  "phase": "P174",
  "target_id": "cap_set_8",
  "reproduction_size": 512,
  "reproduction_source": "P171 snapshot (source_id + sha256 aqui)",
  "algorithms": ["BytecodeEvolution", "RandomSearch", "SimulatedAnnealing"],
  "budget_sec_per_seed": 60.0,
  "max_evaluations_per_seed": 200000,
  "seeds": [42, 101, 202],
  "funsearch_evaluations": 123456789,
  "funsearch_source": "paper/repo, seção X",
  "verdict_rule": {
    "H2_SUPPORTED": "bytecode atinge >= 512 E usa < funsearch_evaluations, com Random/SA abaixo de 512 no mesmo orçamento",
    "H2_REPRODUCED": "atinge 512 sem vantagem de eficiência demonstrável",
    "H2_NOT_SUPPORTED": "não atinge 512 no orçamento",
    "H2_INCONCLUSIVE": "funsearch_evaluations == 'not_obtained' (eficiência não julgável)"
  }
}
```

O executor preenche `funsearch_evaluations` com o número pinado **ou** a string
`"not_obtained"` — nunca um chute. O valor `123456789` acima é placeholder detectável:
se ele aparecer num manifesto commitado, a fase falhou (exemplo copiado sem pesquisa).
Commit do manifesto **antes** da campanha
(`git commit` separado ou mesma PR com timestamp anterior à execução registrado no JSON).

### Passo 4 — `benchmarks/h2_capset_evolution.py` e execução

Script com `--manifest experiments/p174-h2-manifest.json --output experiments/p174-h2-results.json`:
para cada `(algoritmo, semente)`, roda sob o orçamento duplo (tempo OU avaliações, o que
estourar primeiro) e certifica qualquer candidato ≥ 512 com o verificador P171. Gera o JSON
com trials brutos + hashes. Tempo esperado: minutos por configuração (é campanha, não teste).

### Passo 5 — Testes `tests/test_h2_calibration.py` (todos < 0,2 s; suíte < 3 s)

1. `test_capset_verifier_calibration`: `{0,1}³` válido; `{(0,0),(1,1),(2,2)}` inválido;
   ponto duplicado e coordenada `3` rejeitados (via P171, sem reimplementar).
2. `test_greedy_builds_cube_from_static_priority`: construtor P173 + prioridade estática
   monta exatamente `{0,1}³` em < 0,1 s (reprodutível, determinístico).
3. `test_evolution_loop_counts_evaluations`: `evolve_priorities` num objetivo brinquedo
   (ex: maximizar soma de 8 bits) retorna `evaluations` igual ao número real de chamadas
   ao objetivo; mesma semente, mesma trajetória (determinístico até o orçamento).
4. `test_manifest_schema`: o manifesto tem todos os campos da regra de veredito;
   `funsearch_evaluations` é inteiro positivo ou a string exata `"not_obtained"`.
5. `test_manifest_has_no_example_placeholder`: o valor `123456789` do exemplo desta
   especificação **nunca** aparece num manifesto commitado (tripwire anti-cópia:
   quem commitou o exemplo não executou a pesquisa).
6. `test_no_llm_no_network_in_loop`: AST dos módulos do loop não importa `openai`,
   `anthropic`, `transformers`, `torch.hub`, `urllib`, `requests` nem `socket`.

### Passo 6 — Relatório `docs/research/p174-h2-calibration-report.md`

Orçamento FunSearch pinado (ou `not_obtained` com evidência da tentativa), tamanhos máximos
por método/semente, avaliações gastas, veredito literal da regra (`H2_SUPPORTED` /
`H2_REPRODUCED` / `H2_NOT_SUPPORTED` / `H2_INCONCLUSIVE`) e limitações.

## Regras de parada (PARE, não commite, reporte)

- O conjunto de 512 pontos não for localizável no snapshot da P171.
- O verificador rejeitar o objeto publicado do snapshot.
- Orçamento do FunSearch indisponível → publique `INCONCLUSIVE` na perna de eficiência
  (não invente número).
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer busca dentro de `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_h2_calibration.py -q -m "not slow"   # FAST LOOP, ~1s
python3 benchmarks/h2_capset_evolution.py --manifest experiments/p174-h2-manifest.json --output experiments/p174-h2-results.json
python3 -m pytest tests/test_h2_calibration.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/priority_evolution.py benchmarks/h2_capset_evolution.py \
  experiments/p174-h2-manifest.json experiments/p174-h2-results.json \
  tests/test_h2_calibration.py docs/research/p174-h2-calibration-report.md \
  docs/phases/P174-h2-preregistered-funsearch-calibration.md
git diff --cached --check
git commit -m "feat(research): implement p174 h2 preregistered funsearch calibration"
git push -u origin HEAD
gh pr create --base codex/p173-constructive-bytecode-priority-engine \
  --title "feat(research): p174 h2 preregistered calibration" \
  --body-file /tmp/evobyte-p174-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p174-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (tamanhos máximos, avaliações, veredito literal), limitações
(orçamento FunSearch pinado ou `not_obtained`) e o link do relatório.
