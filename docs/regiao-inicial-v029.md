# Lote v029 — hospedagem e nomes dinâmicos de veículos

A v029 acrescenta **22 registros traduzidos** e preserva integralmente as 5.870 traduções anteriores. Total: **5.892 de 7.231 registros conhecidos do MAP.MCT**, aproximadamente 81,48% do catálogo. Não é percentual do jogo inteiro, palavras ou áreas completas.

O lote inclui boas-noites na hospedagem, recebimento de veículos, tutorial do comando Drive, anúncio de nome, mensagem sobre arar o campo, uma conversa sobre nomes de veículos e a comemoração de Dr. Palm pelo tanque. A [política v011](controle-n0-v011.md) mantém `%N$0`, `%T$0`, `%B$15`, os valores e nomes resolvidos pelo motor. O nome Drive e as risadas continuam em inglês como solicitado; não se traduziu nenhum nome de tanque.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: recompila e valida sem criar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a imagem consolidada atual.
- Receita: `translations/regiao-inicial-v029.json`.
- Plano completo, revisão bilíngue e relatório: `work/regiao-inicial-v029/`.
- ISO: `work/regiao-inicial-v029/MetalSaga-ptbr-regiao-inicial-v029.iso`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v029.json --output work/rebuild-v029 --build-iso
python tools/audit_translation_coverage.py --build-dir work/regiao-inicial-v029 --output work/auditoria-v029-nova
python tools/plan_remaining_texts.py --build-dir work/regiao-inicial-v029 --output work/pendencias-v029-novas.json
```

## Conferência posterior no save corrido

O Codex não executou esta versão no PCSX2. Acumular a conferência para a passagem contínua solicitada pelo usuário; não exigir acesso imediato a Dr. Palm. O perfil de acentos v005 aprovado nas falas de Nina permanece vinculado à receita.

| Contexto textual | Amostra | Conferir ao encontrar |
| --- | --- | --- |
| Hospedagem | `map.msg.038d5e40`, `map.msgn.01df74f0` | Nome/tratamento dinâmicos, quebra e boa-noite |
| Recebimento e tutorial | `map.msg.06493cbc` | Nome do veículo e comando Drive coerente com a interface |
| Anúncio de nome | `map.msg.07b26e8c` | Nome, huh? e instrução ao grupo |
| Campo arado | `map.msg.07b273fc` | Referência resolvida e mensagem da ação |
| Nomes de veículos | `map.msg.0be102b4` | Referência e relação com músicas antigas |
| Tanque de Dr. Palm | `map.msg.1fd480c4`, `map.msg.1fd48150` | Recebimento, nome, apelido B15, risadas e convite para testar |

Os contextos vêm das falas e rótulos; não são um vínculo completo com cidades, retratos ou progressão. Manter também a revisão das dicas, presentes, preços e escolhas dos lotes anteriores. Preservar os saves; não usar savestate antigo como prova do conteúdo carregado da ISO atual.

## Cobertura e limites

São 6.315 segmentos traduzidos no catálogo de 1.595 grupos SSD. Os 665 registros com avisos conservadores de largura são herdados; este lote não acrescenta avisos. Essa estimativa não mede pixels nem substitui a validação visual de nomes dinâmicos compridos.

Dos 1.339 registros intactos, 123 permanecem adiados: 109 opacos em 28 grupos disjuntos e 14 com bytes nativos. Os 19 nomes N3 continuam preservados e tecnicamente bloqueados para edição. Mantêm-se ainda 599 controles/pontuação, 458 sugestões de nomes/expressões e 159 na categoria heurística de revisão, incluindo o marcador F já decidido.

Próximo alvo recomendado: controles numéricos `%$0` e `%$2`, com 12 registros exclusivos cada. Provar cada argumento e sufixo antes de ampliar a política; não liberar formatos fracionários ou outros índices por semelhança. Não voltar a N3 para traduzir nomes preservados.

## Validação automatizada

Passaram 87 testes direcionados em 122,824 segundos: controles anteriores e N0, reinserção, escolhas nomeadas e evidências, cobertura, terminologia, cache/layout/desenho de glifos, regressões integrais dos lotes v028/v029 e recusa de decisão de preservação inconsistente. Não foi repetida a descoberta completa de todos os testes nesta rodada; extratores e recursos independentes não mudaram. Seleção e comando em `reports/regiao-inicial-v029-tests.json`.

A regressão compara os 7.231 descritores com a v028. Somente os 22 IDs previstos mudam de tradução e bloqueio; todas as 5.870 traduções anteriores permanecem iguais. Drive, huh? e as risadas mantêm suas contagens. Os testes não executam o jogo no PCSX2.

A ISO tem 1,704,427,520 bytes. Comparação integral: 488,415 bytes alterados, todos previstos pelos patches. Diretórios e extents idênticos. SHA-256: `02ca2cada8a231cbc11fe125450a409414515934b5d9f78741a5ac08b40482d0`.

A releitura independente confirmou o ELF e as duas GFI idênticos byte a byte aos da ISO de layout v005 aprovada. Relatórios próprios em `reports/regiao-inicial-v029-validation.json`, `reports/regiao-inicial-v029-coverage.json` e `reports/plano-pendencias-v007.json`.

A retenção removeu somente a ISO gerada v021, a mais antiga elegível, e mantém dez imagens: v022 a v029 e layouts v004/v005. Original, BIOS, saves e configurações preservados. Receitas e relatórios históricos continuam disponíveis. O iniciador foi conferido para a imagem v029 existente, sem abrir o emulador.
