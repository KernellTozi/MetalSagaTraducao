# Lote consolidado v012 — resposta ASCII e nova rodada

## Exceção solicitada: nao

O usuário autorizou expressamente testar `nao` no registro `map.msg.1df8bec0`.
Foi removido somente o adiamento desse registro, e a tradução passou a ser
exatamente `nao`, sem ponto. O restante do prefixo v011 permanece idêntico.

| Propriedade | Valor |
| --- | --- |
| Offset do registro no MAP.MCT | `0x1DF8BEC0` |
| Offset do texto no MAP.MCT | `0x1DF8BEE0` |
| Tamanho do registro | 36 bytes |
| Capacidade do texto | 3 bytes |
| Antes, com terminador | `4E 6F 2E 00` |
| Depois, com terminador | `6E 61 6F 00` |
| Codificação do alvo | ASCII |

Um teste compara o cabeçalho completo, tamanho e terminador; outro ponto de
verificação leu o registro diretamente da ISO final. O relatório específico é
`reports/nao-slot-v012-validation.json`. O resultado comprova reinserção binária,
sem comprovar a exibição no PCSX2. `Não` continua exigindo quatro bytes no codec
atual; não cabe nesse slot.

No diálogo correspondente, Eddy tenta ajudar Nina na oficina após ser incentivado
a passar tempo com ela; a resposta curta à oferta de ajuda agora é `nao`.
A atribuição foi inferida pela sequência textual. Conferir no jogo quando esse
evento estiver disponível, observando a palavra isolada e o prosseguimento da
conversa. Não é necessário navegar autonomamente para alcançar a cena.

A exceção não autoriza retirar acentos de outras falas. O preparador não usa
esse registro como fonte de aliases, evitando espalhar automaticamente a forma
sem acento. O campo `resume_deferred` permite retomar adiamentos de modo explícito:
exige ID adiado no pai e alvo próprio no filho; duplicatas, conflitos e ausência
de alvo são recusados. Essa operação não libera estruturas binárias bloqueadas.

## Cobertura da rodada

| Lote | Registros | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v011 | 1.177 | 990 | 1.044 |
| v012 | 1.363 | 1.083 | 1.140 |

O intervalo conhecido `0x1DF47F0C..0x1FF30844` acrescenta 186 ocorrências: eram
as restantes após o limite da v011 no índice atual. Há 119 alvos únicos
preparados, 24 aliases por identidade de todos os segmentos originais e 43 novos
bloqueios. São 92 registros novos traduzidos, mais a resposta `nao` retomada do
prefixo anterior: aumento total de 93 traduções. Os 280 preservados incluem 67
adiados. Nomes e textos sem alteração não são contados como tradução nova.

Isso não representa a tradução completa do MAP.MCT ou do jogo: há outros
registros anteriores ao início deste recorte, além das limitações dos parsers.
O próximo avanço precisará organizar outro recorte, em vez de continuar somente
aumentando o offset final deste lote histórico.

## Contexto e termos

O novo trecho inclui exploração na sucata, sequência de batalhas contra
procurados, acampamento de comerciantes e laboratório de Dr. Palm. A regra de
combates sem descanso foi preservada. Nomes de procurados, apelidos e nomes de
armas permanecem no original; suas ocorrências não inflacionam a contagem.

Dr. Palm mantém entusiasmo exagerado e insistência em amizade/apelidos;
Thursday conserva o tratamento grosseiro aos humanos. A relutância de Rosa e
as falas de incentivo dos acompanhantes foram lidas em sequência. Falantes sem
rótulo continuam sujeitos à confirmação visual; não há identificação automática
comprovada de retratos.

Alguns títulos genéricos continuam em inglês por capacidade e consistência,
incluindo `Junk Mountain`, `Trader Camp` e `Impound Lot`. Não truncar palavras
para aparentar cobertura maior. O título do laboratório foi adaptado conservando
o nome Dr. Palm. Nomes de armas e apelidos nas opções permanecem inalterados.

A política agora protege os nomes dos procurados encontrados e distingue o
adjetivo `shiny` do nome `Shiny`. A tradução obrigatória de material `junk` não
se aplica dentro de um nome preservado como `Junk Zombies`, mas continua
obrigatória se houver referência separada ao material. Há testes para os dois
casos. Essa lista explícita não substitui revisão contextual de nomes ambíguos.

## Bloqueios e validação

Dos 43 novos adiamentos, 41 são controles opacos e dois têm terceira string
sem edição liberada. Permanecem intactos, junto dos 24 adiamentos anteriores
restantes após retomar a resposta curta. Não foram ampliados slots ou registros,
nem relaxados controles para aumentar a contagem.

103 testes passaram. Incluem prefixo anterior com uma única exceção autorizada,
bytes ASCII e NUL, retomada explícita de adiamentos, nomes, termos ambíguos e
exclusão da exceção ASCII no reaproveitamento automático. A construção verificou
hashes, leitura de retorno, limites SSD, diretórios e diferenças integrais da
ISO. A compilação final não teve recusas ou violações terminológicas.

Todos os registros modificados usam slots existentes, sem realocação. O relatório
conserva 155 avisos conservadores de largura no lote completo. Não são medições
de pixels nem aprovação visual. Não houve execução desta versão no PCSX2.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: compila e valida sem outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a v012.
- ISO: `work/regiao-inicial-v012/MetalSaga-ptbr-regiao-inicial-v012.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v012/`.
- Metadados publicáveis: `reports/regiao-inicial-v012-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v012 --build-iso
python -m unittest discover -s tests
```

SHA-256: `8b994c171760090cb48f2364fd5eab2107fe5c3c2a2e00b31911b2ee37b113a6`.

A retenção removeu a ISO antiga v005 para manter dez imagens de trabalho.
Receita e relatórios estão preservados; `--iso region-v005` exige reconstrução.
A v011 continua disponível. ISO original, BIOS, saves e configurações não foram
alterados.
