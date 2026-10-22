# P171 — Catálogo de fronteira v2: alvos genuinamente abertos, snapshots datados e verificadores calibrados

**Status:** Done (2026-10-22).
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P170 concluída; esta especificação vive no branch `codex/plan-p171-p190-frontier-discovery`.
**Owner:** agente executor; revisor humano (Alexandre) valida a lista final de alvos no PR.
**Branch:** `codex/p171-frontier-target-catalogue-v2` (a partir de `codex/plan-p171-p190-frontier-discovery`).
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042),
[`docs/research/p166-campaign-verdict.md`](../research/p166-campaign-verdict.md) §5.1.

## Por que esta fase existe

O catálogo v1 (`docs/research/targets/open_targets.json`, P163) só continha valores **exatos já
provados** (W(3,3)=27, W(2,6)=1132, S(5)=160) e uma conjectura transcrita de forma vazia. A campanha
P166 estava, portanto, condenada ao resultado nulo **antes** de rodar. Nenhuma busca, por melhor que
seja, supera um valor provado ótimo.

Esta fase constrói o catálogo v2: só entram como alvo de recorde problemas cujo melhor valor
publicado **não é provado ótimo**, com fonte primária datada, snapshot com hash e um verificador
independente que foi **calibrado contra objetos conhecidos** antes de julgar qualquer candidato.

## Pergunta falsificável da fase

> Existem, nas famílias *covering designs*, números de Schur fracos/fortes e *cap sets*, alvos cujo
> melhor valor publicado (a) não é provado ótimo, (b) tem fonte primária recuperável e (c) tem
> certificado verificável em menos de 60 s por um verificador só com biblioteca padrão?

Se a resposta for "não" para uma família, a família sai do programa, e isso é registrado como resultado.

## Fatos de partida (consultados em 2026-10-22, **re-verifique todos**)

Estes fatos foram lidos pelo planejador. O executor **deve** reconsultar cada um e registrar
divergências; nenhum deles pode ser copiado para o catálogo sem snapshot próprio.

| Fato | Fonte consultada | Observação |
|---|---|---|
| LJCR tem 8.759 entradas `C(v,k,t)`, 6.832 com `size > low_bd` | `github.com/dmgordo/LJCR`, `coverings/coverdata.json`, commit `459bcaf247bd8d34610d946b0465864f7d4dfa37` (2022-12-19) | 1.204 melhorias em 2021 e 1.257 em 2022: a fronteira **se mexia** |
| O site ao vivo `ljcr.dmgordon.org` não resolveu DNS a partir desta máquina | `curl`, 2026-10-22 | O README do repositório diz que o site "eventually will go away" |
| Entradas exatas: C(7,3,2)=7, C(9,3,2)=12, C(8,4,3)=14 | `coverdata.json` (size = low_bd) | Usadas só como calibração |
| Schur fraco (OEIS A118771, convenção "menor s **sem** partição"): 3, 9, 24, 67; comentário de 2023: a(5) ≥ 197, a(6) ≥ 583, a(7) ≥ 1741 | `oeis.org/A118771` | **Conflito:** a busca web cita WS(6) ≥ 646 (Ageron et al., 2022) e WS(6) ≥ 650 (2026). Resolva com a fonte primária |
| Schur (OEIS A030126, mesma convenção): 2, 5, 14, 45, 161; a(6) ≥ 537, a(7) ≥ 1681 | `oeis.org/A030126` | Na convenção "maior N **com** partição": S(5)=160 (provado, Heule 2017), S(6) ≥ 536, S(7) ≥ 1680 |
| *Cap sets* máximos exatos (OEIS A090245): n=0..6 → 1, 2, 4, 9, 20, 45, 112 | `oeis.org/A090245` | n=8 ≥ 512 (FunSearch, *Nature* 2024, doi `10.1038/s41586-023-06924-6`). n=7: **extraia** a melhor cota da fonte primária (tabelas de Yves Edel e o paper do FunSearch); não presuma |

> [!IMPORTANT]
> **Regra de convenção.** O catálogo grava `best_known_value` na convenção "maior N com partição
> válida" (Schur) ou "tamanho do objeto" (cap set, covering), **e** grava a convenção de origem em
> `source_convention`. Confundir as convenções gera um "recorde" falso de +1.

