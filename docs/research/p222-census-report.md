# P222 — Arquivo parcial do censo de códigos bicíclicos bivariados

Arquivado em 4 de novembro de 2026 no recorte com `ℓ·m ≤ 10`. O plano
integral previa `ℓ·m ≤ 16`, com `n ≤ 32`. O arquivo cobre até `n = 20`.
O aceite integral da fase permanece pendente.
[Plano da P222](../phases/P222-bb-code-exhaustive-census.md)

Em 5 de novembro de 2026, Alexandre determinou o arquivamento com estado
`ARCHIVED / INCOMPLETE`. O recorte foi preservado para consulta. Os gates
globais permanecem pendentes após o timeout de 180 segundos da auditoria
Lean P113 na validação isolada. A preparação posterior do Lean foi
interrompida. Este registro documenta o estado parcial para o
[novo programa](next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md).

## Cobertura e dados

Foram enumerados 65.016 pares de suportes em cinco grupos, com
`2 ≤ ℓ ≤ m`, pesos 3 ou 4 em ambos os blocos e a origem em `A`. São
pares de suportes no domínio da fase. A contagem pode incluir descrições
equivalentes do mesmo código.

- `k = 0` em 34.731 pares, contabilizados no resumo.
- `k > 0` em 30.285 pares, com uma linha JSON por par e distância exata
  no limite de busca de peso 7. Nenhuma linha usou `d_gt`.
- Os maiores valores medidos foram `d = 4` para `(n,k) = (16,2)`
  e `d = 6` para `(n,k) = (20,2)`. O resumo registra os máximos, contagens
  e exemplos de todos os pares `(n,k)` observados.
- A rotina independente da P221, em Python com biblioteca padrão,
  recomputou posto e distância de seis exemplos de máximos com
  `d ≥ 4`. A reverificação foi feita sobre esses exemplos.
  [Recálculo P221](../../tests/test_p221_independent_recompute.py)

O arquivo bruto ocupa 3.338.360 bytes. Seu SHA-256 é
`623474978937de805bce0b0588d17307b5f8f3d629c3dbb8a8cdcf5722340509`.
[Censo em JSON por linha](../../experiments/p222-bb-census.json) ·
[Resumo com máximos e exemplos](../../experiments/p222-bb-census-summary.json)

## Reprodução do recorte

Os cinco testes da P222 passaram. Duas reexecuções em CPU produziram
arquivos brutos idênticos entre si e ao arquivo recuperado, incluindo
as duas calibrações de saída e a reverificação independente. A base Git
da reprodução era `4eb274795ae0fcdc78483f10994c5eccef9451dd`, com o
enumerador da P222 ainda local. Ambiente da reprodução em Intel Core
i7-13620H, 16 CPUs lógicas visíveis, 31 GiB de RAM total exibidos por
`free -h`, Python 3.12.2 e NumPy 2.4.6. Foram usados 16 processos e
nenhuma GPU. A enumeração é determinística e independe de semente.
O teste de comutação usa semente 42.

Os tempos da função de censo registrados nas duas reexecuções foram
6,05 s e 5,15 s. Eles cobrem a enumeração antes da ordenação final,
da gravação e do recálculo independente. São tempos de reprodução em
um ambiente compartilhado. Para comparar eficiência, será necessário
medir o mesmo trabalho sob um orçamento de CPU controlado.

```bash
set -e
p222_replay=$(mktemp -d)
python3 -m pytest tests/test_bb_census.py -q
for p222_run in a b; do
  python3 scripts/run_p222_census.py --max-lm 10 \
    --out "$p222_replay/$p222_run.json" \
    --summary "$p222_replay/$p222_run-summary.json"
done
cmp "$p222_replay/a.json" "$p222_replay/b.json"
cmp "$p222_replay/b.json" experiments/p222-bb-census.json
sha256sum "$p222_replay/b.json"
```

## Evidências reaproveitáveis

O recorte serve como conjunto de referência para comparar o custo de
certificar o mesmo `(k,d)`. A P214 fornece a rota SAT, a P217 fornece
certificados e um verificador autônomo, e a P221 fornece o recálculo
independente e provas Lean para instâncias concretas. Um próximo ciclo
documental deve separar geração do certificado, verificação da testemunha
de peso `d` e certificação da ausência de lógicos de peso menor. Essa
separação permite comparar tempos, memória e tamanho de certificado sob
a mesma garantia matemática.
[P214](p214-sat-bposd-report.md) · [P217](p217-v4-certificates-report.md) ·
[P221](p221-formal-honesty-report.md)
