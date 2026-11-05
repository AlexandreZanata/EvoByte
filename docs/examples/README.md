# Exemplos de formatos

Todos os arquivos desta pasta são **EXEMPLOS**, não configurações autorizadas nem
resultados reais. `is_example=true` obriga a CLI futura a rejeitar sua execução.
Valores null indicam campos ainda não medidos ou produzidos. Hashes reais devem
ser calculados pela implementação, nunca copiados de um exemplo.

- [run-config.example.json](run-config.example.json): envelope ilustrativo de configuração.
- [campaign.example.json](campaign.example.json): limites do cenário R=10 e campos
  de congelamento ainda não preenchidos.
- [candidate.example.json](candidate.example.json): C5 com três vértices isolados,
  construção matematicamente válida para n=8, sem certificação executada.
- [result.example.json](result.example.json): formato de resultado esperado; os
  campos de medição/certificação permanecem vazios. O candidato do exemplo teria
  cinco arestas se ambos os verificadores confirmassem o payload.

Ao implementar, produzir schemas finais compatíveis com `03` e acrescentar os
campos de configuração obrigatórios; estes exemplos não são manifests completos.
