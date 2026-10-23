# Metal Saga — Projeto de Tradução PT-BR

## Objetivo

Desenvolver uma tradução de Metal Saga (PlayStation 2) para português brasileiro, modificando os recursos necessários do jogo original para execução no emulador PCSX2.

Este projeto é independente de qualquer iniciativa de recompilação nativa para PC.

## Papel do Codex

O Codex é o líder técnico e executor principal do projeto.

Possui autonomia para:

- Investigar arquivos e formatos binários.

- Desenvolver scripts, ferramentas e testes.

- Executar Python, PowerShell e programas auxiliares.

- Utilizar o PCSX2 para testes.

- Pesquisar documentação e ferramentas externas.

- Instalar dependências necessárias.

- Organizar e refatorar a estrutura do projeto.

- Criar commits e realizar pushes no repositório autorizado.

Deve priorizar resultados verificáveis, soluções reproduzíveis e documentação técnica.

## Limites do projeto

O diretório de trabalho autorizado é:

`C:\Projetos\MetalSagaTraducao`

É proibido acessar, pesquisar, ler, modificar ou utilizar arquivos de outros projetos, especialmente:

`C:\Projetos\MetalSagaV2`

Não utilizar conhecimentos obtidos diretamente dos arquivos da recompilação nativa.

Ferramentas e programas instalados no computador podem ser utilizados quando necessários, mas não devem servir como caminho para investigar outros projetos.

Não modificar arquivos externos ao workspace sem necessidade justificada. Para alterações administrativas, configurações globais ou operações destrutivas fora do projeto, solicitar autorização.

## Preservação dos arquivos

A pasta `JOGO` contém os arquivos de referência do jogo, incluindo a ISO original e os arquivos extraídos.

- Tratar esses arquivos como fontes imutáveis.

- Nunca sobrescrever a ISO original.

- Nunca modificar os arquivos extraídos de referência.

- Trabalhar em cópias controladas.

- Produzir ISOs modificadas separadamente.

- Preservar a possibilidade de reproduzir o processo de construção.

A pasta `PCSX2` contém o ambiente de emulação e poderá ser utilizada para testes.

Preservar BIOS, cartões de memória e configurações existentes.

## Metodologia técnica

1. Investigar antes de modificar.

2. Identificar formatos e estruturas por evidências.

3. Registrar offsets, codificações e hipóteses relevantes.

4. Desenvolver ferramentas automatizadas sempre que possível.

5. Criar testes para validar extração e reinserção.

6. Verificar alterações no PCSX2.

7. Documentar descobertas e limitações.

8. Registrar progresso em commits Git.

Preferir Python para ferramentas de análise e manipulação binária, sem impedir o uso de outras linguagens quando tecnicamente justificável.

Não presumir que o jogo utiliza ASCII, Shift-JIS ou qualquer formato específico sem investigação.

## Tradução

O idioma de destino é português brasileiro.

Preservar significado, personalidade dos personagens, contexto narrativo e consistência terminológica.

Manter nomes próprios e termos oficiais quando apropriado.

Considerar limitações de espaço, fontes, caracteres acentuados, ponteiros e estruturas internas do jogo.

A tradução não deve comprometer a execução do jogo.

## Git e GitHub

Repositório autorizado:

`https://github.com/KernellTozi/MetalSagaTraducao`

O Codex pode criar branches, commits e pushes automaticamente.

Não versionar:

- ISOs e imagens de disco.

- BIOS.

- Arquivos originais extraídos do jogo.

- Executáveis proprietários.

- Saves pessoais.

- Arquivos temporários e resultados volumosos.

Antes de commits, verificar os arquivos preparados e respeitar o `.gitignore`.

Não modificar repositórios de outros projetos.

## Comunicação

Responder em português brasileiro.

Apresentar descobertas, problemas e próximos passos de forma objetiva.

Não interromper o desenvolvimento para solicitar aprovação de decisões técnicas rotineiras.

Solicitar orientação quando houver decisões irreversíveis, riscos relevantes ou necessidade de alterar recursos externos ao projeto.

Distinguir claramente fatos comprovados, hipóteses e resultados ainda não testados.

## Primeira prioridade

Realizar o reconhecimento técnico dos arquivos do jogo, identificar possíveis recursos textuais e determinar um caminho viável para extração, tradução, reinserção e testes.

Não iniciar uma tradução em massa antes de validar tecnicamente o processo.

