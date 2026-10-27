# Plano para concluir a tradução

**Escopo gráfico atualizado e v040 — 26/10/2026:** por orientação do usuário,
preservar todas as imagens dos pôsteres wanted e dispensar recriação de títulos
de cassino/minijogos como WIN, LOSE e ROUND. Manter trabalhos já feitos.
Now Loading recebe somente [Carregando](interface-v040.md), numa alteração
isolada dos pixels de RLOADING. Menus e instruções em texto continuam no
escopo, assim como as propostas de pintura ainda separadas para revisão.
Créditos não recebem novas intervenções. O planejamento de cartazes genéricos
e títulos gráficos abaixo é histórico e foi substituído por esta orientação.

**Orientação atual e gráficos de pintura — 26/10/2026:** manter os créditos
já traduzidos e encerrar essa frente, conforme pedido do usuário. Apresentar
comparações visuais no chat para avaliar as próximas artes. Foram preparadas
[seis propostas de pintura](pintura-graficos-proposta-v001.md), ainda fora da
ISO. Tabelas e oito encaminhamentos originais de textura/GANM conferidos;
composição em memória preserva as 228 legendas existentes. Nove testes novos
aprovados. A revisão da arte não impede continuar os outros mecanismos.
Base jogável continua v039, com 3.804 campos de interface.

**Atualização — descoberta v002 e interface v039, 26/10/2026:**
As 81 raízes antes sem parser foram separadas em 18 contêineres de animação,
55 modelos vinculados a consumidores, cinco bancos de som e três recursos
especiais ainda opacos. Com os 140 contêineres anteriores, há 5.876 partes de
animação/571 conteúdos distintos descompactados e verificados; não são textos
novos. Semântica interna permanece parcial, sem declaração de cobertura total.
Ver [descoberta v002](descoberta-desconhecidos-v002.md).

A tradução foi retomada com 50 linhas dos créditos finais, totalizando
3.804 campos de interface na [v039](interface-v039.md), sem alterar diálogos,
nomes ou a tipografia aprovada. Marketing preservado não conta como tradução.
Próximos conjuntos: concluir vínculos dos recortes de pintura e traduzir seus
botões em conjunto; depois carregamento/minijogos/cartazes conhecidos. Não
condicionar esses lotes a uma engenharia completa de geometria e áudio sem
evidência de texto. As pendências específicas de TITLE, fontes maiúsculas,
rótulos sem espaço e nativos continuam separadas.

**Descoberta das entradas desconhecidas — 26/10/2026:**
[Relatório técnico](descoberta-desconhecidos-v001.md). As365entradas foram
agrupadas e investigadas:284têm estrutura identificada e81continuam sem parser.
Não tratar os140contêineres de41partes como totalmente compreendidos:
5740conteúdos internos continuam opacos. Recuperadas172imagens, revisadas em
15folhas; dois candidatos gráficos e muitos carimbos/modelos/logotipos a
preservar. Parsers separados dos importadores históricos, sem edição liberada.
48testes aprovados. Próxima investigação: consumidores dos36cabeçalhos numéricos
semelhantes e dos blocosSAF, sem presumir texto; para localização, manter os
candidatos gráficos reais no mapa de trabalho. Zero tradução ou ISO nova;
base jogávelv038 preservada. Demais indicações abaixo são históricas.

**Preparação retomada após v038:** o usuário esclareceu que esperava os
mecanismos e a triagem antes de mais tradução. Entrega em
[Preparação de edição v001](preparacao-edicao-v001.md): recompressor e pacote
de 51 linhas selecionáveis dos créditos, doze recortes de pintura (dez
editáveis/dois protegidos), transporte reversível dos119atlas e revisão visual
de todos eles em18folhas.50testes aprovados. Não houve tradução ou ISO nova.
O transporte produz cópias locais, sem integração automática; concluir vínculos
de uso da pintura e apresentação dos créditos antes dessa integração.365entradas
desconhecidas continuam explícitas. Próximo lote pode agrupar pintura,
carregamento, minijogos e elementos genéricos de cartazes conforme forem
liberados, preservando nomes/categorias. A base jogável continua v038.

**Retomada da tradução — interface v038:** usuário autorizou iniciar a tradução
após a descoberta. [Legendas de pintura](interface-v038.md): doze nomes distintos
aplicados às 228 referências, com células fixas e teto conservador de dez bytes.
Interface totaliza 3.754 campos; MAP v037, fontes/layout v005 e arte v014 intactos.
Próximo conjunto: preparar os rótulos gráficos de pintura a partir dos atlas
descobertos, vinculando recortes/consumidores e conservando MAIN/SUB/SE. Créditos
exigem recompressor/semântica do renderizador; destinos, TITLE e nomes pendentes
continuam separados conforme descoberta. Não reabrir indiscriminadamente o teto
dos itens ou as células de fonte. Entregar conjuntos completos seguros e uma
imagem consolidada por rodada. Detalhes anteriores abaixo são históricos.

