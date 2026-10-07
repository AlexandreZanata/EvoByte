# P67 entrega 4 — Registro da comparação H06 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `4ba8e9f`), pelo comando congelado `experiments/p67-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P67 --config experiments/p67-config.json --output /tmp/evobyte-p67-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `PROMISING`
  (learned library compresses strictly more) — triagem de compactação,
  não confirmação; ganho de certificado segue medida separada e não
  alegada aqui.
- Escopo do claim: compactação de macros com igualdade de execução em
  programas development; outcome reportado, nada promovido.
- `run_id=96e55cd85f07d98c`, `revision=4ba8e9f`, `dirty=''` (limpa).
- Configuração: `experiments/p67-config.json`,
  `sha256=4ab08dd375ad5b63689a7626d5ef6c77069a5ee86f1fecb5c263030bb508687e`.
- 8 programas development: learned 8 macros, compactação média 0.1375,
  round-trip 8/8, execução igual; clássica 0.0; aleatória 0.0.
- Saída externa: `/tmp/evobyte-p67-acceptance.json`
  (`sha256=92e8d1d9374beb92418283fc7590cbd8c1bc84bb7169e8c968e37cdbe20b83d8`,
  2019 bytes; transitória, não versionada).

## Limites

- PROMISING aqui = triagem de compactação; não promove H06 para ganho de
  certificado nem novidade. Próxima hipótese da bancada: P68.
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–95) ainda necessária.