## Organização e continuidade técnica

- Ferramentas próprias em `tools/`, testes em `tests/`, documentação em `docs/`.
- Metadados reproduzíveis em `reports/`; textos extraídos e binários experimentais em `work/`, fora do Git.
- Consultar `docs/reconhecimento.md` para estruturas comprovadas, limitações e comandos.
- Antes de reinserir, verificar hash de origem, tamanho dos slots e tokens de controle.
- Nunca confundir round-trip binário ou geração de ISO com teste de execução no PCSX2.
- Não assumir suporte a acentos; preservar bytes desconhecidos até identificar o mapeamento.
- Em testes futuros do emulador, usar cópias isoladas dos recursos mutáveis e preservar os dados existentes.
- O mapeamento de acentos em `docs/acentuacao.md` é uma extensão experimental das fontes; não é CP932 padrão. Os dois diálogos de Nina receberam validação visual preliminar pelo usuário, sem aprovação geral de tipografia ou outros contextos. Preservar os bancos ASCII e exigir fonte compatível com os bytes reinseridos.
- Priorizar o extrator local `Extrair-Dialogos.cmd`; não investigar ajustes visuais menores das fontes enquanto a prioridade for infraestrutura de extração. Não usar IA/APIs para análise binária repetitiva.
- Consultar `docs/extracao-v002.md` para os parsers msg/msgn e as quatro classes de extração. Validação estrutural não libera edição dos perfis v002. Preservar o fingerprint dos 2.049 registros v001, bytes de controles opacos, segunda string de msgn e intervalos de zeros; não promover registros com contexto incompleto somente para aumentar contagens.
- A v003 acrescenta limites SSD e onze layouts em `docs/extracao-v003.md`. Preservar também os 6.140 registros v002 por fingerprint. Enquadramento atualizado fica no wrapper `validation` e em `contexto-ssd.jsonl`, sem apagar evidência histórica. A cobertura de 13 famílias SSD não comprova 100% do arquivo; a edição segue as políticas v004, com validação visual separada.
- A reinserção atual está em `docs/reinsercao-v004.md` e `Reinserir-Dialogos.cmd`. Compilar lotes contra o original imutável, sem aplicações parciais, com controles e metadados vinculados. Não confundir 6.882 elegíveis binários com execução validada no jogo.
- `slots` usa somente o espaço comprovado; `repack` é limitado a msgn/smsg/2smg dentro do mesmo registro. Não aumentar registros, blocos SSD ou extents ISO sem nova evidência. Opções têm limite de 254 bytes por conta do duplo NUL no buffer temporário; MC/SP/ST mantêm limite conservador de 31 bytes.
- A ISO de desenvolvimento só é alterada com acesso exclusivo e journal. Se `work/desenvolvimento/transacao.json` existir, recuperar antes de usar no PCSX2. Manter receitas Unicode arquivadas e não editar estado/journal manualmente.

## Divisão de testes e avanço em lotes

