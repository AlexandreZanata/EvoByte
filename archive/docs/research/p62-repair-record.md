# P62 entrega 4 — Registro da comparação pareada H01 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `540ee17`), pelo comando congelado `experiments/p62-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P62 --config experiments/p62-config.json --output /tmp/evobyte-p62-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `NULL`
  (no more certificates and no faster loop) — fim íntegro, sem promoção.
- Escopo do claim: políticas pareadas em starts development com treino em
  origens disjuntas; outcome reportado, nada promovido.
- `run_id=ef3025947a54fb3b`, `revision=540ee17`, `dirty=''` (limpa).
- Configuração: `experiments/p62-config.json`,
  `sha256=2f3a8a096ecf3b0d0eb318a5395733141e7834898fe4b4af095006d68f652368`.
- Treino: 31 amostras de clonagem (origens 4, 8), reparador 129 params,
  acc treino 0.3871, custo 0.2082 s faturado ao learned.
- Comparação em 4 starts development (origens 6, 9): clássico 4/4
  (4 ciclos), learned 2/4 (17 ciclos), random 0/4 (28 ciclos).
- Saída externa: `/tmp/evobyte-p62-acceptance.json`
  (`sha256=0a412a13044b1e6a0fe2b07ed284767c972ad84ba3893527ae6842cffd7e01fd`,
  2218 bytes; transitória, não versionada).

## Limites

- NULL development encerra o teste sem promoção e libera a próxima
  hipótese da bancada (P63). Clonar o clássico não supera o professor
  por construção.
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–90) ainda necessária.
