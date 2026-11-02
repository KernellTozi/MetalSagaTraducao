# Interface v064 — Vendas, Carregar e crédito independente

Pai imutável: translations/interface-v063.json, MAP v045 e layout v005.
Receita vinculada: translations/menu-titulo-v001.json. Implementação local:
tools/title_menu_revision.py. Não altera ELF, fontes, itens, falas, saves,
configurações do emulador ou vídeos. A troca Minério ignoto→Minério pequeno
permanece aguardando a liberação pedida pelo usuário; item 665 fica como v063.

## Botão e título de vendas

SALES LIST passa a VENDAS na região direita [120,144,256,156] do atlas de
S_PACK+0x8C830. Usa os glifos raster nativos, dez pixels de altura, sem escala.
HABILIDADES à esquerda e todos os demais títulos traduzidos permanecem iguais.

RETOMAR passa a CARREGAR. A palavra inteira foi criada pela ferramenta integrada
de imagens, usando work/title-wordart-v001/master.png apenas como referência de
estilo. Não é colagem de letras recortadas. A etapa local reduz a palavra com
uma única escala para as duas dimensões, corpo branco de 16 pixels, e converte
para a paleta RGB/alpha original. Célula 228×24, largura máxima de 224.

Arquivos preservados em work/title-revision-v064/carregar-master.png e
carregar-paleta-original.png, vinculados por SHA-256 na receita. O primeiro
é o resultado da criação de imagem; o segundo é o recurso usado no jogo.
As palavras NOVO JOGO e INSTALAR, borda, preenchimento e fade do atlas RTITLE
mantêm seus pixels. Somente a célula y=128..151 recebe CARREGAR. O crédito antigo
é retirado de y=238..253; a região restante abaixo do botão deve ser transparente.
O frame 1 passa de (0,128,256,256;128,12) para
(14,128,242,152;114,12), preservando o centro do botão e sem incluir o rodapé.
Os outros cinco frames e a correção histórica das posições do menu ficam iguais.

Prompt completo utilizado na ferramenta integrada, sem CLI/API externa:

> Create a single isolated game UI word asset reading exactly CARREGAR in
> uppercase. Reference image is STYLE REFERENCE ONLY: match its heavy slab-serif
> playful slightly slanted white lettering with sharp black outline and subtle
> dark lower-right extrusion, PS2 Metal Saga title menu typography. Draw the
> complete word CARREGAR as new coherent lettering, not a collage of cropped
> letters. Straight baseline, equal cap height, clear spacing and legible R/G
> counters. No additional words or objects. Wide horizontal single-line composition
> with transparent background and generous transparent margins. To be reduced to
> a 228 by 24 pixel sprite: favor clean strong shapes and restrained outline over
> fine texture.

## Origem real do bloco de créditos

A investigação localizou as três linhas oficiais na segunda textura de
DATA/ADATA/ATTLTEX.SDA: offset 0x40430, 512×512/8 bpp, 263.184 bytes.
O atlas também contém o logo Metal Saga e logos de empresas. Eles não são
alterados. A hipótese de créditos incorporados ao vídeo de fundo não se
confirmou: DEMO.STM foi apenas inspecionado, sem alteração ou recompactação.

O bloco oficial ocupa UV [275,298,510,338]. Sua exibição é descrita pelo nó 5
de DATA/ADATA/ATTLSCN.LDT, em 0xCB8, distinto dos sprites RTITLE dos botões.
O retângulo possui largura 235, altura 40, centro Y 176, limites locais
Y=-19/20 e UVs normalizados por 512. A v064 amplia a altura para 54, centro
Y=183, limites locais -26/27, e UV superior Y=284/512. A borda superior
calculada permanece em 381, e a inferior vai de 420 a 434, numa projeção
isolada com origem vertical 224. Esses valores não comprovam a posição final
após o leitor de cena e suas transformações. A igualdade local comprovada é
176-19 = 183-26 = 157; a borda inferior local aumenta de 196 para 210.
Tempo das chaves, relações de nós, cores, largura, limite UV
inferior e todos os demais campos ficam preservados.

