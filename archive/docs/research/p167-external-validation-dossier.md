# Dossiê de validação externa e exportação de certificados autônomos (P167)

- **Fase:** P167 — Dossiê de validação externa e exportação de certificados autônomos
- **Data:** 2026-10-22
- **Dependência:** P166 (campanha pré-registrada) concluída
- **Verificador autônomo:** [`scripts/verify_certificate_standalone.py`](../../scripts/verify_certificate_standalone.py)
- **Exportador de certificados:** [`src/evobyte/certificate_exporter.py`](../../src/evobyte/certificate_exporter.py)
- **Certificado de exemplo:** [`dist/external-validation/sample_certificate.json`](../../dist/external-validation/sample_certificate.json)

---

## 1. Por que esta fase existe

Em matemática, nenhum pesquisador ou mantenedor de tabela aceita um resultado porque "o
software EvoByte disse que é válido". O resultado precisa ser **auto-contido e externamente
verificável**. Esta fase entrega:

1. o certificado da solução exportado em JSON padronizado;
2. um script de verificação **independente**, que usa **exclusivamente a biblioteca padrão do
   Python** (sem `numpy`, sem `scipy`, sem dependências internas do projeto);
3. um caminho de 3 comandos para qualquer pesquisador atestá-lo em menos de 1 segundo;
4. a minuta padronizada de comunicação formal com a comunidade científica externa.

## 2. O que o certificado contém

| Campo | Significado |
|---|---|
| `certificate_version` | Versão do formato do certificado (`1.0.0`) |
| `target_id` | Alvo do catálogo pré-registrado (`vanderwaerden_w3_3`) |
| `certificate_type` | `vanderwaerden` ou `schur` |
| `candidate_length` | Tamanho $N$ do objeto certificado (26) |
| `coloring` / `partition` | O objeto matemático certificado (vetor de cores / partição) |
| `r`, `k` | Parâmetros necessários à verificação (3 cores, PA de 3 termos) |
| `reference_literature` | Referência bibliográfica da cota contra a qual se compara |
| `sha256_checksum` | SHA-256 do JSON canônico de `{certificate_type, target_id, candidate, parameters}` — ou seja, do **objeto matemático** certificado |
| `sha256_scope` | Declara explicitamente o escopo do checksum interno |
| `reproduction_seed` | Semente que reproduz a busca que gerou o candidato |
| `provenance` | Algoritmo, orçamento, avaliações e tempo da execução de origem |

**Distinção importante:** o `sha256_checksum` interno identifica o **objeto matemático**
certificado; o verificador autônomo imprime o SHA-256 do **arquivo** recebido, que é
outro valor (o arquivo traz metadados adicionais). Os dois são publicados para que a
cadeia de custódia não dependa de interpretation.

## 3. Guia passo a passo para um pesquisador externo

Três comandos, sem instalar o pacote `evobyte`, sem `numpy`, sem rede:

```bash
# 1. Baixar o verificador e o certificado (qualquer mirror do repositório ou anexo do e-mail)
curl -O https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/scripts/verify_certificate_standalone.py
curl -O https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/dist/external-validation/sample_certificate.json

# 2. Verificar o certificado com Python 3.9+ limpo
python3 verify_certificate_standalone.py sample_certificate.json

# 3. Conferir o hash do arquivo baixado contra o publicado no dossiê
sha256sum sample_certificate.json
```

Saída esperada do passo 2:

```text
[*] Certificate target: vanderwaerden_w3_3 (Type: vanderwaerden)
[*] File SHA-256: b77e1f59ebb7679ce91c7ee28e19acc5f81503346dd2b39a63914205d6725a47
[SUCCESS] VERIFIED: zero monochromatic 3-term APs in 1..26
```

Código de saída `0` significa certificado aceito; `1` significa recusado (e a recusa vai
para `stderr`).

### O que o verificador autonomyamente decide

