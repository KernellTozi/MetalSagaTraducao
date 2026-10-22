# Lote consolidado v023 — perguntas e opções nomeadas

## Resultado e escopo

O lote retoma 91 registros smnn/2snm antes bloqueados pela terceira string, mediante a [política específica v005](reinsercao-v005.md). O catálogo continua com 7.231 registros. O resultado consolidado é de 5.758 registros alterados, contra 5.667 na v022: aproximadamente 79,63% dos registros catalogados. Isso não mede palavras nem equivale à tradução completa do jogo.

Foram traduzidas perguntas e opções de hospedagem, recrutamento, oficinas, diálogos de Hunter, situações cômicas e decisões de missões. A tradução mantém categorias e números dos quartos, calibres, nomes próprios, comandos, quebras e ordem das opções. A terceira string é um rótulo protegido e permanece no original; não foi interpretada como ID canônico de personagem.

A receita filha contém todos os 91 IDs em `resume_deferred`. A regressão compara os 7.231 registros com o pai: preserva suas 5.667 traduções e todos os metadados, exceto a atualização justificada de bloqueios nos 112 descritores de escolhas nomeadas. Os 21 registros dessa família com controles opacos continuam bloqueados.

Permanecem 258 adiamentos: 244 por controles opacos e 14 por bytes nativos. Os demais preservados incluem pontuação, expressões, nomes e textos a revisar, conforme a auditoria. Não foram liberados controles desconhecidos nem encodings alternativos.

## Execução local

- `Preparar-Regiao-Inicial.cmd`: recompila o lote atual e valida, sem gerar nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada no ambiente isolado.
- `Auditar-Traducao.cmd`: gera auditoria local, incluindo preservados a revisar.
- Receita: `translations/regiao-inicial-v023.json`.
- ISO: `work/regiao-inicial-v023/MetalSaga-ptbr-regiao-inicial-v023.iso`.
- Plano, relatório e revisão bilíngue: `work/regiao-inicial-v023/`.

Para reconstruir, usar uma saída nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v023.json --output work/reconstrucao-v023 --build-iso
python -m unittest discover -s tests -v
```

## Validação visual pendente

Não houve navegação nem teste desta versão no PCSX2 pelo Codex. Fontes v002 e espaçamento v003 mantêm o estado anteriormente assumido pelo usuário. A validação binária não confirma enquadramento ou navegação das opções.

Quando estiver acessível, testar a hospedagem de Junkyard (`map.2snm.1d0b4464`) e observar pergunta, nomes dos quartos, seleção/cancelamento e resposta após escolher. Também testar perguntas de personagens que exibam opções de resposta: conferir se o rótulo permanece legível e se cada opção aciona a resposta correspondente. Inicializar a ISO diretamente, evitando carregar savestate de outra versão. Não é necessário percorrer todos os 91 registros de uma vez.

Cabeçalhos, slots, offsets, tamanho de registros e blocos SSD são preservados. Não há realocação dessas famílias. Limites de buffer, sequência de controles, Unicode e leitura dos bytes compilados continuam verificados. A exceção ASCII `nao` permanece restrita ao ID autorizado anteriormente.

## Testes executados

A execução completa abrangeu 133 testes em 448,905 segundos: 132 passaram e o novo teste de regressão encontrou um erro no próprio teste ao consultar `resume_deferred` após o carregador consumir esse campo. O teste foi corrigido para consultar a receita filha original e repetido isoladamente, passando em 39,691 segundos. Assim, os 133 testes possuem resultado aprovado após essa correção, sem alteração do compilador para contornar a falha.

## Construção e retenção verificadas

São 6.137 segmentos traduzidos em 1.595 grupos SSD. Há 650 avisos conservadores de largura, que não equivalem a medição em pixels. A compilação final tem zero recusas e zero violações de terminologia.

A ISO possui 1.704.427.520 bytes. A comparação integral confirmou que os 476.657 bytes diferentes correspondem exatamente aos patches previstos, incluindo fontes e espaçamento. O diretório do disco permaneceu idêntico.

SHA-256: `915a7e998f0d543ea8326ddd36bf6556062f12f396b25ba8c115168d98dd682d`.

Relatórios próprios: `reports/regiao-inicial-v023-validation.json`, `reports/regiao-inicial-v023-coverage.json` e `reports/regiao-inicial-v023-tests.json`. Revisão bilíngue e fontes originais ficam somente em `work/` e `JOGO/`, fora do Git.

A retenção removeu a ISO v013 mais antiga. Permanecem dez imagens de trabalho, v014 a v023; a ISO original fica fora da contagem. Receitas e relatórios anteriores foram preservados. O iniciador foi conferido com `--dry-run`, sem executar o PCSX2.
