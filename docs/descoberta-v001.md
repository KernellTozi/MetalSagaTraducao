# Descoberta consolidada do catálogo restante

Rodada de 25/10/2026, exclusivamente de investigação. Base: interface/MAP v037,
com fontes/layout v005 e arte v014. Nenhuma tradução, fonte, receita ou ISO foi
alterada. A imagem jogável continua sendo a indicada por `Iniciar-Teste.cmd`.

## Entrega e reprodução local

Na pasta do projeto, executar:

```powershell
python tools/discover_remaining_catalogue.py
```

O comando substitui somente seu catálogo local em
`work/descoberta-catalogo.json` e atualiza o planejamento existente em
`work/planejamento-interface.json`. Funciona sem IA, APIs ou internet. Depende
dos módulos Python do projeto, referências originais e construção v037 íntegra;
recusa uma ISO inconsistente ou com recuperação pendente. Não constrói imagem.
O processamento inclui compilação de validação em memória e hashes integrais,
portanto pode levar alguns minutos. A busca textual lê blocos com janela
limitada; MAP usa mapeamento de arquivo, sem carregar outra cópia integral.

Para registrar outro resumo público, usar um nome ainda inexistente:

```powershell
python tools/discover_remaining_catalogue.py --summary reports/descoberta-revisao.json
```

O catálogo local contém originais, bytes, IDs, offsets, hashes, aliases,
contextos próximos e pendências por registro. Deve permanecer fora do Git.
O resumo versionado desta execução está em `reports/descoberta-v001.json`;
não contém o catálogo de falas nem imagens originais. Não foram criados novos
iniciadores ou lotes de tradução.

## Onde estão as pendências

Offsets abaixo são de arquivo, em hexadecimal; endereços explicitamente
marcados VA são endereços do executável em memória.

| Conjunto | Localização | Resultado e situação |
| --- | --- | --- |
| Rótulos de falantes | MAP.MCT, 49 IDs no catálogo local | Todos são msgn de duas strings. Faltam de 1 a 4 bytes mantendo a fala e os terminadores. Não há separador de opções adicional para aproveitar. |
| Texto nativo | MAP.MCT, oito IDs/contextos | Os oito contêm a mesma sequência original. Contexto e uso ainda inconclusivos; não classificados como debug nem traduzidos por suposição. |
| Revisão editorial | MAP.MCT, 129 registros preservados | Inclui nomes, sons, risadas e expressões; 32 têm expressões entre asteriscos. Não equivale a 129 falas narrativas faltantes. |
| Nomes de itens | S_PACK.SDA, tabela 0x820, 1.349 registros de 128 bytes | Restam 25 propostas: 20 excedem o teto conservador de 16 bytes, uma exige Ó e quatro têm questão terminológica/de nome protegido. |
| Legendas de pintura | S_PAINT.SDA, entrada 22, 0xAE6A0 | 228 registros de 36 bytes, 19 grupos de 12; 12 nomes distintos, cada um com 19 referências. Estrutura e encaminhamento do nome comprovados, edição ainda não implementada. |
| Botões gráficos de pintura | S_PAINT.SDA, texturas 0x34360 e 0xCCE0 | Dez rótulos e três legendas de componentes observados nos atlas decodificados. Preservar MAIN/SUB/SE; falta vincular recortes e consumo gráfico antes de importar alterações. |
| Créditos finais | FD_END.SDA, entrada 0, slot 0x800–0x1800 | Fluxo comprimido recuperado: 292 linhas CRLF, 209 não vazias; 57 contêm bytes não ASCII. Nomes de profissionais devem ser preservados. Falta recompressor para texto editado e interpretação do renderizador. |
| Destinos | S_PACK.SDA, nó 0x35000, entrada 3 em 0x7E720 | 25 registros com ponteiros relativos, nomes e metadados. Lookup original conferido para todos; separar destinos genéricos das cidades protegidas. Não é um pool simples de strings. |
| Variantes de motores | S_PACK.SDA, 0x320F0 | Dez registros de 124 bytes, 50 campos, 26 nomes não vazios. Preservar nomes de motores; extração estrutural não prova todos os consumidores. |
| Comando TITLE | ELF, literal 0x32A31E | Um único slot de cinco bytes. Inicialização e transições internas investigadas; destino externo não comprovado. Não atribuir tradução por inferência do nome. |
| Maiúsculas PT-BR | SUC20I22.GFI e SUC24I26.GFI | Oito letras ainda sem mapeamento no perfil atual. Quatorze pares de células vazias comuns são candidatos de armazenamento, sem liberação automática. |
| Outros gráficos | 17 arquivos SDA, 119 texturas reconhecidas | Índice por arquivo/offset e interseção com patches existentes. Textura sem patch não implica texto inglês; revisão visual adicional ainda necessária. |

