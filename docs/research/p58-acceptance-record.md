# P58 R4 — Registro da medição final read-only (2026-10-07)

Medição executada em árvore limpa, revisão aceita, configuração congelada
(R3, commit `8890aa5`). Interface existente, sem escrita em entrada
versionada (`git status` limpo após a execução) e sem abertura de final.

## Comando

```text
python3 benchmarks/science_matrix.py --acceptance-phase P58 --config experiments/p58-config.json --output /tmp/evobyte-p58-acceptance.json
```

## Resultado medido

- Veredito: `ACCEPTED`, achados: `[]` (zero falhas técnicas).
- Escopo do claim: somente reconciliação de evidências P40–P57; nenhuma
  busca nova, nenhuma novidade ou descoberta.
- `run_id=af5b084d4e47f886`, `revision=8890aa5`, `dirty=''` (limpa).
- Configuração: `experiments/p58-config.json`,
  `sha256=ac3a57fc89c20f64ddc866f4fac2764447c494c6e1a654810bd3095757a307b`.
- Selos: 3/3. Certificados: 932/932 rechecados com o checker exato.
  Raw durável: 3/3. Recuperação: 18/18 `ALREADY_DURABLE`, 0 ausentes.
- Decisões: 6/6 íntegras, 0 achados. Revisão de código: aceita, 0 achados.
  Aprovações pendentes bloqueantes: 0; dispensadas por disposição
  restritiva válida (reportadas, não ocultas): p46, p47, p48, p54, p56.
  `p58-scope-review` aprovada por delegação expressa (escopo técnico).
- Saída externa: `/tmp/evobyte-p58-acceptance.json`
  (`sha256=e683fe9a42be69e0804cec0f90eb9547084b7dc87a1b3302e92990d9006a0589`,
  19688 bytes; transitória, não versionada).

## Limites

- A aceitação vale para o escopo técnico da base; não certifica
  conclusões científicas históricas, independência, ganho ou descoberta.
- P59 fica elegível por esta aceitação; a integração do predecessor
  (merge do PR #86) continua necessária para trabalhar sobre a base aceita.
