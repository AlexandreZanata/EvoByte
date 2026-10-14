# P70 entrega 4 — Registro da busca H10 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `4062d99`), pelo comando congelado `experiments/p70-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P70 --config experiments/p70-config.json --output /tmp/evobyte-p70-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `NULL`
  (no novel proven template in the frozen grid) — fim íntegro, sem promoção.
- Escopo do claim: busca de templates em grade congelada com scan integral
  de novidade; outcome reportado, nada promovido, gramática inalterada.
- `run_id=7361352d632f5e45`, `revision=4062d99`, `dirty=''` (limpa).
- Configuração: `experiments/p70-config.json`,
  `sha256=4f6060041798bf5551a97d93c1fbb39310688b536eefb743e414c3a6899020d4`.
- Grade: 124 templates, 3 positivos (controles). Proponente 65 params,
  acc 0.9758, rotulagem 5.196 s faturada.
- Braços: proponente acha control-mult3 (11 verificações), estruturada e
  clássica acham control-even (1). Scan integral: zero templates novos
  provados.
- Saída externa: `/tmp/evobyte-p70-acceptance.json`
  (`sha256=0354ca629c4e18ff1f1931f71a2d5526b045c7908bd4bee07f794cdb1a9ac744`,
  2172 bytes; transitória, não versionada).

## Limites

- NULL fecha a bancada H01–H10 sem nenhuma promoção de novidade:
  P61 NULL, P62 NULL, P63 NULL, P64 NULL, P65 NULL, P66 NULL, P67
  PROMISING-compactação, P68 PROMISING-eficiência, P69 NULL, P70 NULL.
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–98) ainda necessária.