As três linhas oficiais são movidas 14 pixels para cima **somente no atlas**,
com cópia exata dos índices. A compensação de UV/posição mantém seu lugar e
tamanho na tela. A nova quarta linha é **tradução: Kernell Tozi**, centralizada,
branca com contorno preto. Fonte instalada Arial Bold em corpo 11, rasterizada
com supersampling e limiar para corresponder à nitidez de duas cores do bloco.
Isso é uma aproximação visual; a fonte original não foi identificada por nome.
Arquivo arialbd.ttf vinculado por hash, sem distribuir a fonte. A assinatura
compartilha o recurso e a animação do bloco oficial, sem herdar a cor de Carregar.

## Amostra de cor compartilhada e proteção do fade

O espaço necessário não estava totalmente vazio: uma amostra branca/preta de
16×8 pixels, [320,290,336,298], era usada por outros nós do mesmo LDT. A primeira
preparação recusou sobrescrevê-la e não gerou ISO. A solução a move, sem mudar
um único índice, para a área transparente [480,480,496,488]. Mantém uma borda
transparente de um pixel ao redor da origem e do destino para a filtragem.

Foram identificadas doze chaves UV que apontam para a amostra, em offsets
0x288, 0x294, 0x2A0, 0x2AC, 0x308, 0x314, 0x320, 0x32C, 0x914, 0x964,
0xF70 e 0xFB0. Todas recebem a mesma translação (160/512,190/512). Valores de
tempo, cores e outros campos das curvas não mudam. O censo deve encontrar
exatamente esses doze pares no LDT original. O transporte dos índices, o
reverso integral dos dois recursos, os limites e os campos são testados.

A identificação do nó, das curvas e dos UVs vem da estrutura binária e da
arte correspondente. **O leitor LDT completo, a interpolação nativa e a GPU
não foram executados.** Não declarar aprovação visual ou de todos os estados
de animação; conferir a entrada do título, o fade e as opções no PCSX2.

## Reprodução e conferência

```powershell
python tools/title_menu_revision.py
python -m unittest discover -s tests -p test_title_menu_revision.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v045.json --interface-draft translations/interface-v064.json --compact-output --build-iso --output work/interface-v064
```

O preparador reutiliza o master salvo, sem repetir a criação por IA. A extração
e compilação binária continuam inteiramente locais. Comparações em
work/title-revision-v064/carregar-comparacao.png, creditos-comparacao.png e
vendas-comparacao.png são previews de arte e geometria, não capturas do emulador.

Roteiro para o usuário: inicialização limpa; conferir CARREGAR selecionado e
desabilitado, crédito sempre junto às três linhas oficiais, sem vínculo com
a cor do botão; conferir logos, fundo e transição/fade; abrir a lista de vendas
e verificar VENDAS, mantendo HABILIDADES e EQUIPAMENTOS iguais à v063.

## Entrega e verificações executadas

Passaram 49 testes distintos: 14 novos e 35 de regressão. A compilação aceitou
6.044 registros MAP e 4.363 unidades de interface, sem recusas. Permanecem
633 campos de nomes de itens, 610 valores distintos, 5.991 corpos/opções,
991 referências explícitas e 108 nomes padrão herdados. VENDAS é uma unidade
nova; revisão do botão e mudança do crédito não são traduções novas.

Preflight aprovou tamanho, SHA-256 integral, recibo e ausência de transação
ativa. Comparação integral v063→v064 confirmou **11.059 bytes em 23 patches**,
sem diferenças extras. Diretório ISO, ELF, fontes/layout, vídeos, itens e
diálogos permanecem iguais à v063. Resumo reports/interface-v064.json;
comparação reports/interface-v064-delta.json. Não houve execução no PCSX2.

ISO: work/interface-v064/MetalSaga-ptbr-interface-v064.iso, 1.704.427.520 bytes.
SHA-256: `27ed954e7a018e9769c0d4e394f8c41da8beeb6f2e2eccad24c1c2a0a9e3db4e`.
Iniciar-Teste.cmd, atalho de pasta, preparador e auditor acompanham v064;
os dois iniciadores foram conferidos em simulação e o auditor de capacidade
foi executado com a receita nova.

Backup v059 teve hash integral e atributo somente leitura reconferidos.
Cinco ISOs de trabalho: a retenção removeu somente a base antiga de investigação
em work/falantes-lookup-v001/. Seus relatórios/receitas permanecem, e ela pode
ser recriada do backup protegido se necessário. A v063 segue disponível.
Os arquivos grandes de inspeção do vídeo foram removidos após a investigação;
masters, índices usados e comparações gráficas foram preservados.
