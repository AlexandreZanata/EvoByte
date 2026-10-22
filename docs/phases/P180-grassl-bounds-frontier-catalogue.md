# P180 — Catálogo de fronteira QECC a partir das tabelas de Grassl

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P179 concluída (verificador de distância); branch a partir de `codex/p179-quantum-stabilizer-code-verifier`.
**Owner:** agente executor; revisor humano valida a lista final no PR (cotas vêm de fonte externa).
**Branch:** `codex/p180-grassl-bounds-frontier-catalogue`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P179-quantum-stabilizer-code-verifier.md`](P179-quantum-stabilizer-code-verifier.md).

## Por que esta fase existe

A Trilha quântica só pode atacar o que é **aberto**: parâmetros `[[n,k,d]]` onde a distância
`d` tem um intervalo em aberto entre limitante inferior e superior nas tabelas de Markus
Grassl (`codetables.de`). Esta fase constrói o catálogo congelado desses alvos com snapshot
datado e hash — e registra explicitamente o que **não** pôde ser obtido, em vez de presumir.

## Pergunta falsificável da fase

> Existem parâmetros `[[n,k,d]]` com `d` em intervalo aberto `[d_lo, d_hi]`, `d_lo < d_hi`,
> documentados em fonte primária recuperável (Grassl snapshot ou paper), verificáveis pelo
> verificador da P179 em instâncias de referência?

Se nenhum alvo com gap aberto for documentável, o catálogo registra zero alvos de recorde
(mais calibrações) e a Trilha quântica não avança sem decisão humana.

## Fatos de partida (ilustrativos — o executor reconfirma tudo contra snapshot)

| Fato | Status |
|---|---|
| Exemplo de gap citado no programa: `[[20,2,d]]` com `6 <= d <= 7` | **Ilustrativo.** Usar somente se o snapshot confirmar; senão, descartar o exemplo e usar o que o snapshot contiver |
| `codetables.de` é mantido por Markus Grassl e referenciado pela literatura | Verificar alcance na execução; registrar `reachable`/`unreachable`/redirect |
| Steane [[7,1,3]] e Shor [[9,1,3]] como calibração | P179 (verificador já os confirma) |

> [!IMPORTANT]
> **Regra de ouro.** Nenhum `best_known_*` entra no catálogo sem `source_id` com URL (ou
> referência bibliográfica completa), data de acesso e SHA-256 do snapshot. Valor sem fonte
> é proibido, mesmo que "todo mundo saiba".

## Escopo

**Arquivos que você pode criar:**
- `docs/research/targets/qecc_frontier_v1.json` (catálogo congelado)
- `docs/research/targets/qecc_sources_v1.json` (fontes: URL, data, SHA-256, status)
- `docs/research/targets/qecc_pool_raw/` — **não** commitado (snapshots brutos ficam em `data/raw/quantum/`, já ignorado; ver Passo 2)
- `scripts/build_qecc_catalogue.py` (constrói o catálogo deterministicamente a partir dos snapshots)
- `tests/test_qecc_catalogue.py` (só esquema e regras; suíte < 3 s)
- `docs/research/p180-qecc-catalogue-report.md`

**Arquivos que você pode editar:**
- `docs/phases/P180-grassl-bounds-frontier-catalogue.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- inventar cotas, intervalos ou "melhorias recentes" sem snapshot;
- digitar estabilizadores de referência de memória (só de snapshot ou paper com DOI);
- testes que baixem qualquer coisa da rede (tudo offline, a partir de `data/raw/quantum/`).

## Trabalho ordenado

### Passo 1 — Branch e pré-condições

```bash
git status --short
git switch codex/p179-quantum-stabilizer-code-verifier
git switch -c codex/p180-grassl-bounds-frontier-catalogue
mkdir -p data/raw/quantum
python3 -m pytest tests/test_qecc_verifier.py -q -m "not slow"   # P179 verde
```

### Passo 2 — Snapshots com proveniência

Tentar, nesta ordem, registrando tudo em `qecc_sources_v1.json`:

1. `https://codetables.de/` e subpáginas de tabelas (anotar HTTP status, redirects e se o
   conteúdo é estático ou JS-dinâmico; se dinâmico e não espelhável, registrar
   `status: "not_obtained_dynamic_site"` com o motivo — **não** copiar valores de memória).
