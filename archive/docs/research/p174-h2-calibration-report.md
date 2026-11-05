# P174 — Relatório de calibração pré-registrada da hipótese H2

**Data:** 2026-10-23
**Fase:** P174 — Descoberta na Fronteira (D042)
**Alvo:** `cap_set_8` (F₃⁸, reprodução do 512-cap do FunSearch; papel de calibração, não recorde)

---

## 1. Veredito literal

**H2_NOT_SUPPORTED**

Nenhum método atingiu 512 no orçamento duplo (60 s / 200 000 evals por semente).
Perna de eficiência: **INCONCLUSIVE** (`funsearch_evaluations = "not_obtained"` — sem número pinado, nenhuma alegação de eficiência é feita).

## 2. Orçamento FunSearch: não obtido (com evidência da tentativa)

- Snapshot P171 pinado: `funsearch-nature-2024`, URL `https://raw.githubusercontent.com/google-deepmind/funsearch/main/cap_set/n8_size512.txt`, SHA `8d6df45c3039b6a7ee1aae7216b100c3f4c075179dc6471f4f51b968a26d8905`. O artefato contém **apenas os 512 pontos** (verificado via fetch em 2026-10-23), nenhum contador de avaliações.
- Busca web por contagem de avaliações comparável: tentativa em 2026-10-23 via provedor Exa retornou erro de cota (`rate limit`); paper (doi `10.1038/s41586-023-06924-6`) não expõe número único de "avaliações de candidatos" comparável ao nosso contador em artefato acessível.
- Conforme a regra anti-alucinação da especificação, nenhum número foi inventado: manifesto registra `"not_obtained"` com a tentativa documentada.

## 3. Método (pré-registrado antes da campanha)

- Manifesto: `experiments/p174-h2-manifest.json` (`created_at` 2026-10-23T23:02:58+00:00) anterior a `started_at` 2026-10-23T23:04:48+00:00 nos resultados.
- Universo: todos os 6561 pontos de F₃⁸ gerados por produto cartesiano (o conjunto de 512 pontos **nunca** foi digitado; só o snapshot P171 foi lido para origem e verificação).
- Construtor: greedy de passada única em ordem de prioridade com conjunto proibido incremental (equivalente ao `greedy_construct` com contexto estático; O(N) avaliações de prioridade por construção em vez de O(N²)).
- Fitness: tamanho do cap construído; certificação final de sanidade via `verify_cap_set` da P171 (portão do cubo `{0,1}³` válido executado no script).
- Três algoritmos sob o mesmo orçamento duplo por (algoritmo, semente), sementes 42/101/202:
  - **BytecodeEvolution:** `evolve_priorities` sobre programas v1 (`evaluate_priority` com `feat` = coordenadas, `ctx` = estático); 1 eval = 1 programa (1 construção).
  - **RandomSearch:** prioridades `rng.random(N)`; 1 eval = 1 construção.
  - **SimulatedAnnealing:** têmpera sobre vetor de prioridades (vizinho = perturbar 32 posições); 1 eval = 1 construção.

## 4. Números medidos

| Algoritmo | Semente | Tamanho máximo | Avaliações | Tempo (s) |
|---|---|---|---|---|
| BytecodeEvolution | 42 | 256 | 185 | 60,4 |
| BytecodeEvolution | 101 | 256 | 237 | 60,2 |
| BytecodeEvolution | 202 | 288 | 237 | 60,1 |
| RandomSearch | 42 | 275 | 1950 | 60,0 |
| RandomSearch | 101 | 273 | 1943 | 60,0 |
| RandomSearch | 202 | 275 | 1948 | 60,0 |
| SimulatedAnnealing | 42 | 276 | 1931 | 60,0 |
| SimulatedAnnealing | 101 | 278 | 1866 | 60,0 |
| SimulatedAnnealing | 202 | 276 | 1845 | 60,0 |

Máximos: bytecode **288**, random **275**, SA **278**. Alvo 512 **não atingido** por nenhum método/semente. O orçamento de tempo ligou antes do de avaliações em todos os trials (tempo ≈ 60 s; evals 185–1950 ≪ 200 000).

## 5. Testes e gates

- `tests/test_h2_calibration.py`: 6 testes (portões do verificador, cubo `< 0,1 s`, contagem de avaliações e determinismo do loop, esquema do manifesto, tripwire anti-placeholder, AST sem LLM/rede). Suíte `< 3 s`.
- `make verify` (lint + 1020+6 testes + `benchmarks/synthetic.py --smoke`): verde antes do commit.
- Nenhuma busca em F₃⁸ dentro de `tests/`; campanhas só em `benchmarks/`.

## 6. Limitações e próximos passos

- Escopo CPU e orçamento curto (60 s/semente): resultado negativo **não** prova que evolução em bytecode jamais alcance 512; prova apenas que, neste orçamento e com contexto estático, não alcançou.
- Contexto estático (`[0,0,0]`): prioridades não reagem ao estado parcial; contexto dinâmico (tamanho, cobertura) é trabalho futuro (P175+), com custo O(N²) a tratar via GPU.
- Comparabilidade: 1 eval = 1 construção nos três métodos; custos por eval diferem (bytecode ≈ 0,12–0,3 s vs random/SA ≈ 0,03 s) porque `evaluate_priority` executa 6561 programas por construção. O orçamento duplo (tempo OU evals) mantém a comparação honesta em parede.
- Eficiência vs FunSearch: **não julgável** sem número pinado; qualquer P-futura que alegue vantagem deve primeiro pinar o orçamento FunSearch com URL+SHA.
