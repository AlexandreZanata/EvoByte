# Parecer — p54-statistical-review (2026-10-07)

- Responsável: Alexandre (delegação expressa D019, 2026-10-06).
  Executor deste parecer: agente executor (identificado).
- Revisão examinada: `docs/phases/P54-matched-budget-pilot.md` (veredito
  DROP: clássico exato 30/30; híbrido 29/30 porém 3–7× mais lento;
  procedimento pareado e censura exigem revisão estatística antes de medir)
  e `experiments/p54-pilot-report.json` (dados originais preservados).
- Escopo: uso do resultado P54 na base técnica P58.
- Justificativa: DROP mantido e modelo desligado — nenhum caminho do
  auditor P58 carrega ou executa `p53-proposer.pt` (só confere seu hash
  como raw). A revisão estatística prévia está ausente e o intervalo
  publicado é exploratório (condicionado aos sucessos); não se renomeia
  revisão posterior como prévia nem se autoriza KEEP ou ganho de
  descoberta (braço Horner com fórmula privada não sustenta comparação
  justa). Uso admitido somente como referência histórica do DROP e da
  análise exploratória.
- Disposição: `reference_only`.
- Usos permitidos: `reconciliation-audit`, `drop-reference`,
  `exploratory-stats-reference`.
- Usos proibidos: `keep-claim`, `gain-claim`, `confirmatory-claim`,
  `novelty-claim`, `final-test`, `superiority-claim`.
- Aprovação científica: `pending` (procedimento estatístico). A restrição
  acima dispensa essa aprovação para o escopo técnico atual; não a concede.
- Esta disposição não certifica retrospectivamente limiares, revisão prévia,
  independência, ganho ou descoberta.