O script **não** confia em nenhum campo do certificado além do objeto e dos parâmetros:
- `verify_vdw_pure` enumera **todas** as progressões aritméticas de $k$ termos com
  $d \le (N-1)/(k-1)$ e rejeita a coloração se encontrar uma monocromática;
- `verify_schur_pure` testa todos os pares $(x, y)$, $x \le y$, dentro de cada classe e
  rejeita se $x + y$ pertence à mesma classe;
- cores/classes fora do intervalo permitido são rejeitadas.

O verificador não usa `numpy`, `scipy` nem qualquer módulo do `evobyte`: apenas `json`,
`sys` e `hashlib` da biblioteca padrão.

## 4. Certificado de exemplo e sua origem

O certificado publicado **não** é um artefato sintético: é o objeto exato que a campanha
pré-registrada da P166 produziu e certificou.

| Campo | Valor |
|---|---|
| Alvo | `vanderwaerden_w3_3` (empate com o recorde publicado $W(3,3) = 27$) |
| Origem | Campanha pré-registrada P166, Tabu Search, semente 42, orçamento 10,0 s |
| Avaliações até o hit | 27.517 |
| Tempo até o hit | 1,174 s |
| SHA-256 do objeto (convenção da campanha P166) | `00775b4c5a10e2393ca8eb1b9fffe6561faa0ba90fa1bab68a4e554c1d2da4aa` |
| SHA-256 do objeto certificado (`sha256_checksum` do certificado) | `96cdfc64bd9cc48085c5544e8ce47813a6d3d6a26dd64d66e3dc83819425c655` |
| SHA-256 do arquivo | `b77e1f59ebb7679ce91c7ee28e19acc5f81503346dd2b39a63914205d6725a47` |
| Verificação interna (`evobyte.target_catalogue`) | `valid: zero monochromatic 3-term APs in 1..26 with 3 colors` |
| Verificação externa (`verify_certificate_standalone.py`) | `SUCCESS` |

O hash `00775b4c…` é **exatamente** o `candidate_sha256` registrado no trial
`10.0s|vdw_3_3_26|TabuSearch|seed 42` de `experiments/p166-campaign/summary.json`, o que
fecha a cadeia de custódia: campanha → certificado → verificação externa independente.

## 5. Minuta de comunicação formal

### 5.1 Markdown

```markdown
Subject: Certificate of a 3-coloring of [1..26] with no monochromatic 3-term
arithmetic progression (W(3,3) >= 27)

Dear colleagues,

We submit an independently verifiable certificate for the following statement.

  Claim. There exists a map c: {1,...,26} -> {1,2,3} such that no arithmetic
  progression of length 3 in {1,...,26} is monochromatic under c. Equivalently,
  W(3,3) >= 27.

Certificate. A 3-coloring of {1,...,26} with no monochromatic 3-term arithmetic
progression is published as `sample_certificate.json` (26 entries, values in
{1,2,3}).

Verification. The certificate is checkable with a self-contained script that uses
only the Python standard library:

  python3 verify_certificate_standalone.py sample_certificate.json

The script enumerates every 3-term arithmetic progression of {1,...,26} and
reports SUCCESS (exit code 0) when none is monochromatic. The SHA-256 of the
distributed file is

  b77e1f59ebb7679ce91c7ee28e19acc5f81503346dd2b39a63914205d6725a47

The SHA-256 of the certified object (canonical JSON of the coloring together with
its parameters) is

  96cdfc64bd9cc48085c5544e8ce47813a6d3d6a26dd64d66e3dc83819425c655

Provenance. The coloring was found by a tabu search over single-site recolorings,
under a wall-clock budget of 10 seconds with seed 42, in a campaign whose targets,
budget and success criterion were registered before the run.

Relation to the literature. W(3,3) = 27 is a published exact value (Chvatal, 1970).
The object above reproduces that value; it does not claim a new record. We report
it as an equal record, not as an improvement, and we make no novelty claim.

We are releasing the certificate and the verifier under an open license so that the
statement can be checked independently by anyone with Python 3.9 or later.

Kind regards,
EvoByte Research Consortium
```