As 19 ocorrências N$3 são nomes de tanques já decididos como preservados;
continuam não editáveis, mas não constituem trabalho de tradução a refazer.
As descrições conhecidas de itens permanecem em 566/567, com somente o marcador
preservado. Isso não comprova que todos os recursos textuais do jogo foram encontrados.

## Evidências dos novos formatos

### Créditos comprimidos

`tools/discover_credits.py` identifica a variante LZSS real: dicionário zerado
de **1.024 bytes**, posição inicial **1006**, flags do bit menos significativo
para o mais significativo, 1 para literal. Backreference de dois bytes:
offset `a | ((b & 0xF0) << 4)`, acesso circular de 1.024 bytes e comprimento
`(b & 15) + 3`. Não usar por semelhança um LZSS de 4 KiB.

O cabeçalho declara 4.222 bytes descomprimidos. O fluxo ocupa 2.351 dos 4.096
bytes do slot, restando 1.745 bytes zerados. O resultado tem SHA-256
`53a2c807ae676a11fedeb143000d737e284da43e22ad11a55f774a8a87f2286a`.
Seu primeiro u32 declara 292 linhas e confere com os delimitadores CRLF.

O laço original do decoder, offsets 0x19B7C4–0x19B8F0, foi executado em memória
sintética por 60.933 instruções. Saída e consumo conferiram com Python.
O harness fornece o dicionário zerado e não executa o alocador/prólogo inteiro.
O carregador em 0x139074–0x139100 seleciona a entrada 0 de FD_END, chama o wrapper
0x19B6F8 e lê a contagem de linhas. A reprodução dos tokens originais é exata,
mas **não é compressão de texto alterado**. Ainda faltam o recompressor com
limite do slot, a semântica dos bytes não ASCII e os limites do renderizador.

### Pintura e destinos

`tools/discover_paint.py` verifica a tabela completa e os aliases. Em cada
registro da pintura, byte 0 seleciona o grupo; +1 inicia um campo de 23 bytes
incluindo NUL; +24..35 contém parâmetros adjacentes que permanecem opacos.
O maior nome original ocupa dez bytes. O cálculo da tabela em
0x1DFE18–0x1DFE38 e o encaminhamento em 0x1DFF1C–0x1DFF2C foram executados
para as 228 entradas, chegando à rotina 0x4F810. Isso não executa construtor
completo, layout, GPU ou jogo. Não inferir capacidade visual pelo espaço físico.

Nos destinos, 0x11F35C–0x11F378 foi executado para os 25 índices; o ponteiro
confere com a base e o offset relativo armazenado. O global é VA 0x475B28.
Cada nome tem campo de 32 bytes, seguido por flags em +32 e posições usadas
por escritas em +36/+40. As caudas e os tamanhos dos registros variam.
Preservar esses metadados e os nomes próprios, inclusive Junkyard; os 25
destinos não são 25 traduções autorizadas pela classificação.

### Orçamentos e glifos

Os 49 rótulos têm déficit mínimo de um byte (22 casos), dois (19), três (3)
ou quatro (5), mesmo contando terminadores e aproveitando o próprio registro.
Novo armazenamento exige prova específica. Não cortar artigos, falas ou acentos
para aumentar a contagem.

Nos itens, o ponteiro de descrição começa em +24 e os demais atributos em +28.
Todas as caudas dos nomes originais estão zeradas até +23. As 20 propostas
longas caberiam fisicamente em 23 bytes mais NUL, mas nenhum nome original
excede 16. Alguns encaminhamentos e o renderizador comum estão vinculados;
falta demonstrar os demais consumidores/buffers e a largura das telas. O teto
do compilador continua em 16 bytes.

