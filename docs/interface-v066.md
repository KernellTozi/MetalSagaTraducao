# Interface v066 — tanque, LOVE Machine, locais e bebida

Pai: interface v065, MAP v045 e layout v005. Filho: interface v066 sobre
MAP v046. Ferramenta local tools/tank_drinking_gaps.py e manifesto vinculado
translations/lacunas-tanque-bebida-v001.json. Não altera itens, nomes de
personagens, tanques, equipamentos únicos, LOVE Machine, saves ou configurações.
Minério pequeno continua aguardando liberação; item 665 fica igual ao pai.

## Cabeçalhos

| Origem | Alvo | Célula no atlas S_PACK+0x8C830 |
|---|---|---|
| PARTS LIST | PEÇAS | [118,120,256,132] |
| VEHICLE NAME | NOME | [4,192,158,204] |
| SELECTED ITEMS | SELECIONADOS | [4,228,196,240] |

NOME usa o contexto da imagem do veículo; SELECIONADOS usa a lista de itens
ao lado. São rótulos completos, sem abreviações. Glifos nativos, dez pixels
de altura e intervalo de três, sem redimensionamento. P vem da linha nativa
EQUIPMENT LIST; Ç preserva o C inteiro e acrescenta dois pixels de cedilha
nas duas linhas inferiores da célula de 12 pixels. As outras letras mantêm
a linha de base original. A nova cedilha requer conferência visual nesse
cabeçalho; não modifica a fonte GFI ou outros códigos do motor.

## Locais e consistência

| Origem | Alvo | Ocorrências de nome |
|---|---|---|
| Abandoned Building | Prédio abandonado | 1, nó tipo 6, mapa 108 |
| Abandoned Buildings | Prédios abandonados | 4, tipos 2/7, mapa 218 |
| Sunken Ruins | Ruínas submersas | 2, tipos 2/7, mapa 183 |

Offsets MAP: 0x970D7DC; 0x1B0A0FDC/0x1B0A1800/0x1B0AB800/0x1B0B4800;
0x1771318C/0x17727000. Preservar os nós e o restante dos registros. O nome
singular codifica em 18 bytes, mantendo seu NUL original. O byte FF em +31
do registro tipo 6 não pertence à tradução e permanece intacto. Os demais
alvos usam somente o prefixo necessário, dentro de 32 bytes e com zeros
originais conferidos. As fronteiras continuam no catálogo de 300 mapas e
839 campos de nomes tipo 2/3; não se promove outra estrutura por semelhança.

MAP v046 revisa somente dois títulos supr já traduzidos. O título
map.supr.1b0bc77c passa de “- Prédios Vazios -” a “Prédios abandonados”,
coerente com o local. Há 23 bytes disponíveis: a versão com dois hífens teria
24 bytes; o nome completo sem a decoração tem 20 e cabe. Não abreviar o nome
nem relaxar o limite. map.supr.1857c10c passa de “Ruínas Submersas” a
“Ruínas submersas”, mesma redação/capitalização dos avisos. Tem 17 bytes em
capacidade 19. Registros de 72/68 bytes, cabeçalho de 48, controles, offsets
e demais traduções ficam preservados pelo compilador existente de slots.
O compilador sinaliza conservadoramente uma linha mais larga em Ruínas
submersas; o alvo cabe no slot, mas a margem deve ser conferida em partida.

## Minigame de bebida

A textura HUD é a entrada 96 de NDATA.SDA, offset 0xB6A800, 512×512/8 bpp.
São quatro rótulos: Left:→Tempo, Drinks→Bebidas, DRINK→BEBER e DANGER→PERIGO.
As regiões de limpeza e desenho são vinculadas no manifesto. O temporizador
usa a fonte GFI já existente, dentro dos 48×20 pixels ocupados pelo rótulo
original, com ajuste horizontal registrado; não aumenta o recorte de desenho.
Os outros rótulos usam Arial Bold local em tamanhos 20/19/19, sem resize.

Os índices originais de fundo/tinta são reutilizados. A leitura de cores e os
previews usam a permutação de CLUT CSM1 de 8 bpp, já empregada pela ferramenta
de batalha: troca os bits 3/4 do endereço da paleta. Isso não reordena os
pixels nem altera a paleta no arquivo. Os índices 51/241 do HUD correspondem
a azul (0,83,163,127) e creme (237,229,217,127) após essa leitura. O primeiro
preparo recusou a identificação da tinta porque a cor dominante do pequeno
recorte era a própria palavra, não o fundo; a identificação foi corrigida
com a amostra de fundo original e a CLUT, sem produzir ISO naquela tentativa.

