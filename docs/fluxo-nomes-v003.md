# Nomes de itens: entradas e emissor de caracteres v003

Continuação de 29/10/2026, sobre interface v051/MAP v044. Os seis nomes
aprovados 331, 372, 459, 838, 841 e 849 continuam somente na tabela sintética
do teste. Nenhum nome foi aplicado, teto ampliado ou arquivo do jogo alterado.

## Resultado e plano

O próximo passo escolhido foi conferir as entradas reais e o emissor de células,
em vez de repetir o teste de uma frase curta. O resultado reduz uma dúvida de
proveniência e acrescenta execução de instruções originais do emissor:

- A chamada pequena 0x549E8 vem de 0x1FAD80. O encaminhador 0x1FACE0 recebe
  duas chamadas diretas, 0x1FA0E4 e 0x1FA750, com literais fixos sem `%I`.
  Correspondem a uma interjeição e cinco pontos de dois bytes. Não são duas
  mensagens que cresceriam quando o nome de um item muda.
- A outra chamada pequena, 0x473C8, ainda recebe resultados de métodos
  virtuais. O literal de mapa-múndi é apenas um ramo; não prova todos os demais.
- O emissor 0x1B5B20 foi executado até retornar, incluindo despacho pela tabela
  original, leitor original dos argumentos de `%I`, emissão de letras ASCII,
  letras PT-BR de dois bytes, espaços, quebras de linha e célula final.
- A cadeia do emissor foi estendida: objeto+0x38 em 0x1FD2C0, construtor
  0x1FCEC0, encaminhador 0x1FE978 e oito chamadas vindas dos handlers da VM.
  As quatro origens observadas carregam o ponteiro textual de objeto+0x1C.
  Isso liga o caminho às mensagens, sem provar todas as entradas possíveis.

As chamadas do encaminhador são 0x1C6334, 0x1C6368, 0x1C64C0, 0x1C64F8,
0x1C6A00, 0x1C6A3C, 0x1C6CE0 e 0x1C6D1C. Instruções e janelas são vinculadas
ao SHA-256 do ELF original. A receita atual também é vinculada por hash.
Um override futuro dos dois literais invalida a conclusão sobre suas entradas.
Não foram excluídos aliases ou chamadas indiretas calculadas.

## Limite de células, diferente do limite de bytes

A alocação observada tem 800 bytes, com células de oito bytes. O código final
5 ocupa uma célula: cabem **99 células de conteúdo**, para essa alocação.
Os testes agora executam esse caminho, em vez de somente inferir seu tamanho.

Foram conferidos os limites de 99/100 letras ASCII, 99/100 letras acentuadas e
99/100 quebras de linha. Um `é` ocupa dois bytes na entrada, mas uma célula.
Uma quebra também consome célula. Uma mensagem expandida com nome de item
passa com 99 células e é recusada pelo harness com 100. O argumento a3=30 não
limitou esses casos a 30 células. O próprio emissor não recebeu uma correção
de overflow: a detecção é da ferramenta de investigação.

O teste negativo de nome expandido revelou que a primeira escrita excedente
pode ser o payload da célula em +4, antes do cabeçalho. O diagnóstico trata
ambas como estouro da alocação observada, sem realizar a escrita.

## Catálogo compilado atual

A ferramenta recompila em memória os **7.231 registros**, pelos mecanismos
existentes, e examina o texto final de cada segmento. Foram identificados
**34 campos e 35 páginas com referências I**. A separação por TAB considera
somente páginas pertinentes; não trunca um texto para fazê-lo passar.

| Resultado | Páginas | Cenários |
|---|---:|---:|
| Executadas com os seis contextos amostrados | 25 | 150 |
| Pendentes por outros controles dinâmicos | 10 | 60 |

O maior resultado dos cenários executados foi **76 células**, incluindo
conteúdo e quebras, antes da célula final. Nenhum deles alcançou o limite.
Cada cenário atribui o mesmo item testado aos seletores indiretos da mensagem.
Isso **não recupera o item canônico da cena**, não testa todas as combinações
de valores diferentes e não autoriza crescimento universal de nomes.

Os seletores I examinados são 0, 1, 2, 9, 10, 15 e 19, já presentes nas
políticas anteriores. A ferramenta não libera controles no compilador.
Os dez casos pendentes misturam comandos fora do subconjunto desta sonda;
não foram reduzidos por remoção de tokens nem classificados como overflow.
Seus IDs, páginas, hashes e motivos ficam no relatório, sem texto original
no Git. Os textos completos permanecem somente nas saídas locais em work/.

As dez páginas pendentes são de map.msg.0a138544, map.msg.0a1387a4,
map.msg.0b8fc504, map.msg.0b8fc764, map.msg.0b8fe774, map.msg.0be0f99c,
map.msg.0e76dabc, map.msg.0e76dd0c, map.msg.1df5f13c e map.msg.1df6435c.
Em todas, o bloqueio desta sonda foi a presença de outros comandos.

Há ainda 12 cenários sintéticos exatos com os seis nomes, por referência literal
e variável zero, e 42 combinações de nome/seletor nos testes. São cenários
internos; não devem ser somados à contagem de testes unitários.

## Reproduzir localmente

```powershell
python tools/item_name_stream.py --audit-map
python -m unittest discover -s tests -p test_item_name_stream.py
```

Saída substituível: `work/fluxo-nomes-atual.json`. Sem `--audit-map`, executa
somente proveniência e os 12 cenários sintéticos, sem recompilar o MAP.
Só usa biblioteca padrão do Python e módulos próprios. A desmontagem inicial
usou Capstone instalado dentro de work/python-deps; ele não é dependência
da ferramenta entregue. Sem rede, IA ou APIs durante sua execução.

## Limites e próxima decisão técnica

O harness modela classificação de bytes, registro de glifos, tabela de nomes e
valores do contexto. Não executa alocador, inicialização dessas tabelas, GPU,
PCSX2, chamadores completos ou todos os comandos do emissor. As sondas usam
o ELF original vinculado; não constituem validação visual do ELF modificado.

Próxima frente delimitada: acrescentar ao diagnóstico os controles mistos dos
dez casos, reaproveitando os leitores/handlers já investigados, e identificar
os retornos virtuais que alimentam 0x473C8. Não repetir o censo bruto de 54/190
candidatos nem tratar o contador 150 como prova de todos os estados do jogo.
Depois da prova restante, preparar política opt-in para os seis nomes e os
cinco rótulos de ação relacionados. Os nove nomes mais largos e o glifo Í
permanecem frentes separadas; escolhas humanas não serão abreviadas.

A versão jogável continua v051. Sem nova ISO, fontes, OneDrive ou emulador.
O usuário revogou o desligamento: `shutdown /a` retornou 1116, indicando que
nenhum desligamento estava pendente; nenhum outro foi agendado nesta rodada.

## Verificações concluídas

**69 testes unitários distintos passaram**, 15 novos deste módulo; zero falhas,
erros ou testes ignorados na execução final. A regressão abrange também
buffers, capacidade, teto de nomes, revisão humana, batalha e consistência.
Repetições durante o desenvolvimento não aumentam essa contagem.

A ISO v051 foi reconferida por hash integral, tamanho e ausência de transações:
SHA-256 `5c3489e7837ae4938e00f84a9a5599c11e48ebb259366b7377e1fe351f725c12`,
1.704.427.520 bytes. Os dois literais da cadeia pequena também foram lidos
diretamente da ISO e coincidem com os originais, incluindo os terminadores.
Resumo próprio em reports/fluxo-nomes-v003.json; detalhes locais em work/.