As letras sem mapeamento são **À Â Ê Í Ó Ô Ú Ü**. Os pares comuns vazios são
`825c 825d 825e 825f 827a 827b 827c 827d 827e 8280 829b 829c 829d 829e`.
São candidatos, não uma nova codificação. Antes de atribuí-los, auditar uso,
cache, os dois caminhos de layout, métricas e regressões dos dois tamanhos de
fonte. Os 18 mapeamentos aprovados e os bancos ASCII continuam intactos.

## O que a varredura não comprova

Foram verificados os hashes de 58 referências originais. A busca limitada de
strings ASCII encontrou 2.838 candidatos por forma, majoritariamente dentro de
campos conhecidos, nomes preservados ou dados binários. Não são 2.838 novos
textos. Após a classificação, restam sete candidatos com forma de frase e
73 com forma binária/textual inconclusiva. Os bytes e contextos estão no JSON
local. Não foram promovidos automaticamente.

O catálogo ELF tem 4.299 linhas, incluindo símbolos técnicos, fragmentos e
460 sequências que parecem endereços. A busca limitada do primeiro JAL próximo
não encontrou novo candidato direto ao formatador comum; não equivale a uma
análise completa de todos os chamadores nem prova ausência de outras interfaces.

Em S_PACK, entre o fim declarado do filho 0xF5260 e o limite 0xF5800 há
1.440 bytes, dos quais 432 não são zero. Um registro de 276 bytes em 0xF5278
é idêntico ao conhecido em 0x76278. Isso sugere cópia residual, mas não prova
inatividade: leitura e uso ainda precisam ser demonstrados. Não extrair esses
vestígios como diálogos ativos nem usar o intervalo como espaço livre.

A revisão de FNP_VIEW mostrou molduras/fundos, sem palavras legíveis nos dois
previews. FD_POST, variantes de FNAME_DT, PASSWORD e recursos RMG de minijogos
continuam no índice gráfico para triagem. Há entradas desconhecidas, possíveis
conteúdos comprimidos e bytes nativos fora do alcance do filtro ASCII.
Não existe comprovação de cobertura de 100% do jogo ou percentual total preciso.

## Ordem recomendada após esta fase

1. Preparar mecanismos em conjunto: edição restrita das legendas de pintura,
   recortes gráficos vinculados e recompressor/validador dos créditos. Completar
   o rastreamento de TITLE e dos consumidores dos nomes de itens/destinos.
2. Completar a triagem visual dos atlas indexados, agrupando palavras por tela
   e distinguindo imagens decorativas, nomes protegidos e texto traduzível.
3. Resolver a necessidade de Ó e das outras maiúsculas como extensão explícita
   do perfil aprovado; investigar estratégia dos 49 rótulos sem repetir testes
   de espaço já esgotado. Manter o contexto dos oito nativos como pendência.
4. Só então montar um lote amplo por recursos/telas com alvos, orçamentos,
   controles e aliases conhecidos. Traduzir o conjunto editável, validar inteiro
   e construir uma única versão consolidada para teste manual.

Não é necessário bloquear todo o projeto por um recurso inconclusivo: ele pode
ficar explicitamente separado do lote seguro. Esta rodada não inicia esse lote.

## Validação executada

- **34 testes distintos aprovados**: 19 novos de descoberta, sete de preflight,
  cinco de retenção e três da alpha. Incluem fronteiras de streaming, offsets,
  limites/recusas, round-trip dos tokens comprimidos, casos dos leitores
  originais em memória sintética e classificação conservadora.
- Hashes das 58 referências conferidos; 84 receitas comparadas antes/depois,
  sem alterações. Compilação de validação da base em memória, sem reinserção.
- ISO v037 conferida integralmente antes/depois: 1.704.427.520 bytes, SHA-256
  `e7e65c661409946eb81b8e185c1c71478710cf1aa1538f74a04bd5fbd4c63789`.
- Nenhuma navegação PCSX2 executada, tradução/ISO criada, transferência OneDrive
  ou desligamento nesta fase. Probes de instruções não equivalem a teste visual.

Reexecutar os testes locais:

```powershell
python -m unittest discover -s tests -p "test_discovery*.py"
```
