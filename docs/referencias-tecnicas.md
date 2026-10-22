# Referências públicas e comparação com Metal Saga

Pesquisa em 21/10/2026. Leitura de fontes públicas pelo conector GitHub e consulta web;
nenhum código externo foi incorporado ou executado. Os resultados de outros projetos
são relatos dos autores e evidências de implementação, não testes reproduzidos aqui.

## Revisões consultadas e manutenção

| Projeto | Revisão fixada | Último commit da revisão (UTC) | Licença observada |
| --- | --- | --- | --- |
| [Busin0Translation](https://github.com/Fabulu/Busin0Translation/tree/756ae1376d63d068885c2a6db4f6860414358ed6) | `756ae1376d63d068885c2a6db4f6860414358ed6` | 11/10/2026 | sem arquivo LICENSE/COPYING na árvore consultada |
| [Kuriimu2](https://github.com/FanTranslatorsInternational/Kuriimu2/tree/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83) | `6babcdc3562975f445f258f0b7f1d9bd8e5e2a83` | 28/08/2026 | LICENSE.md, GPL versão 3 |
| [ps2-translator](https://github.com/fubenlewis-hub/ps2-translator/tree/a6f90b8e720682f4c4d13962b81be32b5dfe5312) | `a6f90b8e720682f4c4d13962b81be32b5dfe5312` | 25/08/2026 | sem arquivo de licença; README limita uso a estudo/pesquisa e não comercial |
| [game-localization-mvr](https://github.com/Charpup/game-localization-mvr/tree/731948f419d7458f29a700531a07a0b43fa19878) | `731948f419d7458f29a700531a07a0b43fa19878` | 09/04/2026 | README declara MIT, mas sem arquivo LICENSE/COPYING na árvore consultada |

Datas indicam atividade observada, não garantia de manutenção. Antes de eventual
reutilização de código, resolver a licença e os avisos aplicáveis à versão exata.
A decisão atual é estudar as técnicas e manter implementação própria. Não foi feita
análise jurídica nem auditoria completa das dependências desses projetos.

## Busin 0: referência mais próxima de engenharia PS2

O [README](https://github.com/Fabulu/Busin0Translation/blob/756ae1376d63d068885c2a6db4f6860414358ed6/README.md)
relata uma tradução jogável, alterações de fontes/métricas e testes em hardware.
Também documenta regressões reais: realocação de fontes colidindo com memória de
batalha, extensão de ELF recusada pelo loader e perda de códigos de controle.
Isso reforça a necessidade de validar boot, navegação e cenas após mudanças.

O formato é específico: PACKDATA.DIG e índices de glifos de 16 bits dependentes do
recurso. Não equivale ao texto de um byte observado no diário do Metal Saga.

O [disassembler sec1](https://github.com/Fabulu/Busin0Translation/blob/756ae1376d63d068885c2a6db4f6860414358ed6/tools/sec1_disasm.py)
percorre instruções por fluxo e reconhece operandos. O
[patcher de offsets](https://github.com/Fabulu/Busin0Translation/blob/756ae1376d63d068885c2a6db4f6860414358ed6/tools/patch_section1_offsets.py)
distingue referências por palavras, saltos por bytes e índices que não devem mudar.
É uma técnica útil para o futuro parser msg/msgn: identificar primeiro quais campos
são comprimento, ponteiro, ID ou salto. O código de Busin não deve ser transplantado
para MAP.MCT. Há lógica de fallback e casos especiais no patcher; o README resume
a metodologia de forma mais simples do que a implementação completa.

[glyph_metrics.py](https://github.com/Fabulu/Busin0Translation/blob/756ae1376d63d068885c2a6db4f6860414358ed6/tools/glyph_metrics.py)
centraliza avanço e deslocamento lateral. O
[gerador de atlas](https://github.com/Fabulu/Busin0Translation/blob/756ae1376d63d068885c2a6db4f6860414358ed6/tools/generate_font_atlas.py)
usa packing de nibbles e parâmetros TEX0 próprios dos recursos estudados lá.
Para GFI, aproveitar o princípio de separar bitmap, mapeamento e métricas; os offsets,
paletas e dimensões precisam ser determinados no Metal Saga.

Os [testes ISO](https://github.com/Fabulu/Busin0Translation/blob/756ae1376d63d068885c2a6db4f6860414358ed6/tests/test_iso_level.py)
abrem recursos dentro da imagem final. Recomenda-se essa verificação além do arquivo
intermediário, junto à comparação de bytes fora da região autorizada já implementada
em nosso disc.py. O aviso de boot limpo no README é pertinente: estados do emulador
podem restaurar RAM com textos antigos. Não usar savestate antigo para aceitar build.

## Kuriimu2: biblioteca e arquitetura, sem compatibilidade demonstrada

O [README](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/README.md)
apresenta plugins separados para arquivos, imagens, textos e fontes. Há arquitetura
reutilizável e implementação substancial; a versão consultada requer .NET 8+.
Não foi encontrado na árvore um plugin explicitamente identificado como Metal Saga,
SDA ou GFI. Isso não é prova de ausência em todo o ecossistema ou forks.

O [plugin PS2Disc](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/plugins/Sony/plugin_sony/Archives/Ps2DiscState.cs)
implementa carregamento (`ILoadFiles`), sem método de escrita nessa classe. Portanto
não serve como evidência de reconstrução de ISO. Seu
[leitor](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/plugins/Sony/plugin_sony/Archives/Ps2Disc.cs)
assume posições fixas para ignorar entradas de diretório e dados adicionais; não
há vantagem comprovada sobre nosso leitor já validado nos 58 arquivos deste disco.

[Ps2Swizzle.cs](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/src/lib/Kanvas/Swizzle/Ps2Swizzle.cs)
oferece padrões de swizzle por profundidade de pixels. Pode ajudar numa comparação
visual futura, depois de identificar o packing GFI. Aplicar deswizzle genericamente
pode embaralhar uma imagem que já está linear. O
[modelo de glifo Level5](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/plugins/Level5/plugin_level5/Common/Font/Models/FontGlyphDescriptionData.cs)
separa posição e dimensões, mas pertence a outro formato. Nenhum GFI foi aberto ou
validado no programa nesta missão. A licença está em
[LICENSE.md](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/LICENSE.md).

## ps2-translator: estrutura de projeto útil, promessas exigem leitura do código

O [README](https://github.com/fubenlewis-hub/ps2-translator/blob/a6f90b8e720682f4c4d13962b81be32b5dfe5312/README.md)
descreve plugins para Tokimeki Memorial, tradução por IA, glossário e retomada.
Os testes citados são desses jogos; não há demonstração de Metal Saga.
O pequeno número de commits observado e a ausência de licença padrão aconselham
avaliar cada componente antes de adotar dependência.

Limitações comprovadas pela leitura:

- [generic_sjis.py](https://github.com/fubenlewis-hub/ps2-translator/blob/a6f90b8e720682f4c4d13962b81be32b5dfe5312/ps2hantool/plugins/generic_sjis.py)
  ignora arquivos acima de 64 MiB, omitindo MAP.MCT; `writeback` retorna zero
  gravações e informa que o formato genérico não tem reinserção automática.
- [extractor.py](https://github.com/fubenlewis-hub/ps2-translator/blob/a6f90b8e720682f4c4d13962b81be32b5dfe5312/ps2hantool/text/extractor.py)
  usa cp932, filtros voltados a japonês, redução de quebras de linha e deduplicação.
  Esse fluxo pode omitir inglês ou apagar distinções estruturais importantes aqui.
- [bitmap.py](https://github.com/fubenlewis-hub/ps2-translator/blob/a6f90b8e720682f4c4d13962b81be32b5dfe5312/ps2hantool/font/bitmap.py)
  gera bitmaps; `FontInjector.analyze/inject` lançam `NotImplementedError`.
  Gerar caracteres não comprova que o motor do jogo os reconhece.
- [iso.py](https://github.com/fubenlewis-hub/ps2-translator/blob/a6f90b8e720682f4c4d13962b81be32b5dfe5312/ps2hantool/iso.py)
  cria novo filesystem via pycdlib; ordem de inclusão não garante os LBAs originais.
  Há divergência entre comentários de preservação de layout e implementação.
  Além disso, calcula um nome alternativo `target` quando a saída existe, mas chama
  `iso.write(str(out_iso))`: a proteção anunciada contra sobrescrita não é aplicada
  nesse caminho. Não executar essa rotina sobre nossos discos.

O [modelo de texto](https://github.com/fubenlewis-hub/ps2-translator/blob/a6f90b8e720682f4c4d13962b81be32b5dfe5312/ps2hantool/text/model.py)
associa arquivo, offset, categoria e ID. Adotar o conceito de identidade estável,
acrescentando hash de origem e índice estrutural; não deduplicar ocorrências físicas
na reinserção. Traduções podem compartilhar uma sugestão, mas cada slot precisa
continuar identificado e validado individualmente.

## game-localization-mvr: validação textual para uma etapa posterior

O [README](https://github.com/Charpup/game-localization-mvr/blob/731948f419d7458f29a700531a07a0b43fa19878/README.md)
propõe CSV → proteção de placeholders → glossário → tradução → validação → exportação,
com preservação das linhas de entrada e manifestos. É um fluxo textual, não um
reconstrutor de binários PS2 ou parser de GFI.

[normalize_guard.py](https://github.com/Charpup/game-localization-mvr/blob/731948f419d7458f29a700531a07a0b43fa19878/scripts/normalize_guard.py)
substitui placeholders por IDs e guarda um mapa reversível. O
[exportador](https://github.com/Charpup/game-localization-mvr/blob/731948f419d7458f29a700531a07a0b43fa19878/scripts/rehydrate_export.py)
rejeita tokens sem mapeamento. Para Metal Saga, proteger `%N1`, `%N2`, bytes especiais
e controles próprios de cada recurso; somente os trechos linguísticos devem chegar
à IA. As regras genéricas do outro projeto não definem a gramática do nosso jogo.

Na [validação rígida](https://github.com/Charpup/game-localization-mvr/blob/731948f419d7458f29a700531a07a0b43fa19878/scripts/qa_hard.py),
a comparação usa contadores de tokens e transforma um caso de duplicação em aviso.
Isso não serve como política automática para nossos binários: controles não podem
ser duplicados sem justificativa, e ordem/posição podem ser significativas.
Antes de reinserir, exigir gramática válida, tokens preservados, codificação aceita,
limite em bytes e largura em pixels. Glossário e revisão humana complementam os testes.

## Decisões para Metal Saga

| Recurso | Técnica recomendada | O que ainda impede expansão |
| --- | --- | --- |
| DIARY.DAT | manter slots e hash; aceitar somente alteração controlada e teste visual | codificação especial, largura e limite de corpo |
| MAP.MCT | parser por registros e blocos, mapa de referências tipadas e round-trip | semântica de IDs/saltos/offsets ainda não demonstrada |
| S_PACK.SDA | reconstrução SDA recursiva, tamanhos lógicos separados de padding | estruturas internas e alinhamentos de cada recurso |
| GFI | correlacionar leitor no ELF, mapa código→glifo, bitmap e métricas | nenhum packing ou suporte a acentos comprovado |
| ISO | manter substituição de tamanho idêntico e comparação integral | mudanças de tamanho exigem investigar referências a LBA |
| Tradução por IA | IDs estáveis, glossário versionado, tokens reversíveis e validação bloqueante | só iniciar depois de fechar reinserção e renderização |

Não há benefício demonstrado em substituir recon.py, diary.py ou disc.py neste
momento. A incorporação imediata foi de procedimentos de pesquisa e teste, sem
copiar bibliotecas externas. O teste funcional usa boot novo e New Game, sem
restaurar RAM de outra build. Ver o relatório funcional desta fase para a evidência.