> [!IMPORTANT]
> **Regra do pior caso.** Se fontes discordarem, `best_known_value` é o valor **mais forte** já
> alegado (máximo para maximizar, mínimo para minimizar), mesmo que não verificado. Todos os valores
> alegados vão para `claimed_values` com fonte. Isso impede declarar "recorde" sobre uma cota
> desatualizada.

## Escopo

**Arquivos que você pode criar:**
- `src/evobyte/frontier_catalogue.py` (verificadores e carregador; **só biblioteca padrão**)
- `scripts/build_frontier_catalogue.py` (constrói o catálogo de forma determinística a partir dos snapshots)
- `tests/test_frontier_catalogue.py`
- `docs/research/targets/frontier_targets_v2.json` (catálogo congelado)
- `docs/research/targets/frontier_sources_v2.json` (fontes: URL, data de acesso, SHA-256, commit)
- `docs/research/targets/ljcr_pool_v2.json` (subconjunto filtrado do LJCR usado na seleção, pequeno)
- `docs/research/targets/certificates/` (certificados publicados obtidos, cada um < 1 MB)
- `docs/research/p171-frontier-catalogue-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P171-frontier-target-catalogue-v2.md`: só a linha de Status e o bloco final de execução.

**Snapshots brutos** (ficam em `data/raw/frontier/`, **não** são commitados, já ignorados pelo `.gitignore`):
`coverdata.json` do LJCR, páginas OEIS em `fmt=text`, PDFs e arquivos auxiliares dos papers.

**Proibido:**
- alterar `docs/research/targets/open_targets.json` (v1 fica como registro histórico);
- alterar o bytecode, a VM ou qualquer módulo de busca;
- adicionar dependências ao `pyproject.toml`;
- inventar qualquer número; cada valor do catálogo aponta para uma entrada de `frontier_sources_v2.json`.

## Trabalho ordenado

### Passo 1 — Branch e árvore limpa

```bash
git status --short          # precisa estar vazio
git switch codex/plan-p171-p190-frontier-discovery
git switch -c codex/p171-frontier-target-catalogue-v2
mkdir -p data/raw/frontier
```

### Passo 2 — Snapshots com proveniência

Para cada fonte abaixo: baixe para `data/raw/frontier/`, calcule SHA-256 e registre em
`frontier_sources_v2.json` com `source_id`, `url`, `accessed_at` (ISO 8601 com fuso),
`sha256`, `pinned_commit` (quando houver) e `notes`.

1. LJCR: `https://raw.githubusercontent.com/dmgordo/LJCR/<commit>/coverings/coverdata.json`, com o
   commit obtido em `https://api.github.com/repos/dmgordo/LJCR/commits?per_page=1`. Tente também o site
   ao vivo (`https://ljcr.dmgordon.org/cover/table.html` e `https://dmgordon.org/cover`). Registre
   `live_site_status` como `reachable`, `unreachable` ou `redirect:<url>`.
2. OEIS: `https://oeis.org/search?q=id:A118771&fmt=text`, idem para `A030126` e `A090245`.
3. Paper do FunSearch (doi acima) e o repositório público do FunSearch: localize o *cap set* de
   tamanho 512 em n=8 como lista explícita de vetores ou como o programa publicado que o gera.
4. Schur fraco: localize o paper primário com o certificado de WS(6) mais forte (busque "New lower
   bounds for Schur and weak Schur numbers", Ageron et al., e qualquer trabalho posterior que alegue
   valor maior, por exemplo de 2026). Baixe a partição explícita se publicada (arquivos auxiliares do arXiv).
5. Schur forte: fonte primária de S(6) ≥ 536 e S(7) ≥ 1680 (Fredricksen & Sweet, 2000, ou posterior)
   e, se disponível, a partição explícita.
6. *Cap sets* n=7 e n ≥ 9: tabela de Yves Edel (`yvesedel.de`, caps) e o paper do FunSearch.

Se uma fonte não puder ser obtida, registre `status: "not_obtained"` com o motivo. **Não substitua
por valor de memória.**

### Passo 3 — `src/evobyte/frontier_catalogue.py` (só biblioteca padrão)

Contrato obrigatório. Todas as funções retornam `(ok: bool, message: str)` e **nunca** lançam
exceção para entrada malformada: entrada malformada é `(False, "<motivo>")`.

