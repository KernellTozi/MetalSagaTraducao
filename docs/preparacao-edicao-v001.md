# Preparação dos mecanismos e triagem gráfica

Rodada dedicada a concluir a preparação que faltou na entrega v038. Não houve
novo lote de tradução, desenho de fontes, construção de ISO, navegação PCSX2
ou cópia OneDrive. A versão jogável permanece interface v038/MAP v037.

## Resultado concreto

| Conjunto | Preparado nesta rodada | Limite ainda existente |
| --- | --- | --- |
| Créditos finais | Recompressor LZSS, JSON editável com vínculos e reconstrução de FD_END.SDA em cópia | Apresentação/fontes no renderizador e integração à ISO ainda não liberadas |
| Botões de pintura | Doze recortes indexados com exportação/importação, dez editáveis e dois protegidos | Associação de uso completa dos atlas principal e de carimbos ainda pendente |
| Atlas restantes | Transporte reversível das 119 texturas em 14 recursos, mantendo paletas/alpha | Transporte de pixels não comprova recortes nem uso em execução |
| Triagem gráfica | Todas as 119 texturas reconhecidas revisadas em 18 folhas | 365 entradas de estrutura desconhecida continuam fora da inspeção visual |

Os pacotes estão juntos em `work/preparacao-edicao-v001/`. Imagens, originais
e JSON com textos do jogo ficam somente nessa pasta, fora do Git. A classificação
pública por textura, offset e hash está em `reports/triagem-grafica-v001.json`.
Os resultados de integridade estão em `reports/preparacao-edicao-v001.json`.

## Créditos: mecanismo implementado

`tools/credits_edit_pack.py` reaproveita a extração comprovada de FD_END e
acrescenta compressão determinística da variante LZSS de dicionário zerado de
1.024 bytes, posição inicial 1006, flags LSB, comprimentos 3–18 e referências
com sobreposição/circulação. Não incorpora código externo.

A recompressão dos 4.222 bytes originais ocupa **2.348 bytes** no slot de
4.096 bytes; o fluxo original ocupava 2.351. Ambos descomprimem para os mesmos
bytes. A nova saída foi conferida pelo decoder Python e pelo laço de instruções
original do jogo em memória sintética. Os testes incluem zeros iniciais,
sobreposição, volta do dicionário, bytes aleatórios e alterações sintéticas.
Sem edição, a importação conserva o fluxo original byte a byte.

O JSON contém as 292 linhas, com IDs, hashes, bytes e categoria. São **51 linhas
selecionáveis**: 49 cabeçalhos de funções e duas frases de encerramento. As
outras 241 linhas (incluindo nomes, empresas e layout) permanecem imutáveis.
O prefixo nativo de dois bytes dos cabeçalhos é preservado como bytes opacos;
não foi reinterpretado como caractere português. Não se traduzem profissionais
ou empresas. A ocorrência Atlus da frase de apresentação também é protegida.

Só editar o campo `translation` das linhas selecionáveis. `null` mantém a
origem. Preservar IDs, ordem, metadados, prefixos, espaços originais das linhas
protegidas e todos os delimitadores CRLF. O importador rejeita comandos,
inserções de linhas, glifos não mapeados, texto acima de **35 bytes por linha**,
saída descomprimida acima de 4.222 bytes e compressão acima de 4.096 bytes.
Os limites são conservadores, não convite para abreviar traduções para caber.

Evidência adicional: em 0x1390B4–0x1390C4 o consumidor guarda o tamanho
descomprimido vindo do cabeçalho; 0x139D88–0x139E28 procura CRLF e substitui o
delimitador consumido por espaços na memória; 0x139D40 distingue o início `#`,
e 0x139E60 trata seu caminho numérico. O texto é copiado ao buffer temporário
em 0x1399E4–0x139A10. Os novos limites evitam exceder o maior tamanho de linha
original. Esses trechos foram inspecionados e vinculados por hash; **não foram
executados como um renderizador completo**. Somente o decoder foi executado no
harness. Ainda verificar fonte, largura, alinhamento e fluxo real antes de
integrar traduções desses créditos à ISO.

Reproduzir em caminhos novos:

```powershell
python tools/credits_edit_pack.py export --output work/meu-pacote/creditos.json
python tools/credits_edit_pack.py import --pack work/meu-pacote/creditos.json --output work/meu-pacote/creditos-reconstruidos
```

Saída: `FD_END.SDA` separado e relatório, sem tocar no original ou na ISO.
Todos os bytes fora de 0x800–0x1800 permanecem idênticos; tamanho e descritores
SDA não mudam. O campo `iso_integration: false` é intencional.

## Pintura: recortes prontos para edição local

`tools/paint_button_pack.py` exporta os dez retângulos do GANM da entrada 14,
um retângulo de componente da entrada 7 e o botão de edição de carimbo da
entrada 9. As texturas correspondentes são as entradas 13, 6 e 8.
O botão adicional no atlas de carimbos não havia sido incluído na lista inicial
de treze rótulos. A seleção agora está explícita, sem presumir que cada imagem
inteira é texto traduzível.

As linhas exclusivas de SUB/SE do atlas principal são protegidas contra edição
de pixels. A linha mista do chassi/arma principal continua editável para futura
composição, mas **preservar MAIN nela exige revisão da arte**: o importador não
reconhece palavras por OCR. Não alegar proteção semântica automática de toda
palavra dentro de uma imagem.

