# Pendências atuais — v068, com auditoria histórica v054

## Minigames consolidados na v068 — conferência em partida pendente

O usuário revogou a dispensa de títulos, resultados e painéis japoneses dos
minigames. A v068 localiza os recursos conhecidos, com 200 rótulos, 17 novos
painéis, três inscrições e 27 textos internos, preservando seis painéis já
em português. Catálogo de 107 recursos revisados em
`reports/minigames-cobertura-v001.json`; procedimentos e roteiro em
`docs/interface-v068.md`. Não equivale a cobertura de todas as chamadas no
PCSX2. Conferir resultados animados, cartas, comandos, rótulos pequenos e
estados de seleção. Nomes de músicas e sapos permanecem próprios.


## Relatos após v066 aplicados na v067 — visual pendente

O pedido posterior de iniciar a tradução encerrou a pausa de recepção.
A v067 aplica os relatos abaixo. Procedimento, offsets, limites e roteiro
em docs/interface-v067.md. Conferir em partida Sem tanques, Meu braço!,
Vila dos Aposentados, Túnel 1 - Ferrovia Continental, Encouraçado Tiamat,
TEMPO/Dançar/Sair/Ajuda, a confirmação de pintura e as duas falas de MC Hamir.
O texto sobre o coração recebe aviso conservador de largura. As descrições
dos relatos a seguir preservam o contexto observado antes da correção.

- **Tank Stop:** aviso ainda em inglês ao lado do ícone de proibição de
  tanques. Priorizar uma redação curta. “Sem tanques” é a proposta inicial,
  a conferir no contexto e no espaço do aviso. Preservar o ícone.
  Evidência: codex-clipboard-2e31f51e-1105-4bf4-9f7b-7b56733509aa.png.
- **Diário — My Arm!:** título e corpo ainda em inglês. A entrada menciona
  que Dr. Mortem não consegue ajudar e que talvez o professor Grey consiga.
  Revisar ambos os campos e preservar os nomes dos personagens.
  Evidência: codex-clipboard-ee17f75f-677b-4df6-84e6-13516c5aa947.png.
- **Retirement Compound:** nome de local ainda em inglês. Conferir o
  contexto antes de definir a redação.
  Evidência: codex-clipboard-507c3c09-5823-410c-97e7-6675cd825549.png.
- **First Continental RR Tunnel:** nome de local ainda em inglês. Conferir
  o nome da ferrovia e a terminologia já usada para o local.
  Evidência: codex-clipboard-e73f477c-9d9c-414e-884d-8a64bb92a566.png.
- **Nome de local — Land Battleship Tiamat:** rótulo de entrada ainda em
  inglês, conforme nova captura do usuário. Investigar e traduzir futuramente
  o descritor genérico, preservando Tiamat como nome próprio. Redação final,
  origem binária e limite de espaço ainda não verificados. Somente registro,
  sem autorização para retomar o desenvolvimento nesta recepção. Evidência:
  codex-clipboard-d7b2f393-a1a6-4588-ad3a-53041fcb8b05.png.
- **Minigame de dança:** TIME na barra e legenda Dance / Exit / Help ainda
  em inglês. Traduzir futuramente preservando os ícones e suas associações
  aos comandos. Evidência: codex-clipboard-29c39654-72c9-4562-87d5-7eda08be87ae.png.
  Esse rótulo funcional de tempo é uma solicitação específica; não confundir
  com a dispensa anterior de recriar títulos decorativos de minigames.
- **MC Hamir — revisão contextual e de tom:** o usuário considera as falas
  sem sentido/formais e pede adaptação para português brasileiro natural,
  menos formal. Capturas: “O que eu fazer? Isto não é bom... Para onde foi!?”
  e “P-Por que falar comigo tão de súbito!? Faz mal ao coração!”. Rever o
  original e as falas vizinhas antes de escolher a redação, preservando nome,
  personalidade, hesitação e contexto, sem inventar intenção ou caricatura.
  Evidências: codex-clipboard-5d080ba2-f97a-4ef6-aa8f-f8b577156a7a.png e
  codex-clipboard-8f81ac09-b2a1-4249-a667-e727ab61adb0.png.
- **Pintura — confirmação ao carregar amostra:** ainda aparece
  “Load the selected sample paint? (Previous paint will be lost)”. Registrar
  a pergunta e o aviso como uma pendência conjunta; preservar futuramente
  as opções Sim/Não, seus controles e o sentido de substituir a pintura
  anterior. Evidência: codex-clipboard-63816b6e-ba25-484e-8bf1-63ae96e9db6b.png.

