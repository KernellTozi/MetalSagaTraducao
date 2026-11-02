# Interface v063 — revisão das capturas e Renascimento

Base: interface v062, MAP v044, fontes/layout `ptbr-layout-v005`. O filho
MAP v045 revisa uma única fala. A pausa após v062 foi encerrada pelo pedido
do usuário de continuar e aplicar os textos enviados. Não houve PCSX2 nesta
rodada; a conferência das novas telas fica com o usuário.

## Nomes e contexto

| Origem | Aplicação | Campo |
|---|---|---|
| Scrap Armor | Colete quebrado | item 190 |
| Revitalizer / Revigorante | Renascimento | item 336 e referência no pool de reações |
| Unknown Ore | Minério ignoto | item 665 |
| Medium Ore | Minério médio | item 666 |
| Large Ore | Minério grande | item 667 |
| No enemies in the vicinity | Sem inimigos por perto. | ELF 0x3179B0 |
| Equip | Equipar | ELF 0x349540 |
| Who will learn? | Quem aprenderá? | formato ELF 0x342DD0 |
| EQUIPMENT LIST | EQUIPAMENTOS | atlas S_PACK+0x8C830 |
| First Strike | Primeiro golpe | duas variantes no atlas de batalha 1586 |

Renascimento foi escolhido explicitamente pelo usuário. Os nomes de itens
continuam dentro do teto comprovado de 16 bytes codificados: 15/12/15/15/15.
Os campos físicos têm 24 bytes dentro dos registros de 128 bytes; atributos,
índices e demais bytes ficam intactos. “Ignoto” significa desconhecido e evita
abreviar “Minério desconhecido”, que ultrapassa o limite. Isso não amplia o
teto global nem libera outros itens bloqueados. Não há ação homônima no
catálogo de ações que exija uma segunda tradução destes cinco nomes.

O pool de reações passa a listar “1. Evil Toy Sword  2. Renascimento|3. ?  4. ?”.
O nome próprio, delimitadores, todas as outras strings, referências, 179 chaves
e cauda opaca são preservados. O leitor usa as referências lógicas da tabela
original para localizar a string já realocada no pai; não aplica offsets antigos
sobre o pool compilado. O rebuild sem alterações precisa reproduzir o pai.

## Montagem e trocadilho

`Qual componente de %s?` em ELF 0x341CA8 passa a `Escolha a peça %s.`. O
argumento era um ordinal inglês, não um nome de peça. Quatro células de oito
bytes em 0x349EA0/EA8/EB0/EB8 passam de first/second/third/last a 1/2/3/4;
os quatro ponteiros em 0x2FCB38 ficam intactos. O usuário verá “Escolha a peça
1.” etc. Preservam-se o argumento `%s`, os endereços e os NULs das células.
O censo de referências é conservador, não uma execução de todos os chamadores.

O título lógico 318 do pool UI passa de Montar itens a Combinar peças. O
serviço também combina outros objetos: não foi renomeado globalmente para
Montar mapas. Os 378 ponteiros e grupos de aliases são reanalisados; todas
as demais strings precisam ser iguais. Usa-se somente o extent já comprovado.

O registro `map.msg.0be1a0e0`, 88 bytes, recebe:

```text
...Dis...assembler...
te... desmonta...!<TAB>Mwahahahaha!
```

São 53 bytes em capacidade de 55. A origem dizia “...Dis...assemble...
into... pieces...!”, jogando com o verbo e o nome Disassembler. A adaptação
preserva nome entrecortado, ameaça e risada, sem afirmar que o original dizia
literalmente o nome completo. Foram consultadas as falas vizinhas sobre o
mecânico, a chegada e a ameaça de desmontar tudo. Cabeçalho de 32 bytes,
controles, LF/TAB, tamanho e demais registros MAP permanecem preservados.
O filho v045 não aumenta a contagem histórica de diálogos traduzidos. A
medição conservadora do compilador sinaliza a primeira linha como mais larga
que a origem; conferir a quebra e a margem em partida, além do sentido da fala.

## Nomes de locais

| Origem | Alvo | Offsets MAP.MCT |
|---|---|---|
| Iwasaki Medical Laboratory | Laboratório Médico Iwasaki | 0x9FDC, 0xA800 |
| Mysterious Transport Pod | Estranha cápsula de transporte | 0x1AF037DC, 0x1AF04000 |
| Grand Master's Tent | Tenda do Grand Master | 0x1CCE7FDC, 0x1CCE8800 |
| Lake Bridge East Gate | Portão leste da Ponte do Lago | 0x1C6427DC |

Sete ocorrências nos campos existentes de até 32 bytes, dentro de nós tipo 2
ou 7. Os alvos têm respectivamente 28/31/21/30 bytes, mais NUL. Conferem-se
300 mapas, 839 campos de nomes tipo 2/3, nós, hashes dos registros e zeros
somente no intervalo ocupado. Não mover nós, scripts, offsets ou registros.
Iwasaki e Grand Master permanecem; o pedido específico autoriza traduzir os
descritores destes locais. Não executar substituições globais em falas.

