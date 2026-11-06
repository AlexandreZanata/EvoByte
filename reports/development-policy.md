# Braços aprendido e sem treino em ensaios curtos

**Protocolo:** P0-development-v1 (`3811a92f...`)  
**Manifesto:** `configs/development-policy.json`  
**Hash do manifesto:** `c991ce46720e429fe43eeb59eb36a25fd7b5ebfca9d22330f3304e62a26e34e0`  
**Commit da execução:** `5317ffd56671ab9dea00934193df25613384b8a4`  
**Data:** 6 de novembro de 2026

Este relatório cobre apenas ensaios curtos de integração. Validade não prova
novidade nem optimalidade. A ressalva F3 sobre o harness de eventos continua
válida para F04-T05/F04-T06 e campanhas de 600 s; nenhuma delas foi iniciada.

---

## 1. Escopo

- `local_linear`: treina do zero em cada execução, usando `local_uniform` como
  gerador de completações e o alvo de curto horizonte; pesos ajustados uma vez.
- `local_untrained`: mesmas 12 características e mesmo motor local, pesos
  `N(0,1)` sorteados na semente de inicialização, sem treino e sem atraso
  artificial.
- Tamanhos `n ∈ {8,10,12,16}`, dois blocos novos (`2` e `3`), 60 s por execução.
- Total: 2 métodos × 4 tamanhos × 2 blocos = **16 execuções**, 960 s reservados.
- Parâmetros locais iniciais da grade P0: `k_max=1`, `S=50`; `local_linear` com
  `ridge_lambda=1.0`. Não é o motor final tunado.

Streams derivados por bloco, método e n:

```text
índice: local_linear=4, local_untrained=5
base = bloco*100000 + n*100 + índice*10
initialization = base+1; data = base+2; completion = base+3;
search = base+4; perturbation = base+5
```

Cada execução recebeu configuração canônica, supervisor, ledger, reserva antes do
spawn, certificado vazio de preflight, checkpoint, inventário e certificado final.
O trabalhador da política grava eventos incrementalmente, sem o dump pós-busca
que causou timeouts na F03.

---

## 2. Resultados por execução

| método | n | bloco | treino | pares | ajuste (s) | m | certificado | parede (s) | aval. caract. | eventos |
|---|---:|---:|---|---:|---:|---:|---|---:|---:|---:|
| `local_linear` | 8 | 2 | trained | 4096 | 0.0005 | 10 | CERTIFIED | 54.2 | 499447 | 218107 |
| `local_linear` | 10 | 2 | trained | 4096 | 0.0005 | 15 | CERTIFIED | 54.3 | 421922 | 91829 |
| `local_linear` | 12 | 2 | trained | 4096 | 0.0005 | 18 | CERTIFIED | 54.3 | 441847 | 50153 |
| `local_linear` | 16 | 2 | trained | 4096 | 0.0005 | 28 | CERTIFIED | 54.2 | 338613 | 16182 |
| `local_untrained` | 8 | 2 | not_trained | — | 0.0000 | 7 | CERTIFIED | 54.3 | 598524 | 123912 |
| `local_untrained` | 10 | 2 | not_trained | — | 0.0000 | 9 | CERTIFIED | 54.4 | 297800 | 41014 |
| `local_untrained` | 12 | 2 | not_trained | — | 0.0000 | 18 | CERTIFIED | 54.5 | 216846 | 25142 |
| `local_untrained` | 16 | 2 | not_trained | — | 0.0000 | 28 | CERTIFIED | 54.6 | 154409 | 7133 |
| `local_linear` | 8 | 3 | trained | 3687 | 0.0028 | 10 | CERTIFIED | 54.5 | 173576 | 75801 |
| `local_linear` | 10 | 3 | trained | 3803 | 0.0009 | 15 | CERTIFIED | 54.7 | 158766 | 34301 |
| `local_linear` | 12 | 3 | trained | 3878 | 0.0010 | 18 | CERTIFIED | 54.8 | 151597 | 17123 |
| `local_linear` | 16 | 3 | trained | 3519 | 0.0010 | 28 | CERTIFIED | 55.0 | 117962 | 5533 |
| `local_untrained` | 8 | 3 | not_trained | — | 0.0000 | 9 | CERTIFIED | 54.5 | 213526 | 60066 |
| `local_untrained` | 10 | 3 | not_trained | — | 0.0000 | 9 | CERTIFIED | 54.5 | 247914 | 34126 |
| `local_untrained` | 12 | 3 | not_trained | — | 0.0000 | 18 | CERTIFIED | 54.3 | 467551 | 53323 |
| `local_untrained` | 16 | 3 | not_trained | — | 0.0000 | 28 | CERTIFIED | 54.3 | 361312 | 17183 |

