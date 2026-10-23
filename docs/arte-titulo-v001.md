# Arte completa das palavras do título — proposta v001

Por solicitação do usuário, esta etapa cria as palavras completas antes da
reinserção. NOVO JOGO, RETOMAR e INSTALAR foram desenhadas em uma nova arte
transparente, usando o título original somente como referência de estilo.
Não é um alfabeto/font TTF nem uma montagem de recortes dos glifos existentes.

Foi usada a ferramenta integrada **image_gen**, sem CLI/API externa configurada
no computador. O resultado foi copiado para o workspace:

- `work/title-wordart-v001/master.png`: arte RGBA 1983×793.
- `work/title-wordart-v001/preparado/*-master.png`: palavras separadas em alta resolução.
- `work/title-wordart-v001/preparado/*-24px.png`: palavras em células RGBA 228×24.
- `*-paleta-original.png`: PNG indexado, com RGB/alpha brutos da paleta RTITLE.
- `*-preview-paleta.png`: preview com alpha normalizado para visualização comum.
- `comparacao.png`: original à esquerda e proposta à direita, ampliação 2×.
- `tamanho-real.png`: revisão de legibilidade em escala 1:1.
- `work/title-wordart-v001/palavras-editaveis.zip`: pacote local com as artes e metadados.

Os PNGs permitem edição em um editor de imagens; não contêm camadas vetoriais
ou letras separadas. O master preserva a transparência. A separação é por linha
inteira, sem cortar/remontar caracteres. A redução usa um único fator em ambos
os eixos para cada palavra, corpo branco de 16 pixels e topo comum na linha 4.
Nenhum eixo é apertado independentemente para forçar o encaixe.

Ferramenta local: `tools/prepare_title_wordart.py`. Detecta três linhas separadas,
recusa fontes opacas, overflow e diretório de saída existente; produz os PNGs,
conversão para a paleta original e manifesto de hashes. Não altera texturas do
jogo ou ISOs. A geração artística não faz parte da execução repetitiva local:
uma vez salvo o master, a preparação funciona integralmente em Python/Pillow.

```powershell
python tools/prepare_title_wordart.py --master work/title-wordart-v001/master.png --output work/titulo-nova-preparacao
python -m unittest discover -s tests -p "test_title_wordart_preparation.py" -v
```

Quatro testes passaram: preparação e paleta, preservação do master, recusa de
saída existente, entrada sem transparência e número incorreto de linhas.
Relatório: `reports/title-wordart-v001.json`.

**Situação:** proposta artística inspecionada pelo agente, sem aprovação visual
do usuário e sem teste no PCSX2. A ISO/iniciadores continuam na interface v013.
Não apresentar a conversão de paleta como reinserção ou execução validada.
As fontes do diálogo, Satcom, assinatura e créditos oficiais não foram alteradas.
O próximo passo é avaliar o desenho no tamanho pequeno e, após definir a arte,
vincular os índices revisados à receita gráfica e aos testes de integridade.

## Prompt da geração

Referência: `work/title-original-enlarged.png`; transparência solicitada à
ferramenta integrada. Prompt:

> Use case: text-localization. Create a production lettering asset for a Brazilian Portuguese localization of this PS2 title menu. Reference image is ONLY a typeface/style reference, not a background to reproduce. Draw three NEW complete lines, exact text: "NOVO JOGO", "RETOMAR", "INSTALAR". Spell R-E-T-O-M-A-R clearly with proper R counters and diagonal legs; J must be an actual J. Match reference's distinctive extremely heavy, playful slab-serif uppercase lettering: chunky slightly right-leaning irregular trapezoid stems, short angular slab serifs, white fill, thin charcoal/black outline and a restrained gray lower-right drop shadow. Preserve the original old-console bold character, avoid generic Arial/sans-serif, rounded bubble lettering, modern typography or overdecorated logos. Draw clean coherent original letter shapes as complete words, consistent cap height, common straight baseline, natural tight but NON-TOUCHING spacing. All text straight horizontal, no perspective or arc. Composition: three centered lines separated by large clear transparent gaps, plenty of exterior transparent margin. NOVO JOGO on top, RETOMAR middle, INSTALAR bottom. Same cap height for all three lines. Transparent background, no other text or labels, no map, border, logos, checkerboard, watermark, button panels, highlights or extra graphics. This must remain legible when each line is reduced to about 180-200 pixels wide by 24 pixels tall. Do not reproduce the coarse enlarged pixel grid from the reference; create crisp master lettering so it can be carefully downsampled later.