- O usuário realiza preferencialmente a navegação prolongada, verificações visuais pontuais e testes periódicos de versões consolidadas.
- O Codex continua responsável por engenharia reversa, ferramentas, tradução, reinserção, ISOs, testes binários e documentação. Pode executar diagnósticos curtos no emulador quando necessários.
- Não jogar autonomamente para alcançar cada fala. Entregar ISO identificada, alteração exata, caminho, tela e critérios de observação ao usuário.
- Após validar amostra representativa e conhecer os limites de um mecanismo, avançar autonomamente em lotes compatíveis, com glossário, preservação de contexto/tokens e verificações automatizadas. Não pedir aprovação para cada texto.
- Tratar variantes estruturais, fontes não validadas e controles desconhecidos separadamente antes de expandir o mecanismo.
- Manter lotes reversíveis e manifestos por versão; gerar versões consolidadas para testes periódicos, sem acumular ISOs redundantes.
- Uma validação visual pendente não impede investigações e melhorias técnicas independentes e seguras.
- O trabalho de desenho das fontes está em `docs/fontes-v002.md`; o perfil v002 é experimental e separado do perfil v001 usado pela reinserção. Não declarar o espaçamento resolvido por uma mudança de bitmap.
- O perfil experimental de espaçamento v003 está em `docs/espacamento-v003.md`: mantém bitmaps v002 e altera somente a marca de largura dos 18 códigos PT-BR no cache. Testes de instruções não equivalem a validação visual; não promover automaticamente esse patch do ELF à ISO de desenvolvimento ou às receitas v004.
- O usuário autorizou avançar assumindo provisoriamente os caracteres corretos. O piloto contextual de 26 registros está em `docs/piloto-inicial-v001.md` e `translations/piloto-inicial-v001.json`, com glossário em `docs/glossario.md`. A premissa não equivale a validação visual. Construir pelo perfil explícito de `tools/build_translation_pilot.py`; o comando legado v004 continua usando fontes v001. Textos originais e revisões bilíngues ficam somente em `work/`.
- Prioridade atual: avançar em lotes maiores por cenas/regiões, com tradução contextual, validação local e uma ISO consolidada por lote. O Codex decide a ordem técnica sem perguntar qual recurso traduzir primeiro. O lote atual está em `translations/regiao-inicial-v022.json`; consultar `docs/regiao-inicial-v022.md`. Preservar as receitas anteriores; revisões ficam no filho, com IDs explícitos e comparação dos demais registros; a v022 tem 7.231 registros e mantém 349 adiamentos, sem liberar controles opacos. Preservar nomes e enganos intencionais como Dr. Martin na fala de Biff.
- Regras de tradução do usuário: preservar Hunter e Soldier; mecânico pode ser traduzido. Preservar personagens, tanques, cidades, procurados/wanted e nomes únicos de equipamentos, motores, componentes e inimigos. Locais genéricos podem ser traduzidos, exceto a primeira cidade, que fica em inglês. Traduzir junk como sucata, não lixo; manter expressões/risadas e empréstimos usuais como punk e upgrade. Adiar itens/inimigos se o espaço criar dificuldade. Contexto e naturalidade têm prioridade; nunca omitir artigos para caber. Glossário em `docs/glossario.md`, verificações em `translations/politica.json`.
- Manter no máximo dez ISOs de trabalho sob `work/`; `tools/iso_retention.py` remove as mais antigas elegíveis antes de novas construções. Manter as dez imagens geradas mais recentes por data, sem fixar experimentos antigos, conforme esclarecimento do usuário. Não tocar na ISO original, links, arquivos desconhecidos ou recursos de recuperação. Preservar receitas e relatórios quando uma ISO antiga for removida.
- Testes com ISOs fictícias devem simular a retenção global e executar remoções reais somente em raízes temporárias isoladas. Consultar `reports/iso-retention-test-isolation.json`. A ISO experimental ASCII v001 foi removida antecipadamente por uma contagem de fixture já corrigida; plano e relatório históricos foram preservados.
- A receita e os relatórios do experimento do diário permanecem preservados; sua ISO participa da retenção das dez mais recentes, mesmo sem confirmação visual. O piloto atual de diálogos é a fala sobre tornar-se Hunter.

- Exceção expressamente autorizada pelo usuário: map.msg.1df8bec0 recebe somente nao (ASCII 6E 61 6F), por caber no slot de três bytes. Não remover acentos de outras falas. Preservar a exclusão dessa exceção na fonte de aliases; retomadas de adiamento exigem resume_deferred e alvo explícito no filho.

- O preparador permite ampliar o intervalo por --start-offset ou --end-offset (exatamente um). Ao acrescentar offsets anteriores, comparar todo o recorte anterior por identidade e metadados, sem assumir que ele continua no início da lista ordenada.

- A v021 abrange o catálogo conhecido de 7.231 registros do MAP.MCT, sem comprovar todo o jogo. Auditar preservados com `Auditar-Traducao.cmd` e consultar `docs/auditoria-cobertura.md`; categorias de nomes/expressões são sugestões conservadoras, não aprovação de tradução ou edição. Não promover automaticamente candidatos nem modificar lotes anteriores sem revisão contextual.

- A v022 revisa somente os 31 títulos listados em `reviewed_changes`. Consultar `docs/escolhas-nomeadas-investigacao-v001.md`: o caminho da terceira string até o método de rótulo foi conferido no ELF original, mas smnn/2snm continuam bloqueados no compilador legado. Uma liberação futura exige política opt-in de slots fixos, rótulo imutável e testes próprios; controles opacos e bytes nativos não foram liberados.


## Continuidade v023 — escolhas nomeadas

