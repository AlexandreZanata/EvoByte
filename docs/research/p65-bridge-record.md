# P65 entrega 4 — Registro da comparação H04 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `98c379c`), pelo comando congelado `experiments/p65-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P65 --config experiments/p65-config.json --output /tmp/evobyte-p65-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `NULL`
  (model-pick adds no certificate over structured-first) — fim íntegro,
  sem promoção.
- Escopo do claim: bibliotecas pareadas nos mesmos alvos com ledgers
  faturados; outcome reportado, nada promovido.
- `run_id=cf7562112ad0818c`, `revision=98c379c`, `dirty=''` (limpa).
- Configuração: `experiments/p65-config.json`,
  `sha256=2e83b654b8444b37c98a1b50ab1e093891d7c0e4382290592cdb1825acf650db`.
- 6 alvos development: random-pick 1/6, structured-first 5/6,
  model-pick 5/6 (treino faturado), direct-search 6/6 (enumeração, não
  descoberta).
- Saída externa: `/tmp/evobyte-p65-acceptance.json`
  (`sha256=b8017c025b8453e5ca2c05cc81d3eb2475400183b3e550e2e1bb1d33ee399523`,
  2089 bytes; transitória, não versionada).

## Limites

- NULL development encerra o teste sem promoção e libera a próxima
  hipótese da bancada (P66).
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–93) ainda necessária.
