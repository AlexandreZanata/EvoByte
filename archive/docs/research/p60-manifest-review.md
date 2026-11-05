# Revisão do manifesto da bancada P60 (2026-10-07)

- Alvo: `experiments/p60-workbench-manifest.json` v1
  (`sha256=e6204e980cb0170e09432155e86fb6a2b0814f949f4b5f465a3cc3d0b85045e7`,
  entrega 1, commit `908b089`).
- Revisor: Alexandre, por delegação expressa (D019, 2026-10-06).
  Execução desta revisão: agente executor (identificado; não é autoria
  independente nem certificação científica).

## Conferido

- Família: construções limitadas de Erdős–Straus, candidato tupla inteira
  ou template versionado com domínio declarado, certificado exato,
  verificador imutável nos dez braços; P57 como desenvolvimento, nunca
  teste fresco.
- Seis tarefas development (`es-dev-04/06/08/09/10/12`, n pequenos
  compostos, `max_coord=10^9`); disjuntas de qualquer final futuro novo
  por construção declarada; controles conhecidos/falsos fora da métrica.
- Três seeds (7, 42, 101) com regra de repetição intra-tarefa; comparação
  baseline × uma hipótese por vez.
- Orçamentos: 10 s busca/certificação por tentativa, teto 30 min/hipótese
  com coleta+treino, 5 h teto inicial dos dez pilotos, raw 1 GiB/execução,
  reserva ≤100k e teto absoluto 1M de parâmetros — coerentes com o runbook.
- Desfecho primário (tarefas certificadas no mesmo conjunto) e triagem
  PROMISING/NULL/INCONCLUSIVE/BLOCKED idênticos à regra congelada no
  runbook; censura (timeout nunca some), agrupamento por tarefa e relato
  de todos os braços/tarefas/seeds presentes.
- Dez mecanismos H01–H10 com hipótese de uma linha e família de técnica
  existente apontada para checagem de novidade; nomes não provam novidade.
- Final P71 novo e fechado reservado, sem caminho referenciado.

## Limitações registradas (não bloqueantes para o congelamento)

- Triagem de seis tarefas/três seeds não garante poder nem confirmação;
  é escolha operacional de desenho.
- Sobreposições de literatura são ponteiros de revisão, não vereditos;
  cada hipótese passa por revisão própria antes de medir.

## Veredito

`accepted` para congelamento do pré-registro P60. Esta revisão não
certifica novidade, ganho ou qualquer resultado futuro das dez hipóteses.
