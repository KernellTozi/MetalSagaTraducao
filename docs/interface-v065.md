# Interface v065 — legibilidade do crédito

O usuário reprovou a leitura de Kernell Tozi na v064, especialmente a letra
e, na captura codex-clipboard-9c9c2023-4e3f-458c-ad8d-64f81e21b255.png.
Essa validação negativa substitui qualquer avaliação favorável do preview
anterior. A v065 revisa somente a linha de tradução, sobre a v064 imutável.
Não declara a nova proposta aprovada no PCSX2.

## Novo desenho

A v064 desenhava Arial Bold em 44 pixels, reduzia para corpo 11 e aplicava
limiar 96. A amostra recebida mostra espaços internos pouco legíveis. A v065
desenha **Arial Bold diretamente em 12 pixels**, com o ajuste do rasterizador
para esse tamanho. Cada glifo começa numa coordenada inteira; os avanços são
arredondados para cima, sem compressão, interpolação ou redução posterior.
O limiar 128 mantém tinta branca e contorno preto da paleta existente.

Texto exato: **tradução: Kernell Tozi**. Máscara 129×15 pixels, contorno de
um pixel, centralizada na largura original de 235. A letra e tem seis por
sete pixels de tinta, um espaço interno fechado de quatro pixels e abertura
inferior direita ligada ao fundo. Os testes protegem o espaço interno e a
abertura, além do posicionamento inteiro, limites e cores. O desenho não
depende de geração de imagem ou API; é reproduzível em Python local.

O arquivo instalado arialbd.ttf é vinculado por hash e não é distribuído.
A família é uma aproximação visual, não identificação da fonte original.
Ela não altera as GFI, fontes de diálogo, métricas ou mapeamento de acentos.

## Escopo binário

Pai: translations/interface-v064.json. Filho: translations/interface-v065.json.
Política credit-native-hinted-integer-raster-v001 em tools/credit_readability.py;
manifesto translations/credito-legivel-v001.json, vinculado por hash.

Somente o patch herdado title.official-block-credit muda, na segunda textura
de DATA/ADATA/ATTLTEX.SDA. A edição fica em [275,323,510,338]. A linha utiliza
15 linhas de atlas em vez de 13; a linha adicional superior era padding
transparente do bloco oficial, verificado antes de escrever. Nenhum pixel de
tinta ou contorno das três linhas oficiais é substituído. Os demais pixels,
paleta, cabeçalhos, amostra de fade realocada, doze UVs, ATTLSCN.LDT inteiro,
tempo das animações, posição e dimensões do bloco continuam como na v064.

CARREGAR, NOVO JOGO, VENDAS e todos os demais gráficos são preservados. Não
modifica ELF, vídeos, itens, diálogos ou configurações. Minério ignoto continua
como antes: o pedido Minério pequeno ainda está em espera por ordem do usuário.
Esta revisão não aumenta a contagem de textos traduzidos.

## Reprodução e teste

```powershell
python tools/credit_readability.py
python -m unittest discover -s tests -p test_credit_readability.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v045.json --interface-draft translations/interface-v065.json --compact-output --build-iso --output work/interface-v065
```

Preview comparativo em work/credit-v065/comparacao.png, sobre fundo semelhante
ao mapa. É uma composição local, não captura do PCSX2. O usuário deve conferir
Kernell Tozi, abertura dos e, separação das letras, cedilha/til e leitura em
tamanho normal; os créditos oficiais devem conservar posição e aparência.

## Verificação da entrega

Passaram 35 testes distintos: nove novos e 26 de regressão. A compilação
consolidada aceitou 6.044 registros MAP e 4.363 unidades de interface, sem
recusas. Permanecem 633 campos de nomes de itens e 610 valores distintos;
nenhuma tradução ou nome foi acrescentado nesta revisão.

Preflight verificou SHA-256 integral, tamanho, recibo e ausência de transação
ativa. A comparação integral v064→v065 confirmou **697 bytes em um único
patch**, restritos à faixa do crédito. Todas as demais partes da ISO,
inclusive as três linhas oficiais, cena, UVs, fade, ELF, fontes GFI, textos,
diretório e botões, ficam iguais à v064. Isso não é teste de execução ou
aprovação visual do novo desenho.

ISO: work/interface-v065/MetalSaga-ptbr-interface-v065.iso, 1.704.427.520 bytes.
SHA-256: `b7cb81733648703bd6ff3898cb7dfae5b35c97a751f05ae4032c2ba034f96275`.
Iniciar-Teste.cmd, atalho de pasta, preparador e auditor atualizados. Os dois
iniciadores foram conferidos em simulação e o auditor de capacidade executado.
Resultados em reports/interface-v065.json e interface-v065-delta.json.

Backup v059 teve hash integral e atributo somente leitura reconferidos.
A retenção manteve cinco ISOs de trabalho, removendo somente a antiga v060;
receitas/relatórios permanecem e a v064 continua disponível. Não houve PCSX2,
cópia para OneDrive ou desligamento nesta rodada.
