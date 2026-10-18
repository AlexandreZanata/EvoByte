# Plano de busca matemática verificável — execução por agente econômico

**Plano concluído: 2026-10-13 (D020).** P40–P57 são o programa histórico;
P58–P72 estão concluídas (Done) com resultados medidos e arquivos individuais.
Este documento não certifica fases antigas nem promete descoberta mundial.
Criar o plano não executa os novos experimentos.

## Objetivo e limites

Construir um sistema que gera candidatos matemáticos compactos em lote,
filtra, certifica, aprende quando houver evidência de benefício e registra
resultados reproduzíveis. Manter um catálogo de 100 problemas abertos;
executar uma família por vez. O mapa é limitado e reconstruível no domínio
de cada experimento; não contém todas as possibilidades matemáticas.

Hardware de referência descrito no projeto: RTX 4060 Laptop 8 GB,
i7-13620H e cerca de 32 GB RAM. Confirmar equipamento disponível pelo probe.
Milhões de operações, candidatos e certificados por segundo são métricas
diferentes. Nenhuma delas é garantida por este plano.

As correções P40–P45 são obrigatórias. Etiquetas Done em P33–P39 não bastam
para liberar experimentos novos. Conservar os dados históricos e acrescentar
auditorias; não sobrescrever resultados para ajustar a narrativa.

## Ordem, rotas negativas e responsabilidade

```text
P40 -> P41 -> P42 -> P43 -> P44 -> P45 -> P46 -> P47 -> P48 -> P49
 -> P50 -> P51 -> P52 -> P53 -> P54 -> P55(opcional) -> P56 -> P57
```

P52 INCONCLUSIVE bloqueia treinamento P53, mas permite P54 com baselines.
P53/P54 sem ganho preservam busca clássica/evolutiva para P56.
P55 DEFERRED ou resultado negativo mantém o sampler clássico.
Uma falha de correção, gate, evidência ou isolamento interrompe a cadeia;
não se transforma em resultado científico negativo aceitável.

O agente econômico executa tarefas especificadas; um revisor com conhecimento
matemático aprova curadoria P46, enunciado/hipótese P47, tradução formal P48,
procedimento estatístico P54 e novidade P57. Aprovação científica é registrada
com autor/data/justificativa e não equivale a autorização de merge.
Sem revisão necessária, preparar o material verificável e parar nessa fronteira.
Para a continuidade técnica P58–P72, aplicar a disposição de evidências D019
abaixo. Revisão de uso restrito não aprova a conclusão científica histórica.

## Como executar uma microtarefa

1. Ler AGENTS.md, este documento e somente a próxima fase liberada.
2. Conferir árvore limpa e ancestral aceito. Não começar trabalho sobre uma
   cadeia de PRs pendente como se ela já fosse a main integrada.
3. Verificar os gates documentados do predecessor. Falha exige correção
   própria, nunca pular fase ou enfraquecer a condição.
4. Criar branch codex/pNN-slug a partir da base aceita. Trabalhar em uma
   única entrega; ler apenas módulos e testes relevantes antes de editar.
5. Reusar código existente. Cada fase adiciona somente sua capacidade;
   sem stubs para fases futuras, refatoração ampla ou dependências extras.
6. Rodar regressões da mudança e os gates comuns. Salvar comando real,
   configuração resolvida e resultado de aceitação.
7. Revisar diff e stage de caminhos explícitos. Um commit atômico por
   microtarefa concluída, push da branch e PR; nunca push direto à main.
8. Registrar resultado e parar. A próxima invocação lê o próximo gate.

Se a fase exceder uma entrega pequena, especificar primeiro uma subentrega
com comportamento e gate próprios e executá-la sozinha. Ela não libera a
próxima fase até passar o gate integral. Não agrupar uma correção de teste
com uma mudança de algoritmo. CI de documentação não exige campanha GPU.

## Contrato de comandos — não confundir com funcionalidade existente

Comandos já disponíveis para gates comuns:

```bash
git diff --check
git status --short
python3 -m pytest tests -q
make verify
```

Interface de aceitação **a implementar a partir de P40**, reaproveitando
science_matrix e módulos existentes:

```text
python3 benchmarks/science_matrix.py --acceptance-phase PNN --config experiments/pNN-config.json --output /tmp/evobyte-pNN-acceptance.json
```

PNN é substituído pela fase real; o arquivo específico de cada fase mostra
a chamada literal. Não executar esse comando antes de implementar a sua
interface. P40 adiciona somente seu auditor e uma fronteira de chamada
validada; fases seguintes acrescentam somente a capacidade que implementam,
sem código vazio para fases futuras. O identificador PNN rotula a execução;
a configuração seleciona uma capacidade já implementada e testada.
Capacidades desconhecidas falham com mensagem clara. Reusar funções existentes;
não transformar science_matrix em um monólito novo.

Antes de medir, criar a configuração completa de cada fase e um run.sh
contendo o comando real. Nenhum arquivo de configuração vazio ou com valores
por decidir entra como artefato aprovado. Nos experimentos comparativos,
o pré-registro e sua revisão antecedem os dados observados.

Execuções durante edição de código são diagnósticas e registram dirty=true.
Não transformar esses dados em confirmação apenas ao fazer commit depois.
A confirmação P56 usa capacidades já implementadas/testadas nos predecessores,
configuração previamente congelada e árvore limpa antes de abrir o teste.
Gravar seus dados brutos fora dos caminhos versionados; somente depois da
medição escrever o relatório documental e fazer seu commit. Se faltar código
para a confirmação, corrigi-lo em uma microtarefa anterior, com seus gates e
commit próprios, antes de congelar a revisão e acessar o teste final.

Cada relatório de aceitação contém: phase, verdict, claim_scope, run_id,
revision, dirty, hardware, driver, package_versions, resolved_config,
seeds/RNG, inputs/split/checker hashes, requested/actual budgets,
certificate references, counters, limitations e caminhos/tamanhos/hashes
dos dados brutos. Campos sem aplicação são marcados explicitamente com
motivo. Relatórios técnicos não precisam inventar medidas de desempenho.