| Função | Semântica exata | Rejeita obrigatoriamente |
|---|---|---|
| `verify_covering_design(blocks, v, k, t)` | Todo t-subconjunto de `{1..v}` está contido em ao menos um bloco | bloco com tamanho ≠ k; elemento fora de `1..v`; elemento repetido no bloco; não inteiro; `t > k` ou `k > v` |
| `verify_weak_schur_partition(coloring, k)` | `coloring[i-1]` é a cor de `i`; não existe `x < y` com `x + y = z ≤ N` e as três cores iguais | cor fora de `1..k`; lista vazia; não inteiro |
| `verify_cap_set(points, n)` | Pontos de F₃ⁿ, distintos, sem três distintos com `a+b+c ≡ 0 (mod 3)` coordenada a coordenada | coordenada fora de `{0,1,2}`; comprimento ≠ n; ponto duplicado |
| `load_frontier_catalogue(path)` | Lê o JSON v2, valida o esquema e retorna objetos imutáveis | campo ausente; `role` inválido; alvo de recorde com `proven_optimal = true` |

Requisitos de implementação:
- **Covering:** marque os t-subconjuntos cobertos em um `bytearray` de bits indexado pelo posto
  colexicográfico (sistema numérico combinatório); `ok` se e só se o número de bits ligados for
  `comb(v, t)`. Recuse com `(False, "too large")` se `comb(v, t) > 10**7`.
- **Weak Schur:** a regra é `x < y` estrito; `x + x = 2x` é **permitido** (diferença para Schur forte).
- O verificador de Schur forte já existe (`target_catalogue.verify_schur_partition`, P163). Não o
  duplique; o catálogo v2 o referencia pelo nome.
- Nenhum `import` fora da biblioteca padrão (o teste 8 confere via AST). Um auditor externo precisa
  rodar o arquivo sozinho, como na P167.

### Passo 4 — Catálogo `frontier_targets_v2.json`

Esquema de cada alvo (todos os campos são obrigatórios):

```json
{
  "target_id": "covering_C_32_16_6",
  "family": "covering_design | weak_schur | schur | cap_set",
  "params": {"v": 32, "k": 16, "t": 6},
  "objective": "minimize | maximize",
  "role": "record | calibration",
  "stratum": "stale_construction | active_frontier | random_control | named_open | calibration",
  "best_known_value": 286,
  "source_convention": "texto livre descrevendo a convenção da fonte",
  "claimed_values": [{"value": 286, "source_id": "ljcr-coverdata-459bcaf", "verified_object": false}],
  "lower_bound": 154,
  "proven_optimal": false,
  "last_improvement": "1996-11-14",
  "last_method": "JCD article",
  "certificate_status": "verified_published_object | not_obtained | site_unreachable | constructed_calibration",
  "certificate_path": null,
  "verifier": "verify_covering_design",
  "verifier_runtime_s": 0.0
}
```

O exemplo acima é **ilustrativo**: os valores reais saem do snapshot que você baixar.

**Seleção de covering designs (regra congelada; não ajuste depois de ver resultados):**

1. *Pool:* entradas com `size > low_bd`, `2 ≤ t ≤ 6`, `comb(v,t) ≤ 10**7` e `size ≤ 2000`.
   Grave o pool em `ljcr_pool_v2.json` (nome, size, low_bd, data e método da última melhoria `imps[0]`).
   Na leitura do planejador o pool tinha 3.827 entradas; diferenças devem ser explicadas no relatório.
2. *Estrato `stale_construction` (20 alvos):* `construction = 1` se o texto (minúsculo) de método
   mais autor da última melhoria contém algum de `multiple of`, `construction`, `extraction`,
   `remainder`, `combin`, `jcd article`, `greedy`, `wang`, `from (`; caso contrário 0.
   `score = 1.0*construction + 0.02*min(2026 - ano, 25) + 0.5*(size - low_bd)/size`.
   Ordene por `(-score, v, k, t)` e pegue os 20 primeiros com no máximo 5 por valor de `t`.
3. *Estrato `active_frontier` (10 alvos):* fora do estrato anterior, entradas com ≥ 2 melhorias
   datadas de 2020 em diante; ordene por `(-n_melhorias_desde_2020, nome)` e pegue 10.
