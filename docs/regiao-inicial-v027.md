# Lote v027 — despedidas com referência dinâmica

A v027 acrescenta **18 despedidas traduzidas** e preserva integralmente as 5.838 traduções anteriores. Total: **5.856 de 7.231 registros conhecidos do MAP.MCT**, aproximadamente 80,98% do catálogo. Não é percentual do jogo inteiro, palavras ou áreas completas.

São 14 despedidas de boa sorte e quatro de cuidado/despedida. O tratamento fica como sr.; a referência `%T$0` e o conteúdo inserido pelo motor permanecem intactos. A nova [política v009](controle-t0-v009.md) exige slots fixos, tokens vinculados e ausência de crescimento por segmento. Não libera N, I ou outras variantes de T.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: recompila e valida sem gerar nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada atual.
- Receita: `translations/regiao-inicial-v027.json`.
- Plano completo, revisão bilíngue e relatório: `work/regiao-inicial-v027/`.
- ISO: `work/regiao-inicial-v027/MetalSaga-ptbr-regiao-inicial-v027.iso`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v027.json --output work/rebuild-v027 --build-iso
python tools/audit_translation_coverage.py --build-dir work/regiao-inicial-v027 --output work/auditoria-v027-nova
python tools/plan_remaining_texts.py --build-dir work/regiao-inicial-v027 --output work/pendencias-v027-novas.json
```

## Conferência posterior no save corrido

O Codex não executou esta versão no PCSX2. Manter a conferência acumulada para a passagem contínua solicitada pelo usuário; não exigir navegação imediata até Dr. Palm. O layout v005 aprovado nas falas de Nina continua vinculado à receita.

| Variante | Amostra | Conferir ao encontrar |
| --- | --- | --- |
| Boa sorte, uma linha | `map.msg.057cdbcc` | Referência resolvida, sr., pontuação e margem |
| Boa sorte, duas linhas | `map.msg.0a6111f0` | Quebra antes do tratamento e conteúdo dinâmico |
| Cuidado/despedida | `map.msg.0a611a8c` | Cuide-se, referência e reticências |

Os contextos vêm das falas; não se comprovou um vínculo canônico com todas as áreas/personagens. Conferir também preços, ônibus, hospedarias, Banjo, balsas e construção de tanques dos lotes anteriores quando aparecerem naturalmente no save. Evitar savestate antigo como prova do conteúdo carregado; preservar os saves existentes.

## Cobertura e próximo grupo

São 6.278 segmentos traduzidos no catálogo de 1.595 grupos SSD. Os 659 registros com avisos conservadores de largura são herdados; estas despedidas não acrescentam avisos. Não confundir essa estimativa com medição em pixels ou aprovação visual.

Dos 1.375 registros intactos, 159 estão adiados: 145 com controles opacos em 30 grupos disjuntos e 14 com bytes nativos. Os 19 nomes de tanques N3 continuam preservados e tecnicamente bloqueados para edição. A auditoria mantém ainda 599 controles/pontuação, 458 sugestões de nomes/expressões e 159 na categoria heurística de revisão; esta última inclui o marcador F já decidido, além das 158 situações anteriores.

Próximo alvo previsto: `%I$0`, 14 registros exclusivos. A triagem também mostra 22 `%N$0`, pois combinações antes separadas com T0 agora se agrupam nesse único opaco restante. Isso não libera sua edição nem comprova que todos precisem de tradução.

## Validação automatizada

Passaram 75 testes direcionados em 120,748 segundos: controles anteriores e T0, reinserção, escolhas nomeadas e suas evidências, cobertura, terminologia, cache/layout/desenho de glifos, regressões integrais dos lotes v026/v027 e recusa de decisão de preservação inconsistente. Não foi repetida a descoberta completa de todos os testes nesta rodada; extratores e recursos independentes não mudaram. A seleção e o comando reproduzível estão em `reports/regiao-inicial-v027-tests.json`.

A regressão compara os 7.231 descritores com a v026. Somente os 18 IDs previstos mudam de tradução e bloqueio; todas as 5.838 traduções anteriores permanecem iguais. Os testes não executam o jogo no PCSX2.

A ISO tem 1,704,427,520 bytes. Comparação integral: 485,492 bytes alterados, todos previstos pelos patches. Diretórios e extents idênticos. SHA-256: `b4937049fbe7042a45678652e5afbf6145313fcecaf56f7f1264886f54100b2b`.

A releitura independente confirmou que o ELF e as duas GFI são idênticos byte a byte aos da ISO de layout v005 aprovada. Relatórios próprios em `reports/regiao-inicial-v027-validation.json`, `reports/regiao-inicial-v027-coverage.json` e `reports/plano-pendencias-v005.json`.

A retenção removeu somente a ISO gerada v019, a mais antiga elegível, e mantém dez imagens: v020 a v027 e layouts v004/v005. Original, BIOS, saves e configurações preservados. Receitas e relatórios históricos continuam disponíveis. O iniciador foi conferido para a imagem v027 existente, sem abrir o emulador.
