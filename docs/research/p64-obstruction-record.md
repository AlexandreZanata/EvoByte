# P64 entrega 4 — Registro da economia de obstruções H03 (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `964882f`), pelo comando congelado `experiments/p64-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P64 --config experiments/p64-config.json --output /tmp/evobyte-p64-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcome da hipótese: `NULL`
  (no proven rule with positive net saving) — fim íntegro, sem promoção.
- Escopo do claim: regras provadas em caixas declaradas com economia
  medida; outcome reportado, nada promovido.
- `run_id=b25f80931994a537`, `revision=964882f`, `dirty=''` (limpa).
- Configuração: `experiments/p64-config.json`,
  `sha256=71a005af2dd472706fce637653842234d54d830a6ba653f89dd1f253c7febb0a`.
- Regra sum_le≤4 (n=4, caixa 6): PROVEN, 4 eliminados, net −0.0002 s
  (a prova custa mais do que poupa nestas caixas).
- Regra paridade x-ímpar: REFUTED com contraexemplo, zero eliminações.
- Conhecidos válidos mantidos: 3/3. Scan priorizado: fração não-filtrada
  0.102 ≥ piso 0.1.
- Saída externa: `/tmp/evobyte-p64-acceptance.json`
  (`sha256=8263f315095993476f876876cc93f3cc0b2bff7caddc921a2fc2b7c1656214a5`,
  2078 bytes; transitória, não versionada).

## Limites

- NULL development encerra o teste sem promoção e libera a próxima
  hipótese da bancada (P65). Raro não é impossível.
- Confirmação em P71 e novidade em P72 seguem fora de questão aqui.
- Integração dos predecessores (PRs #86–92) ainda necessária.