Totais:

- 16 tentativas, **16 exit 0**, **16 certificados CERTIFIED**, 0 overrun,
  0 reservas abertas;
- 8/8 `local_linear` treinados; 3519–4096 pares; ajuste < 0,003 s;
- ledger: **871,30 s** consumidos de 960 s reservados; saldo 88,70 s;
- desenvolvimento acumulado: 1.920 s (F03) + 871,30 s = **2.791,30 s** de 2.880 s.

---

## 3. Comparação descritiva

Referências publicadas do P0 para os tamanhos de desenvolvimento: `10, 15, 18,
28`. Igualdade é comparação, não prova de optimalidade.

| método | n | m bloco 2 | m bloco 3 | referência P0 |
|---|---:|---:|---:|---:|
| `local_linear` | 8 | 10 | 10 | 10 |
| `local_linear` | 10 | 15 | 15 | 15 |
| `local_linear` | 12 | 18 | 18 | 18 |
| `local_linear` | 16 | 28 | 28 | 28 |
| `local_untrained` | 8 | 7 | 9 | 10 |
| `local_untrained` | 10 | 9 | 9 | 15 |
| `local_untrained` | 12 | 18 | 18 | 18 |
| `local_untrained` | 16 | 28 | 28 | 28 |

- `local_linear` igualou a referência P0 nos quatro tamanhos e nos dois blocos.
- `local_untrained` ficou abaixo em n=8/10 e igualou n=12/16; o controle é mais
  fraco onde a política treinada agrega valor, sem declarar superioridade
  científica.
- O efeito de teto nos valores P0 limita a discriminação entre métodos.

---

## 4. Custos e integração

- Eventos da busca gravados incrementalmente; nenhum timeout pós-busca.
- Custo de características medido pelo seletor: 117.962 a 598.524 avaliações de
  características por execução; consultas de máscara/BFS contabilizadas no
  `search-result.json`.
- Ajuste ridge < 3 ms em todas as execuções; geração de dados dentro da janela de
  11,5 s; busca restante até o marco de 54 s.
- Streams separados para inicialização, dados, completações, busca e perturbação.
- `local_linear` treinou do zero em cada execução, sem reutilização de pesos.
- Smoke de integração separado (20 s + 6 s) consumiu 23,86 s na quota de
  testes/harness, fora das 16 tentativas.

Evidência local: `runs/development-policy/development-policy/<run_id>/` com
config, ambiente, eventos do supervisor/ledger, eventos da busca incremental,
checkpoint, inventário, candidato, envelope, certificado final e
`search-result.json`; `runs/development-policy/ledger.json`,
`driver-summary.json` e `campaign-summary.json`.

---

## 5. Limitações e portões

- Parâmetros locais e `ridge_lambda` ainda não são o motor tunado de F04-T05/T06.
- Apenas ensaios curtos de integração; nenhuma campanha de 600 s ou tamanho final.
- O controle sem treino é uma referência de inicialização, não uma política
  aprendida.
- A ressalva F3 sobre o harness de eventos permanece para F04-T05/T06; o
  trabalhador incremental desta tarefa é evidência de integração curta, não
  substitui a tarefa de reparo formal se exigida.
- Nenhum resultado é declarado ótimo, superior ou generalizável.