- Lote atual: `translations/regiao-inicial-v023.json`, manual `docs/regiao-inicial-v023.md`: 5.758 alterados de 7.231; 258 adiados. Substitui a indicação de lote atual v022 acima; as descrições históricas permanecem válidas.
- A política opt-in `fixed-record-named-choice-slots-v005` está documentada em `docs/reinsercao-v005.md`. Autoriza somente corpo e opções de smnn/2snm nos slots originais, após hash e 22 verificações de instruções do ELF original. Rótulo, cauda, cabeçalhos e offsets imutáveis; sem repack dessas famílias. A política v004 continua bloqueando esses registros.
- Não liberar controles opacos nem bytes nativos. A regressão compara integralmente a v022, preservando suas 5.667 traduções. Os 91 IDs retomados são explícitos; validação binária não comprova execução visual.


## Prioridade tipográfica — layout v004

- O usuário reprovou os acentos em capturas de Nina em 22/10/2026; a premissa anterior de caracteres corretos não representa aprovação visual. Priorizar essa correção antes de ampliar a tradução.
- Consultar `docs/layout-v004.md`: o cache v003 não corrigia a largura/margem/bearing/avanço da rotina em `0x3E520`. O experimento opt-in `ptbr-layout-v004` preserva bitmaps v002 e os textos v023, fazendo somente os 18 códigos PT-BR herdarem métricas ASCII da letra-base. Retorna o código acentuado e consome os mesmos dois bytes.
- Testar por `Testar-Acentos-Corrigidos.cmd`; não promover à ISO de desenvolvimento ou substituir silenciosamente o perfil histórico. O teste de instruções não equivale a validação visual no PCSX2. Não afinar/redimensionar bitmaps para compensar um erro de escala do layout.


## Retorno visual e desenho individual v005

- O usuário testou v004 e confirmou que o alargamento persistiu. Não considerar aquela correção suficiente ou visualmente validada.
- Consultar `docs/layout-v005.md`: existe outro caminho em `0x3E2E0`, com largura/avanço independentes. O perfil opt-in `ptbr-layout-v005` combina cache v003, layout v004 e desenho individual v005; mantém códigos do cache e bitmaps v002. Usa a tabela adjacente v004, vinculada por hash. A validação visual continua pendente.
- `Testar-Acentos-Corrigidos.cmd` passa a abrir a ISO v005 separada. Pacote de células editáveis em `work/fontes-editaveis-ptbr.zip`; ferramenta `tools/edit_font_pack.py`. PNGs/GFI/referências ficam somente em work/, sem envio ao Git. A importação cria cópias e não altera automaticamente ISO ou fonte original.


## Aprovação visual v005

- Em 22/10/2026, após a entrega v005, o usuário confirmou: “ficou perfeito, combinou muito bem com o modelo”. Considerar o resultado visual aprovado no contexto das falas de Nina apresentado; não generalizar para todos os caracteres/fontes/menus. Evidência separada em `reports/layout-v005-visual-user.json`.
- O iniciador principal aponta para a imagem corrigida `work/fontes-layout-v005/MetalSaga-ptbr-layout-v005.iso`, com os textos v023. Não há necessidade de outra ISO somente para trocar o nome.
- Usar explicitamente `--layout-profile ptbr-layout-v005` nas próximas construções consolidadas. Preservar o padrão histórico das receitas antigas; não voltar silenciosamente ao perfil sem correção. O construtor mantém o default antigo para reprodução histórica. Não alterar a ISO de desenvolvimento legada sem compatibilizar seu perfil.


## Continuidade v024 — controle B15 e plano de conclusão

- Lote atual: `translations/regiao-inicial-v024.json`, manual `docs/regiao-inicial-v024.md`: 5.790 alterados de 7.231; 226 adiados (212 opacos e 14 nativos). Acrescenta somente 32 registros da cena de construção/reforma de tanques; preservar integralmente as traduções v023.
- A política opt-in `fixed-record-b15-preserved-slots-v006` reconhece somente `%B$15`, com prova do leitor/dispatch/handler no ELF original. Não liberar outros comandos por semelhança. Registros B15 exigem slots e segmentos sem crescimento em bytes frente à própria origem, além dos limites anteriores; comandos, valores e sequência imutáveis. Ver `docs/controles-b15-v006.md`.
- A receita v024 vincula `layout_profile: ptbr-layout-v005`; o construtor usa esse perfil sem flag adicional e recusa override incompatível. Receitas antigas sem o campo mantêm reprodução histórica. Não alterar esse vínculo para voltar às fontes/layout anteriores.
- Plano de trabalho em `docs/plano-conclusao.md`; próxima família a investigar é `%$1`, ainda bloqueada. Triagem por grupos em `tools/plan_remaining_texts.py`; spans do lexer não provam gramática ou semântica. Os 158 preservados têm 112 combinações distintas, sem decisão automática de tradução.

