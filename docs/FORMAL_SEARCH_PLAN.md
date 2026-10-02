# Plano de busca matemática verificável — execução por agente econômico

**Status: Proposed. Data: 2026-10-01.** Este documento é planejamento, não
implementação, certificação das fases antigas ou promessa de descoberta.
Novas fases: P40–P57. Não executar nenhuma delas durante a criação deste plano.

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

Os arquivos de fase têm Status Proposed. Marcar Done requer gate executado,
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
> da primeira fase P40–P57 ainda não aceita cujos predecessores passaram.
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