## Formatos e gráficos

O aviso de Busca cabe no próprio literal. Equipar utiliza os oito bytes da
célula 0x349540, com cauda original zerada e nenhuma referência interior
detectada. O formato de aprendizado tem 32 bytes; a primeira linha
`%-20s    %8dG` e o LF permanecem iguais, com o texto completo ocupando 30
bytes mais NUL. Parâmetros, dinheiro e habilidades não são alterados.

EQUIPAMENTOS ocupa 159 pixels por dez de altura, gap 3, na célula
[4,180,176,192] do atlas original 256×256/8 bpp. Letras nativas, incluindo
Q/P da própria linha original, sem redimensionar glifos. Os cinco títulos
anteriores, paleta, cabeçalhos e UVs permanecem iguais.

Primeiro golpe altera somente os dois limites de tinta encontrados nas
células [27,200,125,220] e [127,200,225,220] da entrada 1586 de MMBATTLE.BIN.
O seletor original em ELF 0x1090E0 contém 0x24020632. A entrada descompacta
em um TIM2 linear de 66.624 bytes. A palavra completa usa Impact inclinada,
com contorno e quatro tons da paleta existente, como o mecanismo de efeitos
anterior. Não redesenha números, MISS ou LEVEL UP. Recompactação cabe no
slot original; diretório, cabeçalho/paleta, outros pixels e padding ficam
vinculados. O laço original do descompactador foi executado em memória
simulada, conferindo bytes e consumo. Isso não é teste no PCSX2.

A ocorrência First Strike dentro da ajuda Scout Mode já estava traduzida;
ela não é a origem deste rótulo gráfico e não foi alterada novamente.

## Reprodução

```powershell
python tools/capture_release.py
python tools/capture_release.py --previews
python -m unittest discover -s tests -p test_capture_release.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v045.json --interface-draft translations/interface-v063.json --compact-output --build-iso --output work/interface-v063
```

Receita vinculada: translations/capturas-v001.json. O compilador recompõe o
pai imutável, exige exatamente 18 adições físicas e seis revisões UI, sem
sobreposição. São 20 unidades novas: sete literais ELF, três itens, sete
nomes de mapa, EQUIPAMENTOS e duas variantes de Primeiro golpe. As duas
variantes compartilham um patch novo, e EQUIPAMENTOS revisa um atlas já
traduzido; revisões dos nomes, pools e fala não aumentam essa contagem.
Comparador integral normaliza somente a união
de 24 bytes do item 336; não descarta diferenças fora desse intervalo.

Previews reproduzíveis em work/interface-v063-previews/equipamentos.png e
primeiro-golpe.png. Conferir no jogo os nomes, a aprendizagem, montagem,
Busca, ameaça de Disassembler e as duas variantes do ataque preventivo.
As categorias abreviadas e os 13 falantes explícitos curtos são pendências
distintas; não são resolvidos por este lote. Backup v059 preservado.

## Verificação da entrega

Passaram 76 testes distintos: 16 novos e 60 de regressão. A construção
consolidada aceitou 6.044 registros MAP e 4.362 unidades de interface, sem
recusas; são 633 campos de nomes de itens e 610 valores distintos. Continuam
5.991 corpos/opções e 991 referências explícitas de falantes, além dos 108
nomes padrão herdados. Não converter essas contagens em porcentagem do jogo.

Preflight aprovou tamanho, SHA-256 integral, recibo e ausência de transação
pendente. Comparação integral v062→v063: **14.375 bytes em 25 patches**,
sem diferenças extras; diretório, fontes e layout idênticos. Auditorias de
diálogos e capacidade foram executadas sobre a v063. As 16 revisões históricas
de nomes já resolvidas nas v052–v054 continuam com zero bloqueadas.

ISO: `work/interface-v063/MetalSaga-ptbr-interface-v063.iso`, 1.704.427.520 bytes.
SHA-256: `977181c148d6c49c4e166301d6d113da0b3f54e538ba5815e20f42855b08488d`.
Iniciar-Teste.cmd e Abrir-Pasta-da-Ultima-Versao.cmd conferidos em simulação;
preparador e auditor atualizados. Resumo reports/interface-v063.json e delta
reports/interface-v063-delta.json. Nenhuma execução no PCSX2 foi declarada.

Retenção manteve cinco ISOs de trabalho, removendo somente a antiga cópia
de trabalho work/interface-v059/MetalSaga-ptbr-interface-v059.iso. O backup
independente em dist/backup-v059/ e a base isolada de investigação permanecem.
Hash integral do backup e atributo somente leitura foram reconferidos.
Não houve cópia para OneDrive nem desligamento.