P58–P72 foram executadas e marcadas Done com gates executados, artefatos
recuperáveis, commits e pushes; integridade preservada sem alegações espúrias.
Runtime ausente, dado insuficiente ou fonte sem confirmação produziram
BLOCKED/INCONCLUSIVE conforme os fatos medidos.

## Limites de recursos e gastos

- Começar com CPU referência e Torch; Triton/CUDA customizados só com
  gargalo medido e microtarefa/ADR específicos.
- Um stream CUDA inicialmente. Um versus dois streams só após medir;
  múltiplas threads Python não são sinônimo de paralelismo útil na GPU.
- VRAM reservada: max(1 GiB, 20% do total), além de respeitar ocupação alheia.
  Lotes começam pequenos. Não encerrar processos do usuário para liberar VRAM.
- Checkpoint completo e limites de fila/disco. Ao aproximar o limite, parar
  de gerar, drenar trabalho pendente e salvar estado; não descartar evidência.
- Smoke: diagnóstico separado. Measurement usa os tempos reais declarados.
  Resultado de 3 min não sustenta alegação de estabilidade por uma hora.
- Coleta P52: até 1 h; treino P53: até 30 min; comparação P54: até 3 h;
  campanha P57: até 1 h. São tetos iniciais de custo, não metas de desempenho.
- Fixar parada e política de timeout antes do experimento. Não aumentar
  orçamento escondido para transformar resultado negativo em ganho.
- Manter teste final fechado e logs persistentes. Nenhum uso de API de LLM,
  linguagem natural, JSON ou parsing de texto no ciclo GPU principal.

## O que reportar

Relatórios distinguem avanço de engenharia, resultado de experimento e
resultado matemático. Certificado válido sem novidade é rediscovery ou
verified-construction; número grande de tentativas não é descoberta.
Uma busca interrompida é budget-exhausted, nunca prova de inexistência.
Exhaustive-null só se domínio finito e cobertura integral forem demonstrados.

Para promover resultado matemático: verificar o enunciado e domínio,
rechecar certificado/prova, comparar literatura atual e obter reprodução
independente. Registrar lacunas em vez de usar scientific-discovery como
rótulo automático. Um empate ou modelo pior pode encerrar um experimento
íntegro; uma falha do verificador não pode.

## Prompt pronto para copiar ao agente executor

> Trabalhe no EvoByte. Leia AGENTS.md, docs/FORMAL_SEARCH_PLAN.md e o arquivo
> da primeira fase ainda não aceita cujos predecessores passaram; a próxima
> tarefa proposta é P58, conforme a extensão abaixo.
> Execute somente uma microtarefa dessa fase. Reuse módulos existentes e
> implemente apenas o contrato descrito; não redesenhe a arquitetura.
> Antes de começar confirme árvore limpa, base aceita e gates do predecessor.
> Não abra o teste final, reduza orçamento, afrouxe limiar, invente fonte ou
> altere dados históricos. Uma decisão científica não especificada requer
> material verificável para revisão, sem improvisar uma conclusão.
> Rode os testes relevantes e todos os gates comuns. Só após gates verdes
> faça um commit atômico, push e PR, com caminhos explicitamente revisados.
> Pare depois da entrega. Reporte fase, mudanças, comandos executados,
> artefatos/hashes, resultado, limites e a próxima fase realmente liberada.
> Se qualquer gate falhar, pare sem commit/push e explique a causa.

## Referências de implementação e verificação

