# Continuação da descoberta: animações, modelos e som

Investigação de 26/10/2026, reproduzível em `tools/discover_binary_remainder.py`.
Complementa a v001 sem alterar seu relatório ou promover parsers históricos.
O relatório público contém offsets/hashes; o catálogo detalhado fica em work/.

## O que foi recuperado

Foram investigadas 221 entradas: os 140 contêineres de F_PCDKF e as 81 raízes
que a v001 deixava sem parser suficiente. Sem duplicar as ocorrências:

| Resultado | Raízes | Limite |
| --- | ---: | --- |
| Contêineres de animação | 158 | Metadados e descompressão; valores dos quadros ainda não interpretados |
| Recursos vinculados a consumidores de modelos | 55 | Tabelas/offsets/tamanhos comprovados; geometria interna opaca |
| Bancos de som SAF | 5 | Empacotamento e seções HD; amostras BD não decodificadas |
| Recursos especiais com vínculo parcial | 3 | Sem formato interno ou finalidade exata suficientemente comprovados |

Dos 158 contêineres, 140 são os anteriores; os outros 18 estavam nas 81
pendências. Eles contêm **5.876 ocorrências de partes**, correspondentes a
**571 conteúdos binários distintos**. Descompactaram-se 11.653.536 bytes
distintos; maior saída: 139.424 bytes. F_PCDKF sozinho contém 5.740 ocorrências,
436 conteúdos distintos e 8.855.080 bytes descompactados distintos.

O filtro ASCII de frases aplicado às 571 saídas não encontrou candidatos.
Isso não exclui texto nativo/codificação personalizada. A conclusão de uso
para animação depende também dos consumidores originais, não apenas do filtro.
Não há 5.876 diálogos novos. Nenhum desses recursos foi liberado para edição.

## Envelope de animação comprovado

Offsets são de arquivo, números little-endian:

- Contêiner: u32 quantidade, seguido por offsets u32 relativos. Primeiro
  offset = `4 + 4*quantidade`; intervalos ordenados, distintos e limitados.
- Parte: primeiro u32 preservado opaco; quantidade de tracks **u16 em +4**;
  u16 de +6 opaco; ponteiro relativo u32 para fluxo comprimido em +8.
- Metadados começam em +12. Cada track tem oito bytes básicos. Os bytes +6
  e +7 desse cabeçalho contam duas listas de blocos adicionais. Cada bloco
  tem oito bytes básicos mais `8*u16(bloco+0)`. O fim da caminhada precisa
  coincidir exatamente com o ponteiro do fluxo comprimido.
- Fluxo: tamanho descompactado u32 e a mesma variante LZSS de dicionário
  zerado de 1.024 bytes já identificada nos créditos. Replay dos tokens e
  recomposição do envelope conferem com todos os bytes da origem.

Não confundir os contadores u16 com um u32: a metade superior tem valores
opacos em alguns recursos. Não interpretar o primeiro u32 como duração
canônica sem comprovação adicional de unidade e uso.

O consumidor percorre a estrutura em 0x18BAA4–0x18BB8C e lê a referência do
fluxo em 0x18BC08–0x18BC54. O carregador F_PCDKF em 0x13C9B4–0x13CA04 encaminha
o recurso à rotina 0x190FC8 e ao associador 0x18BA18. Em 0x1906E4, o caminho
de animação chama o wrapper 0x19B738, que usa o decoder 0x19B780. Janelas
originais estão vinculadas ao hash do ELF no relatório.

Foram executados três casos distintos do **laço original de descompressão**
em RAM sintética: envelope simples (1.184 bytes), metadados variáveis
(17.784 bytes) e cauda não zerada (4.736 bytes). Saída e consumo conferem
com Python. Metadados/consumidores foram inspecionados; não foi executado o
carregador completo, animação esquelética, alocador, GPU ou PCSX2.

### Caudas não são espaço livre

