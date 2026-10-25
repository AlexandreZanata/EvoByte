# P184 — Verificador autônomo zero-dependency para qualquer pesquisador validar em < 10 s

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P171 (verificadores de referência), P179 (verificador QECC) e P167 (padrão de empacotamento) concluídas; branch a partir de `main`.
**Owner:** agente executor; revisor externo simulado (rodar numa máquina limpa sem o repo instalado).
**Branch:** `codex/p184-external-validation-standalone-verifier`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), `scripts/verify_certificate_standalone.py` (padrão P167 a estender).

## Por que esta fase existe

Uma descoberta só existe quando um estranho consegue verificá-la sem instalar nada nosso.
Esta fase empacota **um script CLI zero-dependency (só biblioteca padrão)** que valida
qualquer certificado do programa — covering designs, Schur fraco/forte, cap sets e códigos
estabilizadores QECC — em menos de 10 segundos numa máquina limpa, mais certificados de
exemplo certificados end-to-end.

## Pergunta falsificável da fase

> Um pesquisador com apenas Python 3.9+ valida cada certificado de exemplo do programa em
> menos de 10 s, sem instalar o pacote, sem NumPy, sem rede — com código de saída 0 para
> válidos e 1 para corrompidos?

## Fatos de partida

| Fato | Fonte |
|---|---|
| Padrão de verificador autônomo existe e funciona (`verify_certificate_standalone.py`: só `json`/`sys`/`hashlib`) | `scripts/verify_certificate_standalone.py` (P167, ler antes de estender) |
| Verificadores de referência existem para covering, Schur fraco, cap sets e QECC | P171 (`frontier_catalogue.py`) e P179 (`qecc_verifier.py`) |
| Certificados de exemplo do programa: amostra P167 (`dist/external-validation/sample_certificate.json`) + certificados P168 | Artefatos commitados |

## Escopo

**Arquivos que você pode criar:**
- `scripts/verify_frontier_certificate.py` (CLI zero-dependency: covering, schur, weak_schur, cap_set, qecc_stabilizer)
- `src/evobyte/frontier_certificate_exporter.py` (exporta o JSON padronizado a partir dos objetos internos)
- `tests/test_frontier_standalone_verifier.py` (só lógica + subprocesso; suíte < 3 s)
- `dist/external-validation/frontier_sample_*.json` (um certificado de exemplo por família, cada um < 1 MB)
- `docs/research/p184-external-validation-dossier.md` (guia de 3 comandos + matriz de validação)

**Arquivos que você pode editar:**
- `docs/phases/P184-external-validation-standalone-verifier.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- importar qualquer módulo fora da biblioteca padrão no script CLI (teste AST trava isso);
- exigir `numpy`, `pip install` ou rede em qualquer ponto da validação externa;
- testes que baixem qualquer coisa ou rodem buscas (tudo offline e instantâneo).

## Trabalho ordenado

### Passo 1 — Branch e leitura do padrão

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p184-external-validation-standalone-verifier
sed -n '1,80p' scripts/verify_certificate_standalone.py
```

### Passo 2 — `scripts/verify_frontier_certificate.py`

Copiar a arquitetura do script P167 (cabeçalho, `main(argv)`, códigos de saída 0/1/2) e
estender o despacho por `certificate_type`:

| `certificate_type` | Campos do JSON | Verificação (só stdlib) |
|---|---|---|
| `covering` | `blocks`, `v`, `k`, `t` | todo t-subconjunto de `{1..v}` coberto (rejeita bloco de tamanho ≠ k, elemento fora, repetido) |
| `schur` | `partition`, `k` | sem `x + y = z` monocromático (permite `x = y`) |
| `weak_schur` | `partition`, `k` | sem `x < y`, `x + y = z` monocromático (`x = x` permitido) |
| `cap_set` | `points`, `n` | pontos distintos de F₃ⁿ, sem três distintos com soma ≡ 0 |
| `qecc_stabilizer` | `stabilizers` (lista de strings), `n`, `k_claimed`, `d_claimed` | comutam dois a dois; posto `n-k`; distância exata por varredura simplética por peso (puro Python; para os exemplos de calibração; documentar o limite de escala) |

Saída: `[*] Certificate target / File SHA-256`, `[SUCCESS] ...` (exit 0) ou `[FAILED] ...`
em stderr (exit 1); uso errado (exit 2). Sem `import` além de `argparse`, `hashlib`, `json`, `sys`.

