# P71 entrega 2 — Registro de confirmação independente (2026-10-13)

Medição executada em árvore limpa com configuração congelada (entrega 1,
commit `78f79ad`), pelo comando congelado `experiments/p71-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução).

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P71 --config experiments/p71-config.json --output /tmp/evobyte-p71-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`. Outcomes da confirmação: `INCONCLUSIVE`
  em ambas as faixas (H06 e H08) por insuficiência de grupos decisivos (<4).
- Escopo do claim: confirmação em dados finais novos de no máximo dois
  resultados da triagem com procedimento congelado; status PROVISIONAL
  sem reexecução do operador independente; nenhum claim de novidade matemática.
- `run_id=f793fbdc79f05de2`, `revision=78f79add5ea1ecde5063efe070daf221092eb513`,
  `dirty=''` (limpa).
- Configuração: `experiments/p71-config.json`,
  `sha256=996d988db456e8ac26f3a2a124b91b256c2ae926ff2aa4b2f7f21b2cced29b85`.
- Dados finais: `experiments/p71-final.json`,
  `sha256=69894f32ad09c67c21562dcf7ea108c236be1f5c8ab28eb85216b8790d52dcbd`.
- Biblioteca H06: `experiments/p71-h06-library.json`,
  `sha256=6761cdd4566058097e6afcc08d48b8fd38595377380a22f1219cc41c08e1d00e`.
- Pesos H08: `experiments/p71-h08-weights.json`,
  `sha256=f28bf8a87e4582d2dba4c437316df24683ffba7ce80fdacfa79988f6a60e8c2d`.
- Faixa H06 (macro-compactação): W=0, L=0, T=6 (6 empates em 6 sementes 1000–1005),
  p=1.0000, holm=1.0000 -> `INCONCLUSIVE` (fewer than 4 decisive groups).
- Faixa H08 (eficiência do atacante): W=2, L=0, T=4 (2 vitórias nos templates
  even [62,81] e [82,101], 4 empates em múltiplos de 3 e resíduos mod 3),
  p=0.5000, holm=1.0000 -> `INCONCLUSIVE` (fewer than 4 decisive groups).
- Saída externa: `/tmp/evobyte-p71-acceptance.json`
  (`sha256=77da5c7c9f49f1fd035b3d34f80bd71cd9104acf30fd058bbaeaa4cbb800777b`,
  5660 bytes; transitória, não versionada).

## Pacote de reprodução e operador independente

- Instrução: reexecutar `experiments/p71-run.sh` em revisão limpa e reportar
  `run_id` e sha256 do relatório.
- Operador designado: IA independente em outra máquina (confirmado 2026-10-07;
  status pending).

## Limites

- INCONCLUSIVE encerra a confirmação das duas hipóteses de triagem sem confirmação
  de ganho em dados finais novos.
- Nenhuma hipótese alcança significância estatística após correção de Holm.
- Nenhuma hipótese promovida a P72; a fase P72 operará com baselines aceitos.
- Integração dos predecessores (PRs #86–98) ainda necessária.
