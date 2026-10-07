# P63 entrega 4 — Registro da comparação H08 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `8aad2cc`), pelo comando congelado `experiments/p63-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P63 --config experiments/p63-config.json --output /tmp/evobyte-p63-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `NULL`
  (real feedback adds no certificate or speed) — fim íntegro, sem promoção.
- Escopo do claim: um scorer, três feedbacks em starts development com
  treino em origens disjuntas; outcome reportado, nada promovido.
- `run_id=36167860b1e9f5f2`, `revision=8aad2cc`, `dirty=''` (limpa).
- Configuração: `experiments/p63-config.json`,
  `sha256=0e07be4ddfb3c7a251aac0e8a715c0e0cd428fa46c8b8bb77a6aea692c214ea6`.
- Treino: 31 amostras de clonagem (origens 4, 8), scorer 145 params,
  acc treino 0.9677, custo 0.2272 s.
- Comparação em 4 starts (origens 6, 9): real 4/4 (82 queries), shuffled
  4/4 (82 queries), scalar 4/4 (12 queries, sem consultas por vizinho).
  Os códigos estruturados não superam o escalar nestes starts.
- Saída externa: `/tmp/evobyte-p63-acceptance.json`
  (`sha256=faedbfdc4aed165c05ce989662f79cbe476fc95f3b222122c68700949db6f81c`,
  2136 bytes; transitória, não versionada).

## Limites

- NULL development encerra o teste sem promoção e libera a próxima
  hipótese da bancada (P64).
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–91) ainda necessária.