**Prioridade atual — descoberta consolidada, 25/10/2026:** por orientação do
usuário, investigar o restante antes de outro lote de tradução. Mapa e ordem
de preparação em [Descoberta v001](descoberta-v001.md), metadados em
`reports/descoberta-v001.json` e catálogo local substituível em
`work/descoberta-catalogo.json`. Novos conjuntos localizados: créditos LZSS,
legendas/botões de pintura e tabela de destinos. Nomes protegidos, candidatos
binários e estruturas ainda sem consumidor completo ficam separados; não contar
tudo como texto faltante. Preparar mecanismos e triagem gráfica em conjunto,
depois traduzir um lote amplo consolidado. A base jogável permanece interface/MAP
v037: 6.024 registros alterados, 5.983 corpos/opções e 912 referências de rótulos
traduzidas. Não houve tradução, fonte ou ISO nova nesta fase. Atualizações abaixo
são históricas.

**Atualização diálogos v033:** [controles restantes, texto nativo e auditoria](dialogos-v033.md). Foco do usuário voltou aos diálogos pendentes. Recuperados 14 registros; total 5.983 traduções/27 adiamentos (19 N$3 preservados e oito textos nativos repetidos). Outros oito controles foram reconhecidos com preservação exata das peculiaridades de origem; %NO e preços com % não foram reparados. Todos os 5.969 patches anteriores e interface/fontes/arte preservados. Auditor local agora consolida um JSON e mapeia 134 rótulos de falantes/1.527 referências, sem liberá-los. Varredura de 54.125 comandos SSD fora dos parsers conhecidos encontrou zero candidatos pelo filtro ASCII, sem comprovar completude do MAP. Próximos alvos: consumidor dos rótulos genéricos, contexto dos oito nativos e revisão editorial/visual. A instrução de desligar da rodada anterior foi atendida e não se repete automaticamente.

**Atualização v032:** [títulos do personagem e recompensas](interface-v032.md). Rodada extensa de 75 campos: 73 títulos e duas mensagens de prêmio, com 3.526 campos acumulados. Cinco títulos preservados por decisão explícita; aliases mantidos e títulos compartilhados revisados para servir aos dois grupos. MAP v032 permanece em 5.969 traduções/41 adiamentos; nomes de itens 516/25 pendentes, descrições 566/925 referências, layout v005 e arte v014 intactos. O comando TITLE de nomeação é distinto dos títulos da ficha e continua pendente. Testes e delta integral no relatório v032. Usuário confere em partida normal. Desligamento solicitado nesta rodada somente após conclusão e envio ao GitHub; não se torna regra para outras rodadas.

**Atualização v031 / MAP v032:** [sucata para construção de tanques](interface-v031.md). Rodada normal de oito diálogos; total 5.969 MAP traduzidos e 41 adiamentos. Interface/fontes/arte anteriores intactas, 3.451 campos. Somente três tokens com divisor literal 100 liberados por política opt-in, sem permissão genérica de f. Testes e comparação integral registrados no relatório v031; visual pendente em passagem normal. TITLE e demais bloqueios continuam para rodadas próprias. Indicações anteriores abaixo são históricas.

**Atualização v030 / MAP v031:** [serviços e conclusão da entrada de nomes](interface-v030.md): 69 traduções novas e dois gráficos FIM; 5.961 registros MAP e 3.451 campos de interface. Retomadas 74 ocorrências, com cinco preservações sem contar como tradução; todas as traduções anteriores intactas. Restam 49 adiamentos técnicos: 19 nomes N$3 preservados, 14 nativos e 16 outros, incluindo oito formatos numéricos com f. Próxima rodada pode investigar TITLE e esses formatos em conjunto, com provas próprias. Mantidos fontes/layout v005, título v014, 566 descrições/925 referências e 516 nomes/25 pendentes. Comparação integral: 5.845 bytes em 70 intervalos autorizados; nenhuma execução PCSX2. Cinco ISOs e alpha protegida. Indicações anteriores abaixo são históricas.

**Atualização v029:** [painel de senha e navegação de nomes](interface-v029.md): três botões gráficos traduzidos e BACK→VOL. nos três slots, sem contar revisões como registros novos; total 3.449 campos. Números, senha, texto digitado, fontes e demais traduções intactos. TITLE e variantes gráficas FNAME_DT ainda exigem prova de uso; 25 nomes mantêm seus bloqueios. Uma ISO consolidada, teste visual pendente. Indicações anteriores abaixo são históricas.

**Atualização v028:** [descrições conhecidas concluídas](interface-v028.md): 566/567 traduzidas, 925 referências, zero adiamentos nesse catálogo; somente ??? preservado. Repack vinculado ao pool original e pai v026; caso 80%% e contexto canino de Coat comprovados separadamente. São 27 campos novos e 3.446 acumulados. Uma ISO consolidada; próximos alvos: nomes bloqueados, TITLE/BACK, lacunas gráficas e teste visual corrido. Indicações anteriores abaixo são históricas.

**Atualização v026:** [expansão consolidada de batalha e interações](interface-v026.md), 1.298 campos novos e 3.419 acumulados. Preflight de integridade implementado; recorte nominal revisado (25 pendentes, preservações separadas). MAP/fontes/arte anteriores intactos. Próximos alvos: prova de capacidade/consumidores para as 24 descrições de espaço, controle 80%% separado, 25 nomes pendentes, Coat/TITLE/BACK e revisão visual/contextual consolidada; fragmentos MAP por último. Não forçar outro lote desse volume sem conteúdo seguro. As indicações anteriores abaixo são históricas.

