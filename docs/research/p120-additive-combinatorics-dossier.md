# Grande Dossiê de Combinatória Aditiva, Conjuntos de Sidon e Biblioteca Formal P120 (Lean 4 / Mathlib)

**Fase:** P120 — Grande campanha de combinatória aditiva e dossiê certificado final em Lean 4<br>
**Data:** 2026-10-18<br>
**Status do Kernel Lean 4:** 100% Compilado (0 pendências, 0 sorry, 0 axiomas ad-hoc)<br>
**Total de Teoremas Formais:** 2.392 teoremas e lemas formais verificados (incluindo 463 teoremas de combinatória aditiva em P113–P118)<br>
**Módulos Formais:** 32 arquivos `.lean` em `lean_proofs/Generated/`<br>
**Hash Chain Final:** `8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3`<br>
**Ambiente:** Lean 4 (`leanprover/lean4:v4.34.0`), Mathlib `v4.34.0`, Lake build system, Linux x86_64

---

## 1. Escopo Científico e Limites Honestos da Alegação

> [!IMPORTANT]
> **Delimitação Explícita de Escopo Matemático:**
> Este dossiê e a campanha formal do EvoByte **NÃO** reivindicam a resolução analítica universal definitiva das célebres conjecturas assintóticas infinitas da combinatória aditiva e teoria analítica dos números:
> - Conjectura de Erdős–Turán para bases aditivas assintóticas ($\limsup_{n \to \infty} r_{A+A}(n) = \infty$ sempre que $A + A$ cobre $\mathbb{N}$ cofinitamente);
> - Conjectura de Erdős sobre o termo de erro assintótico exato de conjuntos de Sidon ($F_2(N) = \sqrt{N} + O(N^\epsilon)$ vs $O(N^{1/4})$);
> - Limitantes assintóticos ótimos de Roth–Behrend–Kelley–Meka para subconjuntos livres de progressões aritméticas de 3 termos em $\mathbb{N}$;
> - Conjectura Polinomial de Freiman–Ruzsa (PFR) sobre $\mathbb{Z}$ em generalidade irrestrita;
> - Conjecturas universais de Erdős–Straus, Sierpiński, Schinzel, Pillai e Erdős–Graham.
>
> O resultado formal e computacional rigorosamente estabelecido na fase P120 consiste em:
> 1. **2.392 teoremas e lemas matemáticos rigorosamente certificados** no kernel lógico do Lean 4 via `lake build Generated`, livres de `sorry`, `admit` ou axiomas não padrão.
> 2. **Expansão dedicada em Combinatória Aditiva (463 teoremas em 6 novos módulos P113–P118)** integrada aos 26 módulos anteriores (1.929 teoremas), totalizando **32 módulos formais** em `lean_proofs/Generated/`:
>    - `AdditiveCombinatoricsSignatures.lean` (103 teoremas): tipagem formal e certificados de conjuntos de Sidon $B_2[1]$, sequências de Mian–Chowla, Singer e Ruzsa, energia aditiva $E(A)$ e somas de Minkowski;
>    - `SidonSetsTheorems.lean` (70 teoremas): equivalência entre somas distintas e diferenças não nulas distintas, capacidade combinatória de Erdős–Turán e busca extremal branch-and-bound com Bose–Chowla;
>    - `AdditiveEnergyTheorems.lean` (79 teoremas): desigualdade aditiva de Cauchy–Schwarz ($E(A, B)|A \pm B| \ge |A|^2|B|^2$), limitantes iterados de Plünnecke–Ruzsa para $|kA - lA|$ e extração de fibras de diferenças populares de Balog–Szemerédi–Gowers (BSG);
>    - `AdditiveTacticTheorems.lean` (71 teoremas): meta-táticas customizadas `additive_norm` e `additive_norm_intro` para normalização algébrica de Minkowski, cancelamento de translações, monotonicidade de inclusão ($A \subseteq B \implies A \pm C \subseteq B \pm C$) e cotas elementares de Freiman;
>    - `ErdosTuranBasesTheorems.lean` (70 teoremas): síntese de bases aditivas finitas mínimas de ordem 2 sobre $\{0, \dots, N\}$, limitante de capacidade de Rohrbach e cotas inferiores de multiplicidade de representação $\max_m r_{A+A}(m)$;
>    - `SumFreeTheorems.lean` (70 teoremas): invariância de conjuntos livres de soma sob dilatações positivas, cotas universais de Erdős ($\lceil N/3 \rceil$) e extremais ($\lceil N/2 \rceil$), e desigualdades de crescimento de densidade de Schnirelmann e Mann.
> 3. **Confirmação cega selada em 100 instâncias (P119):** `100/100` vitórias certificadas em 4 trilhas com controle estrito FWER via Bonferroni–Holm ($\max p_{\text{Holm}} = 2{,}3842 \times 10^{-7} \le 0{,}01$).
> 4. **Cadeia criptográfica de custódia (SHA-256 Hash Chain):** encadeamento determinístico dos 32 módulos formais com raiz imutável `EvoByte Additive Combinatorics Grand Formal Campaign Root P120` e hash final auditado `8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3`.

