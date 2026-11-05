# P58 R2 — Dossiê rastreável e recuperação (2026-10-07)

Escopo: somente inventário e recuperação da base P58. Nenhuma disposição
dos seis itens (R3), nenhuma medição final (R4), nenhuma liberação de P59.

## Manifesto de artefatos duráveis

`experiments/p58-durable-manifest.json`
(`sha256=5b21bd4b5d1119b43812128c1b763b5813221fc5f5ec7c413574ab8294c432a6`,
25 entradas, 1012331 bytes no total). Cada entrada registra
caminho, tamanho e hash:

- Manifestos selados (3): `p52-certified-data.json`,
  `p53-proposer-manifest.json`, `p56-final-tasks.json`.
- Certificados (1): `p57-certificates.json` (145794 bytes).
- Raw durável (3): `p52-certified-data-raw.json`,
  `p53-proposer.pt` (119079 bytes, pesos do proponente),
  `p53-proposer-raw.json`.
- Aceitação recuperada (18): `p58-recovered-acceptance/p40..p57-acceptance.json`
  (cópias transitórias recuperadas sem selo prévio; seguem provisionais).

## Recuperação dos pesos sem depender de `/tmp`

Verificado em 2026-10-07 via `git ls-files experiments/`: as 25 entradas,
inclusive `experiments/p53-proposer.pt`, estão rastreadas no Git, apesar do
padrão `*.pt` no `.gitignore` (inclusão forçada anterior). Logo, um checkout
novo recupera pesos, raw e manifestos pelo próprio clone, sem `/tmp`.
Presença local isolada não foi usada como prova: o critério aplicado foi o
rastreamento versionado, reproduzível em outra máquina com
`git clone` + `git ls-files` + conferência do manifesto.

## Fonte externa: sem afirmação de estado aberto atual

Catálogo P46 (`docs/research/open-problems.json`,
status `built-pending-human-review`): snapshot datado
`consulted_at=2026-10-02`, dataset `Teorth/erdosproblems`
commit `6754c649e41328f461412eb1d08ea72f1d4bb5d1` de 2026-09-28
(`dataset_file_sha256=cd3f949a…c923dfeb`). As páginas vivas
(erdosproblems.com) **não** foram reconsultadas neste ciclo
(2026-10-07; tentativa: não realizada, sem erro de rede a registrar).
Uso restrito ao snapshot datado como referência histórica; nenhum estado
aberto atual é afirmado. Pareceres atuais versionados neste repo:
`docs/research/campaign-review.md`, `docs/research/nomination.md`
(inalterados por esta entrega; hashes conferíveis via Git).

## Objetos matemáticos e controles efetivamente usados pela base

- Certificados P57: 932 triplas de Erdős–Straus, rechecadas com o checker
  exato sob limites estritos (diagnóstico R1: 932/932).
- Dados P52: corpus certificado com positivos, controles e negativos.
- Pesos/raw P53: proponente `SequentialHistoryProposer` (28184 parâmetros)
  e raw associado; modelo segue DESLIGADO da base (P54 DROP).
- Tarefas P56: `p56-final-tasks.json` selado.
- Controles: negativos P52 rejeitados como certificado exato; P54 como
  análise exploratória, sem KEEP.

Revisão concluída no nível de inventário: todos os objetos acima existem,
têm tamanho/hash registrados no manifesto e são recuperáveis por checkout
novo. Juízo sobre cada um dos seis itens (referência datada, exclusão,
limite de uso) pertence a R3 e não é antecipado aqui.