**Planejamento atual sobre v025:** consultar [Próximos passos e cobertura](proximos-passos-v025.md). MAP conhecido: 81,48%; descrições: 95,41%; nomes no recorte não protegido: 91,33%. São métricas de registros, não percentual do jogo inteiro. Prioridade: integridade no iniciador, revisão dos 49 nomes restantes, capacidade das descrições e lacunas reais de interface; fragmentos MAP depois. Nenhuma tradução ou ISO nova nesta rodada.

**Atualização v021:** cinco frentes de nomes somam 268 inclusões, mais 17
mensagens de sistema: 285 ocorrências novas e 2.057 acumuladas. São 457 nomes
traduzidos; descrições continuam 536/567 e MAP v030 intacto. Perfil opt-in de
nomes usa apenas o teto observado de 16 bytes e o preenchimento zerado do próprio
registro, sem alterar +17..+127. NDATA 12 usa perfil específico, com o descritor
de 875 bytes e %INSTALLSIZE% preservados. Restam 47 propostas de nomes pendentes;
o planejador separa motivo histórico de diagnóstico atual. TITLE/BACK e Coat
permanecem bloqueados; não adivinhar ações nem expandir nomes além do teto.
Procedimentos, evidências e teste visual consolidado em `docs/interface-v021.md`.

**Atualização v020:** três blocos em uma única imagem: 189 nomes genéricos/
habilidades (183 rótulos distintos), 41 descrições retomadas e oito campos de
interface. São 536/567 descrições (883 IDs) e 1.772 campos acumulados. A confirmação
de melhoria passa a usar incremento/decremento, mantendo os prefixos in/de
compartilhados e os parâmetros originais. Nomes ficam nos próprios comprimentos,
com atributos e IDs intactos; não expandir o campo aparente de 24 bytes. Restam
29 descrições com orçamento difícil e uma com percentual bloqueado. As propostas
pendentes de nomes exigem revisão editorial futura, mesmo que um limite técnico
venha a ser resolvido; não promovê-las automaticamente. Ver `docs/interface-v020.md`.

**Atualização v019:** 142 adiamentos recuperados por revisão contextual dentro
dos slots existentes: 495/567 descrições traduzidas, usadas por 832 IDs; 70
adiamentos de espaço, um percentual bloqueado e um marcador preservado. Toda
a v018 permanece intacta; total 1.534 campos de interface. Diagnóstico de bytes,
linhas e colunas integrado ao mesmo planejador local. Não reorganizar o pool
sem nova prova dos consumidores; manter as lacunas de interface e os casos
difíceis separados. Ver `docs/interface-v019.md`.

**Atualização v018:** revisão inicial dos 567 alvos do pool conhecido de descrições
concluída: 353 traduzidos (602 IDs), 212 adiados por espaço/linhas, um percentual
bloqueado e o marcador ??? preservado. A rodada acrescenta 239 textos e mantém
toda a v017. Total 1.392 campos de interface. Ver `docs/interface-v018.md`.
Próxima etapa técnica: triagem das causas de espaço e prova de referências/
consumidores antes de qualquer reorganização do pool. Não confundir esse catálogo
revisto com descoberta ou tradução de todos os itens do jogo.

**Atualização v017:** iniciada a etapa de descrições de equipamentos. São 114
textos novos usados por 126 itens; 61 propostas adiadas por espaço e 392 ainda
não revistas no catálogo de 567 alvos. Nomes/atributos intactos e toda v016
preservada. Total 1.153 campos de interface. Próximo lote: continuar as descrições
ainda não revistas, antes de procurar soluções de expansão para os slots difíceis.
Manual `docs/interface-v017.md`. A raiz tem cinco iniciadores úteis, e a retenção
passa a cinco ISOs de trabalho, além da alpha permanente fora da fila.

**Atualização v016:** correio Satcom localizado em S_PACK, com 41 corpos e
38 assuntos traduzidos; também foram traduzidas as 40 descrições de procurados.
São 119 campos novos e 1.039 ocorrências acumuladas de interface, mantendo a
v015 inteira. Nomes/recompensas/metadados e offsets das duas tabelas não mudam.
Política específica, evidências e limites em `docs/interface-v016.md`.
Continuam os testes visuais agrupados pelo usuário; composição de melhoria e
outras lacunas contextuais seguem pendentes, antes da expansão segura para itens.

**Atualização v015:** aplicado o lote consolidado de personagem/inventário,
lojas e serviços, com 279 campos novos e 920 ocorrências totais de interface.
Consultar `docs/interface-v015.md`; o repack é exclusivo da tabela UI S_PACK
em 0x35070/0x2000. Não libera tabelas gerais de itens. Seguem pendentes teste
visual consolidado, composição `%screased`, contexto de Coat e lacunas fora
desse catálogo. Arte v014, MAP v030 e layout v005 preservados.

## Atualização após interface v014

A ordem operacional atual está em `docs/proximas-etapas-interface.md`:
personagem/inventário/equipamentos, lojas/serviços, veículos/batalha e demais
interfaces frequentes; depois tabelas de itens e, por último, fragmentos MAP e
revisão final. Base: interface v014 (641 ocorrências), MAP v030 e layout v005.
As contagens e próximos alvos das seções abaixo são históricos quando divergirem
dessa atualização. Não refazer campos já traduzidos; começar por auditar lacunas
das telas propostas. Nenhuma ISO é criada nesta rodada de planejamento.