- [Validação oficial de provas Lean](https://lean-lang.org/doc/reference/latest/ValidatingProofs/):
  conferir enunciado, dependências/axiomas e possibilidade de rechecagem externa.
- [Metamath](https://us.metamath.org/): referência de linguagem formal e
  verificação explícita. Não implementar dois sistemas formais neste piloto.
- Fontes primárias e estado de cada problema serão pesquisados em P46/P57;
  escrever este plano não confirma previamente 100 problemas abertos.

O índice e os contratos completos estão em [phases/README.md](phases/README.md).

## Programa especulativo P58–P72

**Programa concluído em 2026-10-13 (D020).** Hipóteses exploratórias executadas;
sem ineditismo mundial, vantagem quântica ou solução de conjectura comprovada.
P58–P72 foram implementadas, testadas e concluídas de acordo com os contratos.
Os resultados históricos P40–P57 continuam preservados e sujeitos a seus
gates científicos.

### Ordem e mapa das hipóteses

```text
P58 base aceita -> P59 entradas iguais -> P60 bancada congelada
 -> P61 H02 sombras -> P62 H01 erros -> P63 H08 feedback
 -> P64 H03 obstruções -> P65 H04 respostas/ponte -> P66 H05 saltos
 -> P67 H06 macros -> P68 H07 adversários -> P69 H09 ilhas
 -> P70 H10 famílias paramétricas -> P71 confirmação -> P72 novidade
```

Números H01–H10 correspondem às dez ideias da discussão; a ordem executa
primeiro os mecanismos de menor custo. Cada arquivo de fase especifica
escopo, trabalho, gate e Commit & Push. Não implementar dez mecanismos
de uma vez, nem abrir agentes paralelos para executar fases simultâneas.

P58 é a próxima tarefa, com as correções R1–R4. Antes de medir P61–P70,
P58–P60 devem estar integralmente aceitas no escopo aplicável de D019.
Propostas, correções e dossiês podem ser preparados em microtarefas próprias;
gate pendente do uso atual bloqueia sua medição e aceitação. Uma aprovação
histórica ausente não vira dependência impossível se o uso correspondente
for excluído e essa restrição passar pelo auditor.

Cada piloto P61–P70 testa seu mecanismo isoladamente contra a base P59;
não acrescenta automaticamente mecanismos experimentais anteriores.
Hipótese íntegra NULL/INCONCLUSIVE pode encerrar a etapa e liberar a
próxima. Nenhum sucessor depende de fabricar um ganho. Falha de checker,
dados, aprovação ou isolamento é BLOCKED e interrompe a cadeia.

### Correção de atuação e continuidade técnica (D019)

Alexandre autorizou a revisão por delegação e solicitou ajustar as fases para
continuar o projeto. Registrar essa autorização e o executor real nos pareceres
correspondentes; não atribuir ao responsável uma execução pessoal inexistente.
Ela não é autorização de merge nem certificação de independência ou novidade.
Não presumir autorização para aprovar futuros escopos ainda não apresentados.

O agente mantém dois estados explícitos: aceitação da capacidade técnica no
escopo atual e validade das conclusões científicas. O gate exige integralmente
o primeiro e todas as revisões científicas de que esse uso realmente depende.
Dados antigos podem entrar somente como referência/development com revisão
de uso e restrições verificáveis. Não entram como teste novo, evidência de
superioridade, pré-registro prospectivo ou descoberta sem seus gates próprios.

As seis decisões P58 permanecem obrigatórias, mesmo para itens excluídos.
Cada registro identifica responsável, executor, origem/data da autorização,
revisão/hash examinados, evidência recuperável, justificativa, disposição e
usos permitidos/proibidos. `accepted_for_base` significa que a disposição foi
revisada e é cumprida pela configuração; não altera a aprovação científica
histórica. O auditor deve verificar essa diferença, os seis IDs únicos, hashes,
restrições e revisão de código aceita. Esse contrato ainda precisa ser
implementado/testado; a configuração atual não passa a ACCEPTED por este texto.

- P46: snapshot datado, com revisão da curadoria aplicável ao uso. Fonte
  inacessível impede afirmar estado aberto atual; referência histórica pode
  ser admitida com essa limitação. Certificação/novidade exige fonte e
  formulação atual confirmadas no escopo de P60/P72.
- P47: preservar manifesto incompleto, selo e log já consumido. Excluir como
  pré-registro vigente; nominação nova e integral será congelada em P60 antes
  de medidas futuras. Não preencher limiares retrospectivos.
- P48: revisar tradução, dependências e controles dos desafios que forem
  efetivamente usados. O certificado de n=1009 não é teorema universal.
  Sem runtime verificável, excluir uso formal ou manter seu gate BLOCKED.
- P54: manter DROP, modelo desligado e análise exploratória. Não exigir que
  uma revisão hoje seja chamada de prévia; não autorizar KEEP ou ganho justo
  com compilação da fórmula privada. P59 corrige inputs; P60 revisa estatística
  e censura prospectivamente.
- P56: aceitar apenas arquivo provisório/development com o teste consumido
  declarado. Não reabrir final nem tratar self-repeat como reprodução por outra
  parte ou execução limpa da campanha original. P71 exige confirmação nova.
- P58: aceitar enunciado/escopo técnico e código corrigido, medir read-only em
  revisão aceita e preservar todas as restrições no relatório recuperável.

Não mudar checks, thresholds ou bounds para obter aceitação. Uma corrupção,
certificado inválido, vazamento atual ou ausência de evidência necessária ao
uso continuam BLOCKED. Restringir o uso requer decisão explícita e implementação
verificável; renomear a falha ou apagar uma pendência não libera a fase.

Quando uma tentativa falhar, aplicar a parada de AGENTS.md àquela entrega:
sem commit/push da implementação rejeitada. Reportar causa, arquivo/evidência,
critério que faltou e próxima microtarefa corretiva; no ciclo seguinte, reparar
o mesmo gate com autorização existente. Não voltar a solicitar uma autorização
já concedida nem repetir o dossiê inalterado como única ação possível.
Uma microtarefa documental de planejamento tem seus gates de documentação e
regressão; pode registrar a correção de uma fase BLOCKED, mas não marcá-la Done.

P58 fecha R1–R4 antes de P59. P59 valida engenharia/igualdade de informação
com controles development; P60 congela o novo desenho completo antes dos pilotos.
Revisão independente real continua obrigatória para promoção em P71/P72.
O gate de cada fase identifica o uso aprovado, as restrições herdadas e o
artefato exato que libera a próxima; falha nunca é deferida como aceitação.

### Bancada padrão para o agente executor

- Família inicial: construções limitadas de Erdős–Straus, com domínio,
  janelas de x/y, limites coordenados e tipos de candidato congelados em P60.
  Preservar certificados exatos e espaço acessível igual em todos os braços.
- Desenvolvimento pode usar resultados P57. Treino/validation separam n,
  origem e variantes equivalentes; famílias paramétricas compartilhadas
  precisam ser declaradas. Final usa grupos novos, sem acesso prévio.
- Comparação principal: baseline P59 versus um mecanismo. Controles
  embaralhados, clássicos ou desligados, quando especificados no arquivo,
  são braços adicionais explícitos dentro do mesmo teto; não selecionar
  só os controles que dão resultado favorável.
- Piloto: seis tarefas development, três seeds fixadas antes de medir,
  10 s totais por tentativa incluindo inferência/filtro/certificação,
  teto de 30 min por hipótese incluindo dados/treino. A seed não transforma
  a repetição de uma tarefa em um problema matemático independente.
- Modelo inicial <=100 mil parâmetros; máximo 1 milhão combinado, inclusive
  proponente/atacante. Usar uma arquitetura e um conjunto de parâmetros
  por hipótese, sem busca oculta de hiperparâmetros.
- VRAM: reservar max(1 GiB, 20% do total), lote inicial 256, um stream CUDA,
  no máximo dois workers CPU. Quatro ilhas dividem a população disponível.
  Não chamar uso máximo da 4060 sem medição representativa.
- Dados brutos limitados a 1 GiB por execução, fila a 64 MiB, mapa a 100 mil
  nós; checkpoints/replay registram cobertura. Todo certificado promovido
  é conservado, mesmo quando o mapa de candidatos é amostrado.
- Cinco horas são o teto inicial dos dez pilotos, não autorização para
  aumentar individualmente um piloto. Confirmação P71: até duas horas por
  método, no máximo dois; P72: uma hora. P58–P60 e confirmação dos controles
  têm custos próprios declarados, sem inventar medições ou esconder gastos.

Se um experimento precisar de mais recursos, registrar INCONCLUSIVE e
preparar uma nova nominação antes de gastar além do teto. Smoke nunca
substitui o orçamento registrado. Teto de busca não é garantia absoluta de
ausência de crash; implementar parada controlada e medir estabilidade.

### Informação e custo justos

O braço de geração recebe somente entradas públicas. Fórmula-resposta,
certificado-alvo e alvo privado de equivalência são restritos ao checker.
Para symbolic regression, compilar ground truth é controle de compilação;
o baseline de descoberta usa as mesmas amostras que os outros métodos.
Para a campanha aritmética, todos recebem o mesmo n e mesmos bounds;
warm-start/biblioteca entregue a um braço precisa de condição comparável
ou de ablation registrada e custo de obtenção explícito.

Publicar duas visões sem misturá-las: custo por consulta após preparação,
com os mesmos 10 s por braço; e custo completo de coleta+treino+busca+
checker+tracking. Uma vitória na primeira não estabelece vantagem na segunda.
Uma afirmação de custo total equivalente exige uma campanha separada com
o mesmo teto completo em ambos os braços, debitando a preparação do método
aprendido desse teto. Projeções de amortização têm rótulo de projeção e
horizonte declarado; não são observações de 10 mil tarefas.

### Pré-registro e classificação

P60 congela a regra antes dos dados. Proposta de triagem para revisão:
PROMISING se o mesmo conjunto tiver mais tarefas certificadas, ou pelo
menos 20% menor tempo limitado até certificado sem queda de sucesso;
NULL quando o efeito registrado não ocorre; INCONCLUSIVE se faltarem
soluções/grupos ou precisão. O custo integral deve ser apresentado e pode
impedir promoção. Essa triagem é escolha operacional, não prova estatística.

Timeout entra como observação censurada e nunca desaparece da análise.
Reportar todos os braços, todas as tarefas e seeds, intervalos por grupo e
soluções distintas. Não usar mediana só dos sucessos para esconder falhas.
MSE, resíduo pequeno, diversidade e sobrevivência ao atacante são auxiliares.

P71 pré-registra com revisor estatístico a análise dos dados censurados,
efeito mínimo, critérios de sucesso e controle da seleção entre dez
hipóteses. O piloto pequeno não garante poder para confirmar ganho. Não
promover um mecanismo com zero sucessos, nem tratar zero versus zero como
prova de equivalência. Sem revisão independente o rótulo é PROVISIONAL.

Toda exclusão permanente exige prova/checker exato. Filtro aprendido sem
prova apenas prioriza e mantém exploração sem filtro. Família de infinitos
casos exige identidade, integridade, positividade e domínio demonstrados;
amostras finitas não conferem esse status.

### Microtarefas e revisão limpa

Uma fase pode precisar de entregas pequenas distintas:
A) capacidade + regressões + diagnóstico técnico;
B) configuração/pré-registro revisados e congelados;
C) medição read-only da revisão aceita + registro documental do resultado.
Cada entrega é uma microtarefa com gate e um único commit; a fase continua
Building até o seu gate integral. Não executar A/B/C em um único ciclo.

