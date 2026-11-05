# P230 — Piloto de distância exata por núcleo

Estado `PROPOSED`, proposta de 2026-11-05. Uma tarefa por ciclo.
Executor solicitado pelo usuário — Gemini Flash 3.8.

[Contrato comum obrigatório](../research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md)

## Dependência e objetivo

P229 aceita e E1 elegível em pré-registro revisado. Entradas e revisão congeladas.

Comparar a enumeração em Gray code com o baseline P221, certificando a mesma distância exata nos seis casos.

## Arquivos permitidos

- `src/evobyte/distance_pilot.py`
- `scripts/run_p230_distance.py`
- `scripts/verify_p230_distance.py`
- `tests/test_distance_pilot.py`
- `docs/research/p230-distance-pilot-report.md`
- `docs/phases/P230-exact-distance-kernel-pilot.md`, somente estado e evidências desta tarefa.

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
git switch -c codex/p230-exact-distance-kernel-pilot origin/main
```

Se já estiver na branch indicada e ela estiver limpa, conferir a base e
continuar nela. Se o nome existir em outra posição ou houver arquivos
locais pendentes, parar com o estado observado.

## Passos da tarefa

1. Ler E1 no documento de experimentos e o manifesto P229. Usar somente
   `distance_cases` congelados. Conferir tipos, dimensões, suportes e hash.
2. Implementar a enumeração streaming dos dois núcleos em
   `distance_pilot.py`. Usar eliminação GF(2) existente conferida. Manter
   convenção MSB da P221. Um vetor lógico deve comutar com o check oposto
   e estar fora do espaço estabilizador. Guardar peso e testemunha mínimos.
3. Criar `run_p230_distance.py --prereg PATH --out PATH`, com
   `--case` aceitando `all` ou uma das seis chaves do manifesto e
   `--method` aceitando `all`, `reference` ou `kernel`. O padrão dos
   dois seletores é `all`. Uma chamada por caso/método permite isolar RSS.
   Um processo,
   até 30 s e 512 MiB, cinco repetições alternadas por caso. Medir preparo,
   geração, certificação, total, CPU e RSS. Encerrar com saída parcial
   `INCONCLUSIVE` quando o orçamento interno terminar. Erro de integridade
   retorna código não zero. Guardar a revisão/dirty reais.
4. Criar `verify_p230_distance.py --input PATH`, usando somente biblioteca
   padrão e a implementação P221 carregada pelo caminho/hash congelados.
   O verificador reconstrói as matrizes, reexecuta a busca independente e
   confere a testemunha. Não importar `distance_pilot` no checker.
5. O JSON de saída contém `schema_version`, `revision`, `dirty`,
   `prereg_sha256`, `verdict`, `cases` e `metrics`. Cada caso contém a entrada,
   ranks, k, d, setor X/Z, máscara lógica, status de cobertura e tempos.
   O RSS terá unidade e escopo explícitos. O pico global de um processo
   não será atribuído como pico individual de cada caso.
   Campo d fica `null` se a busca incompleta não certificou o mínimo.
6. Testar as seis referências e rejeição de certificado com testemunha
   alterada, dimensão alterada e alegação d alterada. Para entrada fora
   de n ≤ 20, produzir rejeição explícita. A cota inferior sozinha deve
   ser identificada como tal. Esses testes cobrem falsas alegações de exatidão.
7. Rodar os gates. Escrever resultado por caso e custos de baseline/candidato.
   Ganho ausente produz veredito negativo da hipótese, com os dados íntegros.

## Gate específico

```bash
python3 -m pytest tests/test_distance_pilot.py -q
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 scripts/run_p230_distance.py --prereg experiments/p229-preregistration.json --out /tmp/evobyte-p230-result.json
python3 -S scripts/verify_p230_distance.py --input /tmp/evobyte-p230-result.json
```

Aceitar correção exige concordância dos seis casos completados e rejeição
das adulterações. Uma execução parcial deve expor seu status e receber
revisão, sem alegação de ganho conclusivo. O limiar de retenção ≥ 1,2× será
reavaliado por reprodução na P233, sem mudar os valores pré-registrados.
Os dados brutos ficam fora do Git, com tamanho/hash e referência durável
no relatório antes de qualquer promoção de resultado.


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
do PR em `/tmp/evobyte-p230-pr.md`, com resultado, comandos e limites reais.
Conferir a lista abaixo contra o escopo autorizado.

```bash
git diff --check
git add -- src/evobyte/distance_pilot.py \
  scripts/run_p230_distance.py \
  scripts/verify_p230_distance.py \
  tests/test_distance_pilot.py \
  docs/research/p230-distance-pilot-report.md \
  docs/phases/P230-exact-distance-kernel-pilot.md
git diff --cached --check
git diff --cached --stat
git commit -m "feat(verifier): compare exact distance by kernel enumeration"
git push -u origin codex/p230-exact-distance-kernel-pilot
gh pr create --base main --head codex/p230-exact-distance-kernel-pilot \
  --title "feat(verifier): compare exact distance by kernel enumeration" \
  --body-file /tmp/evobyte-p230-pr.md
git status --short
```

Se houver PR aberto para essa branch, atualizar seu corpo com `gh pr edit`
e o mesmo arquivo. O revisor realiza o aceite e a integração.