## Ordem atual, definida pelo usuário

1. **Em execução: HUD, Satcom, mensagens, menus e diário.** Consolidar strings com referências no ELF, separar rótulos rasterizados e conteúdo em arquivos próprios. Lote atual: 473 campos (200 novos) em `docs/interface-v003.md`; alpha v001 preservada separadamente em dist/. Confirmar apresentação e acentos por tipo de tela; manter os diálogos v029.
2. **Depois: itens/equipamentos.** Extrair tabelas de S_PACK.SDA e investigar os arquivos de dados correspondentes, preservando nomes únicos. Não iniciar essa etapa antes de avançar a interface.
3. **Por último: pendências pequenas do MAP.MCT.** Congelar os 123 adiamentos v029 (109 opacos e 14 nativos), sem perder receitas/evidências. %$0/%$2 deixam de ser o próximo alvo imediato.
4. Revisão contextual e passagem funcional consolidada continuam necessárias.

As seções e estados históricos abaixo registram a ordem anterior; não prevalecem sobre esta atualização. Títulos rasterizados do HUD integram a primeira etapa, mesmo que o procedimento técnico seja de imagem.

## Base e método

Manter a tradução consolidada e o perfil de layout v005 aprovado nas falas de Nina. Cada etapa produz ferramentas locais reutilizáveis, evidência por formato e um lote contextual. Separar extração, edição binária e teste visual. Não trocar confiabilidade por contagem.

A primeira triagem reproduzível está em `reports/plano-pendencias-v001.json`, obtida por `tools/plan_remaining_texts.py`. Na base v023, os 244 opacos formam 39 grupos disjuntos de spans; os 158 preservados a revisar têm 112 combinações textuais distintas. Contagens por token isolado podem se sobrepor e não devem ser somadas.

## 1 — Fechar o MAP.MCT conhecido

**Pausado pela prioridade atual:** liberar uma família de controle por vez, começando por grupos grandes com contexto coerente. Primeiro grupo: 32 registros cujo único opaco é `%B$15`, tratados na v024 com política própria e limite de tamanho mais estrito.

**Segundo grupo:** 31 registros exclusivos `%$1`, tratados na v025 com política v007. O leitor e o handler em `0x1B5DEC..0x1B5E83` confirmam a variável 1 e o formato inteiro `%d`. O caminho com f minúsculo continua bloqueado; a tradução preserva G e não fixa os números. Ver `docs/controles-numericos-v007.md`.

Depois: grupos `%N$3` (19), `%$15` (18), `%T$0` (18), `%I$0` (14) e combinações. Esses números são grupos disjuntos da base inicial, não metas garantidas. Para cada família: provar consumo/argumentos no ELF, preservação dos valores, limites dos buffers e testes negativos; só então acrescentar uma política opt-in. Não liberar sintaxe apenas ampliando regex.

Em paralelo, revisar os 14 registros com bytes nativos e os 112 conjuntos distintos de preservados: nomes, risadas e expressões podem permanecer; descrições de ação ou outros textos só recebem decisão após contexto. Registrar a justificativa por ID, sem inflar o total traduzido por mudanças cosméticas.

**Critério de saída:** cada registro conhecido traduzido, preservado por decisão explícita ou bloqueado com motivo e próximo experimento definido. Isso não prova que todo o MAP foi descoberto.

## 2 — Diário, menus e dados de itens

1. DIARY.DAT: reutilizar os 68 registros/136 campos e a ferramenta existente; rastrear controles, confirmar de onde vem o título exibido, provar acentos nessa interface e só então traduzir o conjunto. Não atribuir o antigo teste negativo a saves sem evidência.
2. S_PACK.SDA: modelar as tabelas internas de equipamentos já localizadas; separar nomes próprios de descrições genéricas, extrair IDs/referências/capacidades e criar round-trip antes da tradução.
3. SLUS_212.93: catalogar mensagens de interface com referências de código; excluir strings técnicas/debug antes de preparar lotes.
4. Investigar MMBATTLE.BIN, BTITEM.DAT, HWEAPON.DAT e TANK.DAT por evidências. Não presumir texto só pelo nome do arquivo.

**Critério de saída:** catálogo por tela/recurso, extrator/reinseridor com testes e amostra visual de cada mecanismo. Ampliar maiúsculas PT-BR faltantes quando necessárias ao conteúdo real, preservando os glifos já aprovados.

## 3 — Imagens e vídeo

Inspecionar F_COMMON.SDA, RTITLE.SDA, PASSWORD.SDA e candidatos adicionais para identificar texto realmente rasterizado. Desenvolver exportação/importação de textura preservando dimensões, paleta e metadados. Conferir DEMO.STM para saber se há texto a localizar; não presumir necessidade de edição ou dublagem.

**Critério de saída:** lista de recursos com e sem texto confirmada visualmente, assets editáveis e round-trip por formato identificado.

## 4 — Revisão contextual por cenas

Relacionar os blocos SSD a cenas/áreas/personagens apenas com evidência. Revisar a tradução por conversa, mantendo ordem de opções, humor, pistas de missões, termos técnicos e nomes protegidos. Não chamar uma cidade de completa somente porque existem textos dela no catálogo.