2. Papers primários com cotas QECC abertas (buscar no arXiv; baixar PDF + fonte do teorema).
3. Para cada alvo candidato: `lower_bound`, `upper_bound`, `gap = upper - lower > 0`.

Se **nenhum** gap aberto for documentável: grave o catálogo só com calibrações
(Steane/Shor + 2-3 códigos pequenos verificados localmente), marque
`"record_targets": []` e **PARE para decisão humana** (regra de parada 4).

### Passo 3 — Esquema `qecc_frontier_v1.json`

Cada alvo (todos os campos obrigatórios):

```json
{
  "target_id": "qecc_20_2_open",
  "family": "qecc_stabilizer",
  "n": 20, "k": 2,
  "d_lo": 6, "d_hi": 7,
  "objective": "achieve d >= d_hi via explicit stabilizer set, or prove d >= d_lo+1",
  "role": "record | calibration",
  "best_known_value": 6,
  "source_convention": "lower bound = maior d com construção explícita publicada",
  "claimed_values": [{"value": 6, "source_id": "..."}],
  "verifier": "qecc_verifier.code_distance",
  "certificate_status": "constructed_calibration | not_obtained | verified_published_object | none_yet",
  "certificate_object": null
}
```

Os valores do exemplo acima são **ilustrativos**; os reais saem do snapshot. `role = record`
exige `d_lo < d_hi` com fonte; sem gap documentado, não há alvo de recorde.

### Passo 4 — `scripts/build_qecc_catalogue.py`

Determinístico: lê `data/raw/quantum/` + regras de seleção codificadas e escreve o catálogo
e as fontes. Rodar duas vezes gera bytes idênticos (teste 4 confere). Calibrações
(Steane/Shor + códigos pequenos) têm certificados embutidos verificados pelo P179.

### Passo 5 — Testes `tests/test_qecc_catalogue.py` (todos < 0,2 s; suíte < 3 s)

1. `test_catalogue_schema`: todo alvo `record` tem `d_lo < d_hi`, fonte com SHA-256 e data;
   `role = calibration` só para códigos com certificado verificado localmente.
2. `test_no_exact_proven_targets`: nenhum alvo `record` tem `lower == upper` provado
   (regra anti-parede: vetado pela AGENTS.md).
3. `test_sources_have_provenance`: todo `source_id` do catálogo existe em
   `qecc_sources_v1.json` com URL+data+SHA ou `status` de não-obtenção com motivo.
4. `test_build_is_deterministic`: rodar o script duas vezes sobre os mesmos snapshots gera
   o mesmo JSON byte a byte.
5. `test_calibration_certificates_verify`: certificados embutidos passam no verificador P179.

### Passo 6 — Relatório `docs/research/p180-qecc-catalogue-report.md`

Fontes com SHA/status, gaps documentados (ou sua ausência), calibrações, o que **não** foi
possível obter e por quê, e a frase literal: "Nenhuma cota foi presumida; todo número tem fonte snapshotada."

## Regras de parada (PARE, não commite, reporte)

- Algum `best_known_*` sem `source_id` válido.
- Site/papel inalcançável **e** nenhum gap documentável → catálogo só-calibração + pedir decisão humana (não inventar alvo).
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer download dentro de `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_qecc_catalogue.py -q -m "not slow"   # FAST LOOP, ~1s
python3 scripts/build_qecc_catalogue.py --check                   # reconstrói e compara com o JSON commitado
python3 -m pytest tests/test_qecc_catalogue.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add scripts/build_qecc_catalogue.py tests/test_qecc_catalogue.py \
  docs/research/targets/qecc_frontier_v1.json docs/research/targets/qecc_sources_v1.json \
  docs/research/p180-qecc-catalogue-report.md \
  docs/phases/P180-grassl-bounds-frontier-catalogue.md
git diff --cached --check
git commit -m "feat(research): implement p180 grassl bounds frontier catalogue"
git push -u origin HEAD
gh pr create --base codex/p179-quantum-stabilizer-code-verifier \
  --title "feat(research): p180 grassl catalogue" \
  --body-file /tmp/evobyte-p180-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p180-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, números medidos (alvos, gaps, calibrações), limitações (o que não foi
obtido) e o link do relatório. **Snapshots brutos ficam em `data/raw/quantum/` (ignorado pelo
git) e nunca entram no commit.**