### 5.2 Texto puro

```text
Subject: Certificate of a 3-coloring of [1..26] with no monochromatic 3-term
arithmetic progression (W(3,3) >= 27)

Dear colleagues,

We submit an independently verifiable certificate for the following statement.

  Claim. There exists a map c: {1,...,26} -> {1,2,3} such that no arithmetic
  progression of length 3 in {1,...,26} is monochromatic under c. Equivalently,
  W(3,3) >= 27.

Certificate. A 3-coloring of {1,...,26} with no monochromatic 3-term arithmetic
progression is published as sample_certificate.json (26 entries, values in
{1,2,3}).

Verification. The certificate is checkable with a self-contained script that uses
only the Python standard library:

  python3 verify_certificate_standalone.py sample_certificate.json

The script enumerates every 3-term arithmetic progression of {1,...,26} and
reports SUCCESS (exit code 0) when none is monochromatic. The SHA-256 of the
distributed file is

  b77e1f59ebb7679ce91c7ee28e19acc5f81503346dd2b39a63914205d6725a47

The SHA-256 of the certified object (canonical JSON of the coloring together with
its parameters) is

  96cdfc64bd9cc48085c5544e8ce47813a6d3d6a26dd64d66e3dc83819425c655

Provenance. The coloring was found by a tabu search over single-site recolorings,
under a wall-clock budget of 10 seconds with seed 42, in a campaign whose targets,
budget and success criterion were registered before the run.

Relation to the literature. W(3,3) = 27 is a published exact value (Chvatal, 1970).
The object above reproduces that value; it does not claim a new record. We report
it as an equal record, not as an improvement, and we make no novelty claim.

We are releasing the certificate and the verifier under an open license so that the
statement can be checked independently by anyone with Python 3.9 or later.

Kind regards,
EvoByte Research Consortium
```

## 6. Limitações e escopo honesto

1. **O certificado é um empate com o recorde publicado, não um recorde novo.** $W(3,3) = 27$
   é um valor exato publicado (Chvátal, 1970). O certificado reproduz esse valor; a minuta
   acima declara isso explicitamente e não usa a palavra "novo".
2. **A verificação externa confirma a afirmação, não a novidade.** O script diz que a
   coloração é válida; ele não pode dizer se $W(3,3) = 27$ continua sendo o valor
   exato. Qualquer afirmação de superioridade exigiria um certificado de um objeto que a
   literatura declara inexistente — e, no catálogo da P163, esses objetos são provadamente
   inexistentes para os alvos atacados.
3. **Um único tipo de certificado é exportado como exemplo** (`vanderwaerden`). O
   exportador e o verificador suportam também `schur`, coberto por teste automatizado, mas
   o exemplo público é o de van der Waerden.
4. **O `sha256_checksum` interno e o hash do arquivo são valores diferentes**, por
   desenho: o primeiro identifica o objeto matemático, o segundo o arquivo distribuído. Os
   dois escopos estão declarados no próprio certificado (`sha256_scope`).
5. **Reprodutibilidade da busca**: o certificado fixa a semente e o orçamento, mas o
   candidato final depende do relógio de parede (a trajetória pode diferir entre máquinas).
   O **certificado em si** é determinístico e verificável; a busca que o produz é
   estatisticamente reprodutível, não bit a bit.
6. **Não há dockerização nem assinatura criptográfica**: a garantia aqui é a
   reprodutibilidade do objeto e a verificação independente, não a autenticidade da origem.

## 7. Reprodução

```bash
python3 -m pytest tests/test_standalone_verifier.py -q
python3 scripts/verify_certificate_standalone.py dist/external-validation/sample_certificate.json
python3 -m pytest tests -q
make verify
```
