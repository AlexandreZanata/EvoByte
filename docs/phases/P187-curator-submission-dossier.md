# P187 — Dossiê formal de submissão aos curadores externos (selo final)

**Status:** Completed.
**Programa:** Descoberta na Fronteira (P171–P190, D042). Trilhas A, B e fundação comum.
**Dependência:** P186 (auditoria de novidade) concluída; branch a partir de `main`.
**Owner:** agente executor prepara; **autor correspondente humano submete** (o agente nunca envia e-mail em nome de ninguém).
**Branch:** `codex/p187-curator-submission-dossier`.
**Leia antes:** [`AGENTS.md`](../../AGENTS.md), [regras do programa P171–P190](README.md#programa-de-descoberta-na-fronteira-p171p190-d042), [`docs/phases/P186-world-literature-novelty-dual-audit.md`](P186-world-literature-novelty-dual-audit.md).

## Por que esta fase existe

O selo final de uma descoberta é externo: o curador da tabela (Dan Gordon / LJCR para
covering, Markus Grassl para QECC, editores do OEIS para sequências) aceita e publica o
objeto. Esta fase gera o pacote formal de submissão por curador — com certificado,
verificador, reprodução e minuta — e registra o protocolo de acompanhamento. Sem
`CONFIRMED` na P186, o pacote gerado é o de **resultado nulo/empate** (igualmente honesto e
igualmente arquivado).

## Pergunta falsificável da fase

> Para cada curador relevante existe um pacote completo e autocontido (objeto + verificador +
> reprodução + minuta) pronto para submissão humana, e o registro de acompanhamento existe
> com status inicial `pending_human_submission`?

## Fatos de partida

| Fato | Fonte |
|---|---|
| Curadores: Dan Gordon (LJCR/coverings), Markus Grassl (codetables.de), editores do OEIS | Padrão do programa; contatos via sites oficiais (não listar e-mails pessoais aqui) |
| O que cada curador aceita (formato de submissão) | Sites oficiais na data da execução (registrar URL+data; se indisponível, `not_obtained`) |
| Objetos a submeter | Vereditos P186 (`CONFIRMED` + certificados) ou empates/nulos documentados |
| Minuta honesta existe como modelo | P167 §5 (minuta de comunicação, adaptar por curador) |

## Escopo

**Arquivos que você pode criar:**
- `scripts/build_curator_package.py` (monta um diretório por curador com tudo necessário)
- `dist/curator-submissions/<curador>/` — **não** commitado (contém cópias; o índice commitado lista hashes)
- `docs/research/p187-curator-packages-index.json` (índice commitado: curador, arquivos, SHA-256, status)
- `tests/test_curator_package.py` (só lógica: completude do pacote, minutas, índice; suíte < 3 s)
- `docs/research/p187-curator-dossier.md` (minutas + protocolo de acompanhamento)

**Arquivos que você pode editar:**
- `docs/phases/P187-curator-submission-dossier.md`: só a linha de Status e o bloco final de execução.

**Proibido:**
- o agente enviar e-mail, abrir issue/ticket ou contatar curadores em nome de qualquer pessoa;
- incluir endereço pessoal de terceiros nos arquivos commitados;
- testes com rede, envio ou dependências externas.

## Trabalho ordenado

### Passo 1 — Branch

```bash
git status --short
git switch main && git pull --ff-only 2>/dev/null || git switch main
git switch -c codex/p187-curator-submission-dossier
test -f experiments/p186-novelty-audit.json || { echo "P186 NAO CONCLUIDA"; exit 1; }
```

### Passo 2 — `scripts/build_curator_package.py`

Para cada curador em `[ljcr_gordon, grassl_codetables, oeis_editors]`:

- monta `dist/curator-submissions/<curador>/` com: `README.md` (o que é, como verificar em
  3 comandos), `certificate.json` (o objeto, se houver `CONFIRMED`; senão
  `null-result-notice.md`), `verify_*.py` (cópia do verificador autônomo da P184),
  `reproduce.sh` (3 comandos literais), `submission-letter.md` + `submission-letter.txt`
  (minuta adaptada: o que se alega, o que NÃO se alega, hashes).
- escreve `docs/research/p187-curator-packages-index.json` com a árvore de arquivos e
  SHA-256 de cada um + `status: pending_human_submission` por pacote.
- **Não envia nada.** O envio é ato humano posterior, fora do repo.

Conteúdo por veredito: `CONFIRMED` → pacote de alegação; só empates/nulos → pacote de
resultado nulo/empate (com os mesmos verificadores e reprodução — curadores também
publicam correções e confirmações).

### Passo 3 — Testes `tests/test_curator_package.py` (todos < 0,2 s; suíte < 3 s)

1. `test_package_has_all_artifacts`: cada pacote tem README, certificado-ou-aviso-de-nulo, verificador, reproduce.sh e as duas minutas.
2. `test_index_matches_disk_hashes`: o índice referencia arquivos existentes com SHA-256 corretos.
3. `test_letters_make_no_unchecked_claims`: as minutas não contêm as palavras `novo`/`new`/`record`/`quebramos` salvo acompanhadas de referência a veredito `CONFIRMED` do JSON da P186 (checagem textual mecânica).
4. `test_status_is_pending_human`: todo pacote nasce `pending_human_submission`; nenhum status de "enviado"/"aceito" é marcado pelo agente.

### Passo 4 — Dossiê `docs/research/p187-curator-dossier.md`

As três minutas (Markdown + texto puro cada), o protocolo de acompanhamento (quem submete,
quando reconfirmar, como registrar aceite/recusa com data e evidência) e a declaração:
"nenhuma submissão foi enviada por agente; todo envio é ato humano posterior e registrado aqui."

## Regras de parada (PARE, não commite, reporte)

- Qualquer minuta afirmar novidade sem `CONFIRMED` correspondente.
- Qualquer endereço pessoal de terceiro nos arquivos.
- Qualquer teste > 0,2 s ou suíte > 3 s; qualquer rede/envio em `tests/`.
- Falha no pytest ou no `make verify`.

## Gate de saída

```bash
git diff --check
python3 -m pytest tests/test_curator_package.py -q -m "not slow"   # FAST LOOP, ~1s
python3 scripts/build_curator_package.py --out dist/curator-submissions --index docs/research/p187-curator-packages-index.json
python3 -m pytest tests/test_curator_package.py -q                 # FINAL GATE, < 3s
make verify
git status --short
```

## Commit & Push (obrigatório)

```bash
git add scripts/build_curator_package.py tests/test_curator_package.py \
  docs/research/p187-curator-packages-index.json docs/research/p187-curator-dossier.md \
  docs/phases/P187-curator-submission-dossier.md .gitignore
git diff --cached --check
git commit -m "feat(research): implement p187 curator submission dossier"
git push -u origin HEAD
gh pr create --base main \
  --title "feat(research): p187 curator dossier" \
  --body-file /tmp/evobyte-p187-pr.md
git status --short
```

O corpo do PR (`/tmp/evobyte-p187-pr.md`) traz: problema, comportamento resultante, comandos de
validação exatos, o que cada pacote contém, limitações (nada foi enviado; envio é humano) e o
link do dossiê. **Nota:** se `dist/curator-submissions/` precisar de exceção no `.gitignore`,
ela entra neste commit como mudança mínima documentada (mesmo padrão da P167); o conteúdo dos
pacotes em si permanece não-versionado, só o índice com hashes é commitado.

## Registro de Execução

- **Script de Montagem:** [`scripts/build_curator_package.py`](../../scripts/build_curator_package.py) (gera diretórios autocontidos por curador com README, aviso de nulo, verificador autônomo, script de reprodução e minutas).
- **Diretórios dos Pacotes:** `dist/curator-submissions/` (`ljcr_gordon`, `grassl_codetables`, `oeis_editors`) mantidos não-versionados (ignorados pelo git).
- **Índice Commitado:** [`docs/research/p187-curator-packages-index.json`](../research/p187-curator-packages-index.json) (rastreia os 18 arquivos, seus hashes SHA-256 e o status `pending_human_submission`).
- **Suíte de Testes:** [`tests/test_curator_package.py`](../../tests/test_curator_package.py) (5/5 testes aprovados em 0,15 s; zero rede; validação de minutas honestas e conformidade de hashes).
- **Dossiê e Protocolo:** [`docs/research/p187-curator-dossier.md`](../research/p187-curator-dossier.md) com as 3 minutas (MD + TXT), cronograma de follow-up e a declaração de não-envio por agentes.
