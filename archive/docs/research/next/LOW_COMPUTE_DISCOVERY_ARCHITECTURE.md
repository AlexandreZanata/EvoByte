# Low-Compute Discovery Architecture

Proposta de 2026-11-05. Python permanece como linguagem de pesquisa.
Inteiros Python, NumPy e SymPy já disponíveis atendem aos pilotos.
Os módulos existentes serão usados após auditoria de suas garantias.
[ADR-0011](../../adr/ADR-0011-low-compute-discovery.md)

## Contratos pequenos

Cada problema recebe um script Discoverer e um script Verifier. O primeiro
produz um objeto e uma alegação. O segundo reconstitui o objeto e confere a
alegação dentro de um domínio explícito, sem importar a busca. O auditor de
novidade registra fontes e limites em documento próprio. Lean atua depois
que o enunciado concreto foi revisado.

O certificado contém versão, representação, domínio, entrada/hash, alegação,
testemunha, evidência da cota inferior quando aplicável, método de replay e
limites. O relatório de execução contém revisão, dirty, configuração
resolvida, hardware, pacotes, tempos, memória e desfecho. JSON é formato de
entrada e saída fora da enumeração. Os loops operam sobre inteiros e arrays.

Para P230, os bits seguem a convenção P221, com a coluna j no bit n−1−j.
O checker relê os suportes e reconstrói as matrizes com a implementação
independente. Para P231, o certificado inclui as permutações de linhas e
colunas e a partição de blocos. Para P232, contém duas palavras de portas
e a tabela exata de ação sobre quatro vetores da base.

A interface comum limita-se a arquivos e campos documentados. Cada piloto
mantém sua lógica matemática local. Um módulo comum será extraído somente
quando duas implementações corretas precisarem da mesma operação. SQLite,
CBOR e Rust exigirão ganho medido ou necessidade concreta de persistência.

## Vinte técnicas a avaliar

Custos abaixo são envelopes teóricos, sem medições do EvoByte. N é o número
de objetos, n o número de bits/qubits, r o posto, m o número de restrições,
L o comprimento de um programa e t a largura estrutural. O fator real de
redução será medido contra o mesmo domínio e garantia.

1. **Quociente por simetria.** Visitar órbitas pode reduzir N pelo tamanho
   médio real da órbita. A ação precisa preservar a propriedade e o peso.
   O custo por órbita inclui canonicalização. Armazenamento pode chegar a
   O(N). Certificar com permutações e prova da ação. Ações com estabilizadores
   impedem dividir automaticamente pela ordem do grupo. Reusar as ações do projeto.
2. **Canonical augmentation.** Gerar somente representantes evita deduplicação
   tardia, mas a árvore continua exponencial no pior caso. Memória em DFS é
   proporcional à profundidade mais a canonicalização. Requer um teste de
   pai canônico completo. nauty/Traces é candidato para grafos. Um hash
   canônico sozinho exige justificativa de completude.
3. **SAT incremental.** Reutilizar cláusulas e hipóteses elimina reconstruções,
   sem ganho universal sobre custo exponencial. Memória inclui cláusulas
   aprendidas. PySAT já existe. UNSAT exige prova rechecável para certificar
   impossibilidade, além da correção da codificação.
4. **SMT.** Restrições de bits e aritmética podem evitar codificação manual.
   Complexidade depende da teoria e pode ser exponencial ou pior. Memória
   depende do solver. Z3 é candidato opcional. Modelo SAT é testemunha,
   e a disponibilidade de certificados UNSAT precisa ser conferida.
5. **Branch-and-bound.** Uma cota admissível elimina subárvores. Pior caso
   exponencial, memória pequena em DFS e grande em best-first. Certificar
   cotas e ramos excluídos. Uma cota heurística incorreta invalida a poda.
6. **Meet-in-the-middle.** Para decomposição em duas metades independentes,
   pode trocar 2^n por cerca de 2^(n/2) estados de tempo/memória. Interações
   entre metades exigem chaves suficientes. Certificar a combinação encontrada
   é barato. A completude do índice exige replay.
7. **Algebraic sieving.** Identidades polinomiais podem excluir candidatos.
   Custo varia por família, frequentemente exponencial. Algoritmos aleatórios
   com cancelamento podem ter falsos negativos. Usar um crivo determinístico
   demonstrado nos pilotos, com certificado das exclusões.
8. **Bases de Gröbner.** Reduzem sistemas algébricos pequenos a formas normais.
   Pior caso duplamente exponencial em variáveis, memória muito alta.
   SymPy é candidato já presente. Testemunhas de combinação de polinômios
   permitem replay. O crescimento dos coeficientes limita o uso.