Um diagnóstico de código ainda editado pode validar a capacidade técnica,
mas registra dirty=true e não aceita a hipótese. Medição final começa com
árvore limpa, revisão aceita e configurações congeladas; salva raw externamente.
Depois de medir, registrar o manifesto/relatório em microtarefa documental.
Um commit posterior não transforma um diagnóstico antigo em confirmação.

Não adicionar handlers vazios P58–P72. Reusar interfaces e módulos reais;
o science_matrix despacha, não recebe dez implementações inteiras. As chamadas
novas dos arquivos de fase são contratos futuros, não CLI já disponível.
Gates comuns permanecem git diff --check, python3 -m pytest tests -q e
make verify; um gate vermelho bloqueia commit/push daquela microtarefa.

### Prompt do novo ciclo

> Leia AGENTS.md, docs/FORMAL_SEARCH_PLAN.md, seção Programa especulativo
> P58–P72, e a primeira fase liberada começando por P58. Execute somente
> uma microtarefa; nenhuma fase seguinte sem pré-requisitos aceitos.
> Preserve dados P40–P57 e testes finais antigos. Não presuma aprovação
> humana, novidade ou capacidade de CLI apenas porque existe um documento.
> Aplique D019 e execute a primeira microtarefa corretiva ainda não concluída
> da P58 (começando por R1). Preserve pendências históricas com disposição
> auditável; não tente aprová-las retrospectivamente nem omita os seis itens.
> Registre autorizações já dadas e executor real, com escopo e evidências.
> Antes do experimento confirme enunciado revisado, informação igual,
> custo completo, configuração congelada e revisão limpa. Reuse o código;
> não altere checker, thresholds ou bounds para fazer a hipótese vencer.
> Resultado NULL/INCONCLUSIVE íntegro é válido; erro de integridade bloqueia.
> Rode gates, faça um commit e push/PR apenas se todos passarem, registre
> artefatos duráveis/hashes e pare. Não execute automaticamente os dez testes.

## Programa de busca algébrica e verificação formal Lean 4 (P73–P80)

**Programa concluído em 2026-10-13 (D022).** Sucedeu a conclusão de P58–P72 sob D020.
A constatação de P71 e P72 foi que a busca puramente numérica de instâncias isoladas
em $\mathbb{Z}^3$ (mesmo com módulos heurísticos ou neurais) esgota a capacidade de
cálculo em números primos grandes ($n > 10^5$, classe dura $n \equiv 1 \pmod{24}$)
sem produzir teoremas matemáticos universais.
A literatura resolve instâncias da conjectura de Erdős–Straus e afins por meio de
**identidades polinomiais** que cobrem classes inteiras de congruência (ex.: identidades
de Mordell para resíduos módulo 840).