Os PNGs usam índices e paleta originais. Dimensões, RGB, alpha, GANM, hotspots,
descritores e pixels fora dos recortes permanecem intactos. O pacote é vinculado
ao recurso, ELF, janelas e geometria originais. Toda a entrada é validada antes
de criar a pasta de saída; reversão e releitura da cópia são conferidas.

O encaminhamento de argumentos em 0x5E250–0x5E284 foi executado até os dois
chamadores: textura em 0xCCE0/tamanho 0x2410 e GANM em 0xF0F0. O harness fornece
a base e o contexto; não executa carregamento completo ou GPU. Para o atlas de
dez botões e o carimbo, a ligação ainda é visual/geometria, sem comprovação
completa do dispatch. Por isso o importador produz apenas uma cópia de
`S_PAINT.SDA`, sem atualizar a ISO ou a receita v038.

```powershell
python tools/paint_button_pack.py export --output work/meu-pacote/botoes
python tools/paint_button_pack.py import --pack work/meu-pacote/botoes --output work/meu-pacote/pintura-reconstruida
```

Editar os PNGs em modo indexado, mantendo tamanho, índices e paleta. Não
redimensionar, quantizar ou converter para RGB antes de importar. Nenhuma arte
foi traduzida nesta rodada.

## Triagem gráfica concluída no universo reconhecido

As 119 texturas dos 17 arquivos catalogados foram classificadas uma única vez:

| Classe | Texturas |
| --- | ---: |
| Interface com texto latino candidato | 18 |
| Texto nativo candidato | 1 |
| Interface mista com categorias protegidas | 1 |
| Texto com mecanismos de tradução existentes, sujeito a revisão | 6 |
| Nomes/assinatura protegidos | 6 |
| Marcações de controles, sigla ou canais de cor protegidos | 3 |
| Sem palavra localizável observada | 84 |

Esses números são de **texturas**, não de frases, palavras ou telas. As imagens
são de origem; uma palavra inglesa no atlas original pode já estar substituída
pela receita v038. A classe dos seis atlas com mecanismos existentes não
comprova que toda palavra desses atlas esteja traduzida.

Novos conjuntos práticos para o próximo lote: instruções/resultados dos
minijogos, carregamento, elementos genéricos dos cartazes e botões de pintura.
Os nomes rasterizados de procurados permanecem protegidos. O atlas de regras
do minijogo de cães contém texto nativo; a presença no arquivo não prova seu
uso na versão em inglês, exigindo rastrear o consumidor antes da edição.
FNP_VIEW e a maior parte de FD_POST são molduras/ilustrações, não trabalho de
tradução a somar automaticamente. Números, setas, sprites de animais e logotipos
também não foram transformados em falsas pendências de texto.

Três arquivos inspecionados não têm texturas aceitas pelo parser atual; as
365 entradas desconhecidas são mantidas no relatório por hash/offset, incluindo
estruturas ou flags ainda não suportadas. Portanto a triagem terminou para os
**119 atlas reconhecidos**, não para todo possível recurso gráfico do jogo.

O transporte antigo de 69 texturas permanece reproduzível. O novo perfil é
explícito e não amplia silenciosamente o importador legado:

```powershell
python tools/interface_atlas_pack.py export --profile remaining-v002 --output work/meu-pacote/atlas
python tools/interface_atlas_pack.py import --pack work/meu-pacote/atlas --output work/meu-pacote/atlas-reconstruidos
python tools/triage_graphic_pack.py --pack work/meu-pacote/atlas --output work/meu-pacote/folhas
```

As 119 texturas estão em 14 recursos; os três arquivos sem texturas reconhecidas
são verificados na origem, mas não são copiados inutilmente para a saída. O
importador pode transportar índices editados, preservando todo o restante; ele
não concede permissão de integração automática de qualquer imagem na ISO.

## Verificação executada

**50 testes distintos aprovados**, incluindo onze novos: recompressão real e
sintética conferida no decoder original, preservação dos nomes/linhas,
orçamentos e recusas, round-trip dos doze recortes, alteração de um pixel com
comparação do recurso inteiro, proteção de SUB/SE e transporte das 119 texturas.
As regressões do perfil legado de 69 atlas, do pacote antigo de seis texturas,
da descoberta, das legendas v038, do preflight, da retenção e da alpha passaram.
Reexecutar os novos testes:

```powershell
python -m unittest discover -s tests -p test_edit_preparation.py
```

Os pacotes locais sem edição foram importados de fato: os 14 recursos dos
atlas, S_PAINT e FD_END resultaram idênticos às referências. A ISO v038 foi
conferida integralmente: SHA-256
`0b4c931e141de804200d4e42c4fe125f9013707308b1e829871f5159102727c0`,
1.704.427.520 bytes. Continuam cinco ISOs de trabalho e a alpha protegida.
Não há nova versão jogável para testar nesta rodada.

## Ordem de continuação

1. Vincular uso/recortes restantes da pintura e compor seus botões em conjunto,
   preservando categorias e aparência. O transporte e as recusas já estão prontos.
2. Preparar receitas de recortes por minijogo/carregamento/cartazes a partir da
   triagem, preservando nomes, ilustrações e símbolos. Não traduzir os atlas
   inteiros indiscriminadamente.
3. Concluir apresentação dos créditos (fonte/métricas/alinhamento) e então
   traduzir os 51 cabeçalhos/frases selecionáveis em um conjunto revisado.
4. Consolidar os conjuntos liberados em uma receita e uma ISO para teste manual.
   TITLE, limites de itens, destinos e texto nativo sem contexto continuam nas
   pendências específicas; esta preparação não removeu esses bloqueios.