Escala honesta: o verificador QECC autônomo usa força bruta com poda por peso e declara no
`--help` e no relatório o limite prático (adequado aos exemplos de calibração; códigos
grandes usam o verificador NumPy da P179, e o dossiê diz isso abertamente).

### Passo 3 — `src/evobyte/frontier_certificate_exporter.py` + certificados de exemplo

Exportador que converte objetos internos (blocos, partições, pontos, estabilizadores) no
JSON padronizado com `target_id`, `certificate_type`, `candidate_length`,
`reference_literature`, `sha256_checksum` (do objeto canônico), `reproduction_seed` e
`provenance` — espelhando `certificate_exporter.py` da P167 sem duplicar seu código
(importar e estender onde couber).

Um certificado de exemplo por família em `dist/external-validation/frontier_sample_*.json`,
cada um gerado por execução real (não digitado) e verificado end-to-end pelos dois
verificadores (interno + autônomo) antes do commit. Exemplos de calibração, não de recorde.

### Passo 4 — Testes `tests/test_frontier_standalone_verifier.py` (todos < 0,2 s; suíte < 3 s)

1. `test_standalone_accepts_valid_covering`: Fano `[(1,2,3),(1,4,5),(1,5? ...)]` — usar o
   Fano exato da P171 — retorna 0 via `subprocess.run` do script CLI.
2. `test_standalone_rejects_corrupted_covering`: remover um bloco do Fano → exit 1 + `FAILED`.
3. `test_standalone_accepts_weak_schur_and_rejects_strong_claim`: a partição fraca de `[1..8]`
   da P171 passa como `weak_schur` e **falha** como `schur` (distinção fraca/forte preservada).
4. `test_standalone_accepts_cap_cube_and_rejects_line`: `{0,1}³` passa; tripla com soma zero → exit 1.
5. `test_standalone_accepts_steane_and_rejects_broken`: Steane passa com `d_claimed = 3`;
   gerador corrompido (uma letra trocada) → exit 1.
6. `test_standalone_imports_only_stdlib`: AST do script só importa stdlib.
7. `test_sample_certificates_verify_both_implementations`: cada exemplo em `dist/external-validation/frontier_sample_*.json`
   passa no script CLI **e** no verificador interno correspondente, com o mesmo veredito.

### Passo 5 — Dossiê `docs/research/p184-external-validation-dossier.md`

Guia de 3 comandos por família (baixar script + certificado, rodar, conferir hash), matriz de
validação (família × verificador interno × verificador autônomo × tempo medido < 10 s),
limites declarados (escala do QECC autônomo) e a frase: "nenhum certificado de exemplo desta
fase alega recorde".

## Regras de parada (PARE, não commite, reporte)

- O script importar qualquer módulo fora da biblioteca padrão.
- Falha na execução do subprocesso do verificador (qualquer família).
- Discrepância entre verificador interno e autônomo sobre o mesmo objeto.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer download ou busca em `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_frontier_standalone_verifier.py -q -m "not slow"   # FAST LOOP, ~1s
for f in dist/external-validation/frontier_sample_*.json; do python3 scripts/verify_frontier_certificate.py "$f" || exit 1; done
python3 -m pytest tests/test_frontier_standalone_verifier.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add scripts/verify_frontier_certificate.py src/evobyte/frontier_certificate_exporter.py \
  tests/test_frontier_standalone_verifier.py dist/external-validation/frontier_sample_*.json \
  docs/research/p184-external-validation-dossier.md \
  docs/phases/P184-external-validation-standalone-verifier.md
git diff --cached --check
git commit -m "feat(research): implement p184 external standalone verifier"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(research): p184 external standalone verifier" \
  --body-file /tmp/evobyte-p184-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p184-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, matriz de validação com tempos medidos (< 10 s cada), limitações (escala do
QECC autônomo; exemplos são calibração) e o link do dossiê.

## Registro de Execução

- **Script Standalone:** `scripts/verify_frontier_certificate.py` (zero imports fora da stdlib).
- **Exportador Padronizado:** `src/evobyte/frontier_certificate_exporter.py`
- **Amostras Padronizadas:** 5 certificados gerados e verificados em `dist/external-validation/frontier_sample_*.json`.
- **Matriz de Validação:** 5/5 famílias verificadas de forma cruzada (interno vs standalone CLI); tempos entre 27 ms e 31 ms (todos < 10 s).
- **Dossiê:** [`docs/research/p184-external-validation-dossier.md`](../research/p184-external-validation-dossier.md)