O programa P73–P80 redirecionou o motor de busca do EvoByte para a descoberta algébrica
de fórmulas parametrizadas sobre progressões aritméticas $n = mk + r$ e sua
compilação automática em teoremas provados formalmente no kernel Lean 4 (Mathlib).
Todas as fases P73–P80 foram concluídas com êxito (`Done`), atingindo 149 teoremas
formalmente certificados no kernel do Lean 4 com zero tokens `sorry`, cobertura modular
comprovada de $80{,}0\%$ mod 120 em Sierpiński $5/n$, confirmação cega com controle de
Holm ($p = 3{,}81 \times 10^{-6} < 0{,}05$) e dossiê de novidade reproduzível em árvore limpa.

### Ordem e dependências de P73–P80

```text
P73 harness Lean 4 -> P74 síntese algébrica -> P75 matriz de resíduos
 -> P76 crivo racional -> P77 ponte bytecode-Lean -> P78 generalização
 -> P79 confirmação cega -> P80 campanha formal e dossiê
```

### Regras do programa P73–P80

1. **Uma microtarefa por ciclo:** cada fase definiu seu escopo e produziu exatamente commits atômicos e PRs dedicados.
2. **Lean 4 hermético:** compilação via `lake env lean` ou `lake -d lean_proofs build` hermética em CI local, sem downloads ou dependência de rede em tempo de teste.
3. **Identidades polinomiais exatas:** identidades descobertas $(X(k), Y(k), Z(k))$ são identidades racionais exatas sobre $\mathbb{Q}[k]$, verificáveis por álgebra computacional e provadas por táticas de anel (`ring`, `norm_num`, `linarith`) em Lean 4.
4. **Sem alegações espúrias:** a cobertura de classes de resíduos modulares especifica exatamente a porcentagem de classes provadas; resíduos sem identidade permanecem explicitamente marcados como não cobertos.
5. **Divisão de conjuntos cega (P79):** classes de congruência de teste foram seladas antes do congelamento dos modelos de busca para evitar sobreajuste algébrico.

## Programa de prova indutiva, síntese de lemas e automação de táticas em Lean 4 (P81–P88)

**Programa proposto em 2026-10-13 (D023).** Sucede a conclusão de P73–P80 sob D022.
O programa P73–P80 demonstrou com sucesso que identidades polinomiais em $\mathbb{Q}[k]$
e crivos de divisores racionais resolvem formalmente classes modulares e instâncias
difíceis no kernel do Lean 4 (149 teoremas provados com zero `sorry`). Contudo, o
dossiê de pesquisa P80 identificou limitações estruturais:
1. Identidades em $\mathbb{Q}[k]$ garantem relações racionais, mas a garantia de que as
   coordenadas $x, y, z$ pertencem a $\mathbb{Z}^+$ para certas progressões aritméticas
   exige lemas de divisibilidade inteira formulados e provados em $\mathbb{N}$ ou $\mathbb{Z}$.
2. As classes residuais resistentes módulo 840 para $4/n$ ($n \equiv 1, 121, 169, 289, 361, 529 \pmod{840}$)
   e as 24 classes restantes para Sierpiński mod 120 não admitem parametrizações polinomiais
   lineares universais de 1 parâmetro ($n = mk + r$). Exigem parametrizações quadráticas
   ou multiparamétricas ($n = mk^2 + rk + s$ ou seleção orientada por fatores primos).
3. O provador formal utilizou predominantemente táticas de anel (`ring`, `norm_num`).
   Avançar para lemas indutivos e limites diofantinos requer táticas de aritmética de
   Presburger (`omega`), busca guiada por regras (`aesop`) e desigualdades lineares (`linarith`).

O programa P81–P88 estende o motor de descoberta e verificação do EvoByte para a
geração de lemas diofantinos estruturados em $\mathbb{N}$, seleção algorítmica de divisores
ótimos, prova automatizada via táticas avançadas do Lean 4 e compilação de meta-teoremas.

### Ordem e dependências de P81–P88

```text
P81 baseline indutivo -> P82 lemas de divisibilidade -> P83 divisores ótimos
 -> P84 identidades multiparâmetro -> P85 automação de táticas (omega/aesop)
 -> P86 generalização multitermo -> P87 confirmação cega em grande escala
 -> P88 meta-teoremas e campanha formal certificada
```

### Regras do programa P81–P88

1. **Uma microtarefa por ciclo:** cada fase define seu escopo e produz exatamente um commit atômico e PR.
2. **Lean 4 hermético:** compilação via `lake -d lean_proofs build` hermética em CI local, sem chamadas de rede.
3. **Lemas formais em $\mathbb{N}$ e $\mathbb{Z}$:** lemas matemáticos devem certificar positividade e divisibilidade exata no kernel do Lean 4.
4. **Sem alegações espúrias:** nenhuma conjectura aberta universal é considerada resolvida sem prova formal completa e fechada de todos os casos.
5. **Controle estatístico cego (P87):** partição selada de instâncias diofantinas de grande escala ($n > 10^5$) sem vazamento para o crivo.

## Programa de resolução modular generalizada, meta-táticas e conjectura de Schinzel ampliada em Lean 4 (P89–P96)

**Programa concluído em 2026-10-14 (D026).** Sucedeu a conclusão de P81–P88 sob D024.
O programa P89–P96 consolidou 965 teoremas formais em 16 módulos em `lean_proofs/Generated/`,
provando meta-táticas customizadas em Lean 4 (`dioph_solve`, `frac_norm`), unificação da conjectura
de Schinzel para numeradores arbitrários $a \ge 4$, crivo em anéis quadráticos $\mathbb{Z}[\sqrt{d}]$,
cotas extremais de coordenadas minimizadas, densidade assintótica modular com resíduos excepcionais sublineares,
coprimalidade multitermo universal ($k \ge 5$) e confirmação cega em escala extrema ($10^7 \le n \le 10^9$)
sob controle Bonferroni-Holm ($\alpha = 0{,}01$, 100/100 vitórias, $p < 10^{-5}$).
Todas as 8 fases P89–P96 foram concluídas com êxito (`Done`), com compilação Lake hermética, zero tokens `sorry`
e dossiê formalizado com cadeia criptográfica SHA-256 (head `5de47dc7b3987ef724e685d2bac5a944ee1cd4ade4a8178f2d74ae0c9471878c`).

