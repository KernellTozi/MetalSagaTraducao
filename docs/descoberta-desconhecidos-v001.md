# Descoberta das 365 entradas desconhecidas

Investigação consolidada em 26/10/2026 sobre o conjunto congelado em
`reports/triagem-grafica-v001.json`. Nenhuma tradução, fonte, receita ou ISO
foi modificada. A versão jogável continua interface v038/MAP v037.

## Resultado e contagens

| Estrutura identificada | Entradas do conjunto original | O que foi comprovado |
| --- | ---: | --- |
| Contêiner sem assinatura, 41 partes | 140 | Tabela de offsets e limites; 5.740 partes internas ainda opacas |
| Contêiner DAI | 45 | Cabeçalho, tamanho, tabela alinhada e imagens internas |
| Contêiner DPI | 10 | Cabeçalho, tamanho, tabela alinhada e imagens internas |
| Carimbos de pintura sem cabeçalho | 48 | Paleta de 16 cores e 2.048 bytes de pixels de 4 bits, 64×64 |
| Blocos CAME | 20 | Contagem e registros de 20 bytes com preenchimento limitado; sem semântica completa |
| GANM com sequências | 15 | Cabeçalho dividido, sprites e 88 sequências, preservando variantes e caudas |
| Imagens RGB diretas | 2 | 512×64, 24 bits e preenchimento zerado; logotipos de empresa |
| Lista de caracteres da entrada de nomes | 1 | 2.965 pares, 46 linhas CRLF e cauda de 58 bytes A5 |
| Nota técnica da entrada de nomes | 1 | Prefixo de 163 bytes e cauda opaca de 29 bytes |
| Recursos já conhecidos: créditos e legendas de pintura | 2 | Correspondem aos formatos investigados anteriormente; não são descobertas novas |
| Sem parser suficiente | **81** | Permanecem separados e não editáveis |
| **Total** | **365** | Sem duplicar entradas |

Há **284 entradas com estrutura identificada**, mas isso não significa 284
recursos totalmente compreendidos. Em particular, os 140 contêineres continuam
com **5.740 conteúdos internos opacos**. Essa pendência não foi escondida pela
classificação dos seus cabeçalhos. Modelos, animações ou câmeras são hipóteses
de uso para algumas famílias numéricas; não foi implementado um decodificador
dessas semânticas para chamá-las de comprovadas.

## Imagens efetivamente recuperadas e revisadas

Os contêineres DAI/DPI contêm 103 imagens indexadas e 19 imagens RGBA diretas.
Com os 48 carimbos e os dois logotipos, foram recuperadas **172 imagens**,
revisadas nas 15 folhas em `work/descoberta-desconhecidos-v001/folhas/`.

- 117 imagens sem palavra localizável observada: superfícies de cenários,
  personagens, veículos e efeitos, entre outras.
- 48 carimbos com símbolos, alfabeto e números, a preservar.
- Dois logotipos de empresa protegidos.
- Três imagens com letras usadas como símbolos de mecânica, preservadas para revisão de uso.
- Dois candidatos gráficos: uma placa no cenário do minijogo de dança e uma
  marcação de chegada no minijogo de corrida de sapos. Exigem contexto/UV/uso
  antes de decidir tradução ou edição.

Os dois candidatos ficam em `RMGDANCE.SDA` 0x43D20 e `RMGKAERU.SDA` 0x15F2E0.
Não há 172 novas caixas de texto. As 172 imagens também não foram incorporadas
silenciosamente ao importador histórico dos 119 atlas. O transporte existente
e suas receitas continuam reproduzíveis.

## Estruturas e evidências

Todos os offsets abaixo são de arquivo. As fontes foram vinculadas aos hashes
do inventário e aos hashes de cada uma das 365 entradas históricas.

**F_PCDKF.SDA:** cada uma das 140 entradas começa com u32=41, seguido por
41 offsets u32 relativos. Primeiro offset=168, offsets distintos/ordenados e
alinhados a quatro, último dentro do registro. Prefixo e 41 intervalos remontam
o registro original integralmente. Os conteúdos internos têm estruturas
numéricas diversas, mantidas opacas no catálogo local. Identificar o contêiner
não autoriza alterar as partes nem associá-las a personagens por suposição.

**DAI/DPI:** assinatura de quatro bytes, tamanho u32, contagem u32 e tabela de
offsets a partir de +12. Conteúdos começam após a tabela alinhada a 16 bytes;
intervalos não se sobrepõem. Os parsers validam o tamanho declarado e preservam
padding e cauda. Cada imagem indexada passa pelo transporte/reversão de índices
já conhecido. Imagens diretas usam cabeçalho de 16 bytes, bpp=24/32, paleta=0 e
offset de pixels=16. Tamanho e cauda são conferidos; os previews não comprovam
o upload/endereçamento real da GPU.

**GANM:** os bytes +4 e +6 são lidos separadamente como u16, em vez de um único
u32 de contagem. +8 mantém stride=16 e +12 aponta para as sequências, depois da
tabela de sprites. Cada sequência tem cabeçalho de oito bytes e entradas de
12 bytes; seu tamanho declarado confere com `8 + quantidade*12`. O índice de
sprite fica no segundo u16 de cada entrada. O primeiro u16, duração e demais
campos são preservados; sua semântica não foi liberada para edição.

