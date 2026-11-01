# Pendências atuais — v061, com auditoria histórica v054

## Entrega v061 — autorização de aplicação recebida

O usuário relatou que a ISO não apresentou defeitos até o momento e autorizou
aplicar as lacunas enviadas. A espera por aplicação descrita nos registros
históricos abaixo foi revogada por essa ordem.

A v061 trata os avisos do tanque, Nome/Nível/Tempo/Salvo, Vazio, Equipamento,
Comparar, CIDADES/MEMBROS/FROTA e a instrução/comandos da máquina de venda.
Detalhes e roteiro em docs/interface-v061.md. Aparência final aguarda partida.
Não houve execução do emulador pelo Codex.

Ainda pendentes: expansão das categorias Máq./Veíc./Descon., revisão de Bio/Cyber
e os 13 rótulos explícitos curtos. Um candidato de compactação de nove strings
em 72 bytes foi identificado para a expansão, mas ainda requer provar todos
os leitores e atualizar referências. BONUS e títulos dispensados permanecem.
Backup v059 e v060 preservados; iniciador e atalho de pasta acompanham v061.

Os próximos registros descrevem as capturas recebidas antes desta aplicação;
não devem ser lidos como impedimento para as traduções já aplicadas na v061.

## Aviso de tanque imobilizado — registrado, não aplicar ainda

Relatado pelo usuário em 01/11/2026: ao tentar utilizar o tanque sem motor e
sem C Unit, o aviso ainda aparece em inglês. A captura mostra o veículo
Buggy e as linhas `immobile:`, `Overloaded`, `No engine installed` e
`No C Unit installed`. Manter Buggy como nome do veículo.

A captura comprova o texto exibido; a origem binária e os limites de edição
ainda não foram investigados. A presença de Overloaded na mesma tela não
comprova se a sobrecarga é independente da ausência de motor. Conferir esse
contexto ao tratar o conjunto de avisos de impedimento de uso do tanque.

**Aguardar nova ordem antes de aplicar correção**, conforme pedido explícito.
Este registro não altera receitas, fontes, ISO ou iniciadores; a versão
jogável continua v060. Evidência: captura fornecida pelo usuário,
`codex-clipboard-ac867316-fcf0-4d79-ad0b-b6f8a1757710.png`.

## Equipamento e categorias abreviadas — pesquisa, sem aplicação

Novas capturas mostram Status/Equip, MEMBER LIST, VEHICLE LIST e Compare parts
em inglês; no menu Caça, Máq., Veíc. e Descon. precisam de nomes completos.
O usuário pediu pesquisar ampliação de limites, sem modificar o jogo enquanto
testa v060. Investigação e plano em docs/menus-equipamento-limites-v001.md.
Foram localizados literais e referências candidatos no ELF: os três rótulos
têm capacidade atual de sete bytes; propostas exigem 9/9/13 bytes no codec.
Realocação com referências atualizadas é uma possibilidade, ainda sem espaço
carregado/buffers/layout comprovados para esses destinos. Cabeçalhos MEMBER
LIST/VEHICLE LIST não foram encontrados como ASCII exato no ELF; não presumir
origem gráfica. Nenhuma receita, ISO, fonte ou iniciador foi alterado.

## Teletransporte, salvamento e máquina de venda — somente registro

Capturas recebidas em 01/11/2026; aguardar nova ordem para implementar:

- Teletransporte: cabeçalho `TOWN LIST` ainda em inglês. Preservar nomes de
  cidades como Junkyard, Newfolk e East Zero, conforme a política do projeto.
- Detalhes do save: rótulos `Name`, `Level`, `Time` e `Saved` ainda em inglês.
  Traduzir futuramente apenas a interface, preservando nome do jogador,
  localização, valores e dados do cartão.
- Seleção de espaço para salvar: `NO DATA` aparece tanto nas linhas vazias
  quanto no painel de detalhes. Conferir os dois contextos. `Onde salvar?`
  e `Cartão: slot 1` já aparecem traduzidos na captura.
- Máquina de venda: instrução `Light the center and win a prize!` e comando
  `Exit` ainda em inglês; `Grana` já está traduzido. A imagem também contém
  `BONUS`, a inventariar nesse contexto, sem autorização para recriar títulos
  de minigames que o usuário anteriormente dispensou.

Complemento da máquina de venda: outra captura mostra a faixa de comandos
`Select:` (direcional), `Buy:` (X) e `Exit:` (círculo) sem tradução. Registrar
Select e Buy junto ao Exit já listado, sem duplicar essa última pendência.
Preservar ícones e associação entre ações e botões quando houver implementação.
Evidência: codex-clipboard-5c673b3d-aa1a-47cc-8b0d-c187be0fcf9d.png.
Somente registro; origem do recurso ainda não investigada e ISO inalterada.