## Continuidade v025 — números variáveis e teste em save corrido

- Lote atual: `translations/regiao-inicial-v025.json`, manual `docs/regiao-inicial-v025.md`: 5.821 alterados de 7.231, com 195 adiados (181 opacos e 14 nativos). Acrescenta somente 31 IDs explícitos, preservando integralmente as 5.790 traduções da v024.
- Política opt-in `fixed-record-numeric1-preserved-slots-v007`: herda escolhas nomeadas e B15, acrescentando somente `%$1` inteiro. Conferir `docs/controles-numericos-v007.md` e `reports/controle-numerico-v007-evidence.json`. O handler distingue f minúsculo, que continua bloqueado; não liberar outros índices ou sintaxes por semelhança. Slots fixos, sem crescimento por segmento, controles imutáveis e mesmos limites anteriores. Lexer e fingerprints históricos não mudam.
- Manter `layout_profile: ptbr-layout-v005`. Não substituir o perfil de acentos aprovado ao construir novas ISOs. Próximo grupo exclusivo a investigar: `%N$3` (19 registros); triagem em `reports/plano-pendencias-v003.json`.
- O usuário informou que Dr. Palm está distante no save e pediu validação conjunta em uma passagem contínua. Não exigir que alcance a cena para continuar tradução e ferramentas. Acumular roteiro e pendências visuais por versão; não declarar execução no PCSX2 sem realizá-la. O roteiro v025 inclui preços, ônibus, hospedarias e construção de tanques.

## Continuidade v026 — variável 15 e nomes de tanques

- Lote atual: `translations/regiao-inicial-v026.json`, manual `docs/regiao-inicial-v026.md`: 5.838 traduções, 177 adiados (163 opacos e 14 nativos), preservando integralmente as 5.821 traduções v025. Dos 18 IDs retomados, somente 17 mudam bytes; `map.supr.01deb784` permanece intacto. Não contar preservação como tradução.
- Política opt-in `fixed-record-numeric15-preserved-slots-v008`: herda v007 e reconhece somente `%$15` inteiro, após evidências do mesmo leitor/handler e execução limitada do leitor para variável 15. Ver `docs/controles-numericos-v008.md`. f minúsculo, outros índices e controles desconhecidos continuam bloqueados. Slots, orçamento original por segmento, tokens e rótulos permanecem vinculados; não relaxar para caber.
- O campo `preservation_decisions` da receita é herdado e exige registros inalterados, existentes e não adiados; o compilador rejeita decisão inconsistente. O marcador com F literal está preservado assim. A categoria heurística de revisão tem 159, incluindo esse marcador já decidido; os outros 158 mantêm a situação anterior.
- Os 19 `%N$3` são nomes de tanques e foram preservados por decisão contextual. Ver `docs/n3-preservacao-v001.md` e `reports/n3-preservation-v001.json`. Continuam tecnicamente adiados porque N não foi liberado para edição. Não repetir a investigação nem traduzir esses nomes para aumentar a contagem. O lookup parcial não comprova identidade canônica de personagem/cena.
- Próximo grupo: `%T$0` (18), depois `%I$0` (14), conforme triagem em `reports/plano-pendencias-v004.json`. Manter layout v005 e o teste visual conjunto no save corrido; não pedir navegação imediata até Dr. Palm.

## Continuidade v027 — despedidas T0

- Lote atual: `translations/regiao-inicial-v027.json`, manual `docs/regiao-inicial-v027.md`: 5.856 traduções, 159 adiados (145 opacos e 14 nativos). Acrescenta somente 18 despedidas, preservando integralmente as 5.838 traduções v026, os nomes N3 e a decisão de preservação do marcador F.
- A política opt-in `fixed-record-t0-preserved-slots-v009` herda v008 e acrescenta somente `%T$0`. Ver `docs/controle-t0-v009.md` e `reports/controle-t0-v009-evidence.json`. O handler, dois accessors, stride e lookup foram conferidos por instruções originais com memória simulada; não inferir identidade canônica do tratamento Mr./sr. Não liberar outros índices, N ou I por semelhança.
- Registros com T0 exigem slots e nenhum crescimento por segmento; tokens, ordem, quebras, spans, rótulos e limites anteriores permanecem vinculados. Não alterar o lexer histórico ou os fingerprints. Manter o layout v005 aprovado nas falas de Nina.
- Próximo alvo previsto: `%I$0` (14). A triagem v005 também agrupa 22 `%N$0`, pois combinações com T0 agora se unem; isso não comprova edição segura. Não repetir N3 nem tratar preservados como traduções. Teste visual continua acumulado para o save corrido.

