# P61 entrega 4 — Registro da comparação pareada H02 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `e874992`), pelo comando congelado `experiments/p61-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P61 --config experiments/p61-config.json --output /tmp/evobyte-p61-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `NULL`
  (filtered arm not cheaper) — fim íntegro, sem promoção.
- Escopo do claim: comparação pareada com/sem filtro em conjuntos
  development; outcome reportado, nada promovido.
- `run_id=19f999d156db749d`, `revision=e874992`, `dirty=''` (limpa).
- Configuração: `experiments/p61-config.json`,
  `sha256=a8a5bf7feadb86612cb5883dbf2ea69c341ff13522d2b63aa6a6a5969d444843`.
- n=4: 8201 candidatos, 11 kept, 10 certificados, acordo CPU/CUDA.
  n=6: 201 candidatos, 1 kept, 1 certificado, acordo CPU/CUDA.
  Certificados idênticos nos dois braços, zero rejeição falsa.
- Custos: filtrado 0.5751 s vs direto 0.1218 s — o checker exato direto é
  tão barato nestes conjuntos que o filtro não se paga.
- Saída externa: `/tmp/evobyte-p61-acceptance.json`
  (`sha256=f29a4a5375d65f86deb709549da6e5a047fcfd1472fecf46f55ea8d9f6ac4b1d`,
  2231 bytes; transitória, não versionada).

## Limites

- NULL development não condena o mecanismo em geral; apenas encerra este
  teste sem promoção e libera a próxima hipótese da bancada (P62).
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–89) ainda necessária.