Evidências, na mesma ordem: capturas codex-clipboard-6dbdd462-6011-4c27-ac33-f923905c673c.png,
codex-clipboard-a48f04ec-806f-4204-993d-d56f6414471f.png,
codex-clipboard-fb1c3096-2f52-4b82-8193-c41507f392ec.png e
codex-clipboard-e8fe9d54-6203-4fec-a804-dd81efd340f0.png.
Origem binária e limites desses campos ainda não foram investigados nesta
recepção. Nenhuma alteração de jogo ou nova ISO.

## Validação pontual recebida — Menino

O usuário confirmou: “o nome menino funcionou perfeitamente”. Registrar como
validação visual relatada pelo usuário do rótulo Boy→Menino entregue na v060.
Não há identificação de qual das duas entradas foi observada; isso não valida
automaticamente os outros 107 campos, os 13 rótulos explícitos pendentes ou
o alinhamento Sim/Não. O Codex não repetiu a navegação no PCSX2.

## Estado consolidado

A v059 é agora a cópia de segurança em dist/backup-v059/; as ISOs antigas
v055–v058 e a antiga alpha foram removidas por nova ordem do usuário, após
verificação integral. A imagem jogável do iniciador agora é a v060. O novo
protótipo dos 13 falantes está em docs/falantes-lookup-v001.md: resolve os
nomes completos em RAM simulada, mas ainda exige reserva comprovada de
armazenamento no ELF/heap. O protótipo dos 13 falantes não foi aplicado à ISO.

A v060 acrescenta 108 campos de nomes padrão (55 traduções), incluindo duas
entradas Boy → Menino no banco de modelos do MAP.MCT. São nomes usados quando
não existe rótulo explícito no diálogo; não resolvem os 13 rótulos curtos abaixo.
Outros 301 campos, incluindo 19 nativos, ficam intactos. A correção de Sim/Não
substitui somente a medição de largura da classe de opções pela medição nativa
dos glifos, sem modificar fontes. Conferir visualmente o carregamento de dados,
outras escolhas e listas. Manual docs/interface-v060.md; 56 testes passaram e
a comparação integral confirmou 929 bytes diferentes em 109 patches previstos.
Nenhum novo teste visual no PCSX2 foi realizado nesta rodada.

A v059 traduz 34 rótulos gráficos de efeitos/atributos nos atlas comprimidos
1587/1588. Só a área das letras originais é alterada; setas, paletas e termos
protegidos conservam os pixels. A aparência e o contexto de exibição aguardam
a partida do usuário. Comparações em work/batalha-atributos-v001/ e manual
docs/interface-v059.md. Permanecem quatro rótulos por contexto: Dummy, UP,
DOWN e Damage Override. O pequeno Underground foi confirmado por ampliação
e traduzido como Subsolo; não existe uma pendência Overpower nesse atlas.

A v058 aplica o lote humano de armas: 86 nomes, 91 referências de ação,
89 MANTER preservados, zero fallback/conflitos. As 15 munições especiais
ficaram intactas. Conferir visualmente equipamentos, lojas e batalha na próxima
partida. Detalhes em docs/interface-v058.md. A habilidade 946 é um alias fora
da autorização e permanece intacta; não traduzi-la automaticamente.

A v057 muda somente os avisos de saída e o fallback ELF para **Mundo aberto**,
conforme pedido do usuário. Demais traduções e pendências da v056 preservadas.

A v056 resolve as capturas de Lojas/meta financeira/aviso de saída: Qual loja?,
Atual, Meta e 113 prefixos Mapa do mundo; revê o desenho de Tempo de jogo.
Ver docs/interface-v056.md. Novos rótulos de navegação não aumentam a contagem
de diálogos. Confirmar apresentação e transição de saída no teste do usuário.

A v055 corrige 14 rótulos de batalha em dois atlas comprimidos que não eram
os de FBS_DATA. O log e a conferência da ISO confirmaram que o usuário usou
corretamente o iniciador v054; não era um save state. Ver docs/interface-v055.md.
Testes visuais da correção ficam pendentes do usuário.

