# Atlas de interface — preparação de cinco conjuntos

Rodada de infraestrutura após a correção de alinhamento Satcom v008. O pedido
atual é continuar a interface em escopo amplo. Foram catalogadas **69 texturas**
de cinco arquivos e implementado transporte reversível em PNG indexado. Não há
novos textos traduzidos nem nova ISO nesta rodada: a v008 continua no iniciador.

## Resultados comprovados

| Recurso | Texturas | GANM | Outros registros |
|---|---:|---:|---:|
| DATA/RDATA/RTITLE.SDA | 1 | 1 | 0 |
| DATA/FDATA/FNAME_DT.SDA | 5 | 2 | 2 |
| DATA/FDATA/F_COMMON.SDA | 9 | 1 | 0 |
| DATA/FDATA/FD_POST.SDA | 47 | 2 | 0 |
| DATA/FDATA/PASSWORD.SDA | 7 | 7 | 0 |

Todos os oito painéis de contato foram inspecionados localmente. Esses previews
mostram RGB da paleta original; não simulam composição/alpha nem execução no PS2.

- **Título:** os três rótulos rasterizados ocupam os primeiros 72 pixels da
  textura RTITLE. Seus desenhos são próprios, pesados e inclinados, distintos
  de Remote e dos GFI de diálogo. Preservar essa identidade na futura composição.
- **Nomeação:** FNAME_DT inclui retrato, molduras e botões de seleção de alfabeto,
  incluindo variantes japonesas. Isso não comprova que todas sejam usadas na
  versão americana. O texto de solicitação do nome existe também no catálogo
  ELF; não é correto assumir que todo o conteúdo da tela está na textura.
- **F_COMMON:** ícones do controle, fundos e molduras. START/SELECT aparecem
  em ícones; não são automaticamente rótulos a traduzir.
- **FD_POST:** cartaz, nomes rasterizados e retratos de procurados. Os nomes
  permanecem protegidos pela regra do usuário. Nenhuma mensagem de correio foi
  identificada nos previews dos 47 registros de textura. Isso não comprova a
  localização do corpo do correio em outro arquivo nem exclui outras estruturas.
- **PASSWORD:** painéis, teclado e comandos rasterizados de bloqueio/saída.
  A geometria e a família visual devem ser tratadas separadamente do Satcom.

Os dois registros FNAME_DT não reconhecidos ficam em `0x86C40` (6.080 bytes) e
`0x88400` (192 bytes). Não foram promovidos a textura ou fonte por semelhança.

## Geometria do título

RTITLE tem somente uma textura reconhecida, em `0x20`, 256×256, 8 bpp, e GANM
em `0x10430`, seis entradas de 16 bytes. Os três primeiros retângulos são:

| Índice | Retângulo x0,y0,x1,y1 | Hotspot |
|---|---|---|
| 0 | 0,0,180,24 | 90,12 |
| 1 | 0,24,180,48 | 90,12 |
| 2 | 0,48,180,72 | 90,12 |

Correspondem geometricamente às três linhas de texto visíveis no atlas. Ainda
é necessário vincular os consumidores e a seleção de textura antes de liberar
patches dessas entradas na ISO. A ferramenta registra **candidatos geométricos**
por limites; nunca associa um GANM a uma textura só por serem vizinhos no SDA.
Hotspots e campos reservados são exportados como metadados, sem alteração.

## Ferramentas e reprodução local

Dar dois cliques em **Preparar-Atlas.cmd**. A saída recebe uma pasta nova com
data/hora em `work/atlas-interface-.../`:

- `previews/`: catálogo JSON, PNGs RGB e oito painéis para inspeção.
- `editaveis/`: 69 PNGs indexados com paleta e alpha originais, mais manifesto.

Não editar os previews RGB. Manter modo P, dimensões, paleta e transparência nos
editáveis. Não converter para RGB/RGBA nem quantizar. As cores transparentes
podem parecer estranhas em editores comuns porque o alpha PS2 é preservado cru.

Exemplo com diretórios novos, na raiz do projeto:

```powershell
python tools/prepare_interface_atlases.py --output work/atlas-minha-revisao
python tools/interface_atlas_pack.py import --pack work/atlas-minha-revisao/editaveis --output work/atlas-minha-revisao/reconstruidos
```

O segundo comando produz cinco cópias SDA verificadas e `roundtrip.json`.
Não altera ISO, originais ou iniciadores. Importação valida todo o pacote antes
de criar saída, rejeitando manifesto alterado, PNG ausente, links de arquivos,
modo/dimensões/paleta/alpha diferentes ou índices fora da profundidade original.
Saída existente e caminhos fora de work/ são recusados.

O transporte anterior de seis texturas continua com sua política e testes
históricos; este módulo separado cobre os cinco novos conjuntos. Não expande
as permissões do compilador gráfico ou de ISO existente.

## Validação e próximos passos

Foi executado round-trip real de todas as 69 texturas: cinco recursos reconstruídos
idênticos aos originais, byte por byte. Testes de alterações pontuais em 4/8 bpp
confirmam que somente o byte do pixel muda; paletas, headers, GANM, caudas e
demais registros ficam intactos. Testes negativos verificam a recusa antes de
produzir cópias parciais. A suíte histórica de seis texturas também foi mantida.

Próximo lote gráfico: título, seguido de comandos de senha e nomeação. Para
cada família, provar consumidor/UV, recuperar os desenhos próprios, compor o
conjunto com linha de base consistente e vincular a receita por hashes. Não
usar automaticamente a fonte de diálogos ou a do Satcom nesses rótulos.
Localização das mensagens do correio continua pendente. Itens e fragmentos MAP
continuam depois da interface. Não foi executado PCSX2 nem houve cópia OneDrive.

Evidências reproduzíveis em `reports/atlas-interface-v001.json`; arquivos do jogo,
previews e cópias reconstruídas somente em work/. Alpha e retenção permanecem
inalteradas, pois nenhuma ISO adicional foi construída.