Gerar um checklist de cobertura por local com status confirmado/provável/desconhecido e revisão de nomes. Ajustar layout e texto com métricas, sem omitir artigos ou remover acentos para caber. Caso um texto realmente precise crescer, tratar realocação como uma investigação independente de ponteiros e extents.

## 5 — Passagem funcional e entrega

O usuário faz navegação e testes periódicos de imagens consolidadas. Cobrir progressão, escolhas, lojas, batalha, diário, salvamento/carregamento e cenas opcionais. Registrar local, ID quando conhecido, versão e defeito. A suíte binária acompanha cada mudança de parser/compilador; não repetir toda a campanha a cada frase.

Na conclusão: uma versão identificada, receitas e ferramentas reproduzíveis, glossário consolidado, lista de limitações e patch de distribuição aplicável à revisão exata da ISO original. Não distribuir ISO, BIOS, saves ou arquivos proprietários.

## Limites para evitar trabalho improdutivo

Se uma família não avançar após investigar o leitor, consumidores e amostras representativas, documentar o bloqueio e passar ao próximo recurso independente. Não inventar compatibilidade entre formatos. Construir apenas uma ISO por lote aprovado; manter no máximo dez. Preservar o histórico de receitas e relatórios.


## Estado após o primeiro passo — v024

Primeiro grupo concluído binariamente: 32 registros B15 traduzidos. Permanecem 212 opacos em 35 grupos disjuntos e 14 nativos. A triagem atual está em `reports/plano-pendencias-v002.json`. Próxima investigação: `%$1`, ainda com 31 registros exclusivos. A revisão dos preservados e a validação visual da cena continuam pendentes.

## Estado após o segundo passo — v025

São 5.821 registros traduzidos, com 31 acréscimos de preços, hospedagem, ônibus e MC Hamir. Permanecem 181 opacos em 34 grupos disjuntos e 14 nativos. Triagem em `reports/plano-pendencias-v003.json`; próximo grupo exclusivo: `%N$3` (19). Preservar os 158 registros a revisar / 112 combinações distintas.

O usuário informou que Dr. Palm está distante no save e pediu teste conjunto em uma passagem contínua. Registrar a pendência visual e continuar o trabalho técnico e a tradução compatível sem exigir acesso imediato à cena. O roteiro cumulativo da v025 inclui preços, ônibus e construção de tanques.

## Estado após o terceiro passo — v026

O grupo `%N$3` foi inspecionado: os 19 corpos apresentam nomes de tanques e permanecem intactos por regra do usuário. O lookup foi parcialmente rastreado no ELF, mas não há política de edição de N. A decisão editorial não equivale a liberar o comando. Evidência em `reports/n3-preservation-v001.json`; não repetir esse grupo sem nova necessidade.

O grupo `%$15` teve 18 registros retomados: 17 traduzidos (ofertas, casa, inscrição, balsas e pagamentos) e um marcador preservado. A política v008 mantém a referência e o comprimento dos segmentos; f minúsculo permanece bloqueado. São 5.838 traduções e 177 adiamentos (163 opacos, incluindo os 19 N3 preservados; 14 nativos). Triagem em `reports/plano-pendencias-v004.json`.

Próximo alvo: `%T$0`, 18 registros exclusivos, depois `%I$0`, 14. A categoria heurística de revisão passou a 159 por incluir o marcador F já decidido; as outras 158 continuam pendentes de revisão contextual. Não contar o marcador ou nomes preservados como traduções novas. Manter o teste visual acumulado para o save corrido, com Dr. Palm, números e escolhas.

Triagem antecipada de T0 em `reports/t0-triagem-v001.json`: 18 despedidas, 14 de boa sorte e quatro de cuidado/despedida, em três variantes de quebras. O prefixo de tratamento não prova qual entidade a variável resolve; investigar o consumidor antes de traduzir. Ainda não foi liberado.

## Estado após o quarto passo — v027

As 18 despedidas T0 foram traduzidas com a referência dinâmica e tratamento sr. preservados em seus papéis. A política v009 verifica handler, dois accessors e dependências no ELF original, com teste de instruções em memória simulada. Não se comprovou uma identidade canônica nem se liberaram N/I. São 5.856 traduções e 159 adiamentos (145 opacos e 14 nativos).

Triagem em `reports/plano-pendencias-v005.json`. Próximo alvo previsto: `%I$0`, 14 registros exclusivos. A liberação de T0 uniu grupos antes separados: `%N$0` agora aparece com 22 registros exclusivos. Investigar sem promover por contagem; manter os 19 nomes N3 intactos. Testes visuais seguem acumulados para o save corrido.

## Estado após o quinto passo — v028

As 14 falas I0 foram traduzidas com nomes dinâmicos preservados: proteção contra o frio, combate, inspeção de peça e presentes. A política v010 confere o handler e a referência à tabela (stride 128) no ELF original, com instruções executadas em memória simulada. Não libera a edição dessa tabela nem comprova seu vínculo completo com S_PACK.SDA.

São 5.870 traduções, 145 adiamentos (131 opacos em 29 grupos e 14 nativos), com triagem em `reports/plano-pendencias-v006.json`. Próximo alvo: `%N$0`, 22 registros, distinto dos 19 nomes N3 preservados. Inclui recebimento de veículos, tutorial de Drive, hospedagem, nomeação e outras referências. Preservar Drive enquanto a interface correspondente mantiver esse nome; não inferir uma entidade fixa pelo índice de variável zero. Manter a revisão visual conjunta no save corrido.