As áreas dos números, relógio, barra, indicadores, garrafas e títulos
READY/START/TIME UP/CLEAR permanecem idênticas. A regra anterior do usuário
dispensa recriar esses títulos decorativos. Rótulos nas embalagens também
ficam como arte original. BEBER fica no mesmo intervalo da palavra DRINK,
compartilhado pelo atlas; confirmar sua exibição no comando do jogo.

A legenda de controle em ELF 0x31F7B0 passa a Beber/Sair/Ajuda, preservando
exatamente os três tokens nativos de botões e sua ordem. Usa a célula de
32 bytes com cauda original zerada, sem referências interiores detectadas;
texto alvo tem 28 bytes e NUL. Os valores de tempo, quantidade, dificuldade
e comportamento dos comandos não são alterados.

## Tutorial

Entrada 69 de NDATA.SDA, offset 0x7B1000, 512×512/8 bpp. O painel explica:
beber tudo antes de o tempo acabar; cada bebida enche a barra em ritmo
diferente; encher completamente a barra faz o personagem engasgar; apertar
o botão várias vezes para beber. O título e a seção de controles também
estão em português. Usa o desenho GFI já adotado em outros painéis, com
quebras automáticas e verificação de colisões, sem compressão horizontal.

Os três ícones de bebidas, o ícone do botão e o rodapé 1/1 são copiados do
original sem perda. Somente o interior [4,4,508,396] é redesenhado; borda e
parte inferior da textura ficam intactas. O fundo e a tinta usam índices
da própria imagem. Cabeçalhos, paleta/alpha, offsets SDA e dimensões não mudam.
O transporte é linear, sem recompressão ou realocação de recursos.

## Reprodução e roteiro

```powershell
python tools/tank_drinking_gaps.py
python -m unittest discover -s tests -p test_tank_drinking_gaps.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v046.json --interface-draft translations/interface-v066.json --compact-output --build-iso --output work/interface-v066
```

Comparações em work/interface-v066-investigacao/cabecalhos-comparacao.png,
bebidas-comparacao.png e tutorial-comparacao.png. São previews locais, não
capturas do PCSX2. O preparador e a compilação funcionam localmente sem IA/APIs.

O usuário deve conferir os três cabeçalhos, cedilha de PEÇAS, avisos externos
e títulos de entrada dos locais, tempo/contador/comando de bebida, estado de
perigo e tutorial com os botões corretos. Não se executou a navegação ou a
GPU nesta rodada; a edição de pixels e os testes binários não comprovam todos
os seletores/recortes de desenho no jogo. O crédito v065 e demais elementos
anteriores continuam aguardando suas próprias avaliações visuais.

## Entrega verificada

Passaram 38 testes distintos: 12 novos e 26 de regressão. A compilação aceitou
6.044 registros MAP e 4.379 unidades de interface, sem recusas. São 16 unidades
novas: três cabeçalhos, sete nomes de nós, uma legenda, quatro rótulos HUD e
um painel de instruções. Os dois títulos de locais são revisões e não aumentam
a contagem de diálogos. Permanecem 633 campos de itens/610 valores distintos,
5.991 corpos/opções, 991 referências explícitas e 108 nomes padrão herdados.

Preflight aprovou hash integral, tamanho, recibo e ausência de transação ativa.
A comparação integral v065→v066 confirmou **27.324 bytes em 13 patches**,
sem diferenças extras. Diretório, fontes/layout, itens, crédito e demais
gráficos/falas fora das revisões explícitas foram preservados. Relatórios
reports/interface-v066.json e interface-v066-delta.json.

ISO: work/interface-v066/MetalSaga-ptbr-interface-v066.iso, 1.704.427.520 bytes.
SHA-256: `51e27dda9854cb369ea49753a67a7bb4d7c1fe5d54f86581821ef6acc32b43e3`.
Iniciador, atalho de pasta, preparador e auditor acompanham v066. Os dois
iniciadores foram conferidos em simulação e a auditoria de capacidade executada.

Backup v059 teve hash integral e atributo somente leitura reconferidos. A
retenção manteve cinco ISOs de trabalho, removendo só a antiga v061-final;
receitas e relatórios permaneceram. Não houve PCSX2, OneDrive ou desligamento.
