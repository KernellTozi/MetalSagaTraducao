# Buffers dos nomes de itens — investigação v002

Rodada de 29/10/2026, sobre a interface v051. Continuação da investigação dos
seis nomes aprovados que ficaram dentro da referência de largura na v001:
331, 372, 459, 838, 841 e 849. Os nomes foram usados somente em uma tabela
sintética na memória do teste. **Nenhuma tradução foi aplicada à ISO.**

## O que foi comprovado nesta rodada

A rotina de expansão em arquivo **0x1CD248..0x1CD4F0** tem quatro chamadas
diretas no ELF examinado. As instruções dos argumentos e dos frames demonstram
as seguintes separações locais:

| Chamada | Destino relativo ao stack pointer do chamador | Próxima área ativa | Espaço antes dela |
| --- | ---: | ---: | ---: |
| 0x473C8 | +0x80 | Contexto em +0x100 | 128 bytes |
| 0x549E8 | +0 | Contexto em +0x80 | 128 bytes |
| 0x1C6FE4 | +0 | Retorno salvo em +0x400 | 1.024 bytes |
| 0x1CCDB0 | +0 | Retorno salvo em +0x400 | 1.024 bytes |

Não se trata de recuperar uma declaração C de array. São limites conservadores
até dados ativos demonstrados nas instruções. A varredura não encontrou
literais alinhados com o endereço da rotina nas seções de dados examinadas;
isso não exclui chamadas indiretas calculadas ou todos os aliases possíveis.

O novo harness executa a função de expansão da entrada até o retorno para os casos %I
examinados, sem cobrir todos os comandos/caminhos, em vez de somente o
laço de cópia isolado da v001. O leitor original dos argumentos também é
executado pelo harness já existente em tools/control_b15.py. O conteúdo de
classificação de bytes, endereço da tabela e valores do contexto são modelados.
Não foram executados o chamador inteiro, alocador, desenhador, GPU ou PCSX2.

Foram executados **48 casos**: seis nomes, quatro separações de área e duas
formas de referência, literal e indireta por variável zero. As saídas
correspondem exatamente a “Recebeu [nome aprovado]!”, com todos os acentos,
NUL final, registradores preservados e sentinela intacta. Diferentemente do
recorte anterior de cópia, a função completa escreve o terminador.

## Por que isso ainda não autoriza aumentar o teto

O nome sozinho não determina a saída: é preciso incluir a frase, todas as
expansões e o NUL. Um caso artificial com sete referências ao item 331 tem
41 bytes de entrada, mas produziria 132 bytes de saída, mais o terminador.
A sonda detecta a tentativa de alcançar a área ativa seguinte no destino de
128 bytes. No de 1.024 bytes, a mesma expansão cabe e termina corretamente.

Esse caso **não foi observado no jogo** e não demonstra um defeito em uma
mensagem existente. Demonstra que a rotina não impõe sozinha uma garantia de
capacidade suficiente para qualquer entrada. É necessário provar os conjuntos
de textos e contextos que chegam aos chamadores reais, sobretudo aos dois
menores. Não liberar crescimento por ter passado uma frase curta no ensaio.

Também foi localizado outro caminho, distinto dessa expansão: o emissor em
**0x1B5B20**, com chamada direta em **0x1FD2BC**. O trecho anterior solicita
**0x320/800 bytes**, guarda o ponteiro no objeto e o encaminha ao emissor.
As células têm stride de oito bytes, e o emissor grava código final 5 após as
células de conteúdo. Para essa alocação observada, cabem até 99 células de
conteúdo antes de reservar a célula final.

Essa é evidência estática de alocação e gravação, **não execução do emissor**,
prova do ciclo de vida completo do objeto ou censo de todas as alternativas
de alocação. O limite de células não é o limite de bytes das strings. Esse
caminho precisa de investigação própria; não transferir a prova de 128/1.024
bytes para ele. As nove advertências de largura e o glifo Í da v001 continuam.

## Ferramenta local e testes

```powershell
python tools/item_name_buffers.py
python -m unittest discover -s tests -p test_item_name_buffers.py
```

Saída detalhada substituível: **work/buffers-nomes-atual.json**. A ferramenta
usa somente Python local e dados imutáveis do workspace, sem IA, rede ou APIs.
Não foi criado outro .cmd nem alterado o iniciador do jogo. O diagnóstico
anterior e Auditar-Traducao.cmd continuam funcionando como antes.

Os testes abrangem as saídas dos 48 casos, limite incluindo NUL, overflow
artificial, múltiplos itens, prefixo acentuado, índice/contexto inválido,
fonte divergente, preservação dos atributos da tabela sintética e manutenção
do bloqueio de crescimento no compilador histórico. Os 48 casos de instruções
não são somados ao número de testes unitários como se fossem casos distintos
de unittest.

## Próximo passo delimitado

1. Rastrear as entradas das duas chamadas de 128 bytes e do emissor de células,
   partindo dos offsets e vínculos já obtidos, sem repetir o censo bruto.
2. Determinar comprimentos expandidos/células máximos por conjunto efetivo de
   entradas, preservando referências dinâmicas e todas as ocorrências de itens.
3. Só depois preparar política opt-in para o subconjunto comprovado e os cinco
   rótulos de ação relacionados. Os casos que excedem a referência de largura
   ou o teto independente das ações continuam em fila separada.

A versão de teste permanece **v051**, com a mesma ISO, fontes e traduções.
Não houve abertura do PCSX2, nova ISO ou transferência OneDrive. O usuário
solicitou desligamento em 35 minutos e antecipação ao concluir; o temporizador
foi programado antes de começar a investigação. O trabalho deve estar salvo,
verificado e versionado antes de antecipar o desligamento.


**54 testes distintos passaram**, oito novos nesta rodada. A ISO v051 foi
reconferida por tamanho, SHA-256 e ausência de transações pendentes, mantendo
5c3489e7837ae4938e00f84a9a5599c11e48ebb259366b7377e1fe351f725c12.
Resumo próprio em reports/buffers-nomes-v002.json. Repetições de sondas e os
48 cenários internos não foram somados novamente à contagem de unittest.
