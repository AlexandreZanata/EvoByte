# P60 entrega 4 — Registro da aceitação técnica da bancada (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `6d9c130`), pelo comando congelado `experiments/p60-run.sh`.
Nenhuma escrita versionada (`git status` limpo após a execução); nenhum
final tocado.

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P60 --config experiments/p60-config.json --output /tmp/evobyte-p60-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`.
- Escopo do claim: aceitação técnica da bancada em tarefas development;
  nenhuma hipótese confirmada ou promovida.
- `run_id=ced679eb2bdcb324`, `revision=6d9c130`, `dirty=''` (limpa).
- Configuração: `experiments/p60-config.json`,
  `sha256=a80a67577379ab92bbf95b29097cb6220f8d353e9624fc76b509c31de469896a`.
- Pré-registro íntegro: manifesto v1 (hash conferido), 6 tarefas, 3 seeds,
  orçamentos espelhados, revisão aceita com registro existente.
- Development: 6 tarefas × 2 braços = 12/12 `certified`, `inputs_hash`
  idêntico entre braços por tarefa, triplas recertificadas pelos dois
  checkers exatos dentro de `max_coord=10^9`.
- Custo medido 0.0003 s vs teto registrado 1800 s.
- Saída externa: `/tmp/evobyte-p60-acceptance.json`
  (`sha256=8dd39918a1203b3a95fbcdac28d4d165c806d1347ef6090a5308fc963b9c670d`,
  4429 bytes; transitória, não versionada).

## Limites

- Igualdade development não prova generalidade nem ganho estatístico.
- P61–P70 exigem esta bancada aceita; cada hipótese mede sob seu próprio
  gate. Confirmação em P71, novidade em P72.
- Integração dos predecessores (PRs #86, #87, #88) ainda necessária.
