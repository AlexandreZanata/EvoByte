# P188 — Pacote Zenodo arquivável e container hermético de reprodução

**Status:** Proposed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P171–P187 executadas (o pacote arquiva o programa inteiro); branch a partir de `main`.
**Owner:** agente executor; revisor de sistemas (hermeticidade real, não alegada).
**Branch:** `codex/p188-zenodo-archive-reproducibility-container`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), `scripts/export_zenodo_bundle.py` (padrão P159/P170 a estender).

## Por que esta fase existe

Reprodutibilidade pública exige dois artefatos independentes: (1) um pacote Zenodo/OSF com
todos os dados brutos, catálogos, verificadores, certificados e o manuscrito, com manifesto
SHA-256; (2) um container hermético (rede desativada) que executa a suíte de verificação de
ponta a ponta. Sem isso, a "descoberta" não é ciência aberta — é arquivo local.

## Pergunta falsificável da fase

> Um terceiro, com apenas o tarball e o Dockerfile, reproduz a verificação completa
> (verificadores sobre certificados + suíte rápida de testes) sem rede, e o manifesto
> SHA-256 valida 100% dos arquivos?

## Fatos de partida

| Fato | Fonte |
|---|---|
| Exportador com manifesto + autoverificação existe | `scripts/export_zenodo_bundle.py` (`generate_bundle`, `verify_zenodo_bundle_integrity`) |
| Padrão de pacote final com índice top-level | P170 (`dist/zenodo-bundle/final-manifest-sha256.json`) |
| Container hermético existe como referência | P159 (Dockerfile `--network none`; reler antes de estender) |
| O que arquivar: catálogos v1/v2 + fontes, verificadores, certificados, campanhas, vereditos, manuscrito, revisões | Saídas das P171–P187 |

## Escopo

**Arquivos que você pode criar:**
- `dist/zenodo-bundle-frontier/final-manifest-sha256.json` (índice top-level do novo pacote)
- `docs/research/p188-reproducibility-dossier.md`

**Arquivos que você pode editar:**
- `scripts/export_zenodo_bundle.py`: **somente** estender globs/coleta para o programa P171–P190 (mesmo padrão documentado da P170; sem mudar lógica de verificação).
- `Dockerfile` (+ `.dockerignore` se preciso): camada de reprodução do programa de fronteira.
- `docs/phases/P188-zenodo-archive-reproducibility-container.md`: só a linha de Status e o bloco final de execução.
- `.gitignore`: somente exceções cirúrgicas para o manifesto final do novo pacote (mesmo padrão P167/P170).

**Proibido:**
- versionar tarballs, bundles extraídos ou snapshots brutos (`data/raw/` continua ignorado);
- rede no container de verificação (teste trava qualquer egress);
- alegar hermeticidade sem executar o container com rede desativada.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p188-zenodo-archive-reproducibility-container
```

### Passo 2 — Estender a coleta do exportador (mínimo documentado)

Incluir: `docs/phases/P17*.md` + `P18*.md` + `P19*.md` relevantes, `docs/research/targets/*`
(JSONs e certificados), `benchmarks/run_*campaign*.py` + `frontier_*.py` + `h2_*.py` +
`verify_frontier_certificate.py`, `src/evobyte/frontier_*.py` + `qecc_*.py` +
`stabilizer_search.py` + `priority_evolution.py` + `constructive*.py`, catálogos v2/QECC,
`experiments/p17*` e `p18*`, `docs/paper/` do novo manuscrito (P189 — se ainda não existir,
registrar `pending_p189` e reexportar depois; **não** bloquear a P188 por isso, mas o pacote
final só fecha após a P189).

### Passo 3 — Exportar, verificar, indexar

```bash
python3 scripts/export_zenodo_bundle.py --output-dir dist/zenodo-bundle-frontier
python3 - <<'PY'
from scripts.export_zenodo_bundle import verify_zenodo_bundle_integrity
sound, findings = verify_zenodo_bundle_integrity("dist/zenodo-bundle-frontier/evobyte-research-bundle")
assert sound, findings
print("bundle OK:", len(findings) == 0)
PY
```

Gerar `dist/zenodo-bundle-frontier/final-manifest-sha256.json` no mesmo formato da P170
(bundle + tarball + lista de evidências com SHA-256, flag `versioned` e pertencimento).

### Passo 4 — Container hermético e teste sem rede

Estender/validar o `Dockerfile`: build, `docker run --network none`, dentro dele
`python3 -m pytest tests/test_frontier_catalogue.py tests/test_qecc_verifier.py -q -m "not slow"`
e os verificadores autônomos sobre os certificados de exemplo. Registrar logs e hashes de
imagem no dossiê. Sem Docker disponível: registrar `container_unverified_locally` com o
motivo e **não** alegar hermeticidade (regra de parada 4 adapta: o gate local exige ao menos
build + teste de rede bloqueada via `unshare -n` ou equivalente documentado, ou PARE).

### Passo 5 — Dossiê `docs/research/p188-reproducibility-dossier.md`

Conteúdo do pacote (contagem de arquivos/bytes), cadeia de custódia, comandos exatos de
reprodução por terceiro, resultado do container hermético (ou `container_unverified_locally`
com motivo) e limitações.

## Regras de parada (PARE, não commite, reporte)

- `verify_zenodo_bundle_integrity` retornar qualquer achado.
- Container com qualquer egress de rede durante a verificação.
- Qualquer teste da suíte rápida > 0,2 s fora do marcado `slow`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
test -f dist/zenodo-bundle-frontier/final-manifest-sha256.json
python3 -m pytest tests -q -m "not slow" 2>&1 | tail -2   # suíte rápida do repo
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add scripts/export_zenodo_bundle.py Dockerfile .dockerignore \
  dist/zenodo-bundle-frontier/final-manifest-sha256.json \
  docs/research/p188-reproducibility-dossier.md \
  docs/phases/P188-zenodo-archive-reproducibility-container.md .gitignore
git diff --cached --check
git commit -m "feat(research): implement p188 zenodo archive and hermetic container"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(research): p188 zenodo archive" \
  --body-file /tmp/evobyte-p188-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p188-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos (exportação, verificação de integridade, container sem rede), números medidos
(arquivos, bytes, hashes) e limitações (Docker indisponível? P189 pendente?) com o link do dossiê.
