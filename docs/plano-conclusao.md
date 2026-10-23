# Plano para concluir a tradução

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