As novas traduções aguardam conferência visual do usuário. Minério pequeno
continua aguardando liberação específica.

## Tanque, locais e bebida aplicados na v066 — visual pendente

PARTS LIST→PEÇAS; VEHICLE NAME→NOME; SELECTED ITEMS→SELECIONADOS. Prédio
abandonado/Prédios abandonados e Ruínas submersas aplicados em sete nomes
de nós, com dois títulos de entrada existentes padronizados no MAP v046.

Minigame: Tempo, Bebidas, BEBER e PERIGO no atlas; legenda Beber/Sair/Ajuda
com os mesmos ícones; tutorial completo em português, preservando os ícones
das bebidas, do botão e o rodapé. Títulos decorativos e arte das embalagens
mantidos conforme a regra anterior. Confirmar seletores/recortes, cor dos
rótulos, cedilha de PEÇAS e acentos dos locais em partida.

Procedimentos e limites em docs/interface-v066.md; comparações locais em
work/interface-v066-investigacao/. O crédito v065 permanece igual e ainda
não recebeu aprovação visual do usuário. Minério pequeno continua em espera.

## Crédito refeito na v065 — aguardando novo teste visual

A captura codex-clipboard-9c9c2023-4e3f-458c-ad8d-64f81e21b255.png confirma
a linha junto ao bloco oficial, mas o usuário reprovou a leitura de Kernell
Tozi, especialmente os e. Não considerar a tipografia v064 aprovada.

A v065 usa rasterização direta no tamanho final, corpo 12 e posições inteiras
por letra. Abertura e espaço interno de e ficam protegidos por testes. Somente
a faixa da assinatura é revista; as três linhas oficiais, a geometria do bloco,
CARREGAR e VENDAS permanecem v064. Preview: work/credit-v065/comparacao.png;
procedimento em docs/interface-v065.md. Conferir novamente em tamanho normal
no PCSX2; a nova proposta ainda não tem aprovação visual do usuário.

## Título e vendas aplicados na v064 — teste visual pendente

SALES LIST→VENDAS; RETOMAR→CARREGAR com palavra completa criada no estilo
aprovado. O crédito antigo foi removido do sprite do botão e a quarta linha
“tradução: Kernell Tozi” foi acrescentada ao recurso ADATA do bloco oficial,
com texto branco/contorno preto, sem herdar a cor do botão. As três linhas
oficiais conservam os pixels; os UVs e limites do próprio bloco foram ajustados.
Conferir a entrada, o fade, as opções e o crédito em partida: o leitor LDT/GPU
não foi executado. Ver docs/interface-v064.md e as comparações locais.

**Pedido em espera:** Minério ignoto→Minério pequeno foi solicitado, mas o
usuário pediu não aplicar ainda. O item 665 e os demais itens permanecem v063.
Não interpretar a retomada das correções de menus como liberação dessa troca.

A base isolada work/falantes-lookup-v001/MetalSaga-ptbr-falantes-base-v059.iso
foi removida pela retenção das cinco ISOs de trabalho ao construir a v064.
Receita/relatórios da investigação permanecem; o backup independente v059 em
dist/backup-v059/ continua íntegro e somente leitura. Recriar uma base a partir
dele, em nova cópia controlada e com hash conferido, se a investigação precisar.

## Capturas aplicadas na v063 — validação visual pendente

O pedido posterior de continuar encerrou a pausa descrita abaixo. A v063
aplica Colete quebrado, Renascimento (nome escolhido pelo usuário), três
minerais, o aviso de Busca, Combinar peças/Escolha a peça 1..4, o trocadilho de
Disassembler, Equipar, EQUIPAMENTOS, Quem aprenderá?, quatro nomes de locais
em sete campos e duas variantes de Primeiro golpe. Ver docs/interface-v063.md.
Os relatos abaixo continuam como histórico, não como bloqueio de execução.

Próxima conferência em partida: esses elementos e o alinhamento de Nível/Prêmio
da v062. A nova compilação não comprova aparência ou alcance de todas as telas.
Permanecem separados os 13 falantes explícitos curtos e a ampliação das
categorias abreviadas. As 16 revisões históricas de nomes já foram tratadas
nas v052–v054: o auditor da receita v063 continua indicando zero bloqueadas
nesse conjunto. Não reabrir essa pendência resolvida nem confundi-la com os
novos minerais, que só agora receberam tradução.

