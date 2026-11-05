# P233 — Reprodução e comparação com garantia equivalente

Estado `PROPOSED`, proposta de 2026-11-05. Uma tarefa por ciclo.
Executor solicitado pelo usuário — Gemini Flash 3.8.

[Contrato comum obrigatório](../research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md)

## Dependência e objetivo

Pilotos elegíveis encerrados com gates técnicos verdes e contratos congelados. O revisor registra os pilotos admitidos à comparação.

Reproduzir os resultados e verificar quais ganhos sobrevivem ao custo completo de certificação.

## Arquivos permitidos

- `scripts/run_p233_comparison.py`
- `docs/research/p233-comparison-report.md`
- `docs/phases/P233-independent-comparison.md`, somente estado e evidências desta tarefa.

Os arquivos de implementação/saída listados acima são entregáveis futuros.
Conferir sua existência antes de editar e preservar alterações prévias.

## Antes de começar

Ler `AGENTS.md`, o contrato comum e o documento de experimentos. Confirmar
os pré-requisitos da fase e a revisão aprovada. A base `origin/main` deve
conter o plano e os predecessores aceitos.

```bash
set -euo pipefail
test -z "$(git status --porcelain)"
git fetch origin main
git switch -c codex/p233-independent-comparison origin/main
```

Se já estiver na branch indicada e ela estiver limpa, conferir a base e
continuar nela. Se o nome existir em outra posição ou houver arquivos
locais pendentes, parar com o estado observado.

## Passos da tarefa

1. Ler pré-registro e relatórios dos pilotos. Fixar revisões e hashes dos
   scripts, checkers e entradas. Identificar quais pilotos foram eliminados
   e o motivo. Uma ausência de resultado permanece no relatório.
2. Criar um orquestrador específico `run_p233_comparison.py --prereg PATH
   --out PATH`, chamando as interfaces já implementadas. Usar subprocessos
   para medir CPU e RSS de cada método, incluindo os filhos quando houver.
   P230 é chamado por `--case` e `--method`. P231/P232 são chamados
   por `--method`, mantendo seus lotes congelados. Os nomes dos seletores
   estão nas fases correspondentes. Uma medição de RSS por processo inteiro
   fica identificada com esse escopo.
3. Executar duas baterias de comparação, sem paralelizar experimentos,
   cinco repetições alternadas por caso. Teto global de 300 s, 2 GiB e
   até 4 núcleos. Registrar primeiro uso/importação e tempo aquecido.
4. Rodar os checkers separados e conferir o mesmo domínio e garantia antes
   de calcular uma razão de tempos. Comparar somente métodos do mesmo
   problema. SAT sem prova rechecável fica com sua garantia própria.
5. Guardar todas as observações, inclusive timeout e perdas. Calcular por
   caso e por piloto mediana, mínimo, máximo, razão e RSS. Agregar apenas
   trabalho equivalente com cobertura completa. Preservar o limiar da P229.
6. Identificar o executor e a implementação de cada checker. Solicitar
   reprodução por outro executor quando necessário ao rótulo de
   independência. Uma repetição própria permanece identificada como tal.
7. Escrever os desfechos `RETAIN_METHOD`, `NO_GAIN`, `REFUTED` ou
   `INCONCLUSIVE`, com evidências. Código de saída não zero é falha técnica
   e interrompe o ciclo. JSON contém revisões/hashes, configuração,
   garantia por caso, medições brutas, resultados dos checkers e vereditos.

## Gate específico

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 scripts/run_p233_comparison.py --prereg experiments/p229-preregistration.json --out /tmp/evobyte-p233-result.json
python3 -m json.tool /tmp/evobyte-p233-result.json > /tmp/evobyte-p233-inspection.txt
```

A tarefa termina com relatório integral, diferenças de garantia expostas e
medidas recuperáveis. Um ganho só é retido quando satisfaz o critério em
ambas as baterias e todos os checkers pertinentes concordam. Uma mudança
de revisão requer repetir a comparação afetada.


## Parada e entrega

Parar em discrepância de hash/resultado, API ausente, erro de execução,
limite técnico excedido sem saída íntegra ou decisão matemática pendente.
Guardar logs e arquivos locais. Um veredito científico negativo previsto
no contrato é entregue com a evidência correspondente e passa por revisão.

Executar os gates comuns, incluindo `make verify` e formatação. Antes de
encerrar, reportar arquivos alterados, comandos e códigos de saída,
artefatos e hashes, veredito, limitações, commit e PR. A fase fica em revisão
até o aceite humano de seu gate final. O próximo ciclo depende desse aceite.

## Commit & Push

Somente depois de todos os gates verdes, revisar o diff e escrever o corpo
do PR em `/tmp/evobyte-p233-pr.md`, com resultado, comandos e limites reais.
Conferir a lista abaixo contra o escopo autorizado.

```bash
git diff --check
git add -- scripts/run_p233_comparison.py \
  docs/research/p233-comparison-report.md \
  docs/phases/P233-independent-comparison.md
git diff --cached --check
git diff --cached --stat
git commit -m "feat(bench): compare certified low-compute pilots"
git push -u origin codex/p233-independent-comparison
gh pr create --base main --head codex/p233-independent-comparison \
  --title "feat(bench): compare certified low-compute pilots" \
  --body-file /tmp/evobyte-p233-pr.md
git status --short
```

Se houver PR aberto para essa branch, atualizar seu corpo com `gh pr edit`
e o mesmo arquivo. O revisor realiza o aceite e a integração.