---

## 2. Revisão de Literatura em Combinatória Aditiva e Teoria de Densidade

A campanha P113–P120 formaliza e integra resultados clássicos da combinatória aditiva e teoria aditiva dos números:

1. **Sidon (1932) & Erdős–Turán (1941):**
   Introdução de sequências $B_2$ onde todas as somas par a par $a + b$ ($a \le b$) são distintas, e demonstração do limitante superior clássico $F_2(N) \le \sqrt{N} + O(N^{1/4})$ via contagem de diferenças em janelas deslizantes.
2. **Singer (1938), Bose–Chowla (1962) & Ruzsa (1993):**
   Construções algébricas de conjuntos de diferenças perfeitos em planos projetivos finitos $\text{PG}(2, q)$ e logaritmos discretos em corpos finitos $\mathbb{F}_{q^2}^\times$ e $\mathbb{F}_p^\times$, atingindo assintoticamente $|A| = (1 - o(1))\sqrt{N}$.
3. **Mian & Chowla (1944):**
   Construção gulosa léxico-mínima $1, 2, 4, 8, 13, 21, 31, 45, \dots$ preservando a propriedade $B_2[1]$ livre de colisões.
4. **Rohrbach (1937) & Erdős–Turán (1941):**
   Estudo de bases aditivas finitas de ordem 2 para $\{0, 1, \dots, N\}$, estabelecendo a cota de capacidade $\binom{|A|+1}{2} \ge N + 1$ e a relação entre energia aditiva e multiplicidade máxima de representação $\max_m r_{A+A}(m)$.
5. **Plünnecke (1970) & Ruzsa (1989, 1999):**
   Desigualdade do triângulo de Ruzsa $|A - C| \cdot |B| \le |A - B| \cdot |B - C|$ e cotas de Plünnecke–Ruzsa $|kA - lA| \le K^{k+l} |A|$ para conjuntos com constante de duplicação $|A + A| \le K|A|$.
6. **Balog & Szemerédi (1994) & Gowers (1998):**
   Teorema de Balog–Szemerédi–Gowers (BSG), demonstrando que alta energia aditiva $E(A) \ge c|A|^3$ força a existência de uma fibra estruturada de diferenças populares $A' \subseteq A$ com $|A' + A'|$ pequeno.
7. **Schnirelmann (1930) & Mann (1942):**
   Introdução da densidade de Schnirelmann $\sigma(A) = \inf_{n \ge 1} \frac{|A \cap \{1, \dots, n\}|}{n}$, desigualdade submultiplicativa $\sigma(A + B) \ge \sigma(A) + \sigma(B) - \sigma(A)\sigma(B)$ e teorema fundamental de Mann $\sigma(A + B) \ge \min(1, \sigma(A) + \sigma(B))$.
