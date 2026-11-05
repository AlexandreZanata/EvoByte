# P231 — Piloto de decomposição BB certificada

Estado `PROPOSED`, proposta de 2026-11-05. Uma tarefa por ciclo.
Executor solicitado pelo usuário — Gemini Flash 3.8.

[Contrato comum obrigatório](../research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md)

## Dependência e objetivo

P229 aceita, E2 elegível e argumento matemático revisado. Fase anterior encerrada e revisão autorizando esta tarefa.

Certificar a transformação de checks em blocos idênticos e medir o trabalho de verificação evitado.

## Arquivos permitidos

- `src/evobyte/bb_decomposition.py`
- `scripts/run_p231_decomposition.py`
- `scripts/verify_p231_decomposition.py`
- `tests/test_bb_decomposition.py`
- `docs/research/p231-decomposition-report.md`
- `docs/phases/P231-certified-subgroup-decomposition.md`, somente estado e evidências desta tarefa.

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
git switch -c codex/p231-certified-subgroup-decomposition origin/main
```

Se já estiver na branch indicada e ela estiver limpa, conferir a base e
continuar nela. Se o nome existir em outra posição ou houver arquivos
locais pendentes, parar com o estado observado.

## Passos da tarefa

1. Ler E2 e o pré-registro P229. A demonstração das permutações precisa
   de revisão anterior à implementação. Uma lacuna no argumento é parada.
2. Ler em streaming os 128 primeiros registros do arquivo P222 validado por
   hash. Construir o subgrupo das diferenças de suporte por fecho aditivo.
   Escrever índices de cosets e permutações completas de linhas e colunas.
3. Usar as fórmulas de normalização descritas em E2. Conferir HX e HZ por
   igualdade exata após a transformação. Certificar blocos idênticos e
   preservar a massa de Hamming por permutações. Tratar k0=0 separadamente.
4. Criar `run_p231_decomposition.py --prereg PATH --input PATH --out PATH`,
   com `--method` em `all`, `reference` ou `decomposition`, padrão `all`,
   com teto interno de 30 s, 512 MiB e um processo. Comparar o custo de
   verificação completa com transformação+checker+verificação de um bloco.
   Registrar também casos sem redução e custos perdidos.
5. Criar `verify_p231_decomposition.py --input PATH`. Reconstruir matrizes
   por caminho independente e conferir que cada índice aparece uma vez,
   as identidades de matrizes e os ranks. Usar componentes por BFS como
   controle da partição. Não importar a lógica geradora de decomposição.
6. A saída JSON contém entrada/hash, permutações, blocos, t, k0, k,
   garantia de distância, tempos e veredito. Testar permutação duplicada,
   índice fora do intervalo, bloco desigual e deslocamento de HZ adulterado.
   Reconfirmar as seis referências de E1 por P221, dentro do orçamento.
7. Relatar `NO_APPLICABLE_REDUCTION` se nenhum caso do lote se decompor.
   Essa observação encerra o recorte. Uma divergência entre a fórmula e as
   matrizes interrompe a tarefa para revisão matemática.

## Gate específico

```bash
python3 -m pytest tests/test_bb_decomposition.py -q
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 scripts/run_p231_decomposition.py --prereg experiments/p229-preregistration.json --input experiments/p222-bb-census.json --out /tmp/evobyte-p231-result.json
python3 -S scripts/verify_p231_decomposition.py --input /tmp/evobyte-p231-result.json
```

A correção exige identidades exatas de ambos os checks, ranks compatíveis
e rejeição das adulterações. A retenção do método exige economia líquida
reproduzível, incluindo o checker. A decomposição e a métrica são
classificadas separadamente da avaliação de novidade.


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
do PR em `/tmp/evobyte-p231-pr.md`, com resultado, comandos e limites reais.
Conferir a lista abaixo contra o escopo autorizado.

```bash
git diff --check
git add -- src/evobyte/bb_decomposition.py \
  scripts/run_p231_decomposition.py \
  scripts/verify_p231_decomposition.py \
  tests/test_bb_decomposition.py \
  docs/research/p231-decomposition-report.md \
  docs/phases/P231-certified-subgroup-decomposition.md
git diff --cached --check
git diff --cached --stat
git commit -m "feat(algebra): certify subgroup decomposition of small bb codes"
git push -u origin codex/p231-certified-subgroup-decomposition
gh pr create --base main --head codex/p231-certified-subgroup-decomposition \
  --title "feat(algebra): certify subgroup decomposition of small bb codes" \
  --body-file /tmp/evobyte-p231-pr.md
git status --short
```

Se houver PR aberto para essa branch, atualizar seu corpo com `gh pr edit`
e o mesmo arquivo. O revisor realiza o aceite e a integração.