9. **GF(2)/GF(q) compactado.** XOR e popcount reduzem custos constantes da
   eliminação. Eliminação densa binária custa aproximadamente O(n³/w)
   operações de palavra e O(n²/w) palavras. Inteiros Python já existem.
   Certificar posto com bases e relações. A redução depende da densidade.
10. **Representações de grupos finitos.** Decomposição pode substituir matrizes
    grandes por blocos. Custo de obter representações deve entrar na conta.
    Característica que divide a ordem pode impedir semissimplicidade.
    GAP é referência opcional. Certificar intertwiners e blocos por identidade exata.
11. **Propagação e nogoods.** Eliminar atribuições incompatíveis antes de
    ramificar pode reduzir a árvore, mantendo pior caso exponencial.
    Aprendizado consome memória. Usar PySAT. Cada nogood precisa decorrer
    das restrições para sustentar uma exclusão rigorosa.
12. **CEGIS.** Contraexemplos removem hipóteses de uma gramática finita.
    O pior caso visita toda a gramática e depende do oráculo. Guardar
    hipóteses e contraexemplos. O certificado é o objeto final mais seu
    teste/prova. Amostras finitas exigem domínio explicitado.
13. **E-graphs.** Igualdades compartilham representações, mas saturação pode
    crescer exponencialmente em tempo e memória. egg é candidato futuro.
    Guardar uma derivação por regras corretas. O custo do circuito extraído
    precisa ser medido. Não priorizar no primeiro piloto.
14. **Execução simbólica.** Estados compactos evitam simulação numérica repetida.
    O número de caminhos pode ser exponencial em L. Memória cresce com
    expressões e estados vivos. Para CNOT+T, usar ação exata finita.
    Certificar por replay em uma representação diferente.
15. **Síntese por gramática restrita.** Enumerar um alfabeto de a portas até L
    custa O(a^L) antes das fusões. BFS consome memória exponencial.
    P232 limita a=6 e L=6. Certificar equivalência por matrizes exatas.
    Minimalidade refere-se somente ao universo enumerado.
16. **Aritmética racional exata.** Remove erro de arredondamento, com custos
    dependentes do tamanho dos numeradores e denominadores. Fraction e SymPy
    atendem aos protótipos. Identidades e LDLᵀ racionais são certificados.
    Crescimento de bits pode dominar o custo.
17. **Intervalos rigorosos.** Envolventes com arredondamento controlado podem
    certificar sinais e cotas. Refinamento pode continuar indefinidamente
    perto de zero. Arb/python-flint é candidato futuro. Registrar intervalos
    e precisão. Um float convertido em intervalo estreito carece de garantia.
18. **Proof-carrying computation.** A busca produz prova ou testemunha e um
    checker menor a revalida. Tempo/memória dependem do tamanho do certificado.
    Lean e checkers LRAT são opções. Uma prova curta é uma meta por medir,
    e sua ligação à instância codificada também precisa ser demonstrada.
19. **Redes tensoriais.** Baixa largura de árvore pode permitir contração
    exponencial em t em vez de n. Memória também cresce exponencialmente
    em t. cotengra é candidato futuro. Conexões densas anulam a vantagem.
    Certificação exata pode ter custo maior que a aproximação numérica.
20. **Busca em classes de equivalência.** Memorizar semânticas evita revisitar
    descrições diferentes, ao custo de O(N) chaves no pior caso. P232 tem
    semântica exata em quatro estados. Hashes aceleram acesso, e a comparação
    completa resolve colisões. Uma equivalência que perde peso invalida
    conclusões sobre distância ou custo ótimo.

[PySAT e provas](https://pysathq.github.io/docs/html/api/solvers.html) ·
[ZX exaustivo](https://arxiv.org/abs/2503.10983v2) ·
[Representação de estabilizadores](https://journals.aps.org/prxquantum/abstract/10.1103/1gjs-2rhx)

## Métrica de eficiência

Medir geração e certificação separadamente e também sua soma. A comparação
principal exige a mesma propriedade e o mesmo domínio, incluindo a leitura
e reconstrução. Informar primeiro uso, repetições aquecidas, CPU-segundos,
RSS e tamanho dos artefatos. Número de candidatos por segundo é diagnóstico.
Classes eliminadas só entram na métrica com ação/decomposição certificada.
[Contrato de execução](EVOBYTE_NEXT_RESEARCH_PROGRAM.md)
