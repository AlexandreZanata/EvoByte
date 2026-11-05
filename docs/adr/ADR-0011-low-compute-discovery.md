# ADR-0011 — Programa local de descoberta com baixo custo

Proposta de 2026-11-05 para revisão. D051 registra a solicitação de mudança
feita por Alexandre. A implementação depende da aprovação deste plano.

A P222 está arquivada com estado incompleto. Seu censo parcial é referência
experimental. D049, os resultados antigos e os opcodes mantêm seus registros.

Para P229–P234, a referência científica será Python determinístico em CPU,
com aritmética binária ou exata. A sequência de pesquisa é pergunta,
redução matemática, hipótese, tentativa de refutação, certificação e auditoria
de novidade. GPU será uma opção posterior que exige benefício medido.
Este ADR altera a prioridade GPU-next somente para este novo programa.

Cada experimento terá gerador e verificador separados. Certificados terão
objetos concretos, domínio e garantia explícita. A prova de distância exata
exige uma testemunha de peso d e uma justificativa verificável da ausência
de lógicos menores. SHA-256 serve à integridade dos bytes.

Rust, SMT, e-graphs e novas dependências serão decisões posteriores ao
perfilamento e à revisão do problema. Os três pilotos usam ferramentas já
presentes ou biblioteca padrão. O programa opera localmente e usa a internet
na preparação bibliográfica, fora dos experimentos.

O executor é identificado no relatório pelo nome realmente usado. O texto
Gemini Flash 3.8 registra a preferência do usuário. A seleção do modelo
ocorre no cliente executor.

[Programa](../research/next/EVOBYTE_NEXT_RESEARCH_PROGRAM.md) ·
[Direção científica](../research/next/SCIENTIFIC_PIVOT.md)
