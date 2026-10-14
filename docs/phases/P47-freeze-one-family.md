# P47 — Congelar uma família e o primeiro experimento

**Status:** Built — pending human mathematical review (P48 blocked).
**Pré-requisito:** P46, com as rotas negativas explícitas do runbook.
**Branch:** `codex/p47-freeze-one-family`.
**Resultado:** nominação congelada (hash `18af5df9…`, auto-excluído) com dois
escopos, hipótese pré-fixada sem MSE, 3 controles conhecidos + 4 falsos,
splits congelados por política, teste final novo fechado (log vazio, 10 ids
P38 proibidos); veredito técnico PENDING_HUMAN_REVIEW — nominação, limiares
e curadoria P46 aguardam aprovação matemática humana.

**Continuidade atual:** Nominação histórica incompleta; D019/P58 exclui seu uso como pré-registro vigente e P60 entrega uma nova.

## Objetivo e escopo

Congelar uma família e o primeiro experimento. Alterações permitidas: experiments/p47-nomination.json, docs/research/nomination.md e benchmarks/science_matrix.py.
Fora de escopo: outras fases, mudança não registrada de hipótese, dados
históricos reescritos e promoção automática de descoberta.

Leia [o runbook](../FORMAL_SEARCH_PLAN.md) antes de implementar. Ele define
gates comuns, limites, esquema de evidência e rotas negativas. Executar uma
microtarefa por ciclo; não implementar todas as fases neste PR.

## Trabalho ordenado

1. Fixar dois escopos separados: desenvolvimento do proponente em polynomial_arithmetic sobre ℚ; campanha científica posterior em instâncias limitadas de Erdős–Straus. Reusar infraestrutura não estabelece transferência do modelo entre essas famílias.
2. Definir controles conhecidos, domínio, limites, representação, certificado, baselines clássicos, agrupamento antileak e sucesso por tarefa. Pré-fixar hipótese: melhoria de sucesso certificado ou tempo até certificado sob custo total equivalente; não usar MSE como sucesso.
3. Congelar splits antes de treinamento: fonte original e equivalências/variações do mesmo alvo ficam no mesmo grupo. Teste final novo tem armazenamento e log de acesso persistentes; o teste P38 já observado não é reutilizado. Nominação e limiares exigem revisão matemática humana.

## Gate de saída

Manifesto integral aprovado, hash congelado, controles conhecidos e falsos definidos, nenhum grupo atravessando splits, teste final ainda fechado. Toda mudança de família ou hipótese exige nova nominação antes dos resultados.

Aplicar os gates comuns e a aceitação desta fase. A chamada abaixo é um
**contrato futuro a implementar**, não um comando já existente:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
python3 benchmarks/science_matrix.py --acceptance-phase P47 --config experiments/p47-config.json --output /tmp/evobyte-p47-acceptance.json
```

Guardar configuração completa, comando real e artefato recuperável. Uma
fase técnica mede sua condição técnica; não fabrica números de velocidade.
Revisão científica, quando exigida acima, antecede a promoção do resultado.

## Uso histórico na continuidade D019

Esta nominação tem valores de limiar pendentes e seu final foi consumido pela
P56. Preservar JSON, selo e log; o estado fechado é o registro original.
Não editar esses artefatos para inventar pré-registro ou aprovação prévia.
P58 deve registrar `excluded_from_claims` como pré-registro vigente. Uma nova
nominação, com valores, fontes, grupos, censura, desfecho e revisão resolvidos,
é entregue em P60 antes de medir. A aprovação do uso histórico restrito permite
reconciliar a base sem aprovar a hipótese antiga nem herdar seus limiares vazios.
Aplicar [D019](../FORMAL_SEARCH_PLAN.md#correção-de-atuação-e-continuidade-técnica-d019).

## Risco principal

Um agente econômico implementa a nominação; não decide sozinho quais problemas são cientificamente inéditos.

## Commit & Push (obrigatório)

Começar de árvore limpa na branch declarada, a partir do predecessor aceito.
Stage apenas caminhos revisados com `git add` explícito. Escrever
`/tmp/evobyte-p47-pr.md` com problema, mudança, comandos reais, resultados,
artefatos e limitações. Todos os gates precisam estar verdes antes deste
bloco. Se esta fase precisar de subentregas, cada uma tem commit próprio e
não marca a fase inteira Done. Não executar merge automático.

```bash
git diff --cached --check
git commit -m "feat(research): implement p47 freeze-one-family"
git push -u origin HEAD
gh pr create --base main --title "feat(research): implement p47 freeze-one-family" --body-file /tmp/evobyte-p47-pr.md
git status --short
```

Usar main somente se o predecessor já estiver integrado; caso contrário,
usar sua branch aceita como base do PR e registrar a dependência. Nunca
push direto à main, force-push ou bypass de hooks.