As duas entradas RMGKAERU em 0x91260 e 0x11A940 têm valores não sequenciais no
primeiro u16 de algumas entradas. Foram tratadas como variante explícita,
vinculada a esses offsets e às fontes, sem renumerar ou corrigir o original.
O consumidor inspecionado seleciona o sprite pelo segundo u16. A cauda de
S_PAINT em 0xCBE0 contém oito bytes não zerados: eles também são preservados.
Remontagem por campos das sequências confere byte a byte com a origem.

Foram executados trechos originais do ELF em RAM sintética: cabeçalho GANM
0x19AF98–0x19AFA8 para as 15 entradas e seleção de sprites
0x19B254–0x19B264 para **335 entradas de quadros**. Isso não executa o carregador
completo das sequências, alocador, desenho ou PCSX2.

**Carimbos:** estão no SDA interno em S_PAINT 0x959D0, com 48 intervalos de
2.112 bytes. Cada um tem 64 bytes de paleta e 2.048 bytes de pixels compactados.
O consumidor inspecionado em 0x670C8–0x670E8 configura dimensões 64×64; a rotina
seguinte separa os nibbles baixo e alto. O trecho 0x67118–0x67130 foi executado
para todos os 256 valores possíveis de byte, confirmando essa ordem. A paleta
e os pixels podem ser separados e remontados exatamente. Não foi executada a
conversão completa com CLUT, GPU ou o caminho de seleção do carimbo no jogo.

**CAME:** assinatura, contagem u32 e `contagem*20` bytes após o cabeçalho de oito
bytes. Restante observado: menos de 16 bytes zerados. Registros e cauda remontam
o original; o significado dos campos e o consumidor continuam pendentes.

**Entrada de nomes:** FNAME_DT em 0x86C40 tem lista de 2.965 pares em 46 linhas;
seu corpo faz round-trip CP932, seguido por 58 bytes A5. Isso vale para a lista,
não muda a codificação do jogo ou o codec PT-BR. Em 0x88400 há nota técnica
relacionada à lista, mas seus últimos 29 bytes não pertencem ao prefixo textual
validado. Não os converter em caracteres por tolerância do decoder. Não são
novos diálogos de história.

## O que permanece desconhecido

As 81 entradas restantes foram agrupadas sem lhes atribuir formatos por aparência:

| Família de investigação | Quantidade |
| --- | ---: |
| Cabeçalho numérico com terceiro u32 igual à representação float de 0,01 | 36 |
| Cabeçalho numérico com terceiro u32 igual à representação float de 1,0 | 9 |
| Outros cabeçalhos numéricos | 31 |
| Assinatura SAF | 5 |

Além delas, permanecem as 5.740 partes dos contêineres F_PCDKF. Os 5.821
intervalos somam 46.473.104 bytes. O filtro ASCII de frases já usado no projeto
foi executado nesses intervalos e encontrou **zero candidatos**. Isso não exclui
texto comprimido, nativo, tokenizado ou com outro enquadramento. O resultado
serve para priorizar a próxima investigação, não para declarar ausência de texto.

O próximo passo técnico nesses grupos é rastrear seus consumidores e tabelas
numéricas, começando pelos 36 cabeçalhos semelhantes. Para o objetivo de
tradução, priorizar em paralelo os candidatos gráficos reais e recursos já
localizados; não transformar a engenharia de modelos/animações inteira em
pré-requisito sem evidência de conteúdo textual.

## Ferramenta local, testes e integridade

```powershell
python tools/discover_unknown_entries.py --output work/descoberta-desconhecidos-atual.json
```

O JSON local pode ser atualizado no mesmo caminho se pertencer a esta ferramenta.
Um JSON alheio é recusado. Para gerar previews e um resumo público novo:

```powershell
python tools/discover_unknown_entries.py --output work/minha-investigacao/catalogo.json --previews work/minha-investigacao/folhas --summary reports/minha-investigacao.json
```

Previews e resumo público exigem caminhos novos. O JSON público guarda somente
metadados; o catálogo local guarda os intervalos das partes e sequências.
Os wrappers `discovery` conservam o motivo histórico da classificação anterior.
Não alterar o parser/importador antigo para promover estes formatos automaticamente.

**48 testes distintos aprovados**, incluindo 14 novos: limites e corrupção de
offsets, todos os DAI/DPI, GANM e variantes, cauda não zerada, probes originais,
carimbos, imagens diretas, CAME, lista/nota, substituição local protegida e filtro
de frases. As regressões da descoberta, preflight, retenção e alpha passaram.

Foram verificados dez arquivos de referência e as 85 receitas permaneceram
iguais antes/depois. A ISO v038 foi conferida integralmente antes/depois:
1.704.427.520 bytes, SHA-256
`0b4c931e141de804200d4e42c4fe125f9013707308b1e829871f5159102727c0`.
Nenhuma tradução/ISO criada, nenhuma execução PCSX2 ou transferência OneDrive.

```powershell
python -m unittest discover -s tests -p test_unknown_entry_discovery.py
```