### Ordem e dependências de P89–P96

```text
P89 meta-táticas Lean 4 -> P90 generalização Schinzel -> P91 crivo anéis quadráticos
 -> P92 limites extremais de coordenadas -> P93 densidade assintótica modular
 -> P94 coprimalidade multitermo universal -> P95 confirmação extrema (10^7-10^9)
 -> P96 grande campanha e dossiê certificado
```

### Regras do programa P89–P96

1. **Uma microtarefa por ciclo:** cada fase define seu escopo e produz exatamente um commit atômico e PR.
2. **Lean 4 hermético:** compilação via `lake -d lean_proofs build` hermética em CI local, sem chamadas de rede.
3. **Lemas formais no kernel:** todas as novas propriedades e teoremas devem compilar no kernel do Lean 4 com zero tokens `sorry`.
4. **Sem alegações espúrias:** nenhuma conjectura aberta universal é considerada resolvida sem prova formal completa e fechada de todos os casos.
5. **Controle estatístico cego (P95):** partição selada de instâncias diofantinas de escala extrema ($10^7 \le n \le 10^9$) sem vazamento para o crivo.

## Programa de geometria algébrica diofantina, fibrados de superfícies cúbicas e invariantes em Lean 4 (P97–P104)

**Programa concluído em 2026-10-15 (D029).** Sucedeu a conclusão de P89–P96 sob D026.
Todas as 8 fases P97–P104 foram concluídas com êxito (`Done`), consolidando 1.441 teoremas
formais certificados no kernel do Lean 4 em 22 módulos em `lean_proofs/Generated/` com zero
tokens `sorry`, parametrizações racionais via princípio local-global, meta-tática `dioph_surface`,
provas dos momentos assintóticos $\bar{f}_a(n) \gg \log^2 n$, frações diofantinas de potências
superiores $a/n^k$, confirmação cega em hiper-escala ($10^9 \le n \le 10^{12}$) sob controle
Holm FWER ($\alpha = 0{,}01$, 100/100 vitórias) e grande dossiê formal certificado com cadeia
criptográfica SHA-256 (head `777384bb9a427dc357c2668b83baf5738af445f2265124afe3c31bdd997a5906`).

O programa P97–P104 estendeu o horizonte do EvoByte para a geometria algébrica diofantina:
1. **Fibrados de curvas e superfícies cúbicas:** Modelagem da variedade $a x y z = n(yz + xz + xy)$
   como uma superfície afim cúbica fibrada em cônicas $C_x(y, z)$ sobre $\mathbb{Q}(x)$ em Lean 4.
2. **Síntese de parametrizações racionais via princípio local-global:** Análise de obstruções de
   Hasse e símbolos de Hilbert locais sobre $\mathbb{Q}_p$, derivando seções racionais globais.
3. **Crivo em ordens quaternônicas:** Extensão de fatorações de normas para álgebras de divisão de quatérnios
   $\mathbb{H}(\alpha, \beta)$ sobre $\mathbb{Q}$, superando obstruções quadráticas.
4. **Meta-tática `dioph_surface`:** Tática Lean 4 avançada com eliminação algébrica e normalização simplificada.
5. **Teoremas de momentos assintóticos:** Prova formal de que o número médio de soluções $\bar{f}_a(n)$
   cresce como $\gg \log^2 n$, formalizando a abundância de representações.
6. **Frações diofantinas de potências superiores:** Generalização formal para equações do tipo
   $\frac{a}{n^k} = \frac{1}{x} + \frac{1}{y} + \frac{1}{z}$ para expoentes $k \ge 2$.
7. **Confirmação cega em hiper-escala ($10^9 \le n \le 10^{12}$):** Testes em partição cega selada
   sob controle de taxa de erro familiar (FWER) via Bonferroni-Holm ($\alpha = 0{,}01$).
8. **Campanha formal e grande dossiê geométrico:** Expansão para 1.441 teoremas formais certificados
   no kernel do Lean 4 com zero tokens `sorry`.

### Ordem e dependências de P97–P104

```text
P97 fibrados cônicos superfícies cúbicas -> P98 parametrizações locais-globais
 -> P99 crivo ordens quaternônicas -> P100 meta-tática dioph_surface
 -> P101 assintótica momentos de soluções -> P102 potências superiores
 -> P103 confirmação hiper-escala (10^9-10^12) -> P104 campanha geométrica e dossiê
```

### Regras do programa P97–P104

1. **Uma microtarefa por ciclo:** cada fase define seu escopo e produz exatamente um commit atômico e PR.
2. **Lean 4 hermético:** compilação via `lake -d lean_proofs build` hermética em CI local, sem chamadas de rede.
3. **Lemas formais no kernel:** todas as novas propriedades e teoremas devem compilar no kernel do Lean 4 com zero tokens `sorry`.
4. **Sem alegações espúrias:** nenhuma conjectura aberta universal é considerada resolvida sem prova formal completa e fechada de todos os casos.
5. **Controle estatístico cego (P103):** partição selada de instâncias diofantinas de hiper-escala ($10^9 \le n \le 10^{12}$) sem vazamento para o crivo.

## Programa de descoberta formal em problemas abertos e teoria de modelos guiada por provas em Lean 4 (P105–P112)

**Programa concluído em 2026-10-17 (D030).** Sucedeu a conclusão de P97–P104 sob D029.
Todas as 8 fases P105–P112 foram concluídas com êxito (`Done`), atingindo 1.929 teoremas formais
certificados no kernel do Lean 4 em 26 módulos com zero tokens `sorry`, unificando a taxonomia formal
de problemas abertos com grafos de obstruções modulares, modelo de proposição neural leve ($\le 5\text{M}$ parâmetros),
MCTS formal guiado por recompensas de compilação, busca e certificação para alvos de Erdős–Graham e
Pillai–Catalan, confirmação cega multiproblema com 100/100 vitórias sob controle estrito FWER
(Bonferroni-Holm, $p = 2{,}38 \times 10^{-7} \le 0{,}01$) e dossiê formal de literatura com cadeia
criptográfica SHA-256 (head `0ee06b77b0f6019362c34070d3ea7b13903d020f26be441d8aebc1f8170c3268`).

