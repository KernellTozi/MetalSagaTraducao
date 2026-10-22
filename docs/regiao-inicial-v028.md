# Lote v028 — equipamento, combate e presentes

A v028 acrescenta **14 registros traduzidos**, preservando integralmente as 5.856 traduções anteriores. Total: **5.870 de 7.231 registros conhecidos do MAP.MCT**, aproximadamente 81,18% do catálogo. Isso não mede palavras, áreas completas ou o jogo inteiro.

As falas tratam de proteção contra o frio, equipamento para enfrentar monstros, chuva ácida, acesso a campos sem tanques, inspeção de uma peça e presentes recebidos. A referência `%I$0` continua sendo resolvida pelo jogo, conforme a [política v010](controle-i0-v010.md). Mantêm-se nomes únicos, Bloodhound, Tindalos, Rocket Snails, Dragon Choppers, Hunter, referências de nome, pausas, risadas e `*cough*`.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: recompila e valida sem criar nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a imagem consolidada atual.
- Receita: `translations/regiao-inicial-v028.json`.
- Plano completo, revisão bilíngue e relatório: `work/regiao-inicial-v028/`.
- ISO: `work/regiao-inicial-v028/MetalSaga-ptbr-regiao-inicial-v028.iso`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v028.json --output work/rebuild-v028 --build-iso
python tools/audit_translation_coverage.py --build-dir work/regiao-inicial-v028 --output work/auditoria-v028-nova
python tools/plan_remaining_texts.py --build-dir work/regiao-inicial-v028 --output work/pendencias-v028-novas.json
```

## Teste posterior no save corrido

O Codex não executou esta versão no PCSX2. Acumular a conferência para a passagem contínua solicitada pelo usuário, inclusive Dr. Palm quando acessível. Manter o perfil de acentos v005 aprovado nas falas de Nina; essa aprovação não comprova todos os contextos.

| Contexto textual | Amostra | Conferir ao encontrar |
| --- | --- | --- |
| Proteção contra o frio | `map.msgn.038dac0c` | Nome dinâmico, pausa W5, linhas e Heh |
| Presente e conserto gratuito | `map.smsg.0be1597c` | Nome de presente, opções e efeito do conserto |
| Chuva ácida e SE | `map.msgn.0be22854` | Bloodhound/Tindalos, equipamento recomendado e largura |
| Campos depois do bosque | `map.msgn.0be22bc4` | Orientação para leste, nome dinâmico e restrição aos tanques |
| Inspeção de peça | `map.msg.0e55131c` | Nome, sequência e reticências |
| Bombas | `map.msgn.1282da58` | As duas referências e distinção de outros ataques |
| Rocket Snails | `map.msgn.14aab6b4` | Quatro expressões cough, conselho e localização |
| Dragon Choppers | `map.msgn.1d0b9e94` | Dica de venda dos olhos, recomendação e tiro único |
| Agradecimentos por presentes | `map.msg.1df5e4a4`, `map.msg.1df5f13c`, `map.msg.1df6435c` | Nome recebido, tom e pausas |

Os contextos são inferidos das falas/rótulos, sem vínculo canônico completo com cenas, personagens ou cidades. Preservar saves e evitar savestate antigo como prova do conteúdo da nova ISO.

## Cobertura e limitações

São 6.293 segmentos traduzidos no catálogo de 1.595 grupos SSD. Há 665 registros com avisos conservadores de largura, seis novos: `map.smsg.0be1597c`, `map.msgn.0be22854`, `map.msg.0e55131c`, `map.msgn.14aab6b4`, `map.msgn.1d0b9e94` e `map.msg.1df5f13c`. Não são medidas em pixels nem aprovação visual; nenhum segmento ultrapassa o orçamento original em bytes.

Dos 1.361 registros intactos, 145 permanecem adiados: 131 opacos em 29 grupos disjuntos e 14 com bytes nativos. Entre eles, os 19 nomes N3 continuam intactos por decisão editorial e bloqueados tecnicamente para edição. A auditoria mantém ainda 599 controles/pontuação, 458 sugestões de nomes/expressões e 159 na categoria heurística de revisão, incluindo o marcador F já decidido.

Próximo alvo: `%N$0`, 22 registros com recebimento de veículos, tutorial de Drive, hospedagem e outras referências. Não repetir N3 nem assumir que N0 resolve sempre o mesmo tipo de entidade. A presença de Drive em um tutorial deverá respeitar o nome efetivamente exibido na interface, que ainda não foi localizado integralmente.

## Validação automatizada

Passaram 81 testes direcionados em 121,209 segundos: controles anteriores e I0, reinserção, escolhas nomeadas e evidências, cobertura, terminologia, cache/layout/desenho de glifos, regressões integrais dos lotes v027/v028 e recusa de decisão de preservação inconsistente. Não foi repetida a descoberta completa de todos os testes nesta rodada; extratores e recursos independentes não mudaram. Seleção e comando em `reports/regiao-inicial-v028-tests.json`.

A regressão compara os 7.231 descritores com a v027. Somente os 14 IDs previstos mudam de tradução e bloqueio; todas as 5.856 traduções anteriores permanecem iguais. Os testes não executam o jogo no PCSX2.

A ISO tem 1,704,427,520 bytes. Comparação integral: 487,307 bytes alterados, todos previstos pelos patches. Diretórios e extents idênticos. SHA-256: `2fd476e110afac604281d1222d0d2f9501a90495e7cef909523077c89a9a9390`.

A releitura independente confirmou o ELF e as duas GFI idênticos byte a byte aos da ISO de layout v005 aprovada. Relatórios próprios em `reports/regiao-inicial-v028-validation.json`, `reports/regiao-inicial-v028-coverage.json` e `reports/plano-pendencias-v006.json`.

A retenção removeu somente a ISO gerada v020, a mais antiga elegível, e mantém dez imagens: v021 a v028 e layouts v004/v005. Original, BIOS, saves e configurações preservados. Receitas e relatórios históricos continuam disponíveis. O iniciador foi conferido para a imagem v028 existente, sem abrir o emulador.
