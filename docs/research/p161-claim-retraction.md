# Retratação de alegações refutadas e guarda de integralidade (P161)

- **Fase:** P161 — Retratação de alegações refutadas e guarda mecânica de integralidade
- **Data:** 2026-10-21
- **Decisão:** D040 (ver `docs/DECISIONS.md`)
- **Auditoria de origem:** D038, programa P161–P170 (branch `codex/plan-p161-p170-validated-discovery`)
- **Nota de ID:** a especificação da fase previa `D039`, mas esse identificador já foi usado
  pela linha "Plano P153–P160" em `docs/DECISIONS.md`. Como o log é append-only com IDs únicos,
  a retratação foi registrada como `D040` e as referências nos avisos apontam para ela.
- **Escopo:** retratação de P150, P158 e P160; sem apagar histórico e sem rodar campanhas novas

---

## 1. Alegações retratadas

| Alegação | Fonte | Evidência medida | Novo status |
|---|---|---|---|
| 49 das 58 identidades de Schinzel são `novel-extension` | `docs/research/p150-novelty-audit-report.md` | Auditoria de integralidade P161 sobre `lean_proofs/Generated/SchinzelHighModuliTheorems.lean`: 58 identidades, 9 integrais em todo `k in 0..49`, 49 sem nenhum `k` com `(x, y, z)` inteiros positivos | **RETRATADA** — as 49 valem só em ℚ; as 9 restantes cobrem classes de rotina; nenhuma novidade é alegada |
| H1 é `SUPPORTED` | `docs/research/p158-h1-verdict-report.md`, `experiments/p158-verdict/summary_h1_verdict.json` | `experiments/p155-baselines/summary_baselines.json`: Classical-SR 100% de sucesso contra 80% do EvoByte, MSE oculto médio menor, CVPS médio maior; PySR-Adapter com `completed_runs = 0`; orçamentos 0,4 s e 0,8 s | **RETRATADA** — o veredito global passa a ser **NOT SUPPORTED** (critério C5 não atendido) |
| O manuscrito afirma orçamentos de 10 s a 1 h, comparação com PySR e residência em VRAM | `docs/paper/main.tex` (P160) | Orçamentos efetivamente executados: 0,5 s/1,5 s (P154) e 0,4 s/0,8 s (P155); PySR não executado; `vram_peak_mb` máximo 2,72 MB, ou seja, residência total da população não foi medida | **RETRATADA** — o manuscrito foi corrigido e o PDF recompilado |

Nenhum número histórico foi apagado: os avisos acima são adicionados no topo dos relatórios e o
conteúdo original permanece intacto abaixo deles.

## 2. Guarda de integralidade (saída medida)

Comando:

```bash
PYTHONPATH=src python3 -m evobyte.claim_audit lean_proofs/Generated/SchinzelHighModuliTheorems.lean
```

Saída:

```json
{
  "k_max": 50,
  "identities": 58,
  "quadratic_residue_classes": 58,
  "integral_for_all_k": 9,
  "integral_for_no_k": 49
}
```

Leitura: as 58 identidades estão em classes quadráticas residuais (condição necessária), mas
apenas 9 produzem inteiros positivos para todo `k` em `0..49`. As outras 49 têm solução apenas
racional. Em ℚ a decomposição `a/n = 1/x + 1/y + 1/z` é trivial para qualquer fração, logo
essas 49 não são evidência de nada.

## 3. Números do P155 (copiados de `experiments/p155-baselines/summary_baselines.json`)

```json
{
  "budgets_sec": [0.4, 0.8],
  "seeds": [42, 101, 202, 303, 404],
  "target_keys": ["x_plus_1", "x2_3x_7"],
  "total_trials": 100,
  "comparison": {
    "Random":        {"completed_runs": 20, "success_rate": 0.5, "mean_hidden_mse": 36.41719174979401,  "median_hidden_mse": 22.28440044174396, "mean_cvps": 4204.96272683719,   "mean_complexity": 5.45},
    "Classic-GP":    {"completed_runs": 20, "success_rate": 0.5, "mean_hidden_mse": 11.05409927368164,  "median_hidden_mse": 8.68596172332764,  "mean_cvps": 44561.890873095625, "mean_complexity": 6.0},
    "Classical-SR":  {"completed_runs": 20, "success_rate": 1.0, "mean_hidden_mse": 3.9130647490056724e-13, "median_hidden_mse": 3.913064749005673e-13, "mean_cvps": 26116.527336271258, "mean_complexity": 6.0},
    "PySR-Adapter":  {"completed_runs": 0,  "success_rate": 0.0, "mean_hidden_mse": Infinity,        "median_hidden_mse": Infinity,        "mean_cvps": 0.0,               "mean_complexity": 0.0},
    "EvoByte":       {"completed_runs": 20, "success_rate": 0.8, "mean_hidden_mse": 0.9786504719908017, "median_hidden_mse": 3.197442310920451e-14, "mean_cvps": 4799.521463293107,  "mean_complexity": 5.2}
  }
}
```