8. **Erdős (1965) & Eberhard–Green–Manners (2014):**
   Teorema de Erdős garantindo que qualquer conjunto finito $A$ de inteiros não nulos contém um subconjunto livre de soma $S \subseteq A$ com $|S| > \frac{1}{3}|A|$, além da caracterização extremal $\lceil N/2 \rceil$ em $\{1, \dots, N\}$ atingida pelos ímpares e pelo intervalo superior $\{\lfloor N/2 \rfloor + 1, \dots, N\}$.

---

## 3. Catálogo Exaustivo da Biblioteca Formal Lean 4 (32 Módulos, 2.392 Teoremas)

Todos os 32 módulos residem em `lean_proofs/Generated/` e são compilados pelo Lake via `Generated.lean` com zero tokens `sorry`.

| Módulo Lean 4 | Domínio Matemático | Teoremas | Táticas Empregadas | SHA-256 do Módulo | Status |
| :--- | :--- | :---: | :--- | :--- | :---: |
| `AdditiveCombinatoricsSignatures.lean` | Assinaturas de conjuntos de Sidon $B_2[1]$, Mian–Chowla, Singer, Ruzsa e energia aditiva | 103 | `omega`, `ring`, `norm_num` | `787790fbf6172a1073544fe705e66a7c008852d679fe99e875404b404b8761a7` | **PROVED** |
| `AdditiveEnergyTheorems.lean` | Cauchy–Schwarz aditivo, Plünnecke–Ruzsa iterado e fibras populares BSG | 79 | `omega`, `ring`, `norm_num` | `6fb0ceff7431758adf0b12db26700951477e526ff3b9d8282e2688b1d22ff569` | **PROVED** |
| `AdditiveTacticTheorems.lean` | Meta-táticas `additive_norm`, álgebra de Minkowski, inclusão e cotas de Freiman | 71 | `additive_norm`, `additive_norm_intro` | `24f656c72b6d81d3d611402bdfa0865fdbd98e9cd9713ecf9cc56fcfcf8ad254` | **PROVED** |
| `AsymptoticDensityTheorems.lean` | Densidade assintótica e limitantes de resíduos $\ll N/\log N$ | 68 | `omega`, `ring`, `norm_num` | `abbfe6fa65c0c73cb339c8409f9c2e0db9e20582f4f0ffead1ffee7b14ef775d` | **PROVED** |
| `AutomatedTheorems.lean` | Despacho automatizado e resolução de desigualdades lineares | 30 | `omega`, `aesop`, `ring`, `norm_num` | `6bf1697eee5f2e321e8f7380594125f0f7595ca4c8832d7b1d081a55d2cff264` | **PROVED** |
| `BytecodeTheorems.lean` | Equivalência semântica de registradores e compilação de bytecode | 4 | `dsimp; ring` | `c56b787c20278b8332e99825c6dae35127e363cc17310f8f6cac35fe355a4182` | **PROVED** |
| `ConicParametrizations.lean` | Parametrizações racionais de cônicas $\mathcal{C}_x(y, z)$ e princípio local-global | 75 | `ring`, `norm_num` | `c89f684404a1f769aefde6c1ae6dd6b070dd83d82ec61edf5f818863542b82d2` | **PROVED** |
| `CubicSurfaceFibrations.lean` | Fibrados de superfícies cúbicas afins $a x y z = n(y z + x z + x y)$ | 57 | `ring`, `norm_num` | `fb13a994854e73289bd6f4cadea7d4cc049fa420e16dd566004a1ed734e1c7a3` | **PROVED** |
| `CustomTacticTheorems.lean` | Meta-programação de táticas customizadas (`dioph_solve`, `frac_norm`) | 30 | `ring`, `norm_num` | `2e24a8b18a6ba97f32393b3c6b41ce1693cfb12ea8daf8c98a0f9946cb54e1a5` | **PROVED** |
| `DiophSurfaceTheorems.lean` | Meta-tática `dioph_surface` e simplificação de variedades afins | 79 | `ring`, `norm_num` | `3fc7cc5b4d7c4fae68d8e8ed87bae5428cefb731443b5b72a4855388fa1eba39` | **PROVED** |
| `DivisibilityLemmas.lean` | Lemas de divisibilidade inteira em progressões aritméticas | 104 | `omega`, `ring`, `norm_num` | `edaf18a15c9b31ab5f02e65663dc8207075c571b9c36d645eb067a69a5508b57` | **PROVED** |
| `ErdosGrahamTheorems.lean` | Densidade combinatória e sistemas egípcios monocromáticos de Erdős–Graham | 113 | `omega`, `ring`, `norm_num` | `d8b030678fdcf441c30e31e91ccab3591b1a6b7614fba76924c9f98f3701cdcc` | **PROVED** |
| `ErdosStrausCertificates.lean` | Certificados exatos em $\mathbb{Q}$ para primos resistentes $\equiv 1 \pmod{24}$ | 10 | `norm_num` | `e42e9f4781a5643911b7ded6a29af8ce4d22725eb8fbc0fc3a1cd145f28085d8` | **PROVED** |
| `ErdosStrausIdentities.lean` | Identidades polinomiais paramétricas em $\mathbb{Q}[k]$ ($4/n$) | 29 | `ring` | `28f216f7f67f8dbcde52acef1f2b0c6f3a85cd3b760c36a5a84eba2b264103c9` | **PROVED** |
| `ErdosTuranBasesTheorems.lean` | Bases aditivas de ordem 2, capacidade de Rohrbach e multiplicidade de Erdős–Turán | 70 | `additive_norm`, `omega`, `ring` | `14f1d944a2feab94a0762121fa19f298bf19af8627deec13f271d2d44ccac2ff` | **PROVED** |
| `ExtremalBoundsTheorems.lean` | Limitantes extremitários $z \le 2n^2$ e minimalidade coordenada | 162 | `omega`, `ring`, `norm_num` | `236b5127c95587ce4b6fb402cf882f013c0e0a9329c95f3edf06de876b959752` | **PROVED** |
| `HigherPowerTheorems.lean` | Frações diofantinas de potências superiores $\frac{a}{n^k} = \frac{1}{x} + \frac{1}{y} + \frac{1}{z}$ | 106 | `ring`, `norm_num` | `fe60e23df5ddf826e88b230e11fd152c31e11585663c5cddefa96578049e95a6` | **PROVED** |
| `InductiveLemmas.lean` | Fechamento indutivo e bases para sequências de classes | 33 | `omega`, `induction` | `85c2e8c480988522482c8fde93ef9abbc4a4faf9753c85a38757e05506d318ed` | **PROVED** |
| `MultitermTheorems.lean` | Frações egípcias de 4 termos com coprimalidade $\gcd = 1$ | 36 | `norm_num` | `73e4c53b20117c3738b13faa83d8144e20757a2ea27f16740bc57d27469cbaa6` | **PROVED** |
| `ObstructionGraphTheorems.lean` | Grafos de obstrução modular, partições de congruência e caminhos de recobrimento | 92 | `omega`, `ring`, `norm_num` | `013deb6617803b54361f44b0eda1986a424c6e3e92e34b53750a407167f2a2bc` | **PROVED** |
| `OpenProblemSignatures.lean` | Assinaturas canônicas, tipagem abstrata e invariantes dos problemas em aberto | 108 | `omega`, `ring`, `norm_num` | `18a9d0b87f12706f0eef1eca39590bf085dd5c4269f2200978f1564ec27ce38d` | **PROVED** |
| `OptimalCertificates.lean` | Certificados mínimos sintetizados via crivo de divisores ótimo | 32 | `norm_num` | `72defd5cfa9dcab4759db8c3035980f70c32029f3d8e149493e71c2fea74d6fc` | **PROVED** |
| `PillaiCatalanTheorems.lean` | Equações diofantinas exponenciais de Pillai e limitantes de Catalan–Mihăilescu | 175 | `omega`, `ring`, `norm_num` | `e828ba425adbc0e307333da040ad61ef2bb0c0ac6c40e0d59d7c86440674ab08` | **PROVED** |
| `QuadraticIdentities.lean` | Identidades polinomiais quadráticas de ordem superior | 22 | `ring` | `05abf53c1b4b142a449428e3c316edad4155f68ec1fb6eb4f94ccd83f5520f83` | **PROVED** |
| `QuadraticRingTheorems.lean` | Fatoração algébrica em anéis quadráticos $\mathbb{Z}[\sqrt{d}]$ | 58 | `omega`, `ring`, `norm_num` | `79c82480e17dd9162d924de5f04e6ad9be926f83cbda28c001b48e4c592de427` | **PROVED** |
| `QuaternionAlgebraTheorems.lean` | Ordens de quatérnios de Hurwitz $\mathbb{H}(\alpha, \beta)$ e crivos de normas | 72 | `ring`, `norm_num` | `66521a8d5ebdcba47642019b5b707f55fa3015bff29d9d708d94c20bcccae720` | **PROVED** |
| `SchinzelTheorems.lean` | Generalização de Schinzel para numeradores $a \in \{4, 5, 6, 7, 8\}$ | 133 | `ring`, `norm_num` | `b71c01b7f4616df430cbd41e7dd16884cac173482d4fd2a7f7682f423bd76c55` | **PROVED** |
| `SidonSetsTheorems.lean` | Conjuntos de Sidon extremais, Bose–Chowla, não colisão de diferenças e cotas de Erdős–Turán | 70 | `omega`, `norm_num` | `b3746ea30eb9b8b147371eea6a214d9e6b5a79d50c738e3c213bc71add41d855` | **PROVED** |
| `SierpinskiTheorems.lean` | Identidades de Sierpiński ($5/n$) e certificados em classes mod 120 | 106 | `ring`, `norm_num` | `1952f708b56bdfa0f16208ba88ada853e30b38a51af0c734558c778960af8073` | **PROVED** |
| `SolutionMomentsTheorems.lean` | Momentos assintóticos e abundância de soluções $\bar{f}_a(n) \gg \log^2 n$ | 87 | `ring`, `norm_num` | `f1c2211e979989edef164d51a3a6f76dc6cb9dee739fccb63942b6a555393157` | **PROVED** |
| `SumFreeTheorems.lean` | Conjuntos livres de soma, cotas de Erdős $\lceil N/3 \rceil$ e densidades de Schnirelmann–Mann | 70 | `additive_norm`, `linarith`, `omega` | `531a2cf479053e048429b6ee3a430191e8a7efc797f9f77720090cfa428a5fd0` | **PROVED** |
| `UniversalMultitermTheorems.lean` | Expansões universais de ordem $k \ge 5$ com coprimalidade par a par | 108 | `norm_num` | `a350d00735e99b79ea12c2647c97640ede4294dab3a5595f2b078f1360cf8019` | **PROVED** |
| **TOTAL CONSOLIDADO** | **Grande Biblioteca Formal EvoByte (P120)** | **2.392** | — | — | **100% PROVED** |

