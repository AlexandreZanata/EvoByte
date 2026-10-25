# Dossiê de Validação Externa e Autônoma (Zero-Dependency) — P184

- **Status:** Concluído.
- **Programa:** Descoberta na Fronteira (P171–P190, D042).
- **Data:** 25 de outubro de 2026.
- **Verificador CLI:** `scripts/verify_frontier_certificate.py` (zero dependências além da biblioteca padrão do Python 3.9+).
- **Exportador Padronizado:** `src/evobyte/frontier_certificate_exporter.py`
- **Amostras em:** `dist/external-validation/frontier_sample_*.json`

---

## 1. Princípio Fundamental de Validação Externa

Uma descoberta científica em matemática e computação só é real quando qualquer pesquisador externo consegue auditá-la e reproduzir a sua verificação sem instalar dependências, compilar módulos ou confiar em código fechado.

O verificador [`scripts/verify_frontier_certificate.py`](file:///home/iiii/PESSOAL-PROJETOS-ALEXANDRE/EvoByte/scripts/verify_frontier_certificate.py):
1. Requer **apenas** Python 3.9+ padrão (`argparse`, `hashlib`, `json`, `sys`, `itertools`, `math`).
2. Funciona em qualquer sistema operacional (Linux, macOS, Windows) sem internet e sem privilégios de administrador.
3. Não importa `numpy`, `scipy` ou módulos internos do `evobyte`.
4. Executa em menos de 0,1 segundo para todos os certificados de calibração.

> **Declaração de Escopo:** *Nenhum certificado de exemplo desta fase alega recorde.* Todos os certificados distribuídos em `dist/external-validation/` são instâncias exatas de calibração destinadas a auditar a integridade dos verificadores.

---

## 2. Guia Rápido de 3 Comandos por Família

Qualquer usuário externo pode validar um certificado executando apenas três comandos no shell:

### A. Covering Designs ($C(v, k, t)$)
```bash
# 1. Obter o script e o certificado
curl -sSL https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/scripts/verify_frontier_certificate.py -o verify.py
curl -sSL https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/dist/external-validation/frontier_sample_covering.json -o sample_cov.json

# 2. Conferir integridade criptográfica SHA-256
sha256sum sample_cov.json  # Esperado: 07bfba962b113f04a3e10b5f2051f1b80bea8dad45169159c3e2035110bb2aec

# 3. Executar validação autônoma (exit code 0 = válido)
python3 verify.py sample_cov.json
```

### B. Partição Forte de Schur ($S(k)$)
```bash
curl -sSL https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/dist/external-validation/frontier_sample_schur.json -o sample_schur.json
sha256sum sample_schur.json  # Esperado: 85baeaa3a25ba903b884ccffef3b0ff5f7d0faef47c1cc85a4dd920b34005f34
python3 verify.py sample_schur.json
```

### C. Partição Fraca de Schur ($WS(k)$)
```bash
curl -sSL https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/dist/external-validation/frontier_sample_weak_schur.json -o sample_ws.json
sha256sum sample_ws.json  # Esperado: 89e2747ecc89d2e25bbd31c5e0e82e7c66f9762e0fe597222d4b8af24cb21685
python3 verify.py sample_ws.json
```

### D. Cap Sets em $\mathbb{F}_3^n$
```bash
curl -sSL https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/dist/external-validation/frontier_sample_cap_set.json -o sample_cap.json
sha256sum sample_cap.json  # Esperado: e895ab155bc628f921cb4b0e9717fcacf3e028f2422c2d9a0f196d8c4e539a46
python3 verify.py sample_cap.json
```

### E. Códigos Quânticos Estabilizadores QECC ($[[n, k, d]]$)
```bash
curl -sSL https://raw.githubusercontent.com/AlexandreZanata/EvoByte/main/dist/external-validation/frontier_sample_qecc_stabilizer.json -o sample_qecc.json
sha256sum sample_qecc.json  # Esperado: 599d4207dc1b0326cf363f3f53e86a60e97ecef309797aeaa7b629058771537c
python3 verify.py sample_qecc.json
```

---

## 3. Matriz de Validação Cruzada (Interno vs Standalone)

Todos os certificados de exemplo foram validados de forma cruzada por duas implementações independentes:
1. **Verificador Interno:** implementações no repositório (`frontier_catalogue.py`, `verify_certificate_standalone.py`, `qecc_verifier.py`).
2. **Verificador Autônomo:** script CLI zero-dependency (`verify_frontier_certificate.py`).

| Família | Certificado Amostra | Target ID | Verificador Interno | Verificador CLI Autônomo | Tempo Medido | SHA-256 do Arquivo |
|---|---|---|---|---|---|---|
| Covering Design | `frontier_sample_covering.json` | `fano_plane_c7_3_2` | `PASSED` (21/21 pares) | `[SUCCESS]` exit 0 | 27.0 ms | `07bfba962b113f04...` |
| Strong Schur | `frontier_sample_schur.json` | `schur_k2_n4` | `PASSED` (zero APs/somas) | `[SUCCESS]` exit 0 | 28.3 ms | `85baeaa3a25ba903...` |
| Weak Schur | `frontier_sample_weak_schur.json` | `weak_schur_k2_n8` | `PASSED` (zero somas $x<y$) | `[SUCCESS]` exit 0 | 31.0 ms | `89e2747ecc89d2e2...` |
| Cap Set | `frontier_sample_cap_set.json` | `cap_set_f3_3_size8` | `PASSED` (zero colineares) | `[SUCCESS]` exit 0 | 27.8 ms | `e895ab155bc628f9...` |
| QECC Stabilizer | `frontier_sample_qecc_stabilizer.json` | `qecc_steane_7_1_3` | `PASSED` ($[[7,1,3]]$ exato) | `[SUCCESS]` exit 0 | 27.2 ms | `599d4207dc1b0326...` |

---

## 4. Limites de Escala Declarados

- **Códigos Quânticos (QECC):** O verificador autônomo executa uma varredura ordenada por peso sobre o centralizador simplético em puro Python. Esse algoritmo exato de força bruta com poda por comutação tem complexidade proporcional a $\sum_{w=1}^d \binom{n}{w} 3^w$. Ele é ideal e instantâneo para instâncias de calibração ($n \le 10$, executando o Steane $[[7,1,3]]$ em $< 0.03\text{ s}$). Para códigos de fronteira em comprimentos maiores ($n \ge 14$), o programa utiliza o verificador vetorial matricial da Fase P179 (`src/evobyte/qecc_verifier.py`), que opera com vetorização simplética GF(2).
- **Covering Designs e Cap Sets:** A validação é linear no número de subconjuntos e quadrática no tamanho do cap set, garantindo execução em sub-segundo para todas as instâncias de calibração e escala de frontier.