Hardware registrado pelo próprio artefato: `NVIDIA GeForce RTX 4060 Laptop GPU`, driver
`580.173.02`, 8188 MiB.

Duas ressalvas de medição, declaradas no manuscrito:

- `Classical-SR` é um ajuste de mínimos quadrados polinomial de graus 1--5. Os alvos Level-A
  medidos são polinômios, logo essa classe cobre a classe do alvo exatamente; os 100% de sucesso
  refletem cobertura da classe de alvo, não um método de busca mais forte.
- A coluna de CVPS não é homogênea: o EvoByte conta candidatos de bytecode verificados, enquanto
  a linha `Classical-SR` divide cinco ajustes polinomiais pelo tempo do ajuste. A comparação de
  vazão é indicativa; a comparação de taxa de sucesso e de erro oculto é direta.

## 4. Correções aplicadas no manuscrito (P160 → P161)

- Abstract: orçamentos reais (0,4 s / 0,8 s), PySR explicitamente não executado, veredito
  `not supported` no critério de baselines honestos, e remoção da alegação de residência em VRAM.
- Seção de protocolo: orçamentos efetivamente executados declarados (0,5 s/1,5 s em P154;
  0,4 s/0,8 s em P155); a faixa 10 s--1 h não foi executada e não é claimada.
- Nova tabela de baselines medidos (`tab:baselines`) com os números do P155.
- Seção de estado de H1: veredito `NOT SUPPORTED`, com aviso de retratação sobre a
  `tab:h1_verdict` (que preserva o veredito pré-retratação do P158 como registro histórico).
- Fronteira de Pareto: removida a alegação de que o EvoByte domina os baselines classical e
  random; os pontos medidos são apresentados como estão.
- Ablações: o fator 15,51× passa a ser atribuído à cascata completa (ablação A8, medida sem a
  cascata) e o fator 2,60× à execução GPU contra CPU (ablação A6), e não a "residência em VRAM".
- Conclusão e texto relacionado: affirmed apenas o que foi medido, incluindo o resultado nulo.

## 5. Testes de guarda

`tests/test_claim_audit.py` (7 testes) falha se:

1. uma identidade de Schinzel deixar de ser integral onde era;
2. uma identidade válida deixar de ser reconhecida;
3. uma expressão fora da lista segura for avaliada;
4. uma identidade falsa deixar de ser detectada;
5. a regressão 58 / 9 / 49 mudar;
6. o abstract do manuscrito contradisser os dados de baseline medidos (PySR junto de
   `not executed`; sem `1\,h` nem `10\,s` quando o orçamento máximo medido é menor que 10 s);
7. faltar um dos quatro avisos de retratação.

O artefato bruto do P155 (`experiments/p155-baselines/`) é grande e não é versionado (regra
`experiments/*-baselines/` do `.gitignore`). Por isso o teste 6 mantém uma cópia commitada dos
números que ele confere (`P155_BASELINE_SNAPSHOT` em `tests/test_claim_audit.py`); quando o
artefato bruto está presente localmente, os dois têm que concordar, e a divergência quebra o
teste.

## 6. Reprodução

```bash
git switch codex/p161-claim-retraction-integrality-guard
python3 -m pytest tests/test_claim_audit.py -q
PYTHONPATH=src python3 -m evobyte.claim_audit lean_proofs/Generated/SchinzelHighModuliTheorems.lean
python3 -m pytest tests -q
make verify
(cd docs/paper && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex)
```

## 7. Conclusão

Nenhuma descoberta matemática inédita foi obtida até P161.
