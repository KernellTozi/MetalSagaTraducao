# Interface v071 — uso de itens, montanhas e pergunta da ajuda

Pedido de 07/11/2026: corrigir as mensagens observadas durante uso de itens,
os nomes Junk Mountain/Monkey Mountain e Select a category na ajuda.
Entregar somente nova ISO; não gerar nem substituir o patch público.

Receita `translations/interface-v071.json`, pai v070 integral; MAP v048 e
layout v005 permanecem iguais. Ferramenta local `tools/item_use_release.py`,
manifesto `translations/uso-itens-v001.json`.

## Conteúdo aplicado

O banco conhecido contém 20 mensagens. Quatorze recebem nova tradução;
seis já estavam em português e são preservadas durante a reorganização.

| Uso/contexto | Nova mensagem, com exemplos de argumentos |
|---|---|
| Cura individual | Kernell recuperou / 1000HP |
| Cura em grupo | Todos recuperaram / 200HP |
| Ração e pelagem | Pelo de Bernie / brilha mais (+5) |
| Veneno | Kernell se curou / do veneno |
| Atordoamento | Kernell se livrou / do atordoamento |
| Falha de ressurreição | Kernell não / reviveu |
| Ressurreição | Kernell voltou / à vida |
| Recuperação de SP | Recuperou 200SP / em Demag |
| Remoção de efeito/objeto | Removeu [nome] / de [alvo] |
| Ácido | Ácido em Demag / neutralizado |
| Reparo de componente | Reparo: Bull / Veículo: Demag |
| Conversão impossível | [componente] não pode / virar / [resultado] |
| Conversão no veículo | [componente] em [veículo] / virou / [resultado] |
| Conversão de objeto | [objeto] virou / [resultado] |

As barras representam as quebras originais, não barras desenhadas na tela.
Nomes e números dos exemplos não são valores escritos no patch: continuam
sendo os argumentos resolvidos pelo jogo. Bull, Demag, personagens, nomes
de itens e HP/SP não são renomeados por essa edição.

Preservados: Ineficaz, Nada a converter..., Modo vigia: mais ataques
preventivos, Modo ameaça: afasta inimigos fracos, Modo evasão: menos encontros
e Ouviu um som. A mensagem genérica Usou %s! já estava traduzida e não muda.

Outros campos:
- Junk Mountain → Montanha de Sucata, três nomes de nós tipo 2/7.
- Monkey Mountain → Monte Macaco, dois nomes de nós tipo 2/7.
- Select a category → Qual categoria?, na pergunta do menu de ajuda.

Monte Macaco acompanha o título já traduzido **- Monte Macaco -**. O título
de entrada Montanha de Sucata também já existia; ambos foram conferidos na
receita e preservados. Não confundir os nomes das árvores do mapa, usados
nos avisos mostrados pelo usuário, com as mensagens supr de entrada.

São 20 unidades novas: 14 mensagens, cinco nomes de nós e uma pergunta.
As seis mensagens anteriores não são contadas novamente como tradução nova.

## Por que os textos faltavam

As mensagens são formatos multilinha do ELF em 0x31A600..0x31A830. O catálogo
legado de literais NUL isolados não inclui arbitrariamente strings com quebras
de linha. A pergunta da ajuda em 0x32D5E0 tem quatro FF imediatamente antes
do texto, e também não deve ser liberada por relaxamento global da busca.

O novo mecanismo é específico desse banco e desse consumidor da ajuda.
Não amplia a autorização para strings técnicas próximas, classes sItem,
mensagens de debug, controles desconhecidos ou outros formatos nativos.

## Reorganização do banco sem crescimento

O intervalo `[0x31A600,0x31A830)` tem 560 bytes. A versão final usa 530 bytes,
com todos os inícios alinhados a oito bytes. As strings mantêm NUL, printf,
tipos e ordem de argumentos, quantidade de quebras e os códigos PT-BR v005.

Os consumidores LUI/ADDIU são recenseados, vinculados ao ELF original por
hash e atualizados somente na parte baixa do endereço. Registradores,
opcodes e parte alta ficam iguais. Uma segunda busca cobre palavras absolutas
alinhadas do ELF; referências interiores conhecidas são recusadas.