## Continuidade v028 — equipamento e presentes I0

- Lote atual: `translations/regiao-inicial-v028.json`, manual `docs/regiao-inicial-v028.md`: 5.870 traduções, 145 adiados (131 opacos e 14 nativos). Acrescenta somente 14 registros, preservando integralmente as 5.856 traduções v027, os nomes N3 e a decisão do marcador F.
- Política opt-in `fixed-record-i0-preserved-slots-v010`: herda v009 e reconhece somente `%I$0`. Ver `docs/controle-i0-v010.md` e `reports/controle-i0-v010-evidence.json`. Handler, leitura da variável 0, base e stride 128 foram conferidos por instruções originais com memória simulada. Não inferir item de ID zero, fonte S_PACK comprovada, terminadores/limites da tabela ou edição autorizada desses registros de 128 bytes.
- Slots sem crescimento por segmento; comandos, índices, quebras, spans, rótulos e limites anteriores imutáveis. Preservar os nomes resolvidos e únicos, risadas e expressões. Não liberar I1/I15, outros índices ou misturas opacas por semelhança. Manter lexer histórico, fingerprints e layout v005.
- Próximo alvo: `%N$0` (22), incluindo recebimento de veículos, tutorial de Drive e hospedagem. É distinto dos 19 nomes N3 preservados; não repetir N3 para aumentar a contagem. Preservar o nome Drive no tutorial enquanto corresponder à interface ainda não traduzida. Teste visual continua acumulado para o save corrido; seis novos avisos conservadores de largura estão listados no manual v028.

## Continuidade v029 — hospedagem e nomes indiretos N0

- Lote atual: `translations/regiao-inicial-v029.json`, manual `docs/regiao-inicial-v029.md`: 5.892 traduções, 123 adiados (109 opacos e 14 nativos). Acrescenta somente 22 registros, preservando integralmente as 5.870 traduções v028, os nomes N3 e a decisão do marcador F.
- Política opt-in `fixed-record-n0-preserved-slots-v011`: herda v010 e reconhece somente `%N$0`. Ver `docs/controle-n0-v011.md` e `reports/controle-n0-v011-evidence.json`. Handler, variável 0, tabela de ponteiros e delay slot foram conferidos com instruções originais em memória simulada. Não confundir com N0 literal, inferir entidade canônica, limites da tabela ou liberar N3/N1/variantes por semelhança.
- Slots sem crescimento por segmento; tokens, ordem, quebras, spans, rótulos, cabeçalhos e limites anteriores imutáveis. A frase de posse de Dr. Palm associa apelido e tanque sem inverter B15/N0. Manter Drive no tutorial enquanto corresponder à interface. Preservar huh? e risadas. Layout v005, lexer histórico e fingerprints mantidos.
- Próximo alvo: `%$0` e `%$2`, 12 registros exclusivos cada, pela triagem v007. Verificar argumentos e sufixos antes de ampliar; f minúsculo continua bloqueado. Não repetir N3 nem contar preservação como tradução. Testes visuais permanecem acumulados para o save corrido.


## Prioridade atual — interface v001