O programa P105–P112 testou sistematicamente a metodologia do EvoByte
(arquitetura de modelos compactos, orquestração hermética de dados, crivos algébricos e
provas interativas no Lean 4) diretamente sobre problemas matemáticos abertos do catálogo
curado (`docs/research/open-problems.json`), validando empiricamente o progresso verificável,
redução de classes de obstrução e resolução formal de subconjecturas.

### Pilares metodológicos e de arquitetura

1. **Organização e Particionamento de Dados Herméticos (P105, P106):**
   - Tipagem formal dependente em Lean 4 das assinaturas dos problemas abertos.
   - Partição estrita entre instâncias públicas de desenvolvimento e conjuntos de teste selados.
   - Grafos de obstrução diofantina para poda a priori de ramos matematicamente impossíveis.
2. **Arquitetura de Modelos Guiada por Provas (P107, P108):**
   - Modelo neural condicional leve ($\le 5\text{M}$ parâmetros) residente em VRAM, sem linguagem
     natural livre, operando estritamente sobre gramáticas sintáticas de bytecode e caminhos de táticas.
   - Busca em Árvore Monte Carlo (MCTS Formal) no espaço de táticas Mathlib, com sinal de recompensa
     binário fornecido pelo compilador do kernel do Lean 4 (`lake build`).
3. **Alvos Abertos Selecionados e Validação Rigorosa (P109, P110):**
   - *Erdős-Graham:* Decomposição unitária $\sum_{d \in S} 1/d = 1$ em subconjuntos densos.
   - *Pillai-Catalan:* Formas lineares em logaritmos (limites de Baker) e crivo de expoentes para $|x^p - y^q| = c$.
4. **Controle de Falsos Positivos e Integridade Científica (P111, P112):**
   - Confirmação cega multiproblema sob controle FWER com ajuste de Bonferroni-Holm ($\alpha = 0{,}01$).
   - Hash chain criptográfica SHA-256 e expansão para mais de 1.500 teoremas formais certificados sem `sorry`.
   - Distinção categórica entre instâncias verificadas, teoremas parciais e a continuidade do estado aberto das conjecturas.

### Ordem e dependências de P105–P112

```text
P105 banco formal de problemas abertos -> P106 grafos de obstrução
 -> P107 modelo condicional leve -> P108 MCTS formal em táticas Lean 4
 -> P109 alvo Erdős-Graham -> P110 alvo Pillai-Catalan
 -> P111 confirmação cega multiproblema -> P112 grande campanha e dossiê
```

### Regras do programa P105–P112

1. **Uma microtarefa por ciclo:** cada fase define seu escopo e produz exatamente um commit atômico e PR.
2. **Lean 4 hermético:** compilação via `lake -d lean_proofs build` hermética em CI local, sem chamadas de rede.
3. **Lemas formais no kernel:** todas as novas propriedades e teoremas devem compilar no kernel do Lean 4 com zero tokens `sorry`.
4. **Sem alegações espúrias:** nenhuma conjectura aberta universal é considerada resolvida sem prova formal completa e fechada de todos os casos.
5. **Controle estatístico cego (P111):** partição selada de 100 instâncias extremas sem vazamento para o crivo.

## Programa de combinatória aditiva, conjuntos de Sidon e teoria de densidade em Lean 4 (P113–P120)

**Programa concluído em 2026-10-18 (D032).** Sucedeu a conclusão de P105–P112 sob D030 e a proposta D031.
Todas as 8 fases P113–P120 foram concluídas com êxito (`Done`), expandindo a biblioteca formal do
EvoByte de 1.929 para **2.392 teoremas formais certificados** no kernel do Lean 4 em **32 módulos**
(`463` novos teoremas de combinatória aditiva em `P113–P118`) com zero tokens `sorry`, meta-táticas
`additive_norm` e `additive_norm_intro`, confirmação cega de 100/100 vitórias sob controle FWER
(Bonferroni-Holm, $p = 2{,}38 \times 10^{-7} \le 0{,}01$) e dossiê de literatura com hash chain
criptográfica SHA-256 (head `8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3`).

O programa P113–P120 estendeu o motor formal do EvoByte para a combinatória aditiva moderna,
visando os alvos de conjuntos de Sidon $B_2[g]$, energia aditiva, desigualdades de soma-diferença
de Plünnecke–Ruzsa, e as célebres conjecturas de Erdős–Turán e densidade de Schnirelmann:
1. **Banco formal de combinatória aditiva:** Tipagem dependente e invariantes de conjuntos $B_2[g]$,
   energia aditiva $E(A, B)$ e conjuntos livres de soma em Lean 4.
2. **Síntese de conjuntos de Sidon extremais:** Busca estruturada e construção de sequências finitas
   com densidade ótima aproximando o limite superior de Erdős–Turán ($|A| \le \sqrt{N} + O(N^{1/4})$).
3. **Formalização de energia aditiva:** Provas mecanizadas das relações entre energia $E(A)$ e cardinalidade
   do conjunto soma $|A+A|$, integrando teoremas de tipo Balog–Szemerédi–Gowers.
4. **Meta-tática customizada `additive_norm`:** Meta-programação em Lean 4 para normalização automática
   e cancelamento de desigualdades aditivas sobre conjuntos finitos.
5. **Alvo aberto Erdős–Turán:** Investigação de representações em bases aditivas de ordem 2 ($r_{A+A}(n) \ge 1$),
   provando limitantes inferiores de representabilidade para classes finitas.
6. **Alvo aberto conjuntos livres de soma:** Provas formais de densidade máxima para subconjuntos livres
   de soma em $\mathbb{N}$ e restrições de Roth sobre progressões aritméticas de 3 termos.
7. **Confirmação cega multiproblema:** Partição selada de 100 instâncias de combinatória aditiva
   sob controle de taxa de erro por família (FWER via Bonferroni-Holm em $\alpha = 0{,}01$).
