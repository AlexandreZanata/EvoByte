# P59 entrega 4 — Registro da medição dos controles (2026-10-07)

Medição executada em árvore limpa com configuração congelada (entrega 3,
commit `e69f235`), pelo comando congelado
`experiments/p59-run.sh`. Nenhuma escrita versionada (`git status` limpo
após a execução); nenhum final P38/P56/P71 tocado.

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P59 --config experiments/p59-config.json --output /tmp/evobyte-p59-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]`.
- Escopo do claim: entradas públicas iguais entre braços em instâncias
  development; compilação separada da descoberta; nenhum ganho estatístico
  declarado (confirmação de hipótese fica para P60/P71).
- `run_id=1655463c6f5b5bea`, `revision=e69f235`, `dirty=''` (limpa).
- Configuração: `experiments/p59-config.json`,
  `sha256=c1c99efff6330735c2961dd89d12d28224daf5e40ad496d4b29f98ea46cc5286`.
- ES: 3 instâncias development (n=4, 6, 9), 6/6 trials `certified` com
  `inputs_hash` idêntico entre braços; origens `classical-*`/`enumerated`
  (warm-start vazio, nada herdado).
- Sentinelas: 2/2 PASS (troca de privada não altera propostas).
- Compilação: 1 controle `exact-horner` com programa e custo separado.
- Ledgers: todos com seis parcelas e total calculado (nada subtraído).
- Escopo: `erdos-straus` comparável; taxicab/diophantine restritas,
  fora de qualquer comparação.
- Saída externa: `/tmp/evobyte-p59-acceptance.json`
  (`sha256=3d27055cafd97683f953a750a964e449835d9c9c0fb43064154df66495005757`,
  3939 bytes; transitória, não versionada).

## Limites

- Controle de engenharia (igualdade de inputs), não evidência de ganho.
- P60 (nova nominação) e P71 (finais novos) seguem pendentes e fora desta
  medição. Integração dos predecessores (PRs #86, #87) ainda necessária.
