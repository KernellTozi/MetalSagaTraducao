# Pintura — comparação visual e preparo de composição

O usuário dispensou novas etapas dos créditos em 26/10/2026: manter o que
já foi entregue na v039, sem expandir essa frente. Pediu comparações visuais
no chat antes/depois para avaliar os próximos desenhos. A ISO jogável continua
v039; esta etapa não cria ou aplica uma nova imagem.

## Seis propostas para análise

Comparação em `work/pintura-graficos-proposta-v001/comparacao-pintura.png`:
original à esquerda, proposta à direita, ambas ampliadas em 2x pelo vizinho
mais próximo, sem suavização adicional. O aspecto no emulador ainda não foi
verificado. A imagem de comparação foi inspecionada e apresentada no chat.

| Recorte da entrada 13 | Original | Proposta |
| --- | --- | --- |
| 0 | Edit | Editar |
| 3 | Vehicle | Veículo |
| 4 | Tools | Ferramentas |
| 5 | Stamp Select | Escolher carimbo |
| 8 | Stamp Edit | Editar carimbo |
| 9 | Palette | Paleta |

Essas propostas usam um alfabeto desenhado por polilinhas em grade inteira,
com corpo maiúsculo de 16 pixels, linha de base comum na linha 20 da célula,
e relevo de um pixel com cores da paleta original. Não usam fontes instaladas,
redimensionamento de palavras ou colagem de letras recortadas. O desenho
permanece **proposta**, sem alegar identidade perfeita com a tipografia nativa
ou aprovação do usuário. O í de Veículo está desenhado dentro do raster;
isso não acrescenta códigos ou glifos ao codec/GFI do jogo.

Zoom, o rótulo misto Chassis/Main, Sub Gun, SE, a legenda de componente e
o botão decorado de carimbo permanecem originais. MAIN/SUB/SE não tiveram
pixels alterados. Não contabilizar as seis propostas como novos campos
traduzidos na ISO: o total jogável permanece 3.804.

## Avanço técnico independente da revisão da arte

Foi localizada a tabela original de quatro pares textura/GANM do painel de
pintura. Tabela de offset/tamanho de textura em ELF 0x318EA0 e tabela GANM
em 0x318EC0:

| Índice | Textura SDA | GANM SDA |
| --- | --- | --- |
| 0 | entrada 11, 0x13F10 | entrada 12, 0x34320 |
| 1 | entrada 13, 0x34360 | entrada 14, 0x54770 |
| 2 | entrada 15, 0x54820 | entrada 16, 0x74C30 |
| 3 | entrada 17, 0x74CF0 | entrada 18, 0x95100 |

Executados oito encaminhamentos de argumentos do código original, em RAM
sintética: 0x5C728–0x5C740 até o consumidor de textura 0x1ACC58 e
0x5C768–0x5C784 até o consumidor GANM 0x19AF80, quatro casos cada. A base do
SDA e os objetos são fornecidos pelo harness. Registradores, tamanho carregado,
ponteiros e correspondência com o SDA foram conferidos; não foram executados
upload, GPU, seleção real, dispatch completo ou PCSX2. Isso substitui a mera
associação visual por evidência de carregamento, sem declarar toda a execução
do menu comprovada. O vínculo de componente anterior continua preservado.

`tools/paint_graphic_proposals.py` gera os dois pacotes indexados, a comparação
e uma cópia local reconstruída pelo importador existente. Paletas, alpha,
dimensões, bordas de dois pixels, GANM, estruturas SDA e demais recursos
continuam intactos. Somente seis interiores da textura 13 são alterados.

### Preservação das traduções de pintura já existentes

Foi implementada uma verificação de composição em memória com os **228 campos
de legenda já traduzidos** da receita v039. O teste aplica a arte ao plano de
pixels da textura e as legendas aos seus campos separados, confere que não
se sobreponham e desfaz tudo até recuperar a fonte original byte a byte.

Isso evita uma regressão importante: importar o SDA inteiro produzido a partir
do original apagaria as legendas traduzidas. Uma integração futura deverá
levar somente os pixels de 0x34770, tamanho 0x20000, e preservar os patches
de legendas em 0xAE6A0. Nenhum arquivo dessa proposta é uma nova ISO.

## Reprodução e testes

```powershell
python tools/paint_graphic_proposals.py --output work/minha-proposta-pintura
python -m unittest discover -s tests -p test_paint_graphic_proposals.py
```

Usar pasta nova. Os rasters, originais e binário reconstruído ficam em work/;
somente ferramenta, testes, manual e metadados próprios vão ao Git.

Nove testes novos verificam os quatro pares originais, bloqueio de fontes
divergentes, dimensões/paleta/alpha, seis recortes preservados, bordas,
corpo/linha de base sem escala, caracteres não previstos, overflow e controles,
rejeição de alterações fora dos interiores, composição das 228 legendas e
recusa de sobrescrita/saída fora de work/. Validação visual em jogo pendente.

Próxima ação depende do parecer sobre o desenho apenas para essas seis artes;
investigação dos demais recortes e conjuntos continua independente. Créditos
não são prioridade. Não copiar OneDrive nem desligar o computador nesta etapa.
