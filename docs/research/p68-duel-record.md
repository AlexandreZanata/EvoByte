# P68 entrega 4 — Registro do duelo H07 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `5d07e07`), pelo comando congelado `experiments/p68-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P68 --config experiments/p68-config.json --output /tmp/evobyte-p68-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `PROMISING`
  (>=20% fewer queries, no refutation drop) — triagem de eficiência,
  não teorema; H07 sem promoção de novidade.
- Escopo do claim: duelo de atacantes em templates development com
  orçamentos iguais; outcome reportado, nada promovido.
- `run_id=4731654ae35c923d`, `revision=5d07e07`, `dirty=''` (limpa).
- Configuração: `experiments/p68-config.json`,
  `sha256=cb2108f22653058622e1b7eb65cffd18c1d146c168be58abb22a88bae2112bcb`.
- Treino: 111 amostras (3 templates), scorer 73 params, acc 1.0,
  custo 1.3058 s.
- Duelo em 2 templates dev: learned 2 refutações em 2 queries, random
  2 em 3, systematic 2 em 3. Refutar templates não refuta Erdős–Straus.
- Saída externa: `/tmp/evobyte-p68-acceptance.json`
  (`sha256=d60b8f1dc8cddcef4f90a565a5b8378dcdadc9c47f50b6ee9d7b82c124e1dc36`,
  2087 bytes; transitória, não versionada).

## Limites

- PROMISING aqui = triagem de eficiência do atacante; pontos cegos
  compartilhados seguem possíveis e o checker fixo continua obrigatório.
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–96) ainda necessária.