## Estado após o sexto passo — v029

Os 22 registros N0 foram traduzidos: hospedagem, recebimento/tutorial de veículos, anúncio de nome, campo arado, referência a músicas e comemoração de Dr. Palm. A política v011 confere o lookup de ponteiros N e o leitor no ELF original, com instruções executadas em memória simulada. Mantém a diferença entre N0 literal e N$0 indireto; não libera N3 ou uma entidade canônica única. Drive permanece igual à interface.

São 5.892 traduções, 123 adiamentos (109 opacos em 28 grupos e 14 nativos), com triagem em `reports/plano-pendencias-v007.json`. Próximo alvo: `%$0` e `%$2`, 12 registros exclusivos cada, após confirmar os argumentos e sufixos. Não promover os caminhos fracionários nem variantes desconhecidas por contagem. Manter os nomes N3 e o teste visual conjunto no save corrido.


## Interface v002 e alpha

A rodada ampliada acrescenta 185 strings, com 273 acumuladas, em opções, status, gerenciamento de veículos, nomeação, campo e minijogos. A preservação integral da interface v001 e do MAP v029 acompanha a comparação da imagem inteira. Os próximos alvos permanecem na interface: comprovar o wrapper das estatísticas/cabeçalhos, localizar avisos de Memory Card e conteúdo de mensagens/ajuda, e preparar importação fiel dos textos gráficos. Não voltar aos pequenos controles MAP antes desses conjuntos.

A alpha escolhida pelo usuário é a interface v001, copiada para dist/alpha-v001/ fora da retenção e com hash conferido; não promovê-la implicitamente para a versão atual. Mantêm-se dez imagens de trabalho além dessa exceção permanente. Ver docs/alpha-v001.md.


## Interface v003 — mensagens do sistema, diário e estatísticas

Os 200 campos novos abrangem 98 mensagens de Memory Card/HD, 100 campos em 65 registros do diário e dois literais de estatísticas/cabeçalho de veículos. O novo leitor CRLF está limitado a duas entradas NDATA e aos tamanhos carregados pelos descritores originais. Preservam-se os 273 textos anteriores e os diálogos v029. A validação visual será consolidada; não é necessário provocar erros de cartão ou formatar saves.

Próximos conjuntos: páginas de ajuda HTML em NDATA (ainda bloqueadas), origem do corpo das mensagens e importação fiel de textos gráficos de Satcom/batalha/título/nomeação. A entrada 12 de instalação de HD permanece original. Os dois corpos nativos do diário seguem bloqueados; manter nomes, expressões e tabelas intactas onde não houve tradução. Não retomar os pequenos controles MAP enquanto a interface estiver na prioridade.


## Interface v004 — ajuda do Satcom

As 44 páginas HTML identificadas foram traduzidas com marcações e imagens preservadas, elevando a interface a 519 campos. MAIN/SUB/SE seguem a regra expressa do usuário; oito diálogos e duas traduções de interface anteriores receberam somente essa revisão terminológica. As páginas têm conferência binária, mas layout, rolagem e quebras automáticas ainda precisam do teste visual consolidado. A próxima etapa permanece na interface: importação fiel dos textos gráficos e localização do conteúdo das mensagens ainda não catalogado, antes de itens e dos fragmentos MAP. Não abrir novamente os pequenos controles opacos por conveniência.


## Interface v005 — índice e preparação gráfica

O índice da ajuda agora tem 53 rótulos traduzidos, com 12 categorias e 44 vínculos de tópico preservados; Satcom/Remote/Alpha Series permanecem iguais. Mais um literal de status usa MAIN/SUB/SE em maiúsculas. São 573 campos acumulados, com os textos anteriores intactos. O transporte local de seis texturas foi comprovado por round-trip sem edição e preservação de paletas/alpha/headers. O próximo passo é mapear recortes/UVs e traduzir os rótulos rasterizados; localizar o conteúdo das mensagens segue pendente. A busca ASCII inicial em FD_POST não encontrou frases de correspondência, mas não identifica seu formato nem exclui codificação/compactação. Testes visuais continuam acumulados.


## Interface v006 — Satcom, batalha e cabeçalhos rasterizados

Foram preparados 40 rótulos gráficos em três texturas FBS_DATA, compostos de glifos nativos e vinculados aos recortes GANM originais. Os 573 textos da v005 e MAP v030 são preservados. MAIN/SUB/SE seguem explícitos; o Assunto de mensagens é contexto distinto. A primeira proposta gráfica foi inspecionada em previews, sem execução do PCSX2. Permanecem os rótulos riscados/miniatura PlayingTime e os conjuntos gráficos separados de opções, título e nomeação. Próximo alvo recomendado: título/New Game/Load Game e rótulos gráficos de opções/nomeação, após mapear seus próprios recortes e consumidores; localizar o corpo das mensagens segue pendente. Não avançar para itens ou fragmentos MAP antes desses conjuntos.


## Correção prioritária da fonte do Satcom — v007

A comparação com Remote confirmou que a v006 empregava outra família (GFI de diálogos), mais arredondada. A v007 recompõe somente os 26 rótulos do Satcom com letras recuperadas do atlas de botões, sem redimensionamento; mantém as outras 14 ocorrências gráficas e todos os textos. L/P/J/j e os acentos necessários são reconstruções, com validação visual pendente. Antes de ampliar outros desenhos, comparar cada família com sua referência original; revisar tipografia de batalha/cabeçalhos separadamente. A investigação de título/nomeação permanece no plano, sem declarar esta correção suficiente para todas as fontes.