Revisão histórica de 175 registros de armas e anexo de 15 munições em
work/revisao-armas-v001/ARMAS-PARA-REVISAR.md. As decisões humanas recebidas
foram aplicadas na v058; os 89 MANTER são preservações, não pendências.
Os atlas comprimidos 1587/1588 receberam o lote v059 descrito acima; os quatro
casos sem contexto não foram promovidos por suposição. A triagem anterior de
20 candidatos gráficos não representava cobertura completa desses recursos.

Auditoria reproduzida na interface v054, sem modificar a ISO.
Relatórios: reports/auditoria-dialogos-v054.json e
reports/pendencias-consolidadas-v054.json.

## Desenvolvimento ainda pendente

**13 rótulos genéricos sem espaço seguro**, em cinco grupos:

| Rótulo atual | Tradução completa prevista | Ocorrências |
|---|---|---:|
| Worker | Trabalhador | 9 |
| Man | Homem | 1 |
| Transporter | Transportador | 1 |
| Cat | Gato | 1 |
| Dog | Cão | 1 |

IDs para consulta:

```text
Worker: map.msgn.057d67dc, map.msgn.0db14094, map.msgn.0db140dc,
        map.msgn.0db147f8, map.msgn.0db14898, map.msgn.0db148e0,
        map.msgn.0e777edc, map.msgn.0e778354, map.msgn.14aad804
Man: map.msgn.0be1acd8
Transporter: map.msgn.0be25188
Cat: map.msgn.0be2d3a4
Dog: map.msgn.19f55614
```

O espaço compilado desses rótulos é, respectivamente, 7/3/11/3/3 bytes;
os alvos precisam de 10/5/13/4/4. As soluções atuais de slot, cauda e
revisão contextual não liberam esses casos. Não encurtar Trabalhador, remover
acentos, apagar falas ou tomar bytes externos. Uma solução futura precisa
de outra hipótese de armazenamento/lookup e de prova própria; não repetir
indefinidamente as buscas de padding já encerradas. Esses rótulos continuam
em inglês, sem impedir a versão jogável.

Essa nova hipótese já tem uma sonda funcional de 170 bytes e propostas
restritas aos 13 registros. O bloqueio atual é a reserva em memória:
classificar 12 referências ao fim da imagem 0x4B599C antes de testar um
segundo segmento. Os zeros do cabeçalho ELF não são uma code cave carregada,
e a limpeza de BSS escreve até 0x4B59A0. Não aplicar os marcadores sem o hook.

**Revisão contextual do inglês remanescente:** 523 referências de falantes
fora desses 13 incluem personagens, nomes, marcadores, Hunter/Soldier/Punk e
termos que ainda exigem contexto. Não são 523 traduções obrigatórias.
Os 124 registros de triagem editorial, 455 candidatos de nomes/expressões e
589 de pontuação/controles também não são contagens de frases faltantes.

**Cobertura fora do catálogo:** o scanner dirigido não encontrou novos
candidatos ASCII em registros SSD fora dos parsers conhecidos. Isso não
exclui texto curto, nativo, comprimido ou fora desse banco. Três raízes
especiais continuam sem semântica textual comprovada; reabrir somente com
indício novo ou tela observada no jogo. Não anunciar 100% de cobertura.

## Conferência visual e encerramento

Falta uma passagem contínua pela versão consolidada: menus de personagens,
inventário/equipamento, lojas e preços, ações de batalha, escolhas, Satcom,
mensagens e diário. Não exigir que o usuário alcance cada cena imediatamente.
Registrar versão, cena, texto e imagem quando aparecer um problema. Os nomes
de até 19 bytes da v054 têm conferência visual pendente, apesar dos testes
binários e de métricas já concluídos.

O pacote local foi preparado e reconstruído com hash idêntico à v054; ver
docs/patch-local-v001.md. Isso adianta a infraestrutura de entrega, mas a
publicação de uma versão final depende da revisão de jogo e das limitações
documentadas. Não houve publicação do pacote nesta rodada.

## O que está encerrado ou deve ser preservado

- As 16 revisões humanas de nomes bloqueadas foram tratadas nas v052–v054.
- Zero grupos nativos e zero outros controles pendentes no catálogo conhecido.
- Os 19 adiamentos técnicos restantes são nomes de tanques N$3 preservados.
- Os 20 candidatos gráficos têm disposição documentada: nove cobertos e
  onze preservados por decisão do usuário. Não reabrir pôsteres Wanted,
  títulos decorativos de minigames/cassino ou o painel japonês dos cães.
- Continuam 6.044 registros MAP alterados, 5.991 com corpo/opções modificados,
  991 referências de falantes traduzidas e 627 nomes de itens aplicados.
  Essas métricas não permitem calcular uma porcentagem confiável do jogo.
