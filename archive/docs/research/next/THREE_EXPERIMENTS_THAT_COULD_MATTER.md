# Three Experiments That Could Matter

Proposta de 2026-11-05. Todos os valores de tempo e memória a seguir são
tetos de pesquisa propostos. A P229 congela os dados e revisa a lacuna
metodológica antes da liberação de um piloto. A novidade fica pendente.

## E1 — Distância exata por enumeração compacta do núcleo

**Pergunta.** Em seis códigos CSS pequenos já arquivados, o núcleo percorrido
em Gray code reduz o custo de certificar a mesma distância exata que a
busca por máscaras de peso crescente?

**Entradas.** Usar o campo `example` de `best_d` do resumo P222 para
`16_2`, `16_4`, `18_2`, `18_4`, `20_2`, `20_4`, nessa ordem. O arquivo bruto
esperado tem SHA-256
`623474978937de805bce0b0588d17307b5f8f3d629c3dbb8a8cdcf5722340509`.
Copiar suportes, n e k para um manifesto congelado na P229.

**Baseline e candidato.** O baseline é a implementação independente
`distance` da P221. O candidato usa uma base exata de `ker(HZ)` e
`ker(HX)`, percorrendo as combinações em Gray code com uma operação XOR
por transição. Para X, eliminar vetores no espaço de linhas de HX.
Para Z, eliminar vetores no espaço de linhas de HZ. A menor massa de
Hamming dos restantes é d. Computar os dois lados.

O custo do candidato cresce com 2^(n−rank(HZ)) + 2^(n−rank(HX)), além dos
testes de pertencimento. Pode perder quando os núcleos são grandes ou a
distância é pequena. Enumerar em streaming evita guardar todas as combinações.

**Verificação.** Um checker com biblioteca padrão reconstrói as matrizes a
partir dos suportes, reexecuta o baseline P221 e verifica separadamente a
máscara testemunha de peso d. O checker terá acesso à implementação P221
identificada por hash e não importará o código do candidato. Duplicar o
arquivo de lógica para chamá-lo de independente seria insuficiente.

**Certificado.** Suportes, ranks, k, d, tipo X/Z, máscara lógica, identidade
do domínio reenumerado e modo de replay. A cota inferior é conferida pelo
replay independente completo. O hash de uma lista não substitui esse replay.

**Orçamento e decisão.** Até 30 s, 2 núcleos e 512 MiB, um processo,
cinco repetições alternadas por caso. Sucesso técnico exige concordância
nos seis casos e rejeição de testemunha alterada. Manter a otimização se
o ganho agregado de mediana for pelo menos 1,2× em duas baterias e o RSS
ficar no teto. Publicar tempos por caso e perdas. Ganho ausente encerra a
hipótese de desempenho nesse recorte com resultado negativo.
[P230](../../phases/P230-exact-distance-kernel-pilot.md)

## E2 — Decomposição de suporte com certificado

**Pergunta.** Uma decomposição em blocos idênticos permite evitar recálculos
de distância nos códigos BB desconectados do arquivo parcial?

**Entrada.** Os 128 primeiros registros do censo, na ordem já arquivada.
Considerar G = Z_l × Z_m. Escolher a0 em A e b0 em B. Construir
A0 = A−a0 e B0 = B−b0. Definir H como o subgrupo gerado por A0 ∪ B0.
Esse é o subgrupo gerado pelas diferenças internas de cada suporte.

**Argumento a revisar antes de programar.** As translações independentes
são transformações de coordenadas em cada bloco de qubits, acompanhadas
pelas permutações adequadas de linhas de HX e HZ. Depois delas, os suportes
estão em H. Ordenar índices por cosets de H deve decompor os dois checks
nos mesmos t = |G|/|H| blocos. A alegação é k = t·k0 e, quando k0 > 0,
d = d0. Um caso k0 = 0 exige tratamento próprio da ausência de lógicos.

O verificador deve conferir as identidades de matrizes e as permutações
completas, incluindo os dois tipos de check. Uma igualdade de ranks
isolada não certifica a distância. Essa decomposição básica é conhecida
como mecanismo algébrico, e a contribuição candidata é seu uso certificado
para reduzir o trabalho do projeto.

Na convenção de linhas usada em P221, a transformação candidata envia a
coordenada g do primeiro bloco de qubits para g−a0 e a do segundo bloco
para g−b0. As linhas de HX conservam seu índice, e uma linha g de HZ
recebe o índice g−a0−b0. Todas as operações são no grupo G. Conferir essas
igualdades em matrizes concretas e no argumento revisado antes de ordenar
os cosets. Essa especificação evita exigir que o executor invente as
permutações durante a implementação.

```text
para cada registro congelado
    normalizar A e B por a0 e b0
    H := fecho aditivo dos suportes normalizados
    construir cosets, permutações e blocos
    checker reconstrói HX e HZ e confere a transformação exata
    se os blocos forem idênticos e k0 > 0
        calcular a distância de um bloco
        transferir a garantia usando a decomposição certificada
    caso contrário, registrar que a redução não se aplica
```

**Verificação e refutação.** Construção independente das matrizes e BFS de
componentes serve de controle. Conferir ranks em todos os 128 registros e
distância por P221 nas seis referências de E1. Alterar uma permutação e
exigir rejeição. Um contraexemplo ao argumento proposto interrompe a linha
para revisão matemática.

