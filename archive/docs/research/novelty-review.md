# P72 Avaliação de Novidade — Alvo erdos-242 (2026-10-13)

Medição executada em árvore limpa com configuração congelada (entrega 1,
commit `4c65657`), pelo comando congelado `experiments/p72-run.sh`.
Nenhuma escrita versionada durante a execução (`git status` limpo após a execução).

## 1. Alvo e Literatura

- **Alvo nominado:** `erdos-242` ("Erdos Problem #242"), catalogado em
  `docs/research/open-problems.json` (`sha256=bd976f3b315bab263cbb956e5b016467b326994c984cfa74baa41efbd75b37c2`).
- **Enunciado:** Para todo $n > 2$, existem inteiros positivos distintos
  $1 \le x < y < z$ tais que $\frac{4}{n} = \frac{1}{x} + \frac{1}{y} + \frac{1}{z}$.
- **Fonte primária:** Thomas Bloom, Erdos Problems database, Problem 242 (https://www.erdosproblems.com/242).
- **Literatura consultada:** Erdős (1948), Mordell (1967), Elsholtz–Tao (2013), Bloom (2026).
- **Estado na literatura:** Aberto em geral; verificado computacionalmente na literatura até $n \le 10^{17}$.
  Identidades paramétricas cobrem classes modulares triviais (pares, $n \equiv 2 \pmod 3$, $3 \mid n$).
  A classe dura é de primos $n \equiv 1 \pmod{24}$.

## 2. Comando e Auditoria

```text
python3 benchmarks/science_matrix.py --acceptance-phase P72 --config experiments/p72-config.json --output /tmp/evobyte-p72-acceptance.json
```

- **Veredito:** `ACCEPTED`, achados: `[]`.
- **Identificadores:** `run_id=54e4999caf6a6bbf`, `revision=4c6565774a6f82bfec94b0ba12ef0bd6b1956605`, `dirty=''` (árvore limpa).
- **Configuração:** `experiments/p72-config.json`,
  `sha256=32911be189603dbe5b3ec8b0155899a335522740a66445f431803dd2e70f9c45`.
- **Saída externa:** `/tmp/evobyte-p72-acceptance.json`
  (`sha256=a4652ba6dc8e967b6f00d7cea144152327d353d43dbc60876ab9807c18106773`, 2731 bytes; transitória, não versionada).

## 3. Resultados Medidos

- **Candidatos avaliados:** 26.585.094 avaliações na janela estrita de busca ($M \le 10^9$).
- **Tempo total:** 1,24 s (campanha 0,92 s, bem abaixo do teto de 3600 s).
- **Instâncias da campanha:**
  1. $n = 1009$: solução encontrada $(253, 85100, 944524900)$, duplamente verificada exata.
     Classificação: `rediscovery` (âncora $k=3$ conhecida da literatura/P47/P57).
  2. $n = 10007$: solução encontrada $(2504, 2801960, 438506740)$, duplamente verificada exata.
     Classificação: `candidate` (instância computacional exata; novidade não sustentada como teorema).
  3. $n = 100003$: não encontrada na janela finita de busca.
     Classificação: `budget-exhausted` (busca limitada em janela, nunca `exhaustive-null`).

## 4. Avaliação de Novidade

- **Novo algoritmo:** Não. Módulos especulativos H01–H10 não obtiveram confirmação
  de ganho em P71 e permaneceram desligados. Utilizou-se exclusivamente a busca aritmética
  aceita com checadores duais exatos.
- **Novo teorema:** Não. A verificação finita de instâncias particulares não resolve a
  conjectura universal nem produz teorema geral.
- **Novidade sustentada:** Não sustentada. Soluções de instâncias em domínios já cobertos
  por computações mundiais ($n \le 10^{17}$) não constituem descoberta matemática inédita.
- **Conclusão:** Campanha encerrada de forma íntegra com classificações honestas
  (`rediscovery`, `candidate`, `budget-exhausted`), sem declarações indevidas de novidade
  ou solução da conjectura em aberto. O programa P58–P72 é concluído com integridade.