## Alinhamento dos glifos — v008

O retorno do usuário aprovou a aparência geral da fonte, mas identificou oscilação vertical. A extração clara reutilizava origens da variante normal; Music/Config/Diary diferem em um pixel entre variantes. A v008 corrige essa amostragem, mantendo os corpos em uma base comum a Remote, sem escala. Descendentes de g/j/ç permanecem naturais. Os testes novos verificam métricas por glifo; a checagem anterior de tamanho/limites não detectava esse erro. Retomar outras famílias gráficas somente mantendo comparação de fonte e métricas por contexto; validação visual em jogo segue pendente.

## Preparação ampla dos próximos conjuntos gráficos

O transporte local agora cobre 69 texturas em RTITLE, FNAME_DT, F_COMMON, FD_POST e PASSWORD, com round-trip integral de cinco recursos e proteção de paleta/alpha/estruturas. Ver `docs/atlas-interface-v001.md` e `Preparar-Atlas.cmd`. A v008 permanece como ISO atual, sem novas traduções nesta rodada de infraestrutura.

Os oito painéis foram inspecionados. FD_POST contém nomes e retratos de procurados, que devem permanecer preservados; a origem das mensagens de correio continua desconhecida. RTITLE tem fonte pesada/inclinada própria e três regiões de 180×24. Priorizar título, depois senha/nomeação em conjuntos completos, após vincular consumidores e métricas, mantendo a identidade visual de cada família. Os dois registros desconhecidos da nomeação não foram liberados. Não ampliar automaticamente as políticas de ISO por ter conseguido transportar PNGs.

## Interface v009 — tela inicial completa

Novo jogo, Retomar e Instalar foram compostos com rasters da própria tela, sem reduzir as letras; V/J/R são reconstruções explícitas de traços nativos. Descritor, carregamento e recortes foram conferidos no ELF original e vinculados por hashes. Preservam-se os 613 campos/ocorrências anteriores, incluindo a linha de base Satcom corrigida; total 616. Conferência no PCSX2 continua pendente. Próximo conjunto: senha, depois nomeação, usando as próprias famílias visuais. Correio continua aguardando localização. Ver `docs/interface-v009.md`.

## Interface v010 — nomeação em texto

Foram localizados e traduzidos o cabeçalho e três legendas mistas no ELF. A busca ASCII não capturava as legendas completas por conterem bytes nativos; a referência do cabeçalho usa registrador salvo distante da janela heurística. A política opt-in preserva os bytes opacos e as posições de cada palavra. São quatro campos novos, 620 acumulados. TITLE/BACK continuam em inglês até conferir o comando, sem bloquear a tradução segura das outras instruções. Fonte, gráficos, MAP e seleção de caracteres permanecem iguais à v009. Próxima investigação: semântica desses comandos e rótulos da senha; não adivinhar funções por rótulo. Ver `docs/interface-v010.md`.

## Interface v011 — correção após captura do usuário

O R do título anterior foi considerado ambíguo e foi reconstruído com espaços internos e perna diagonal. A assinatura pedida foi acrescentada ao rodapé por reorganização específica dos seis frames RTITLE, sem código novo ou edição dos créditos oficiais. A assinatura herda o tom/visibilidade de Retomar; sua distância dos créditos originais e os estados do menu aguardam conferência visual. Manter essa correção como prioridade antes de ampliar outros desenhos. As pendências de nomeação/senha/correio continuam na mesma ordem após a conferência. Ver `docs/interface-v011.md`.


## Interface v022 — uma frente de equipamentos

Atual: `translations/interface-v022.json`, manual `docs/interface-v022.md`, relatório `reports/interface-v022.json`. Acrescenta somente 20 nomes de equipamentos/proteções, incluindo nove trajes caninos LV1..LV9; siglas CVC/BDU e Bio preservadas. São 477 nomes/462 rótulos e 2.077 campos de interface. Retoma explicitamente IDs 141 e 187; ledger com 523 selecionados, 477 aceitos, 45 pendentes e um preservado. Demais propostas, todos os 457 nomes anteriores e seus patches permanecem idênticos.

Mantém teto v002 de 16 bytes, MAP v030, layout v005, arte v014 e 536 descrições/883 referências. Não ampliar nomes únicos, fontes ou controles para caber. Passaram 26 testes distintos; comparação integral v021→v022: 270 bytes diferentes somente nos 20 intervalos autorizados, diretório e demais bytes idênticos. SHA-256 da ISO: `f0d33e8574cdbfee95d349d88a66353ee1292e067a3d5d05bedb6aff4a483230`. Nenhuma execução PCSX2. Iniciador aponta para `work/interface-v022/MetalSaga-ptbr-interface-v022.iso`; cinco ISOs de trabalho e alpha protegida. OneDrive/desligamento só por novo pedido. Próximos bloqueios: nomes que ainda excedem o teto, descrições sem espaço e TITLE/BACK sem semântica comprovada.


## Interface v023 — consumíveis/materiais e móveis/acessórios