65 conteúdos distintos de F_PCDKF têm mais de três bytes zerados depois do
fluxo, somente na última parte. Cinco partes finais de F_SPEND têm caudas
**não zeradas**, de quatro a 14 bytes. O parser preserva tamanho, hash e
bytes opacos; a exceção só vale para a última parte de F_SPEND e menos de
16 bytes. Nas outras partes, exige até três zeros. Nenhuma cauda foi apagada.

## Modelos: vínculos sem inventar um decodificador de geometria

Os registradores de modelos em 0x14D2F8 e 0x14D3A0 usam tabelas de strides
24 e 36. As tabelas verificadas são:

| Recurso | Tabela no ELF | Entradas |
| --- | --- | ---: |
| RMGDOG | 0x2656D0 | 1 |
| RMGKAERU | 0x265E88 | 1 |
| RMGTANK, tabela estática | 0x267A98 | 10 |
| RMGTANK, tabela animada | 0x267B88 | 9 |
| RMGDANCE | 0x267F50 | 11 |
| RMGALAN | 0x2684B8 | 18 |
| F_SPEND | 0x32E7D8 | 5 |

Offset/tamanho do modelo e da textura são os dois primeiros pares u32. Nas
tabelas animadas e em F_SPEND, o terceiro par referencia a animação. F_SPEND
tem carregamento próprio em 0x137174–0x137210, seguido pelo inicializador
comum 0x18A998. Não inferir nomes de personagens dos índices desses arrays.

Os modelos F_SPEND em 0x246A0 e 0x37920 têm respectivamente oito e 12 bytes
não zerados após o tamanho registrado. Esses sufixos também permanecem opacos
e intactos; não são padding que a ferramenta possa limpar.

## SAF: bancos de som

Cinco entradas têm quatro chunks: `SAF `, `HD  `, `BD  `, `END `. Cada chunk
tem tag de quatro bytes, tamanho de payload u32 e dois u32 observados zerados,
seguidos pelo payload alinhado a 16 bytes. O END é vazio e termina a entrada.
O tamanho do primeiro payload varia (32, 144, 256 ou 304 bytes); não impor
o tamanho de uma única amostra às outras.

HD contém seis subchunks contíguos `IECS` + tipo + tamanho: `sreV`, `daeH`,
`igaV`, `lpmS`, `tesS`, `gorP`. Eles precisam cobrir HD exatamente. O leitor
de chunks foi inspecionado em 0x203E08–0x203FBC. Mensagens diagnósticas originais
incluem bancos/HD/BD e alocação de memória SPU; sustentam a classificação de
som. Não houve decodificação de áudio nem execução desse leitor inteiro.
As cinco ocorrências correspondem a quatro conteúdos distintos.

## O que permanece aberto e por que não bloqueia o lote seguro

Três raízes permanecem com finalidade interna insuficientemente identificada:

- RMGALAN 0x381810 e 0x387630: tamanhos 0x5E20 e 0x6BE0; encaminhados pelos
  chamadores 0x171C9C e 0x171CDC ao inicializador 0x135678.
- RMGTANK 0x1661B0: tamanho 0xCA70; par original offset/tamanho em 0x349AC0,
  com referências do consumidor. Não chamar de textura, colisão ou som sem
  prova adicional.

Geometria, valores dos quadros, áudio e algumas semânticas CAME/GANM também
continuam incompletos. Não declarar que todo o jogo foi descoberto. Não há
evidência nova de texto nesses três recursos que justifique bloquear os
conjuntos localizáveis já preparados. A triagem gráfica continua com seus
alvos conhecidos, incluindo os dois candidatos de cenário da v001.

Nesta investigação foram conferidas sete fontes, 85 receitas e a ISO v038
antes/depois, sem alterações. A tradução posterior dos créditos e a ISO v039
são uma etapa separada, documentada em `docs/interface-v039.md`.

Reprodução local, sem IA/API/internet:

```powershell
python tools/discover_binary_remainder.py --output work/descoberta-desconhecidos-v002/catalogo.json
python -m unittest discover -s tests -p test_binary_remainder_discovery.py
```

Resumo público original em `reports/descoberta-desconhecidos-v002.json`.
Usar caminho novo em reports/ para `--summary`; o histórico não é sobrescrito.
