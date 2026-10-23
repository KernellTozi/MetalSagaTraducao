# Rótulos FBS com recortes GANM vinculados

Política opt-in `fbs-ganm-native-glyph-labels-v003`, implementada em
`tools/interface_graphics.py`. O transporte genérico anterior das seis texturas
permanece separado e não foi ampliado silenciosamente.

Recurso original: DATA/FDATA/FBS_DATA.SDA, SHA-256
`5b53111e7e3ee309f813c6cf3284277774f3c5d0aa2b0d6b53b39fed4884c470`.
Seu SDA raiz contém dez entradas. Somente os pixels das texturas 0, 2 e 3 são
editados; a entrada 3 é liberada exclusivamente neste perfil, após inspeção e
vínculo ao conjunto de rótulos do Satcom.

| Uso | Textura | Offset | Profundidade | GANM | Offset GANM |
|---|---:|---:|---:|---:|---:|
| Comandos de batalha | 0 | 0x40 | 8 bpp | 5 | 0x590D0 |
| Cabeçalhos de mensagens/diário | 2 | 0x20860 | 8 bpp | 7 | 0x59300 |
| Rótulos do Satcom | 3 | 0x30C70 | 4 bpp | 8 | 0x59480 |

As texturas possuem header `<HHIII>` com dimensões, profundidade, offset de
paleta e offset de pixels. As três têm 256×256 pixels. Preservar a paleta RGBA
original byte por byte, inclusive alpha cru do PS2; nenhuma conversão de paleta
ou normalização de alpha é autorizada.

GANM usa `ganm`, quantidade, stride 16 e tamanho total `16 + quantidade*16`.
Cada registro de 16 bytes contém oito inteiros de 16 bits: x0, y0, x1, y1,
dois deslocamentos/hotspot e dois campos nulos nos registros utilizados. Os
terceiro/quarto valores são as coordenadas finais, não largura/altura. Todos
esses dados permanecem intactos. Cada rótulo vincula o hash do seu registro.

## Evidência do consumidor

A análise estática do ELF original identificou:

- Tabela de offsets das quatro primeiras texturas em 0x32D740: 0x40, 0x10450,
  0x20860 e 0x30C70; tamanhos em 0x32D750.
- Inicialização em 0x12CD28–0x12CEB0: referências a fbs_data.sda/f_common.sda,
  carga dos offsets e objetos de textura com stride de 0x150.
- Em 0x12CAE4/0x12CAEC o código compõe 0x59480, soma à base FBS e usa o objeto
  de textura acrescido de 0x3F0 (três strides); chamada em 0x12CAFC.
- Outro consumidor em 0x127A50–0x127B10 combina a base FBS com 0x59480 e o
  objeto com 0x3F0. O conteúdo dos 30 recortes coincide com a inspeção do atlas.
- Referências a 0x590D0 e 0x59300 identificadas no mesmo conjunto de interface;
  os recortes individuais de batalha/cabeçalhos coincidem com os desenhos
  inspecionados. Não generalizar esse vínculo para outros GANM ou arquivos.

O ELF inteiro e as janelas indicadas são vinculados por SHA-256. Endereços
virtuais do segmento de código diferem dos offsets de arquivo por **0xFF000**.
Essas evidências não representam execução do jogo nem medição do recorte na tela.

## Composição

Usar SUC24I26.GFI original e as células de acentos do perfil bitmap v002, conferidas
contra os hashes históricos de fontes. Os pares da tabela ASCII de 26 pixels
em 0x316898 auxiliam o espaçamento da composição local; não há patch dessa tabela.
O resultado é um bitmap independente da codificação de texto em execução.

Altura de tela rasterizada: 16 pixels nos botões e 12 nos cabeçalhos. As máscaras
são centradas no interior do recorte, com margem de três/dois pixels. A borda
externa permanece original. O fundo interior é reconstruído com a cor nativa;
isso substitui a pequena textura de fundo existente nessa área, uma escolha de
desenho limitada à região do rótulo.

Usar apenas cores já presentes na paleta, com o mesmo alpha da cor de fundo. O
antialias escolhe índices por distância RGB dentro dessa paleta imutável. Não
quantizar nem reordenar a paleta. A altura não diminui para acomodar palavras:
quando necessário, a largura da máscara é ajustada; fator abaixo de 0,72 é
recusado. “Munição” usa 0,75 nesta primeira proposta e merece observação visual.
Essa composição tem seu próprio espaçamento gráfico; não pretende reproduzir
todos os cálculos do motor de diálogos.

Cada máscara possui hash na receita para detectar mudanças de Pillow/renderizador.
Uma divergência exige investigação/revisão, não atualização automática do hash.
As traduções e IDs são uma lista revisada explícita; não liberar outros desenhos
alterando um retângulo no JSON. Nenhum PNG original ou GFI é versionado.

## Integridade

Após cada rótulo, comparar os índices de pixels e recusar qualquer diferença fora
do retângulo interior autorizado. Ao terminar uma textura, conferir header, paleta
e cauda e realizar reversão de todos os índices ao original. O compilador da ISO
compara ainda cada byte da imagem com os patches esperados. A comparação com a
v005 verifica que nenhum diálogo, fonte, código, índice ou outro recurso mudou.

Os testes incluem ID desconhecido/duplicado, máscara e origem divergentes, mudança
de tradução/retângulo não autorizada, excesso de compressão e Unicode não suportado.
Também comparam integralmente os campos textuais da v005. A validação visual deve
ser acumulada no roteiro do usuário, separada desses testes binários.