Atual: `translations/interface-v023.json`, manual `docs/interface-v023.md`, relatório `reports/interface-v023.json`. Duas frentes: nove ocorrências de consumíveis/materiais e sete de móveis/acessórios. São 493 nomes/477 rótulos e 2.093 campos de interface. Retomados explicitamente IDs 331, 352, 354, 355, 372, 373, 385, 433, 449, 451, 727 e 747; quatro IDs novos 374/619/774/782. Ledger: 527 selecionados, 493 aceitos, 33 pendentes, um preservado. Dados dos outros adiamentos e 477 nomes anteriores/patches intactos. Os aliases Petrol Bomb 354/373 mantêm tradução igual.

Teto de nomes v002, fontes/layout v005, MAP v030, arte v014, 536 descrições/883 IDs mantidos. Passaram 26 testes distintos. Delta integral v022→v023: 204 bytes em 16 intervalos autorizados; demais bytes/diretório idênticos. Iniciador usa `work/interface-v023/MetalSaga-ptbr-interface-v023.iso`; teste visual pendente, sem execução PCSX2. Cinco ISOs e alpha protegida; OneDrive/desligamento só por novo pedido. Próximos bloqueios continuam nomes sem redação natural dentro do teto, descrições sem espaço e TITLE/BACK; não liberar controles/fontes/proteções por conveniência.


## Interface v024 — continuação regular de itens e habilidades

Atual: `translations/interface-v024.json`, manual `docs/interface-v024.md`, relatório `reports/interface-v024.json`. Acrescenta seis nomes (861, 899, 1015, 1043–1045) e retoma cinco descrições (003bb, 0049e, 0310c, 04e00, 04e5a) pelo preparador com resume_deferred explícito. São 499 nomes/483 rótulos, 541 descrições/889 IDs e 2.104 campos de interface. Os 493 nomes e 536 descrições anteriores e seus patches permanecem idênticos.

Ledger de nomes: 532 selecionados, 499 aceitos, 32 pendentes e um preservado; somente 861 retomado, cinco seleções novas. Descrições: 24 pendências de espaço, uma de controle 80%% e um marcador preservado. Hawk Eye 590/877 continua original por alias com componente protegido. Não quebrar a igualdade entre aliases nem liberar o componente para traduzir a habilidade. Manter efeitos, perfis de slots/teto v002, fontes/layout v005, MAP v030 e arte v014.

Passaram 41 testes distintos (cinco do lote, 21 de descrições/preparação, sete do teto, cinco de retenção, três da alpha). Delta integral v023→v024: 261 bytes em 11 intervalos autorizados; demais bytes/diretório idênticos. Iniciador usa `work/interface-v024/MetalSaga-ptbr-interface-v024.iso`; visual pendente, sem execução PCSX2. Cinco ISOs e alpha protegida; OneDrive/desligamento só por novo pedido. Pendências restantes exigem revisão contextual ou prova de capacidade/consumidores; não encurtar sacrificando fatos nem ampliar o formato por conveniência.


## Interface v025 — dezessete nomes, com identificadores preservados

Atual: `translations/interface-v025.json`, manual `docs/interface-v025.md`, relatório `reports/interface-v025.json`. Acrescenta 17 nomes: nove equipamentos, dois acessórios/decorativos, dois componentes genéricos e quatro habilidades. Preservar Kevy/Kaiser/Saratoga/Ali Baba/AAP; foram traduzidas somente designações genéricas. Clay Icon é Imagem de barro, distinto da Figura de barro 459. Revival Keg 870–873 é Barril vital 1..4, distinto de Medicine Keg/Barril de cura 866–869. Não unificar essas séries ou inferir novos efeitos.

São 516 nomes/500 rótulos e 2.121 campos; 541 descrições/889 IDs, MAP v030, layout v005 e arte v014 mantidos. Ledger: 540 selecionados, 516 aceitos, 23 pendentes, um preservado. Nove retomadas explícitas: 179/441/460/646/647/870–873; oito seleções novas. Demais dados e todos os 499 nomes anteriores/patches intactos. Mantém teto v002 de 16 bytes, sem novos glifos, repack ou controles.

Passaram 26 testes distintos. Delta integral v024 restaurada→v025: 217 bytes em 17 intervalos; demais bytes/diretório idênticos. Durante a comparação, a ISO histórica v024 divergiu de seu hash por um byte (ISO 0x1231E377, 1E em vez de 3E). A correção virtual reproduziu o hash histórico; v021/v022/v023/v025 conferiram. A v024 foi inteiramente reconstruída dos originais pelo construtor existente, reproduzindo 7d54ad51ab381a03d3fa8a4a3e42c1ac92914919d8854806876e1019b1213a3e; sem edição de bytes in-place. Relatório anterior preservado em work/interface-v024-invalida/relatorio.json e evidências no relatório v025. Causa indeterminada; não atribuir a hardware ou ao jogo sem evidência. Reconstruir a histórica não a torna versão de desenvolvimento mais recente: iniciador e receita atual são v025.

Iniciador usa `work/interface-v025/MetalSaga-ptbr-interface-v025.iso`; visual pendente, sem execução PCSX2. Cinco ISOs e alpha protegida. OneDrive/desligamento só por novo pedido. Continuar buscando lotes de pelo menos 15 nomes quando houver traduções naturais seguras, sem forçar contagens, limites ou nomes protegidos.