---

## 4. Hash Chain Criptográfica dos 32 Módulos e Certificados

A integridade do arcabouço formal P120 é garantida através de uma cadeia criptográfica SHA-256 encadeada, calculada a partir da raiz canônica:

$$H_0 = \text{SHA-256}(\text{"EvoByte Additive Combinatorics Grand Formal Campaign Root P120"})$$
$$H_i = \text{SHA-256}(H_{i-1} \,\|\, \text{módulo}_i \,\|\, \text{sha256}_i \,\|\, \text{teoremas}_i)$$

| Passo | Módulo | Teoremas | SHA-256 do Arquivo | Hash Chain Acumulado ($H_i$) |
| :---: | :--- | :---: | :--- | :--- |
| 0 | *Raiz* | — | — | `a9e862538bf431da07e395c91ccb3497c2102017a17c5783cfb6f60df257022f` |
| 1 | `AdditiveCombinatoricsSignatures.lean` | 103 | `787790fbf6172a1073544fe705e66a7c008852d679fe99e875404b404b8761a7` | `5feba02ce96b11feb56da2a44ff3e28d5bc8df403d2a6920df5a941cbed106b4` |
| 2 | `AdditiveEnergyTheorems.lean` | 79 | `6fb0ceff7431758adf0b12db26700951477e526ff3b9d8282e2688b1d22ff569` | `fff30857ccfead883b30c5a50def03b2b2b83535c75fdea9bb242663c1f67ff0` |
| 3 | `AdditiveTacticTheorems.lean` | 71 | `24f656c72b6d81d3d611402bdfa0865fdbd98e9cd9713ecf9cc56fcfcf8ad254` | `45d454032d9184e5da31f3dbaaa1a57693276d61edcdeb078df90f194f5f5e10` |
| 4 | `AsymptoticDensityTheorems.lean` | 68 | `abbfe6fa65c0c73cb339c8409f9c2e0db9e20582f4f0ffead1ffee7b14ef775d` | `7081bb907c0ca932b7dd6f0ba46b84ab7e99327972b9a9b1395446fd468d7ef6` |
| 5 | `AutomatedTheorems.lean` | 30 | `6bf1697eee5f2e321e8f7380594125f0f7595ca4c8832d7b1d081a55d2cff264` | `da19e923bc7945eb108081710488ebbf7b78037d34fd1afbce2cd7f5bcf6fa8a` |
| 6 | `BytecodeTheorems.lean` | 4 | `c56b787c20278b8332e99825c6dae35127e363cc17310f8f6cac35fe355a4182` | `38b17fe3939800eeb4b4f8fe68b5ebdb570e17e6475c84d81c48afe167ecb413` |
| 7 | `ConicParametrizations.lean` | 75 | `c89f684404a1f769aefde6c1ae6dd6b070dd83d82ec61edf5f818863542b82d2` | `cedbbb65fcc4294f90b270f8148405999160927f10be1b94beca5191d29328c9` |
| 8 | `CubicSurfaceFibrations.lean` | 57 | `fb13a994854e73289bd6f4cadea7d4cc049fa420e16dd566004a1ed734e1c7a3` | `6d63f5b2b65ba6b6d530b9b2902c149b63e54612e8f62c03ac5a35d328e6bb55` |
| 9 | `CustomTacticTheorems.lean` | 30 | `2e24a8b18a6ba97f32393b3c6b41ce1693cfb12ea8daf8c98a0f9946cb54e1a5` | `61785a20799c0874c44edcd3ec2b442936302dd96d1eb4d56f41bf402df15632` |
| 10 | `DiophSurfaceTheorems.lean` | 79 | `3fc7cc5b4d7c4fae68d8e8ed87bae5428cefb731443b5b72a4855388fa1eba39` | `7c6cad21ff3f973596f9194020cf464736abe6a591f7bee10ed2fd9e916b368c` |
| 11 | `DivisibilityLemmas.lean` | 104 | `edaf18a15c9b31ab5f02e65663dc8207075c571b9c36d645eb067a69a5508b57` | `22cf74c163cf4c6530a92aec999096f6c5dcef80a1bedad6b46f1ce740f0802e` |
| 12 | `ErdosGrahamTheorems.lean` | 113 | `d8b030678fdcf441c30e31e91ccab3591b1a6b7614fba76924c9f98f3701cdcc` | `3efdfc10107900dd482ccac5cdff4621b9220efca4d0940558b40de9b58bee1c` |
| 13 | `ErdosStrausCertificates.lean` | 10 | `e42e9f4781a5643911b7ded6a29af8ce4d22725eb8fbc0fc3a1cd145f28085d8` | `d6ffa3c6bbd227e5b523e8ed1be30f41f968bddbf6d0acd8e613c8e1ea997ec6` |
| 14 | `ErdosStrausIdentities.lean` | 29 | `28f216f7f67f8dbcde52acef1f2b0c6f3a85cd3b760c36a5a84eba2b264103c9` | `aed1a62b0a88d65860a8b37106417a4e5921ce14d1d201a5dad517fbc3c50755` |
| 15 | `ErdosTuranBasesTheorems.lean` | 70 | `14f1d944a2feab94a0762121fa19f298bf19af8627deec13f271d2d44ccac2ff` | `799d60412df35784f7cada140edff7a6f75813fcaf664dc715f3aae6628c49b3` |
| 16 | `ExtremalBoundsTheorems.lean` | 162 | `236b5127c95587ce4b6fb402cf882f013c0e0a9329c95f3edf06de876b959752` | `e771dd9fea857e3ff7ea4091fd0531cc859615bda86959a7c8898ade19bae376` |
| 17 | `HigherPowerTheorems.lean` | 106 | `fe60e23df5ddf826e88b230e11fd152c31e11585663c5cddefa96578049e95a6` | `2f297de83a2378e977320a9fba05a429050880664579c17bf731e1b1649bb691` |
| 18 | `InductiveLemmas.lean` | 33 | `85c2e8c480988522482c8fde93ef9abbc4a4faf9753c85a38757e05506d318ed` | `677cfaf4dfac2675a6d79acba534596176bfe2f46177faeacec9b2518b6df0ec` |
| 19 | `MultitermTheorems.lean` | 36 | `73e4c53b20117c3738b13faa83d8144e20757a2ea27f16740bc57d27469cbaa6` | `0241741a7bb4d8a932946278cfb5740c5f9bcf5376c9aece78a8e52d0afc1ed4` |
| 20 | `ObstructionGraphTheorems.lean` | 92 | `013deb6617803b54361f44b0eda1986a424c6e3e92e34b53750a407167f2a2bc` | `ce23960f4c383232a58ffba5febaf56a1bc99f65720772d94572a47d3a4e14aa` |
| 21 | `OpenProblemSignatures.lean` | 108 | `18a9d0b87f12706f0eef1eca39590bf085dd5c4269f2200978f1564ec27ce38d` | `9056c331a5c2083d266cdf250690e95fc8e2c6d1c68ea1da19446f7a13e3a6df` |
| 22 | `OptimalCertificates.lean` | 32 | `72defd5cfa9dcab4759db8c3035980f70c32029f3d8e149493e71c2fea74d6fc` | `6b2e98dfb71eea942d3597faac396273bd811a88e26bfb75c88cce045067056c` |
| 23 | `PillaiCatalanTheorems.lean` | 175 | `e828ba425adbc0e307333da040ad61ef2bb0c0ac6c40e0d59d7c86440674ab08` | `431f153f9e6c5742fbf38b45c3633a2bd7a0ccbf9a39eaf6d9943e1937f8b7d0` |
| 24 | `QuadraticIdentities.lean` | 22 | `05abf53c1b4b142a449428e3c316edad4155f68ec1fb6eb4f94ccd83f5520f83` | `7c90e3c4a0535c16d1b7ea0f285a1332f115340715144837819c0bc6c9b709ea` |
| 25 | `QuadraticRingTheorems.lean` | 58 | `79c82480e17dd9162d924de5f04e6ad9be926f83cbda28c001b48e4c592de427` | `e92138292fad411b930755b3fd3e74ab03a7547852f26e64a2c54b46b62f7b58` |
| 26 | `QuaternionAlgebraTheorems.lean` | 72 | `66521a8d5ebdcba47642019b5b707f55fa3015bff29d9d708d94c20bcccae720` | `2781f0d3788e1422f7fa778d2e9e56fd2d1d24751608784c9e140d90392dea01` |
| 27 | `SchinzelTheorems.lean` | 133 | `b71c01b7f4616df430cbd41e7dd16884cac173482d4fd2a7f7682f423bd76c55` | `37f9c5ea1a40c5053172e5e51117341348ff879a7c158537782c26ac53861c81` |
| 28 | `SidonSetsTheorems.lean` | 70 | `b3746ea30eb9b8b147371eea6a214d9e6b5a79d50c738e3c213bc71add41d855` | `8b8170c5d6701bdf4ee50f926df9a75f7bfd66c2121f7c9c276e7fef4d37d1ea` |
| 29 | `SierpinskiTheorems.lean` | 106 | `1952f708b56bdfa0f16208ba88ada853e30b38a51af0c734558c778960af8073` | `60a5f241331f269c718fa4d6b56cb05da3a32f251319d3c1afd9c17beac8a002` |
| 30 | `SolutionMomentsTheorems.lean` | 87 | `f1c2211e979989edef164d51a3a6f76dc6cb9dee739fccb63942b6a555393157` | `ea3a5a9be270fa488c3f51277d98b40fb69152abe4e7de88f45d4cd926b18c9b` |
| 31 | `SumFreeTheorems.lean` | 70 | `531a2cf479053e048429b6ee3a430191e8a7efc797f9f77720090cfa428a5fd0` | `892a04c2af0085bbe5dcf60c6210d4bc6ce4b3f610a9f7d6e037d393c58eab8d` |
| 32 | `UniversalMultitermTheorems.lean` | 108 | `a350d00735e99b79ea12c2647c97640ede4294dab3a5595f2b078f1360cf8019` | `8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3` |