- Por orientação do usuário, pausar as pequenas pendências de MAP.MCT, inclusive %$0/%$2. Ordem: HUD/Satcom/mensagens/menus, depois itens e, por último, fragmentos restantes. Não repetir as investigações N3 nem alterar a base v029 para inflar contagens.
- Primeiro lote de interface: `translations/interface-v001.json`, 88 strings do ELF, sobre `translations/regiao-inicial-v029.json`. Manual em `docs/interface-v001.md`. Manter `ptbr-layout-v005`. Sem realocação: tamanho máximo igual à string original, endereço e NUL final originais preservados; validar hashes, referências, aliases internos, parâmetros printf, delimitadores e espaços iniciais. O catálogo de 4.297 strings inclui debug e nomes técnicos; não é catálogo aprovado de interface.
- `Preparar-Interface.cmd` valida; `Testar-Interface.cmd` e o padrão de `Iniciar-Teste.cmd` apontam para `work/interface-v001/MetalSaga-ptbr-interface-v001.iso`. O alias region continua sendo v029. Não confundir a validação binária com teste visual dessa interface.
- FBS_DATA.SDA contém rótulos rasterizados de batalha e Satcom (entradas 0 e 2 confirmadas por preview). `tools/interface_textures.py` exporta somente seis previews inspecionados de FBS_DATA/F_COMMON; não importa PNG nem altera paletas/alpha/arquivos originais. Preparar round-trip próprio antes de editar essas texturas. Não declarar From/Title/Playing Time ou conteúdo das mensagens/DIARY.DAT traduzidos pelo lote ELF.


## Alpha preservada e interface v002 — 23/10/2026

- Por pedido explícito do usuário, preservar permanentemente a última versão disponível no início da rodada: interface v001 + diálogos v029 + layout v005. Cópia independente somente leitura em `dist/alpha-v001/MetalSaga-ptbr-alpha-v001.iso`, SHA-256 `f928e0c375db669e16f078d6a0b7a4bd053ab3e933e7732e3772f14beb00bc58`; manifesto em `reports/alpha-v001.json`, manual `docs/alpha-v001.md`. Não apagar, sobrescrever nem incluir essa cópia na retenção. Exceção expressa: dez ISOs de trabalho sob work/, além da alpha fora dessa pasta. Não versionar a ISO.
- Lote atual de interface: `translations/interface-v002.json`, 273 strings (185 novas), preservando as 88 entradas v001 e todos os diálogos v029. Manual `docs/interface-v002.md`. `Preparar-Interface.cmd` valida v002; `Testar-Interface.cmd` e o padrão de `Iniciar-Teste.cmd` apontam para `work/interface-v002/MetalSaga-ptbr-interface-v002.iso`. A alpha continua sendo v001; não renomear imagens futuras como se fossem o mesmo snapshot.
- Avançar em lotes amplos por conjuntos de telas; testes visuais periódicos consolidados, sem solicitar validação por string. Não interpretar a avaliação do usuário sobre margem de erro como dispensa de testes binários ou prova visual de formatos novos.
- O compilador ELF preserva também espaços finais; não perder alinhamento/concatenação. Estatísticas em 0x32C6C0 e cabeçalho de veículos em 0x32C810 estão localizados, mas têm wrapper anterior diferente de literal NUL isolado; continuam bloqueados. Nomeação em 0x33B3B8 sem referência segura também fica pendente. Não relaxar o catálogo automaticamente. Texturas, Memory Card, mensagens/ajuda/diário seguem dentro da prioridade interface, antes de itens e dos fragmentos MAP.

## Cópia para OneDrive — somente mediante solicitação

- Destino autorizado pelo usuário: `C:\Users\Kernell\OneDrive\METAL SAGA`. Exceção restrita aos limites do workspace para entregar uma cópia da ISO, permitindo testes em outro computador.
- Executar somente quando o usuário solicitar explicitamente a cópia. Não copiar automaticamente após builds, commits ou ao retomar o projeto. Esta configuração do destino não é uma solicitação de transferência.
- Escolher a ISO consolidada de desenvolvimento mais recente com construção concluída e relatório válido; não selecionar a alpha nem a ISO original por engano. Não assumir que a imagem legada chamada desenvolvimento é a mais recente: verificar receitas, relatórios e iniciador atual.
- Antes de copiar, verificar ausência de transações/journals pendentes relativos à imagem, conferir tamanho e SHA-256 integral contra o relatório da construção e recusar fontes parciais, em construção ou inconsistentes. Se houver transação pendente, recuperar pelo mecanismo próprio e revalidar antes da transferência.
- Copiar, nunca mover ou modificar a origem do projeto. Substituir a cópia anterior quando necessário, sem apagar arquivos alheios no destino. Preferir arquivo temporário de destino e substituição somente após conferir tamanho e SHA-256 da cópia; conferir também o arquivo final. Não alterar configurações do OneDrive ou do Windows.
- Informar versão, origem, destino e resultado da verificação. Integridade da cópia local não comprova conclusão do upload/sincronização em nuvem; não declarar sincronização concluída sem evidência.
