# Interface v007 — fonte própria dos botões do Satcom

O usuário apontou que os rótulos v006 eram mais arredondados que “Remote”. A
comparação confirma a causa: a v006 rasterizava os glifos GFI dos diálogos, uma
família diferente da fonte já desenhada nos botões. Ser uma fonte do próprio jogo
não a torna equivalente à fonte original de cada elemento gráfico.

Esta revisão corrige **26 rótulos do Satcom**. Mantém as traduções, os 573 campos
textuais, MAP v030, layout v005 e os outros 14 rótulos gráficos da v006. Total
compilado continua 613 ocorrências/campos; não houve ampliação da tradução nesta
rodada. Batalha e cabeçalhos precisam de comparação tipográfica própria: não
declarar a correção do Satcom como aprovação dessas famílias.

## Fonte recuperada do próprio atlas

Política `satcom-original-raster-typeface-v004`, ferramenta
`tools/satcom_native_font.py`. Somente pixels da textura 3 de FBS_DATA.SDA,
mantendo os recortes GANM 8. A receita v004 vincula por hash a receita histórica
v003; os outros 14 desenhos continuam reproduzíveis e idênticos.

Foram recuperados 21 glifos diretamente dos rótulos originais, incluindo Remote,
Info, Hunt, Mail, Alert, Music, Config, Diary e Help. As duas variantes são
recuperadas separadamente: clara sobre o botão escuro e escura sobre o painel
claro. O conjunto, delimitado por `SAMPLES`, tem cobertura somente dos rótulos
revisados, não é uma fonte completa para qualquer texto.

L/P/J/j e os três caracteres acentuados necessários (á, ú, ç) são construções
explícitas a partir de hastes, barras e descendentes desses glifos nativos. Eles
não foram encontrados prontos no atlas e não devem ser descritos como cópias
exatas de caracteres originais. Os acentos preservam o corpo da letra; não se
reduz sua altura para encaixar a marca.

O corpo de maiúscula mantém os 12 pixels do original dentro de uma célula de
18 pixels, reservando espaço para acentos e descendentes. Não há resize,
interpolação geométrica ou compressão horizontal; rótulo que exceda a largura
permitida é recusado. Procurados/Mensagens cabem no interior de 74 pixels com
espaçamento inteiro de um pixel entre letras. Posições e margens do botão não
mudam. Os bytes de Remote, nas duas variantes, continuam originais.

As coberturas dos glifos são recuperadas das cores da paleta. Na variante clara,
a granulação de fundo não deve virar halo do caractere: a tinta forte original
é preservada, enquanto tons fracos de borda exigem suporte da forma normal com
margem de um pixel. As paletas, alpha, header, GANM e bordas permanecem intocados.
Os índices escolhidos para a composição continuam dentro da paleta original.

## Como conferir

`Preparar-Graficos.cmd` exporta previews da receita corrigida, sem ISO.
`Preparar-Interface.cmd` valida a v007; `Iniciar-Teste.cmd`/`Testar-Interface.cmd`
abrem a ISO consolidada v007 quando construída.

```powershell
python tools/interface_graphics.py --recipe translations/interface-graphics-v004.json --output work/previews-satcom-novo
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v007.json --output work/interface-v007 --build-iso
```

Saídas devem ser novas. A comparação ampliada local fica em
`work/satcom-native-v004/comparacao-fontes.png`: original, v006 e proposta v007.
A inspeção dos previews confirmou a mudança de família e a aproximação do
desenho quadrado. Isso não constitui aprovação visual do usuário ou execução no
PCSX2. Conferir quando conveniente: peso nas duas variantes, letras L/P/J/j,
acentos, cedilha, legibilidade e recorte de Procurados/Mensagens.

Nenhuma cópia OneDrive é realizada automaticamente. Preservar alpha e dez ISOs
de trabalho; manter receitas anteriores para reprodução e comparação.
