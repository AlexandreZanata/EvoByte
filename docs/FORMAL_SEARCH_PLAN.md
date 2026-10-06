# Plano de busca matemática verificável — execução por agente econômico

**Plano atualizado: 2026-10-05.** P40–P57 são o programa histórico, com
resultados e pendências nos arquivos individuais. A extensão P58–P72 tem
Status Proposed. Este documento não certifica fases antigas nem promete
descoberta. Criar o plano não executa os novos experimentos.

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

Os novos arquivos P58–P72 têm Status Proposed. Marcar Done requer gate executado,
artefato recuperável, commit e push; número de fases escritas não é progresso
experimental. Runtime ausente, dado insuficiente ou fonte sem confirmação
produzem BLOCKED/INCONCLUSIVE conforme o caso; nunca simular sucesso.

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

**Status: Proposed, 2026-10-05.** São hipóteses exploratórias; não há
garantia de ineditismo mundial, vantagem quântica, ganho de velocidade ou
solução de conjectura. Este plano implementa nenhuma das novas interfaces.
Os resultados históricos P40–P57 continuam preservados e sujeitos a seus
gates científicos, mesmo onde o arquivo registra Done.

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

P58 é a próxima tarefa, com auditoria e revisões pendentes. Antes de medir
P61–P70, P58–P60 devem estar integralmente aceitas. Propostas e código podem
ser preparados em microtarefas próprias, mas gate pendente bloqueia novos
experimentos e qualquer aceitação científica.

Cada piloto P61–P70 testa seu mecanismo isoladamente contra a base P59;
não acrescenta automaticamente mecanismos experimentais anteriores.
Hipótese íntegra NULL/INCONCLUSIVE pode encerrar a etapa e liberar a
próxima. Nenhum sucessor depende de fabricar um ganho. Falha de checker,
dados, aprovação ou isolamento é BLOCKED e interrompe a cadeia.

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
> Antes do experimento confirme enunciado revisado, informação igual,
> custo completo, configuração congelada e revisão limpa. Reuse o código;
> não altere checker, thresholds ou bounds para fazer a hipótese vencer.
> Resultado NULL/INCONCLUSIVE íntegro é válido; erro de integridade bloqueia.
> Rode gates, faça um commit e push/PR apenas se todos passarem, registre
> artefatos duráveis/hashes e pare. Não execute automaticamente os dez testes.
