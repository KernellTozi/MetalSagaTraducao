# Interface v009 — tela inicial

Acrescenta o conjunto completo de três rótulos da textura da tela inicial,
preservando os 573 campos de texto e as 40 ocorrências gráficas da v008. Total:
**616 campos/ocorrências compilados**, sendo 43 gráficos. Não é uma porcentagem
de cobertura do jogo. MAP v030, layout de acentos v005 e alinhamento Satcom v008
permanecem intactos. A alpha não muda.

| Rótulo original | PT-BR | Largura raster |
|---|---|---:|
| New Game | Novo jogo | 176 px |
| Continue | Retomar | 148 px |
| Install | Instalar | 155 px |

São desenhados em maiúsculas para manter a apresentação original. Retomar mantém
o sentido do comando de continuar a partida salva. Instalar apenas traduz o
rótulo existente; não ativa, desativa nem altera o recurso de instalação.

## Fonte e limites

`tools/title_native_font.py` recupera treze letras dos três rótulos originais,
com seus tons, inclinação e desgaste. V reutiliza a metade direita do W; J usa
a haste e o gancho do U; R combina a haste do E, a parte superior do O e a base
diagonal do N. Essas três são reconstruções explícitas, não glifos completos
encontrados no original. Não se usa fonte de diálogo nem fonte do Satcom.

Todas as células têm 24 pixels de altura, sem resize ou compressão horizontal.
A composição mantém um pixel de sobreposição nas margens dos recortes para
aproximar os traços sem reduzir suas dimensões. Não é kerning geral do motor.
Largura máxima de 176 px dentro dos retângulos de 180×24, com centralização
horizontal. Não aumentar os recortes nem alterar hotspots para caber.

O preview foi inspecionado localmente; a execução no PCSX2 e a aparência final
continuam pendentes. Conferir as reconstruções V/J/R, o centramento, o contorno
e a seleção dos botões numa inicialização limpa, quando conveniente. Os demais
textos gráficos da nomeação e senha continuam no próximo lote.

## Evidências do consumidor

Política opt-in `title-native-raster-v006` em `tools/title_graphics.py`, receita
`translations/interface-graphics-v006.json`. Herda obrigatoriamente a receita
gráfica v005 por hash e acrescenta somente um patch de pixels RTITLE.

- Referência ao caminho RTITLE: LUI de a1 em `0x38524` e ADDIU em `0x38548`,
  no delay slot da chamada `0x177338`, apontando para VA `0x414C38`.
- Descritor original em arquivo ELF `0x2641C8`: textura offset `0x20`, tamanho
  `0x10410`; GANM offset `0x10430`, tamanho `0x70`.
- Laço `0x38644..0x38698`: soma a base carregada aos offsets, associa a textura
  ao objeto e fornece GANM ao leitor. A tabela `0x2641E0` associa os seis objetos
  aos frames **5,0,1,2,4,3**. Os frames 0/1/2 estão em y=296/330/364, x=320.
- Leitor `0x19AF90..0x19AFA4`: base GANM + campo `+8` fornece tabela de frames.
  Neste header estático os campos são tag, u16 frames=6, u16 animações=0,
  offset dos frames=16 e offset das animações=112. **O 16 em +8 é offset**, não
  uma prova de stride apenas por seu valor. O parser histórico não foi ampliado.
- Rotina `0x37E10..0x37E70`: desloca o índice quatro bits (stride de frame 16),
  lê coordenadas como extremos, subtrai os hotspots e calcula largura/altura
  pela diferença entre extremos. Confirma os recortes e sua origem, sem editar
  as instruções ou as tabelas.

As seis janelas originais de código/dados e o ELF inteiro são vinculados por
hash. Houve inspeção das instruções e verificação automatizada das dependências,
não execução completa de CPU/emulador. Não inferir tipos de GANM de outros arquivos
ou liberar animações por semelhança.

## Preservação e reprodução

Somente pixels em x=0..179, y=0..71 da textura RTITLE podem mudar. Paleta RGB e
alpha, header, SDA, GANM, hotspots, ponteiros, seleção e demais pixels são
imutáveis. A receita vincula os três rótulos, ordem, dimensões e hashes dos
rasters. Divergências são recusadas antes da criação da ISO.

```powershell
python tools/title_graphics.py --output work/titulo-revisao-nova
python tools/interface_graphics.py --recipe translations/interface-graphics-v006.json --output work/graficos-revisao-nova
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v009.json --output work/interface-v009 --build-iso
```

Os diretórios de saída devem ser novos. `Preparar-Interface.cmd` valida a v009;
`Iniciar-Teste.cmd` e `Testar-Interface.cmd` abrem sua ISO consolidada:
`work/interface-v009/MetalSaga-ptbr-interface-v009.iso`. A v008 permanece como
alias histórico `interface-v008`, sujeita à retenção normal.

Não houve cópia para OneDrive. Os dez arquivos ISO sob work/ e a alpha permanente
fora da retenção continuam protegidos pelas regras anteriores. Evidências, hash
da construção e comparação integral ficam nos relatórios v009.

## Verificações executadas

- **50 testes de interface aprovados**, incluindo os cinco novos do título,
  regressão dos perfis gráficos históricos, linha de base do Satcom, transporte
  dos 69 atlas, diário, textos ELF e preservação das receitas anteriores.
- Preview próprio do título e exportação multi-recurso executados. A ferramenta
  de previews agora separa os patches por recurso, sem aplicar offsets RTITLE
  sobre FBS_DATA. As compilações antigas continuam reproduzíveis.
- ISO de 1.704.427.520 bytes, SHA-256
  `95ce7f53b708fa7ab6e08e938d256df967f16f17b413be74f6483a3a91b1ae2f`.
  Compilação: 5.892 registros MAP alterados, 1.339 preservados, zero recusas;
  interface com 616 campos/ocorrências.
- Comparação integral v008→v009: **8.282 bytes diferentes em um único patch**,
  todos nos pixels RTITLE. Diretório ISO, restante dos recursos, código,
  diálogos, fontes e alinhamento Satcom idênticos à v008.
- Mantidas dez ISOs sob work/; a retenção removeu a antiga imagem de trabalho
  MAP v028, preservando sua receita e relatórios. A alpha não participa da remoção.
- Não houve execução do PCSX2 nem cópia para OneDrive. A validação visual da
  nova família gráfica permanece pendente, separada dos testes binários.
