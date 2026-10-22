# Lote v026 — ofertas, casa, inscrição e balsas

A v026 acrescenta **17 registros traduzidos**, preserva as 5.821 traduções da v025 e mantém intacto um marcador numérico retomado. Total: **5.838 de 7.231 registros conhecidos do MAP.MCT**, cerca de 80,74% do catálogo. Não representa percentual do jogo inteiro, palavras ou cidades completas.

O lote cobre ofertas de compra/venda, dinheiro recebido/pago, a conversa de Banjo sobre a casa, taxa de inscrição e passagens para Lorelei Bay e Dowan. Preserva Banjo, Hunter, nomes de cidades, G, referências dinâmicas e a expressão `*gasp*`. Não fixa preços na tradução. A política [v008](controles-numericos-v008.md) libera somente a referência inteira exata `%$15`, herdando os mecanismos anteriores.

O grupo `%N$3` foi analisado primeiro: os 19 registros são nomes de tanques e ficaram integralmente preservados. [Decisão e evidências](n3-preservacao-v001.md). Eles continuam tecnicamente bloqueados para edição; não contam como tradução.

## Execução local

- `Preparar-Regiao-Inicial.cmd`: recompila e valida a receita atual sem gerar ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada atual.
- Receita: `translations/regiao-inicial-v026.json`.
- Plano completo, revisão bilíngue e relatório: `work/regiao-inicial-v026/`.
- ISO: `work/regiao-inicial-v026/MetalSaga-ptbr-regiao-inicial-v026.iso`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v026.json --output work/rebuild-v026 --build-iso
python tools/audit_translation_coverage.py --build-dir work/regiao-inicial-v026 --output work/auditoria-v026-nova
python tools/plan_remaining_texts.py --build-dir work/regiao-inicial-v026 --output work/pendencias-v026-novas.json
```

## Teste conjunto no save corrido

O Codex não executou esta versão no PCSX2. Por solicitação do usuário, acumular a conferência com os lotes anteriores em uma passagem contínua, incluindo Dr. Palm quando acessível. O layout v005 aprovado nas falas de Nina permanece vinculado à receita.

| Contexto | Amostra | Conferir posteriormente |
| --- | --- | --- |
| Ofertas | `map.smsg.057cd2bc` | Valor dinâmico e efeito de aceitar/recusar |
| Banjo e a casa | `map.smnn.0e771ce4`, `map.msgn.0e771e18`, `map.msgn.0e771f14` | Preço, sequência das falas, compra e nome |
| Inscrição | `map.smnn.0e77c0e0` | Cobrança e opções completas |
| Venda de veículo | `map.smsg.12120d3c` | Hunter preservado e sentido da recusa |
| Balsas | `map.smnn.14aa9340`, `map.smnn.17749d24` | Lorelei Bay/Dowan, preço e escolha da passagem |

Os contextos vêm dos textos e rótulos. Não comprovam mapeamento completo de áreas, retratos ou progressão. Permanecem também os testes de números em ônibus/hospedarias da v025 e apelido/construção de tanques da v024. Preservar os saves e evitar savestate antigo como prova do conteúdo carregado.

## Cobertura e limitações

São 6.260 segmentos traduzidos no catálogo de 1.595 grupos SSD. Há 659 registros com avisos conservadores de largura; os três novos estão nas opções de inscrição/venda de veículo e no corpo da passagem para Lorelei Bay. Limites binários respeitados não equivalem a medir texto em pixels.

Dos 1.393 registros intactos, 177 são adiados: 163 com controles opacos em 32 grupos disjuntos e 14 com bytes nativos. A triagem separa ainda 599 controles/pontuação, 458 sugestões de nomes/expressões e 159 preservados na categoria de revisão. Nesses 159 está o marcador F com decisão explícita de preservação; portanto, não há 159 falas novas aguardando tradução. As outras 158 mantêm a situação anterior.

Próximo alvo técnico: `%T$0`, 18 registros exclusivos, seguido de `%I$0`, 14. Não liberar comandos por semelhança de grafia. Não repetir a investigação dos 19 nomes N3 para tentar aumentar o total traduzido.

## Integridade executada

A suíte completa passou: 167 testes em 604,125 segundos. A regressão compara todos os 7.231 descritores com a v025 e preserva as 5.821 traduções anteriores. Os 18 IDs retomados mudam somente a classificação de bloqueio e, em 17 deles, a tradução; o marcador permanece intacto. Os testes também recusam uma decisão de preservação aplicada a um registro alterado. Log e evidência em `reports/regiao-inicial-v026-tests.json`.

A ISO tem 1,704,427,520 bytes. A comparação integral encontrou 485,286 bytes alterados, todos previstos pelos patches. Diretórios e extents permanecem idênticos. SHA-256: `377d22ce4085536f11a53c2c656eb30b05faf13169d60709e25e07ac929e8822`.

A releitura independente confirmou o ELF e as duas GFI idênticos byte a byte aos da ISO de layout v005 aprovada. Relatórios próprios em `reports/regiao-inicial-v026-validation.json`, `reports/regiao-inicial-v026-coverage.json` e `reports/plano-pendencias-v004.json`.

A retenção removeu somente a ISO gerada v018, a mais antiga elegível, e mantém dez imagens: v019 a v026 e layouts v004/v005. A ISO original, BIOS, saves e configurações foram preservados. As receitas e relatórios anteriores continuam disponíveis. O iniciador foi conferido para apontar à imagem v026 existente, sem abrir o emulador.