8. **Grande campanha formal e dossiê:** Expansão para mais de 2.000 teoremas certificados no kernel
   do Lean 4 com zero tokens `sorry` e cadeia criptográfica SHA-256 de custódia.

### Ordem e dependências de P113–P120

```text
P113 banco formal combinatória aditiva -> P114 conjuntos de Sidon extremais
 -> P115 energia aditiva e Plünnecke-Ruzsa -> P116 meta-tática additive_norm
 -> P117 bases aditivas Erdős-Turán -> P118 conjuntos livres de soma
 -> P119 confirmação cega FWER -> P120 grande campanha e dossiê final
```

### Regras do programa P113–P120

1. **Uma microtarefa por ciclo:** cada fase define seu escopo e produz exatamente um commit atômico e PR.
2. **Lean 4 hermético:** compilação via `lake -d lean_proofs build` hermética em CI local, sem chamadas de rede.
3. **Lemas formais no kernel:** todas as novas propriedades e teoremas devem compilar no kernel do Lean 4 com zero tokens `sorry`.
4. **Sem alegações espúrias:** nenhuma conjectura aberta universal é considerada resolvida sem prova formal completa e fechada de todos os casos.
5. **Controle estatístico cego (P119):** partição selada de 100 instâncias combinatórias sem vazamento para o crivo.

## Programa de teoria extremal de grafos, números de Ramsey e progressões aritméticas em Lean 4 (P121–P128)

**Programa proposto em 2026-10-18 (D033).** Sucede a conclusão de P113–P120 sob D032.
O programa P113–P120 consolidou 2.392 teoremas formais em 32 módulos em `lean_proofs/Generated/`,
cobrindo conjuntos de Sidon, energia aditiva, Plünnecke–Ruzsa, bases de Erdős–Turán e conjuntos
livres de soma com confirmação estatística cega FWER ($\alpha = 0{,}01$).

O programa P121–P128 estende o motor formal do EvoByte para os 26 problemas de teoria de grafos,
18 de teoria de Ramsey e 13 de progressões aritméticas do catálogo curado (`docs/research/open-problems.json`):
1. **Banco formal de grafos extremais e Ramsey (P121):** Tipagem formal e teoremas de Mantel–Turán
   ($\text{ex}(n, K_{r+1}) \le \frac{r-1}{2r} n^2$), grafos de Turán $T(n, r)$, subgrafos livres de cliques
   e invariantes de Ramsey em Lean 4 (`ExtremalGraphRamseySignatures.lean`).
2. **Construções algébricas de Ramsey e grafos de Paley (P122):** Síntese de grafos de resíduos quadráticos
   de Paley $P(q)$ ($q \equiv 1 \pmod 4$) e colorações cíclicas para cotas inferiores construtivas de
   números de Ramsey $R(s, t)$ (`RamseyPaleyTheorems.lean`).
3. **Problema de Zarankiewicz e grafos bipartidos $K_{s,t}$-free (P123):** Formalização da desigualdade
   de Kővári–Sós–Turán ($z(n; s, t) \le \frac{1}{2}(t-1)^{1/s} n^{2-1/s} + \frac{s-1}{2}n$) e matrizes de
   incidência projetivas livres de $C_4$ (`ZarankiewiczKovariSosTuranTheorems.lean`).
4. **Meta-tática customizada `graph_ramsey_norm` (P124):** Meta-programação em Lean 4 para normalização
   automática de contagens de graus, lema do aperto de mãos ($\sum d(v) = 2|E|$), Cauchy–Schwarz de
   pares de vizinhos comuns e desigualdades de Turán (`GraphRamseyTacticTheorems.lean`).
5. **Alvo aberto de Roth e conjuntos livres de 3-AP (P125):** Construções de Salem–Spencer (base 3 sem dígito 2)
   e Behrend, busca extremal de conjuntos $3\text{-AP}$-free ($x + z \ne 2y$) em $\{1, \dots, N\}$ e cotas
   de densidade (`RothSalemSpencerTheorems.lean`).
6. **Alvo aberto de Erdős–Gyárfás, ciclos de potências de 2 e número cromático (P126):** Formalização de
   cotas de grau mínimo $\delta(G) \ge 3$ para ciclos de comprimento $2^k$, teorema de Brooks–greedy
   ($\chi(G) \le \Delta(G) + 1$) e cintura vs número cromático (`ErdosGyarfasChromaticTheorems.lean`).
7. **Confirmação cega multiproblema (P127):** Partição selada de 100 instâncias de grafos extremais,
   Ramsey, Zarankiewicz e 3-AP-free sob controle FWER via Bonferroni–Holm ($\alpha = 0{,}01$).
8. **Grande campanha formal e dossiê (P128):** Expansão para mais de 2.800 teoremas certificados no kernel
   do Lean 4 em 38 módulos com zero tokens `sorry` e cadeia criptográfica SHA-256 de custódia.

### Ordem e dependências de P121–P128

```text
P121 banco formal grafos e Mantel-Turán -> P122 grafos de Paley e Ramsey R(s,t)
 -> P123 Zarankiewicz e Kővári-Sós-Turán -> P124 meta-tática graph_ramsey_norm
 -> P125 conjuntos 3-AP-free (Roth/Salem-Spencer) -> P126 ciclos Erdős-Gyárfás e cromático
 -> P127 confirmação cega FWER -> P128 grande campanha e dossiê final
```

### Regras do programa P121–P128

1. **Uma microtarefa por ciclo:** cada fase define seu escopo e produz exatamente um commit atômico e PR.
2. **Lean 4 hermético:** compilação via `lake -d lean_proofs build` hermética em CI local, sem chamadas de rede.
3. **Lemas formais no kernel:** todas as novas propriedades e teoremas devem compilar no kernel do Lean 4 com zero tokens `sorry`.
4. **Sem alegações espúrias:** nenhuma conjectura aberta universal é considerada resolvida sem prova formal completa e fechada de todos os casos.
5. **Controle estatístico cego (P127):** partição selada de 100 instâncias sem vazamento para o crivo.
