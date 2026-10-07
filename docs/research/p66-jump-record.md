# P66 entrega 4 — Registro da comparação H05 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `bf7e0fb`), pelo comando congelado `experiments/p66-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P66 --config experiments/p66-config.json --output /tmp/evobyte-p66-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `NULL`
  (guided adds no certificate over controls) — fim íntegro, sem promoção.
- Escopo do claim: guiado × aleatório × isolado em starts development com
  ops reconciliadas; outcome reportado, nada promovido.
- `run_id=5bed77c91ce3f0b5`, `revision=bf7e0fb`, `dirty=''` (limpa).
- Configuração: `experiments/p66-config.json`,
  `sha256=eba34811cec6a0b979c3ffa1bad13fb83653df51132736e17735738325468ae5`.
- Treino: 32 amostras (0 positivas — nenhum pacote aleatório certificou
  nos starts treino), scorer 65 params, acc 1.0, custo 0.5604 s.
- Comparação em 2 starts dev: guided 0 (37 ops, alcance 15), random 0
  (45 ops, alcance 16), isolated 0 (37 ops, alcance 26). Ops guiado ==
  isolado; nenhum certificado em nenhum braço.
- Saída externa: `/tmp/evobyte-p66-acceptance.json`
  (`sha256=ed7fb51390694d414df9ce4035163aff37c37b9412ec82d89a5a18edb6424667`,
  2138 bytes; transitória, não versionada).

## Limites

- NULL development encerra o teste sem promoção e libera a próxima
  hipótese da bancada (P67). Amplitude sem certificado não sustenta nada;
  nenhum tunelamento alegado.
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–94) ainda necessária.