4. *Estrato `random_control` (10 alvos):* `random.Random(171).sample(...)` sobre o restante do pool
   ordenado por nome. Serve de controle: a P174 testa se o escore prevê melhoria.
5. *Calibração:* C(7,3,2), C(9,3,2) e C(8,4,3), com `role = calibration` e `proven_optimal = true`.

**Alvos nomeados (Schur e cap sets):**

| `target_id` | `role` | Observação |
|---|---|---|
| `weak_schur_5`, `weak_schur_6`, `weak_schur_7` | record (se não provado) | `best_known_value` pela regra do pior caso |
| `schur_6`, `schur_7` | record | S(5)=160 entra só como `schur_5` com `role = calibration` |
| `cap_set_7`, `cap_set_9`, `cap_set_10` | record | Valores só das fontes primárias |
| `cap_set_8` | calibration | 512 é o alvo de **reprodução** da hipótese H2 (Trilha B), não de recorde |
| `cap_set_3` … `cap_set_6` | calibration | Valores exatos de A090245 |

### Passo 5 — Calibração dos verificadores (antes de julgar qualquer candidato)

**Objetos construídos** (gere-os no código do teste; não cole listas longas):
- Plano de Fano: `[(1,2,3),(1,4,5),(1,6,7),(2,4,6),(2,5,7),(3,4,7),(3,5,6)]` cobre `(7,3,2)`; sem qualquer um dos blocos, não cobre.
- AG(2,3): as 12 retas de F₃² (pontos rotulados `1 + 3x + y`) cobrem `(9,3,2)`; sem qualquer reta, não cobrem.
- S(3,4,8): os 14 planos afins de F₂³ (pontos rotulados `1 + 4a + 2b + c`) cobrem `(8,4,3)`; sem qualquer plano, não cobrem.

**Objetos publicados:** para cada alvo com certificado obtido no Passo 2, o verificador precisa
aceitá-lo e o tamanho medido precisa ser igual a `best_known_value`. Uma mutação aleatória
(semente fixa) do objeto que viole a propriedade precisa ser rejeitada.
Se o verificador **rejeitar** um certificado publicado, **PARE**: ou o verificador está errado, ou
a convenção foi mal lida. Não ajuste nada para "fazer passar" sem entender a causa.

Meça `verifier_runtime_s` para cada alvo de recorde: para covering, em um conjunto de `size`
blocos aleatórios com semente 171 (o tempo de verificação depende do tamanho, não da validade).

### Passo 6 — `tests/test_frontier_catalogue.py`

Os valores esperados abaixo foram **executados pelo planejador** em 2026-10-22:

1. `test_fano_covers_and_every_removal_fails`: Fano é válido; as 7 remoções são inválidas.
2. `test_ag23_and_s348_cover`: AG(2,3) (12 blocos) e S(3,4,8) (14 blocos) válidos; cada remoção é inválida.
3. `test_covering_rejects_malformed`: bloco de tamanho errado, elemento `0`, elemento `v+1`, elemento repetido, `t > k`.
4. `test_weak_schur_known_partition`: `[1,1,2,1,2,2,2,1]` (classes {1,2,4,8} e {3,5,6,7}) é **válida** para Schur fraco e **inválida** para `verify_schur_partition` (porque 4+4=8).
5. `test_weak_schur_exhaustive_small`: existem exatamente **2** partições fracas de `[1..8]` em 2 classes e **nenhuma** de `[1..9]` (confirma WS(2)=8, ou seja, A118771 a(2)=9).
6. `test_cap_set_small`: `{(0,0),(0,1),(1,0),(1,1)}` é válido; não existe cap de 5 pontos em F₃² (busca exaustiva); `{0,1}³` (8 pontos) é válido; `{(0,0),(1,1),(2,2)}` é inválido; ponto duplicado e coordenada `3` são rejeitados.
7. `test_catalogue_schema_and_rules`: carrega o v2; todo alvo `record` tem `proven_optimal = false`; todo `source_id` existe em `frontier_sources_v2.json` com SHA-256 de 64 hex e `accessed_at`; `best_known_value` obedece à regra do pior caso sobre `claimed_values`; há 20/10/10 alvos nos três estratos de covering e ao menos 3 calibrações de covering.
8. `test_frontier_module_is_stdlib_only`: o AST de `frontier_catalogue.py` só importa módulos da biblioteca padrão.
9. `test_published_certificates_regression`: todo alvo com `certificate_status = verified_published_object` tem certificado em `certificate_path` que verifica e cujo tamanho é igual a `best_known_value`.
10. `test_selection_rule_reproducible`: rodar a função de seleção de `scripts/build_frontier_catalogue.py` sobre `ljcr_pool_v2.json` reproduz exatamente os 40 `target_id` de covering do catálogo.

