# P49 — Congelar uma representação compacta limitada

**Status:** Done.
**Pré-requisito:** P48, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p49-compact-typed-candidates`.
**Resultado:** ACCEPTED — perfil compacto congelado sobre o codec v0 (sem
bump, sem fork, sem ADR: condição não acionada); round-trip 64B, refs
inválidas e versão desconhecida rejeitadas; 4/4 positivos P35 reconstruídos
como o mesmo objeto certificado; cobertura anunciada só da gramática.

## Objetivo e escopo

Congelar uma representação compacta limitada. Alterações permitidas: docs/BYTECODE.md, src/evobyte/bytecode.py, src/evobyte/grammar.py e tests/test_bytecode.py.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Representar candidatos da família escolhida com IDs inteiros, operações permitidas, referências a registradores e constantes racionais limitadas. No início usar o bytecode existente quando suficiente; não criar uma linguagem universal.
2. Definir limites de comprimento, registradores, constantes, tipos/domínios, decodificação e tamanho em bytes. Bump de OPCODE_VERSION somente se mudar a semântica/codec existente; conservar intérprete antigo e aprovar ADR antes da alteração.
3. Gerar estruturas válidas por construção; texto/Lean/SymPy somente na fronteira de certificação. Testar round-trip, referências inválidas, versão desconhecida e reconstrução do certificado.

## Gate de saída

Especificação versionada e testes de codec/conformidade aprovados. Candidato compacto converte para o mesmo objeto matemático certificado; cobertura anunciada é apenas da gramática definida.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P49 --config experiments/p49-config.json --output /tmp/evobyte-p49-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Risco principal

Compacidade não demonstra capacidade de representar toda matemática nem reduz por si só a complexidade da busca.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p49-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p49 compact-typed-candidates"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p49 compact-typed-candidates" --body-file /tmp/evobyte-p49-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