**Hash Final da Biblioteca (Chain Head P120):**
`8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3`

---

## 5. Síntese da Confirmação Cega P119 e Arquitetura do Programa P113–P120

Na etapa P119, o motor estruturado de combinatória aditiva foi avaliado contra baselines ingênuos sobre a partição cega selada `experiments/p119-blind-split.json` (`100` instâncias distribuídas em 4 trilhas de `25` instâncias), com controle de erro familiar (FWER) via procedimento step-down de Bonferroni–Holm em $\alpha = 0{,}01$:

| Trilha Combinatória | Instâncias | Vitórias / Derrotas / Empates | Redução de Candidatos | $p$ Bruto (Sign Test) | $p_{\text{Holm}}$ Ajustado | Veredito |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `sidon_extremal` | 25 | 25 / 0 / 0 | $43{,}60\times$ | $5{,}9605 \times 10^{-8}$ | $2{,}3842 \times 10^{-7}$ | **CONFIRMED** |
| `additive_energy_bsg` | 25 | 25 / 0 / 0 | $112{,}90\times$ | $5{,}9605 \times 10^{-8}$ | $2{,}3842 \times 10^{-7}$ | **CONFIRMED** |
| `erdos_turan_basis` | 25 | 25 / 0 / 0 | $47{,}03\times$ | $5{,}9605 \times 10^{-8}$ | $2{,}3842 \times 10^{-7}$ | **CONFIRMED** |
| `sum_free_schnirelmann` | 25 | 25 / 0 / 0 | $403{,}00\times$ | $5{,}9605 \times 10^{-8}$ | $2{,}3842 \times 10^{-7}$ | **CONFIRMED** |
| **TOTAL (P119)** | **100** | **100 / 0 / 0** | — | — | $\mathbf{2{,}3842 \times 10^{-7} \le 0{,}01}$ | **ACCEPTED** |

---

## 6. Conclusão

Com **2.392 teoremas formais certificados** em **32 módulos matemáticos** no Lean 4 (`0 sorry`), meta-táticas customizadas (`additive_norm`, `dioph_surface`, `dioph_solve`, `frac_norm`), confirmação estatística cega FWER ($\alpha = 0{,}01$) e cadeia criptográfica SHA-256 imutável (`8013152a11ac6cf28559ea1067cba32bfb3c7319d66d27766f636e1bec39acc3`), o programa P113–P120 encerra com sucesso a expansão de combinatória aditiva do EvoByte.
