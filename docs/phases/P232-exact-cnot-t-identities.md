# P232 — Piloto de identidades CNOT+T exatas

Estado `PROPOSED`, proposta de 2026-11-05. Uma tarefa por ciclo.
Executor solicitado pelo usuário — Gemini Flash 3.8.

[Contrato comum obrigatório](../research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md)

## Dependência e objetivo

P229 aceita e E3 elegível após auditoria de redundância. Fase anterior encerrada e revisão autorizando esta tarefa.

Testar uma busca em classes semânticas de palavras pequenas e certificar as identidades extraídas.

## Arquivos permitidos

- `src/evobyte/cnot_t_pilot.py`
- `scripts/run_p232_circuit.py`
- `scripts/verify_p232_circuit.py`
- `tests/test_cnot_t_pilot.py`
- `docs/research/p232-circuit-report.md`
- `docs/phases/P232-exact-cnot-t-identities.md`, somente estado e evidências desta tarefa.

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
git switch -c codex/p232-exact-cnot-t-identities origin/main
```

Se já estiver na branch indicada e ela estiver limpa, conferir a base e
continuar nela. Se o nome existir em outra posição ou houver arquivos
locais pendentes, parar com o estado observado.

## Passos da tarefa

1. Ler E3 e o pré-registro. Fixar ordem `CX01,CX10,T0,T1,TDG0,TDG1`,
   dois qubits, comprimento 0..6, sem ancillas. A soma do domínio é 55.987.
2. Implementar a ação binária reversível e as quatro fases em Z/8Z como
   chave de semântica. Guardar o melhor custo `(T,CX,length)` e palavra
   lexicograficamente mínima. Contar palavras visitadas e classes distintas.
3. Criar `run_p232_circuit.py --prereg PATH --out PATH`, com `--method`
   em `all`, `reference` ou `semantic`, padrão `all`. O controle
   `reference` calcula a ação exata em quatro estados para cada palavra
   completa. `semantic` reaproveita a ação do prefixo da palavra e agrupa
   o resultado. Ambos enumeram o mesmo domínio neste primeiro piloto.
   Usar teto interno
   de 30 s, 512 MiB e um processo. Controlar cobertura pelo domínio bruto
   enumerado. A poda só é permitida com regra de preservação documentada.
4. Implementar o baseline local exato congelado na P229. Relatar os pares
   que melhoram esse baseline e o custo do circuito extraído. Uma identidade
   conhecida pode entrar como calibração identificada.
5. Criar `verify_p232_circuit.py --input PATH` com biblioteca padrão.
   Multiplicar matrizes 4×4 sobre Z[zeta8] com quatro coeficientes inteiros
   por entrada, reduzindo `zeta8**4 = -1`. Esse caminho não importa a chave
   semântica da busca. Conferir fase global e contagem de portas.
6. Testar identidade vazia, CX²=I, T·TDG=I, T⁸=I como unidades de controle
   mesmo quando o comprimento de teste ultrapassar o limite da busca.
   Testar rejeição de uma porta adulterada e da contagem de custo incorreta.
7. O JSON contém alfabeto, comprimento máximo, total esperado/visitado,
   `coverage_complete`, classes, identidades, custos, tempos e veredito.
   Minimalidade no domínio exige cobertura completa. Esgotamento do teto
   recebe `INCONCLUSIVE`. Escrever o relatório sem ampliar o comprimento.

## Gate específico

```bash
python3 -m pytest tests/test_cnot_t_pilot.py -q
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 scripts/run_p232_circuit.py --prereg experiments/p229-preregistration.json --out /tmp/evobyte-p232-result.json
python3 -S scripts/verify_p232_circuit.py --input /tmp/evobyte-p232-result.json
```

A correção exige equivalência independente de todos os pares entregues,
contagem coerente do domínio e rejeição das adulterações. A retenção
exige ganho após extração e diferença em relação ao baseline congelado.
Novidade de uma regra requer revisão bibliográfica humana específica.


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
do PR em `/tmp/evobyte-p232-pr.md`, com resultado, comandos e limites reais.
Conferir a lista abaixo contra o escopo autorizado.

```bash
git diff --check
git add -- src/evobyte/cnot_t_pilot.py \
  scripts/run_p232_circuit.py \
  scripts/verify_p232_circuit.py \
  tests/test_cnot_t_pilot.py \
  docs/research/p232-circuit-report.md \
  docs/phases/P232-exact-cnot-t-identities.md
git diff --cached --check
git diff --cached --stat
git commit -m "feat(circuits): certify exact identities for small cnot t words"
git push -u origin codex/p232-exact-cnot-t-identities
gh pr create --base main --head codex/p232-exact-cnot-t-identities \
  --title "feat(circuits): certify exact identities for small cnot t words" \
  --body-file /tmp/evobyte-p232-pr.md
git status --short
```

Se houver PR aberto para essa branch, atualizar seu corpo com `gh pr edit`
e o mesmo arquivo. O revisor realiza o aceite e a integração.