O texto de atordoamento tem uma referência não capturada pelo catálogo curto:
LUI em 0x70E44, compartilhado por caminhos condicionais, e ADDIU em 0x70E70.
Os dois locais são conferidos explicitamente. Não presumir que uma string
sem referência no scanner está sem uso.

As mensagens sem printf incluem cópias de tamanho fixo. Cada uma recebe
reserva de pelo menos o tamanho original com NUL, mantendo alinhamento.
A tradução deve caber no comprimento lido pelo código; o padding restante
é zero. Ineficaz permanece assim porque Sem efeito seria maior que a cópia
original de dez bytes incluindo NUL. Não se alteram as instruções de cópia
ou as estruturas de uso dos itens.

O compilador coalesce apenas os seis patches históricos contidos nesse banco.
O comparador reconstrói o conteúdo antigo nesses mesmos 560 bytes antes da
verificação integral da imagem. ELF, blocos, ponteiros de contêineres,
fontes e diretórios ISO não crescem.

Os cinco nomes do mapa usam somente os 32 bytes existentes do campo, com
hash de nó e limites conferidos; flags, árvores, scripts e demais campos
permanecem intactos. A pergunta da ajuda preserva o prefixo FF e tem sua
chamada original em 0x12C3EC..0x12C3F8 vinculada.

## Reprodução local

```powershell
python tools/item_use_release.py
python -m unittest discover -s tests -p test_item_use_release.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v048.json --interface-draft translations/interface-v071.json --compact-output --build-iso --output work/interface-v071
```

O construtor exige uma pasta de saída nova. A preparação e a compilação
funcionam localmente, sem IA/APIs ou internet. Extração binária não usa IA.

## Roteiro de conferência em partida

Usar Iniciar-Teste.cmd na v071, sem restaurar save state de uma versão antiga.
Não é necessário alcançar uma fala distante: os casos observados pelo usuário
podem ser conferidos com o save atual.

1. Usar cura individual e de grupo: nomes, valores e HP corretos.
2. Dar ração: pelagem, nome do cão e bônus (+n), sem alterar os números verdes.
3. Usar kit de reparo: componente e veículo corretos, sem trocar argumentos.
4. Conferir cura de estados, SP, ressurreição e conversões quando disponíveis.
5. Abrir ajuda e conferir Qual categoria?.
6. Conferir os avisos de Montanha de Sucata e Monte Macaco.

Testes binários e execução limitada de instruções não equivalem à execução
visual no PCSX2. A cobertura é o banco identificado, não uma garantia de
localização de toda mensagem possível de qualquer item do jogo.

## Verificação da entrega

Os 23 testes automatizados passaram: 11 do novo mecanismo, sete de
verificação da ISO e cinco de retenção. A comparação integral v070→v071
confirmou 579 bytes diferentes nos 21 patches previstos, sem diferenças
fora dessas alterações. Diretórios da ISO, fontes e perfil de layout foram
preservados. O preflight da nova imagem também passou.

Imagem: `work/interface-v071/MetalSaga-ptbr-interface-v071.iso`,
1.704.427.520 bytes. SHA-256:
`3365db67d5feebd4795a1b5b706724c84d0982da30b5b6fd6993b6f3b52e11cf`.
Evidências: `reports/interface-v071.json` e
`reports/interface-v071-delta.json`. Os atalhos foram conferidos em modo de
simulação; o PCSX2 não foi executado nesta rodada. A aprovação visual fica
pendente do teste do usuário.

## Distribuição anterior

O patch público de referência e a cópia da Área de Trabalho continuam v070.
O backup de manutenção v070 também é preservado. Esta rodada entrega
somente a nova ISO de trabalho v071; não utilizar o patch v070 esperando
receber essas correções. O arquivo `.xdelta` v070 presente na pasta do pacote
foi conferido e mantém seu SHA-256 anterior. Na conferência desta rodada o
ZIP não estava mais no caminho registrado; a causa não foi investigada e
o ZIP não foi recriado.

Os 13 rótulos curtos de falantes e os efeitos preservados por contexto
continuam com as mesmas limitações v070.