### Passo 7 — Relatório `docs/research/p171-frontier-catalogue-report.md`

Obrigatório conter:
- tabela de fontes com SHA-256 e status (`obtained`, `not_obtained`, `unreachable`);
- conflitos encontrados (por exemplo WS(6): OEIS × papers) e como a regra do pior caso os resolveu;
- tamanho do pool, os 40 alvos de covering por estrato e os alvos nomeados;
- calibração: quais certificados publicados foram verificados e quais não puderam ser obtidos;
- `live_site_status` do LJCR e a consequência: se o site estiver fora, toda alegação futura de recorde
  em covering depende de reconfirmar a tabela com o curador (P187/P188);
- frase final literal: "Nenhuma descoberta é alegada nesta fase."

## Regras de parada (PARE, não commite, reporte)

- Um verificador rejeita um certificado publicado, ou aceita uma mutação inválida.
- Qualquer teste do Passo 6 falha, ou `make verify` falha.
- Alguma família termina sem nenhum alvo `record` com fonte primária: registre no relatório e peça
  decisão humana antes de seguir (não invente alvo substituto).
- A regra de seleção produz um conjunto diferente em duas execuções.
- Um valor do catálogo não tem `source_id` correspondente.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_frontier_catalogue.py -q
python3 scripts/build_frontier_catalogue.py --check   # reconstrói e compara com o JSON commitado
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add src/evobyte/frontier_catalogue.py scripts/build_frontier_catalogue.py \
  tests/test_frontier_catalogue.py \
  docs/research/targets/frontier_targets_v2.json docs/research/targets/frontier_sources_v2.json \
  docs/research/targets/ljcr_pool_v2.json docs/research/targets/certificates \
  docs/research/p171-frontier-catalogue-report.md \
  docs/phases/P171-frontier-target-catalogue-v2.md
git diff --cached --check
git commit -m "feat(research): build p171 frontier catalogue v2 with calibrated verifiers"
git push -u origin HEAD
gh pr create --base codex/plan-p171-p190-frontier-discovery \
  --title "feat(research): p171 frontier catalogue v2" \
  --body-file /tmp/evobyte-p171-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p171-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (pool, alvos, calibrações), limitações (fontes não obtidas, site
fora do ar) e o link do relatório.

---

**Status da execução (2026-10-22):** Done.

- Snapshots de proveniência baixados em `data/raw/frontier/` e registrados em `docs/research/targets/frontier_sources_v2.json` (10 fontes com URLs, datas ISO 8601, commits e SHA-256 de 64 hex).
- `live_site_status` do LJCR aferido como `unreachable` (falha DNS e HTTP 404), estabelecendo o repositório Git commit `459bcaf` como única fonte recuperável.
- Regra de seleção determinística implementada em `scripts/build_frontier_catalogue.py` e congelada em `docs/research/targets/ljcr_pool_v2.json` (3.827 entradas, 20 `stale_construction`, 10 `active_frontier`, 10 `random_control`, 3 calibrações de covering).
- Alvos nomeados consolidados sob a regra do pior caso: Schur fraco ($N \in \{207, 650, 2146\}$), Schur forte ($N \in \{160, 536, 1680\}$) e cap sets ($N \in \{9, 20, 45, 112, 236, 512, 1082, 2240\}$).
- Verificadores autônomos implementados em `src/evobyte/frontier_catalogue.py` estritamente com biblioteca padrão (aprovado por inspeção AST).
- 12 certificados publicados e de calibração criados e validados em `docs/research/targets/certificates/`.
- 10/10 testes aprovados em `tests/test_frontier_catalogue.py`, `python3 scripts/build_frontier_catalogue.py --check` verde, `make verify` verde.
- Relatório formal consolidado em `docs/research/p171-frontier-catalogue-report.md`.