**Orçamento e decisão.** Nível A. Contabilizar o custo de certificar a
transformação antes do tempo poupado. Sucesso metodológico exige ao menos
uma instância com redução aplicável, identidade exata e ganho líquido
mensurável. Se nenhum dos 128 casos se decompuser, registrar esse resultado
e encerrar o recorte. Não ampliar o lote para buscar um caso favorável.
[P231](../../phases/P231-certified-subgroup-decomposition.md)

**Experimento de 30 minutos.** Com 4 núcleos e 2 GiB, escolheria este problema
após seu piloto. O teto inclui repetir as identidades, extrair uma formulação
paramétrica e procurar contraexemplos à extensão. O domínio continua nos
128 registros e seis referências. Só uma decisão científica posterior
poderia autorizar sua ampliação. O resultado pode ser uma redução conhecida
reproduzida, uma melhoria metodológica ou uma refutação da extensão.

## E3 — Identidades CNOT+T com semântica exata

**Pergunta.** Agrupar palavras pela semântica exata gera regras locais cuja
equivalência pode ser certificada com custo pequeno e benefício após extração?

**Domínio.** Dois qubits, sem ancillas. Alfabeto ordenado
`CX01, CX10, T0, T1, TDG0, TDG1`. Comprimento de zero a seis.
O domínio contém 55.987 palavras. O objetivo lexicográfico é
`(T-count, CNOT-count, comprimento)`, com T e TDG contando uma unidade.
Um empate é resolvido pela ordem lexicográfica da palavra.

**Método.** Para cada palavra, computar uma transformação binária reversível
L e uma fase p(x) em Z/8Z para cada x em {00,01,10,11}. A ação é
`|x> -> zeta8**p(x) |Lx>`. Guardar a palavra mais barata por semântica.
Registrar as fusões e extrair pares equivalentes que melhoram o custo.
A enumeração simples no mesmo domínio é o controle de completude.

**Baseline.** Cancelamento adjacente de CNOT iguais e agregação de T/TDG no
mesmo fio quando adjacentes. A comparação com Amy–Mosca e com o método ZX
publicado é obrigatória antes de alegar originalidade. A P229 pode encerrar
a linha se o trabalho proposto já estiver coberto sem lacuna metodológica.

Para desempenho, o controle calcula diretamente a ação exata de cada
palavra completa nos quatro estados. O candidato reutiliza a ação de seu
prefixo. Ambos cobrem todas as palavras no primeiro piloto. O baseline de
simplificação local acima serve para avaliar a regra extraída. Ele tem
garantia distinta de um sintetizador ótimo e recebe essa identificação.

**Checker.** Reexecutar as duas palavras como matrizes 4×4 exatas sobre
Z[zeta8], com `zeta8**4 = -1`, representando cada entrada por quatro
inteiros. Conferir igualdade e custo por outro caminho de implementação.
Também conferir ações nos quatro estados de base. Exigir rejeição após
alterar uma porta em uma identidade de teste. A tabela de fases do
Discoverer não será tomada como autoridade pelo checker.

**Certificado e escopo.** Duas palavras, ordem dos qubits, relação de fase
global, custos e domínio. O limite de comprimento precisa de cobertura
completa para sustentar qualquer minimalidade nesse domínio. Uma identidade
exata em dois fios pode ser inserida em fios de um circuito maior por
produto tensorial. Sua novidade continua dependendo da literatura.

**Orçamento e decisão.** Nível A, um processo. Se a enumeração estourar
30 s ou 512 MiB, guardar cobertura parcial e `INCONCLUSIVE`. Manter a
linha se houver regra além do baseline declarado, equivalência exata e
vantagem que sobreviva à extração do circuito. Uma regra já publicada
recebe `KNOWN_RESULT`.
[Amy–Mosca](https://arxiv.org/abs/1601.07363v2) ·
[Busca ZX](https://arxiv.org/abs/2503.10983v2) ·
[P232](../../phases/P232-exact-cnot-t-identities.md)

## Quarta aposta — Cargas locais em cadeia com termo de três corpos

Proposta adicional de alto risco, fora das seis tarefas liberáveis agora.
Considerar N em {4,5,6} e condições periódicas. Usar
`H = sum_i (X_i X_(i+1) + Y_i Y_(i+1) + a Z_i Z_(i+1)
+ b Z_i Z_(i+2) + X_i Y_(i+1) Z_(i+2) - Z_i Y_(i+1) X_(i+2))`,
com a,b em {−1,0,1}. Buscar Q como soma das translações de densidades
Pauli de alcance até três. Resolver `[H,Q] = 0` por álgebra linear exata.
Eliminar da análise o espaço conhecido gerado por I, H e cargas óbvias
que realmente comutem. Verificar o residual como matriz exata independente.

Um piloto teria até 30 s, 2 núcleos e 512 MiB no primeiro par de parâmetros.
Uma carga extra só é candidata de tamanho finito. A generalização requer
um argumento local paramétrico ou prova. O risco é reencontrar uma carga
conhecida, um polinômio de H ou um efeito de tamanho finito. A literatura
recente já classifica amplas famílias de cadeias isotrópicas, e grafos de
frustração também têm critérios conhecidos. P229 registra a sobreposição
antes de qualquer liberação desse experimento.
[Dicotomia de integrabilidade](https://arxiv.org/abs/2504.14315v4) ·
[Modelos solúveis por grafos](https://arxiv.org/abs/2003.05465v2)
