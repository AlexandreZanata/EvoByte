# P229 — Auditoria das garantias e pré-registro

Estado `PROPOSED`, proposta de 2026-11-05. Uma tarefa por ciclo.
Executor solicitado pelo usuário — Gemini Flash 3.8.

[Contrato comum obrigatório](../research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md)

## Dependência e objetivo

Revisão deste plano, arquivo P222 durável, árvore limpa e base aceita contendo o plano.

Transformar as três propostas em contratos executáveis, registrando exatamente a garantia de cada caminho existente.

## Arquivos permitidos

- `docs/research/p229-guarantee-inventory.md`
- `experiments/p229-preregistration.json`
- `docs/phases/P229-low-compute-audit-preregistration.md`, somente estado e evidências desta tarefa.

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
git switch -c codex/p229-low-compute-audit-preregistration origin/main
```

Se já estiver na branch indicada e ela estiver limpa, conferir a base e
continuar nela. Se o nome existir em outra posição ou houver arquivos
locais pendentes, parar com o estado observado.

## Passos da tarefa

1. Ler o relatório P222, `tests/test_p221_independent_recompute.py`,
   `scripts/verify_bivariate_certificate.py`, `src/evobyte/sat_distance_solver.py`
   e os cinco documentos em `docs/research/next/`.
2. Confirmar o SHA-256 e as 30.285 linhas do arquivo bruto com os comandos
   abaixo. Conferir no resumo os seis exemplos `16_2`, `16_4`, `18_2`,
   `18_4`, `20_2`, `20_4`. Qualquer diferença é parada.
3. No inventário, registrar separadamente posto, comutação, cota inferior,
   testemunha superior, distância exata, independência e novidade de P214,
   P217 e P221. Citar função, condição de entrada e trecho de código.
   Conferir especialmente o ramo CSS n > 20 e o caminho não CSS da P217.
4. Conferir na fonte primária as hipóteses do resultado mais próximo de
   R01, R02 e R08. Registrar URL, versão, proposição/seção, diferença exata,
   confiança e `ELIGIBLE`, `KNOWN_BASELINE` ou `REJECTED`. Texto inacessível
   fica como lacuna de acesso, que impede liberar a alegação correspondente.
   Para semântica formal de circuitos, registrar uma referência de VyZX/VOQC
   efetivamente lida se houver proposta de prova formal nova.
5. Criar o JSON de pré-registro com `schema_version=1`, `state=PROPOSED`,
   `source_revision`, `input_sha256`, `bit_order=msb_column_zero`,
   `distance_cases` com os seis exemplos completos, `decomposition_limit=128`,
   `circuit_alphabet`, `max_word_length=6`, `baseline_ids`, `budgets`,
   `metrics`, `repetitions=5`, `retention_ratio=1.2` e `literature_dispositions`.
   Usar valores medidos/lidos e escrever o motivo das pendências no inventário.
6. Congelar para cada piloto a pergunta, domínio, fonte do baseline,
   garantia, limiares de decisão, política de timeout e diferença metodológica.
   Reproduções de fatos conhecidos serão classificadas como calibração ou
   engenharia. A liberação científica depende da diferença e revisão.
7. Encerrar com o inventário e pré-registro propostos para revisão. A P229
   é documental. O revisor identifica os pilotos elegíveis antes da P230.

## Gate específico

```bash
sha256sum experiments/p222-bb-census.json
wc -l experiments/p222-bb-census.json
python3 -m json.tool experiments/p229-preregistration.json > /tmp/evobyte-p229-preregistration.txt
```

O hash esperado é
`623474978937de805bce0b0588d17307b5f8f3d629c3dbb8a8cdcf5722340509`.
Validar manualmente os campos contra o contrato acima. Para aceitar a tarefa,
o inventário deve conter três disposições bibliográficas, as seis entradas
congeladas e o escopo de garantia dos três caminhos históricos. Ausência de
uma lacuna pode gerar `REJECTED` para um piloto e fechar corretamente a auditoria.


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
do PR em `/tmp/evobyte-p229-pr.md`, com resultado, comandos e limites reais.
Conferir a lista abaixo contra o escopo autorizado.

```bash
git diff --check
git add -- docs/research/p229-guarantee-inventory.md \
  experiments/p229-preregistration.json \
  docs/phases/P229-low-compute-audit-preregistration.md
git diff --cached --check
git diff --cached --stat
git commit -m "docs(research): audit guarantees and preregister low-compute pilots"
git push -u origin codex/p229-low-compute-audit-preregistration
gh pr create --base main --head codex/p229-low-compute-audit-preregistration \
  --title "docs(research): audit guarantees and preregister low-compute pilots" \
  --body-file /tmp/evobyte-p229-pr.md
git status --short
```

Se houver PR aberto para essa branch, atualizar seu corpo com `gh pr edit`
e o mesmo arquivo. O revisor realiza o aceite e a integração.