## Histórico dos relatos após v062 — pausa já encerrada

O usuário pediu encerrar as alterações por agora e passou a enviar achados
para registro. Aguardar nova ordem antes de investigar/aplicar esses casos;
nenhuma nova ISO ou mudança de receita nesta recepção.

- **Busca sem inimigos:** ao usar a técnica Busca num local sem inimigos,
  aparece `No enemies in the vicinity`. Pendência de tradução da mensagem;
  sugestão contextual: “Não há inimigos por perto.” Origem binária e limite
  de armazenamento ainda não investigados. Evidência:
  codex-clipboard-fe7355a1-7f9c-42e8-9565-fd4ad8435cc1.png.
- **NPC que monta mapas:** segundo o usuário, a tela desse serviço mostra
  o título `Montar itens` e a pergunta `Qual componente de first?`. Revisar
  o contexto do serviço, a frase incompleta/mista e eventual composição de
  segmentos ou variável não traduzida. Não presumir que first seja nome
  próprio, traduzir uma parte isolada ou confirmar o título correto sem
  conferir a origem e os argumentos. Evidência:
  codex-clipboard-40440ede-1acf-4487-8c42-5deb508a5682.png.
- **Trocadilho de Disassembler:** a captura mostra o nome do personagem
  preservado, mas a fala foi traduzida como `...Des...montar... em... pedaços...!`.
  O usuário explicou que ele pronuncia o próprio nome com pausas e faz um
  trocadilho com desmontar. Revisar a fala original e o entorno da cena ao
  retomar, preservando Disassembler, o ritmo entrecortado e o jogo de palavras;
  não tratar automaticamente a sequência do nome como um verbo a traduzir.
  A redação substituta e seus limites ainda não foram investigados ou definidos.
  Evidência: codex-clipboard-c97e161e-6fe8-46a7-abd1-d3d49244810d.png.
- **Nome do item 190:** o usuário substituiu a escolha anterior Colete avariado
  por **Colete quebrado**. Redação aprovada para a próxima aplicação; a receita
  histórica v062 e sua ISO permanecem intactas. O alvo tem 15 bytes no codec.
- **Revigorante, item 336:** o usuário considera a tradução correta, mas quer
  um nome mais marcante para esse item único que revive um personagem.
  Sugestão principal para revisão: Dose Fênix (11 bytes). Alternativas:
  Renascimento (12) e Segunda Chance (14). Todas cabem no teto conhecido de
  16 bytes, sem novos glifos; nenhum nome novo foi aprovado ou aplicado ainda.
  Ao escolher, conferir também referências textuais: a receita acumulada
  contém Revigorante numa lista numerada, além do nome do item. Não alterar
  esses textos por substituição indiscriminada sem vincular o contexto.

As capturas comprovam o texto exibido e o usuário fornece o contexto. Não
comprovam a causa técnica do segundo erro ou o caminho exato da ISO usada.
Versão jogável e atalhos continuam v062; backup v059 preservado.

## Entrega v062 — nova rodada de capturas

Aplicados Colete avariado (190), Instinto animal (itens 864/959 e ação 219),
Vitrola em 11 rótulos e seus comandos, Toca da Cobra no nome e aviso da caverna,
ITENS/HABILIDADES, Reboque/Rebocar/Soltar reboque e a janela de descarte de
placas, com Carga/Livre. Corrigida uma coluna antes dos números de Nível e
Prêmio, preservando parâmetros e valores. Aparência final aguarda o usuário.
Manual e roteiro em docs/interface-v062.md. Faixas musicais e Crimson Manzier
(equipamento único 176) preservados.

Passaram 60 testes distintos e a comparação integral confirmou apenas 1.268
bytes em 26 patches previstos. Fonte/layout e diretório ISO inalterados.
Cinco ISOs de trabalho, dentro do limite; backup v059 preservado. Iniciador
e atalho de pasta acompanham v062. Sem execução de PCSX2 pelo Codex.
Permanecem as categorias abreviadas e os 13 rótulos explícitos curtos listados
abaixo. Capturas de MEMBROS/FROTA documentadas como observação pontual da arte
v061 em reports/interface-v061-visual-user.json.

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
