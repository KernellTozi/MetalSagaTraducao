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


## Continuidade de interface v003 — sistema e diário

- Lote atual: `translations/interface-v003.json`, manual `docs/interface-v003.md`: 473 campos acumulados, 200 novos (98 mensagens NDATA, 100 campos DIARY e dois literais ELF). Preserva integralmente as 273 entradas v002, MAP v029 e layout v005. São 13.949 bytes de origem novos, 5,08 vezes a rodada anterior; não comparar porcentagens do jogo por contagem de campos.
- `Preparar-Interface.cmd` valida v003; `Testar-Interface.cmd` e `Iniciar-Teste.cmd` usam `work/interface-v003/MetalSaga-ptbr-interface-v003.iso`. Alpha v001 permanece intacta em dist/, fora da retenção. Sem cópia automática para OneDrive.
- A política opt-in `ndata-crlf-and-diary-fixed-v003` está em `tools/interface_resources.py`. Libera somente entradas NDATA 186 (0x110D800, 4.951 bytes, 79 linhas) e 200 (0x1344800, 1.083 bytes, 20 linhas), após conferir descritores e leitor do ELF original. Reempacota CRLF no mesmo intervalo lido, sem alterar SDA/ELF descritores, índices, controles ou padding externo. Limite de 511 bytes por linha; somatório não pode exceder o tamanho lido. Preservar ordem de pipes e $MD$/$MP$/$MEM$/$HDD$. O contador original foi executado em memória simulada; isso não executa o leitor inteiro nem o jogo.
- DIARY mantém 68 registros/136 campos e slots fixos; v003 altera 65 corpos/35 títulos. Corpos 16 e 31 nativos e o silêncio do corpo 62 permanecem intactos. Não liberar bytes nativos nem os comandos N do MAP por semelhança com os tokens %N do diário. Nomes e material sucata passam pela política terminológica; nomes próprios exigem caixa exata neste recurso para distinguir junkyard genérico da cidade Junkyard. Preservar nomes únicos de lentes/equipamentos.
- `two-proven-format-literals-v003` permite somente 0x32C6C0 e 0x32C810, com referências diretas ao formatador e janelas vinculadas por hash. Os bytes anteriores não são consumidos pelos dois chamadores comprovados: manter intactos sem presumir um wrapper. Não relaxar a regex/catálogo legado nem liberar nomeação 0x33B3B8 automaticamente.
- Exportação local: `python tools/interface_resources.py --output work/interface-recursos-novo.json`. Originais, revisão bilíngue e bytes exportados somente em work/. Evidências em `reports/interface-v003-format-evidence.json`. O próximo conjunto continua sendo ajuda/mensagens e textos gráficos de interface, antes de itens e dos fragmentos MAP. Validação visual desses novos contextos permanece pendente para teste consolidado do usuário.


## Continuidade interface v004 — ajuda e categorias de armamento

- Lote atual: `translations/interface-v004.json`, base `translations/regiao-inicial-v030.json`, manual `docs/interface-v004.md`: 519 campos acumulados (277 ELF, 98 sistema, 100 diário e 44 páginas de ajuda). Preservar layout v005, alpha e receitas históricas. Os oito IDs MAP revisados constam de `reviewed_changes`; não há aumento das 5.892 traduções nem liberação de controles opacos.
- Regra expressa do usuário: manter **MAIN, SUB, SE** sempre que forem categorias de armamento/ataques dos tanques, incluindo referências em frases. Não traduzir como principal/secundária/especial. Política opt-in `preserve-main-sub-se-v001`; revisar também palavras em texturas quando editáveis, sem confundir imagens ainda originais com strings traduzidas.
- Ajuda: política `ndata-html-help-fixed-load-v004`, índices 127,129,131–172 de NDATA; pares do ELF em 0x322368, parser e carregador vinculados por hash. Preservar tags, atributos, números, %% e quebras; tamanho máximo é o intervalo carregado, não o extent SDA. Não liberar outros índices automaticamente. O contador auxiliar avança por bytes: verificar quebras/rolagem de textos acentuados visualmente, sem alterar fontes preventivamente.
- `Preparar-Interface.cmd` valida v004 e `Testar-Interface.cmd`/`Iniciar-Teste.cmd` apontam para a ISO v004. Teste visual dessas páginas permanece pendente. Próxima etapa: textos gráficos da interface e mensagens ainda não catalogadas, antes de itens e fragmentos do MAP.
- Ferramenta de entrega explícita: `tools/copy_onedrive.py --build-dir work/interface-v004 --report reports/onedrive-interface-v004.json`. Não chamar automaticamente em futuras rodadas. Conferir relatório, tamanho/hash, ausência de journal/partial e cópia final; não afirmar upload completo pela cópia local.


## Continuidade interface v005 — índice e transporte gráfico

- Lote atual: `translations/interface-v005.json`, base MAP v030; 573 campos alterados (519 preservados + 53 rótulos do índice da ajuda + um literal MAIN/SUB/SE de status). `Preparar-Interface.cmd` valida v005; `Iniciar-Teste.cmd` e `Testar-Interface.cmd` usam `work/interface-v005/MetalSaga-ptbr-interface-v005.iso`. Layout v005 e alpha imutáveis.
- Política `ndata-help-index-fixed-load-v005`: somente índice 173, offset 0x10E4800 e 798 bytes carregados, com instruções do leitor/parser vinculadas por hash. 12 categorias e 44 tópicos, prefixos de 4 dígitos ou TAB+3 dígitos, vírgula e LF. Preservar todos os valores, repetições, ordem e vínculo às 44 páginas. Redistribuição somente dentro da carga de 798 bytes; nunca usar folga do extent. Ver `docs/interface-v005.md`. Aprovação visual pendente; não solicitar navegação imediata para continuar.
- `tools/interface_texture_pack.py` exporta/importa somente as seis texturas inspecionadas das entradas 0–2 de FBS_DATA/F_COMMON. PNG indexado P com paleta RGB e alpha originais imutáveis; alterações somente em índices de pixels, em cópias work/. Rejeitar conversão RGB/RGBA, quantização, mudança de dimensões/paleta/manifesto. Preservar nibbles não utilizados, headers, tails e demais entradas. Ver `docs/texturas-interface-v002.md`. Round-trip real foi executado, mas não há desenhos traduzidos nem importação de texturas à ISO.
- Próxima etapa: mapear recortes/UVs dos rótulos rasterizados e preparar arte PT-BR com reinserção controlada; conteúdo das mensagens continua pendente de localização. Não considerar a busca ASCII negativa em FD_POST prova de ausência de textos. Não retomar fragmentos MAP nem itens enquanto a interface tiver prioridade.
- Não repetir cópia OneDrive sem novo pedido explícito: a cópia verificada anterior é interface v004.


## Continuidade interface v006 — primeiro lote gráfico

- Lote atual: `translations/interface-v006.json`, base MAP v030, layout v005; preserva 573 campos de texto e acrescenta 40 ocorrências gráficas (26 variantes Satcom, dez comandos de batalha, quatro cabeçalhos). Total compilado 613; não confundir variantes repetidas com palavras únicas. Receita gráfica `translations/interface-graphics-v003.json` vinculada por hash.
- `fbs-ganm-native-glyph-labels-v003` libera somente pixels das texturas FBS_DATA 0/2/3, em recortes explicitamente revisados de GANM 5/7/8. Preservar header, paleta/alpha, GANM, bordas, índices SDA, offsets e dimensões. Não ampliar o pacote histórico de seis texturas por consequência. Manual: `docs/graficos-interface-v003.md`; execução visual pendente.
- Compor os rótulos localmente dos glifos do jogo, com bitmap v002 conferido e tabela ASCII de origem vinculada. GFI e layout de execução permanecem idênticos à v005. Máscaras têm hash; não aceitar drift silencioso do rasterizador. Margens internas fixas e largura mínima 0,72; altura 16/12 constante. Fundo interior usa a cor original; somente essa área pode perder a textura de fundo.
- MAIN/SUB/SE preservados. O cabeçalho de mensagens “Sub” vira Assunto por contexto distinto. Item fica como está. Drive/Remote permanecem iguais para manter tutoriais/ajuda consistentes; alterações futuras exigem revisão conjunta. Os dois rótulos riscados de Música/Jogos, pequeno PlayingTime, opções gráficas, título/New Game/Load Game e nomeação gráfica continuam pendentes.
- `Preparar-Graficos.cmd` compõe e confere previews em work/ sem ISO. `Preparar-Interface.cmd` valida v006; `Testar-Interface.cmd` e `Iniciar-Teste.cmd` abrem a v006. Não solicitar teste imediato para continuar engenharia independente.
- O usuário reafirmou: OneDrive somente por novo pedido. A última entrega contém interface v005 e PCSX2 portátil, com BIOS/cartões/configurações copiados; os originais foram preservados. Não sobrescrever essa entrega automaticamente. Alpha fora de work/ continua permanente; manter dez ISOs de trabalho.


## Correção tipográfica Satcom v007

- O usuário reprovou a diferença de fonte da v006 em relação a Remote: os GFI de diálogo são outra família. Não confundir “fonte do próprio jogo” com a fonte de um botão específico. Reproduzir o desenho e os pesos de cada família gráfica antes de ampliar seus rótulos.
- Lote atual: `translations/interface-v007.json` e `translations/interface-graphics-v004.json`, política `satcom-original-raster-typeface-v004`. Revisa somente os 26 rótulos do Satcom; 573 textos e outros 14 gráficos v006 permanecem iguais, assim como MAP v030 e layout v005. Ver `docs/interface-v007.md`.
- `tools/satcom_native_font.py` recupera 21 glifos do atlas original nas variantes clara/escura separadas. L/P/J/j/á/ú/ç são reconstruções explícitas de traços nativos, sem GFI para o Satcom. Não generalizar essa cobertura limitada para uma fonte inteira. Corpo de maiúscula 12 px, célula 18 px, espaçamento inteiro; resize e compressão são proibidos, overflow é recusado.
- Preservar Remote original, bordas, paletas/alpha, GANM e rótulos riscados. Receitas históricas v003/v006 continuam intactas; o dispatcher opt-in v004 delega somente esse perfil. Tipografia de batalha/cabeçalhos continua pendente de comparação própria. Previews inspecionados localmente não são validação visual no PCSX2 nem aprovação pelo usuário.
- Preparar-Graficos/Preparar-Interface e os iniciadores de teste passam a usar a correção v007. Continuar sem copiar para OneDrive até novo pedido explícito.


## Linha de base Satcom v008

- O usuário aprovou preliminarmente o desenho dos rótulos, mas reprovou o alinhamento entre letras na imagem da proposta v007. Isso não equivale a teste no PCSX2. A v007 foi interrompida antes do commit; manter suas receitas/ISO como referência, sem promover sua tipografia a aprovada.
- Lote atual: `translations/interface-v008.json`, receita `translations/interface-graphics-v005.json`, política `satcom-native-baseline-v005`; mantém 573 textos e 40 ocorrências gráficas (613 compiladas), MAP v030 e layout v005. Somente o posicionamento do Satcom muda. Ver `docs/interface-v008.md`.
- A origem vertical das palavras claras não coincide com a normal: Music 5→6, Config 6→5, Diary 4→5. Aplicar os ajustes de amostragem antes das construções/acento, separadamente por variante; a política v004 conserva reprodução histórica.
- Referência: Remote, corpo forte em linhas 3–14 de célula 18 (base 15 exclusiva), altura-x em 7–14. g/j/ç descendem até 17; acentos ficam acima. Não nivelar todos os topos nem todas as bordas inferiores. Não escalar as letras. Novos testes exigem linha de base, formas fortes e larguras idênticas dos glifos recuperados; perfil normal permanece igual.
- Iniciadores de gráfico/interface/teste usam v008. Previews e métricas não comprovam aparência em execução. Preservar a alpha, dez ISOs de trabalho e a regra OneDrive somente mediante solicitação. Ignorar `.codex-remote-attachments/` no Git.

## Continuidade gráfica — atlas de cinco conjuntos

- Após v008, preparação em lote de 69 texturas de RTITLE/FNAME_DT/F_COMMON/FD_POST/PASSWORD, com 13 GANM e dois registros desconhecidos FNAME_DT. Manual `docs/atlas-interface-v001.md`; evidências `reports/atlas-interface-v001.json`. A ISO atual continua v008; esta rodada não acrescenta traduções nem gera ISO.
- `Preparar-Atlas.cmd` gera previews RGB e PNGs indexados editáveis em diretório novo sob work/. `tools/interface_atlas_pack.py` reconstrói somente cópias locais dos cinco recursos, com hashes/manifesto/paleta/alpha/dimensões vinculados. Não é liberação de uso em ISO; manter o pacote histórico de seis texturas e as políticas gráficas anteriores intactos.
- `tools/explore_interface_atlases.py` registra retângulos/hotspots GANM e candidatos de textura por limites geométricos. Isso não comprova associação em execução; não inferir consumidor por adjacência SDA. FNAME_DT entradas 7/8 continuam desconhecidas e imutáveis.
- FD_POST foi inspecionado: cartazes/retratos e nomes rasterizados de procurados, preservados pela regra do usuário. Não confundir esse arquivo com correio; a origem do corpo das mensagens ainda é pendente. Próximo conjunto gráfico: título, depois senha/nomeação, preservando suas famílias visuais próprias. Não reutilizar GFI ou fonte Satcom automaticamente. A validação do usuário ainda será consolidada; não exigir teste imediato para continuar.

## Continuidade interface v009 — título

- Lote atual `translations/interface-v009.json`, MAP v030, layout v005. Preserva os 613 campos/ocorrências v008 e acrescenta três rótulos rasterizados da tela inicial: Novo jogo, Retomar, Instalar. Total 616, sendo 43 gráficos; não confundir contagem de campos com cobertura do jogo. Manual `docs/interface-v009.md`. Os iniciadores apontam para a ISO v009; alpha imutável e OneDrive somente por pedido.
- Política opt-in `title-native-raster-v006` e receita `translations/interface-graphics-v006.json` herdam a receita gráfica v005 por hash. Alterar somente pixels x<180,y<72 da textura RTITLE em 0x20; paleta/alpha, header, GANM, hotspots, seleção e demais pixels intactos. Fontes de execução, Satcom e outras texturas preservadas. Não reutilizar esse perfil como fonte geral.
- `tools/title_native_font.py` recupera treze letras da própria tela; V/J/R são reconstruções explícitas de traços nativos, sem resize. Aparência inspecionada em preview, com validação no PCSX2 pendente. Os três rótulos usam centralização nos recortes originais 180×24, sem modificar as métricas do motor.
- Consumidores e descritor ELF 0x2641C8 vinculados em `tools/title_graphics.py`. O GANM estático do título tem seis frames e zero animações; +8 é offset da tabela de frames, não stride. Stride 16 provém do shift no leitor de recortes. Não generalizar essa semântica para outros arquivos nem ampliar o parser histórico automaticamente.
- Próxima família gráfica: senha, depois nomeação, com desenho e consumidor próprios; conteúdo do correio segue pendente. Não voltar aos pequenos fragmentos MAP nem alterar nomes de procurados para aumentar contagens. O pedido de desligamento deste turno é pontual, não uma automação permanente.

## Continuidade interface v010 — textos de nomeação

- Lote atual `translations/interface-v010.json`, MAP v030 e layout v005. Preserva os 616 campos/ocorrências v009 e acrescenta quatro literais ELF: cabeçalho e três legendas; total 620. Manual `docs/interface-v010.md`. `Iniciar-Teste.cmd`/`Testar-Interface.cmd` abrem a v010; alias interface-v009 conserva acesso à anterior enquanto existir. Alpha e dez ISOs de trabalho preservadas; OneDrive somente por pedido.
- Política opt-in `name-entry-fixed-literals-v001` em `tools/name_entry_text.py`: somente 0x33B3B8 (cabeçalho) e 0x32A310/348/380 (legendas mistas). ELF e quatro janelas de consumidor vinculados por hash. O catálogo ASCII histórico permanece conservador; não liberar bytes nativos em geral.
- Legendas: editar somente spans ASCII reconhecidos em slots fixos, preencher folga dentro do span com espaços; preservar bytes 81 40, demais espaços, posições, comprimentos e NUL. Traduções INS./SEL./FIM/CANC./APAGAR revisadas. TITLE e BACK permanecem intactos até conferir semântica dos comandos; não adivinhar sair/apagar/tipo. Não editar a tabela de caracteres selecionáveis. Cabeçalho DIGITE SEU NOME preserva o slot/NUL final, com padding zero.
- O caminho do cabeçalho usa s2 salvo por distância maior que a janela do buscador; encaminha a1 via 0x20A368 para 0x20D608. Os três caminhos de legenda chegam ao mesmo consumidor. Inspeção e hashes não equivalem a execução visual. Próximo passo: esclarecer TITLE/BACK e continuar senha com fonte própria; correio continua pendente. Não repetir o desligamento pontual da rodada anterior.

## Continuidade interface v011 — R do título e assinatura

- O usuário reprovou o desenho do menu em captura da v010 e pediu “Traduzido por: Kernell Tozi”. A v011 corrige somente o glifo R da família do título e acrescenta essa linha. Não considerar os desenhos v009/v010 visualmente aprovados. `translations/interface-v011.json` preserva todos os textos v010, MAP v030 e layout v005; total 621 campos/ocorrências, sendo 44 gráficos. Manual `docs/interface-v011.md`.
- Política opt-in `title-credit-and-raster-v007` em `tools/title_credit.py`: herda por hash a receita gráfica v006, preserva todos os patches FBS e reorganiza somente os seis frames da textura RTITLE. Mantém tamanho dos arquivos/extents, paleta/alpha, cabeçalho GANM, contagens e código ELF. Esta é uma liberação específica de posições/UV/hotspots dos seis frames; o perfil histórico v006 mantém seus limites anteriores.
- Retomar passa a 256×128, hotspot 128,12, mantendo o centro e a posição do texto. A região intermediária é transparente; assinatura em x=247..392,y=430..443 no espaço virtual. As imagens de borda/fundo/fade preservam pixels, dimensões e hotspots. Não alterar vídeos ou substituir créditos oficiais. R revisado é opt-in em `title_native_font.alphabet(revised=True)`; receitas antigas conservam o R anterior.
- Limitação: assinatura pertence ao sprite Retomar e herda sua cor/visibilidade, podendo ficar cinza quando o botão estiver desabilitado. Previews geométricos não incluem o fundo real e não comprovam ausência de sobreposição com créditos oficiais. Exigir conferência visual da linha, estados do botão, bordas e R, sem declarar execução no PCSX2. Não promover esse transporte a repack genérico de atlas.
- `Iniciar-Teste.cmd`/`Testar-Interface.cmd` usam v011; alpha e dez ISOs de trabalho preservadas. Não copiar OneDrive nem repetir o desligamento sem novo pedido. As pendências TITLE/BACK, senha e correio permanecem para depois desta correção.

## Continuidade interface v013 — preservar a família do título

- Versão atual: `translations/interface-v013.json`, gráficos v009; 641 campos/ocorrências (44 gráficos), MAP v030 e layout v005. Iniciadores usam `work/interface-v013/MetalSaga-ptbr-interface-v013.iso`. Manual `docs/interface-v013.md`.
- A v012 foi reprovada visualmente pelo usuário: Arial Black descaracteriza o título; não reutilizar essa família nos botões. A assinatura GFI também foi reprovada. A captura v012 confirma sua exibição, sem aprovar aparência.
- `tools/title_authentic.py` preserva as letras nativas byte a byte e reconstrói somente V/J/R de traços originais. Um pixel entre células, nenhuma escala horizontal; NOVO JOGO usa 197 px dentro da borda. Frames 0/2 passam a 228×24, hotspot 114,12. Assinatura usa Arial Rounded MT Bold 14 px, contorno 1 px, fonte instalada e máscara vinculadas por hash. É aproximação aos créditos, não identificação da fonte oficial. Não versionar fontes/atlas/imagens.
- Ausência do crédito v011: a rotina ELF 0x393A0 usa 306+42*i para duas opções, levando a assinatura a y=448. Duas constantes normalizam esse caso para 296+34*i, igual ao menu de três opções; este permanece intacto. Crédito v013 em y=428..443. Ele ainda herda cor/visibilidade de Retomar e pode ficar cinza quando desabilitado; não declarar independência de cor resolvida.
- Correção de batalha herdada da v012: `battle-ptbr-half-cell-advance-v001`, função 0x8C0B8..0x8C2E0, somente os 18 pares PT-BR; avanço ASCII, mesmo glifo/consumo, sem alterar bitmaps. Execução limitada de instruções e testes binários não equivalem a teste visual. Não estender a outros códigos por semelhança.
- Três campos Soma restauram Total original através da lista cumulativa `restored_originals`; o comparador aceita somente essas restaurações explícitas. Acrescentadas 23 descrições/avisos de batalha, com MAIN/SUB/SE preservados. Demais textos v011 permanecem.
- O usuário escolheu realizar a conferência visual: não reabrir automaticamente PCSX2 nesta rodada. A v013 permanece pendente de aprovação visual; o boot curto v012 atingiu a abertura e foi encerrado antes da conferência do título pelo agente. Manter alpha/dez ISOs de trabalho; sem OneDrive ou desligamento nesta rodada.

## Arte completa do título — proposta v001

- O usuário pediu desenhar novas letras/palavras antes da aplicação, após identificar os remendos da v013. Proposta em `docs/arte-titulo-v001.md` e `reports/title-wordart-v001.json`: palavras completas geradas por image_gen a partir da referência original, sem colagem de glifos. Master/PNGs editáveis/pacote em `work/title-wordart-v001/`, fora do Git.
- `tools/prepare_title_wordart.py` prepara três linhas em células 228×24, proporções uniformes, corpo branco 16 px e paleta original preservada. PNG indexado usa alpha bruto PS2; usar o preview normalizado para avaliar a transparência em editores comuns. Quatro testes de preparação passaram.
- Esta é proposta artística, não fonte completa, reinserção ou teste no PCSX2. Nenhuma ISO foi criada/modificada; iniciadores continuam v013. Não promover a arte automaticamente a aprovada. Preservar o master local e seu hash; a preparação posterior é local e não usa IA/APIs.

## Interface v014 — aplicação da arte aprovada

- O usuário aprovou explicitamente a proposta v001 e autorizou aplicar. Versão atual: `translations/interface-v014.json`, gráficos v010; iniciadores apontam para `work/interface-v014/MetalSaga-ptbr-interface-v014.iso`. Manual `docs/interface-v014.md`. A aprovação é da arte; a aparência desta ISO no PCSX2 continua pendente de teste manual.
- `tools/title_wordart.py` aplica somente os três PNGs completos preparados, com hashes de arquivos/índices, ordem, dimensão P 228×24 e paleta RGB/alpha originais vinculados. Não redesenhar ou gerar outra imagem silenciosamente. Assets aprovados permanecem em `work/title-wordart-v001/`; conservar master e pacote para reprodução local.
- Única mudança frente à v013: pixels das três palavras em RTITLE. Frames/hotspots, assinatura, borda/fundo/fade, ELF, fontes, diálogos e demais textos permanecem idênticos. Células em (0,0), (14,128), (0,24); mudança fora dessas áreas é recusada. A assinatura ainda acompanha a cor de Retomar.
- Continuam 641 ocorrências de interface, MAP v030 e layout v005, sem novas traduções nesta rodada. Preservar alpha/dez ISOs; sem cópia OneDrive, navegação automática ou desligamento.

## Próxima prioridade — personagem e lojas

- Planejamento atual em `docs/proximas-etapas-interface.md`: fechar lacunas de personagem/inventário/equipamentos, depois lojas/serviços, veículos/batalha e demais interfaces frequentes. Tabelas de nomes/descrições de itens vêm depois; fragmentos MAP ficam por último. Defeitos que impeçam uso de menus/transações/progressão têm precedência.
- Já existem campos traduzidos nesses conjuntos; auditar receitas e catálogo por tela antes de acrescentar. Não declarar cobertura completa por grupo/contagem nem retraduzir o que já está pronto. Primeiro lote amplo pode reunir personagem/equipamentos e campos comuns de lojas cujo formato já seja comprovado.
- Esta rodada apenas documentou a ordem, sem traduções ou ISO nova. Continuar com lotes amplos, ferramentas locais, nomes protegidos e uma imagem consolidada por rodada relevante; testes visuais agrupados pelo usuário.

## Levantamento único — interface S_PACK

- `tools/plan_interface_menus.py` atualiza somente `work/planejamento-interface.json`, sem saídas por data. Evidências/resultados em `docs/proximas-etapas-interface.md`; seis testes em `tests/test_menu_planning.py`. Reduzir arquivos intermediários nas próximas rodadas, preservando receitas históricas, evidências e recuperação.
- Tabela UI em S_PACK: SDA 0x35000, entrada 0 em 0x35070, tamanho 0x2000, count 378, offsets relativos e cabeçalho 0x5EC. São 317 alvos únicos, 61 aliases, 315 ASCII e dois nativos (826E/8277). Todos continuam identificados mas não editáveis até provar leitor/buffers/consumidores. Os 11 bytes não ocupados não são capacidade autorizada. Preservar todos os IDs/aliases, NULs e bytes originais; não confundir os códigos nativos com extensão PT-BR.
- Prioridade técnica agora: tabela de interface S_PACK para inventário e lojas/serviços; tabelas gerais de itens continuam posteriores. Mensagem 0x35CE7 contém composição `%screased` e exige revisão dos argumentos/gramática além dos tokens. Não liberar repack por semelhança com outros formatos.
- Literal multilinha de personagem em ELF 0x32B6A0 (51 bytes), referência candidata 0x118A20/0x118A28: identificado, sem política de edição. Não relaxar catálogo/regex. Levantamento cruza 4.299 campos ELF (4.297+2), com 298 já traduzidos; 22 candidatos de referência a revisar e 23 bloqueados não equivalem a strings aprovadas ou telas completas.
- Próxima entrega de tradução deve reunir os mecanismos comprovados em um lote amplo, sem ISO por tela. Esta rodada não traduziu nem alterou a ISO v014.

## Interface v015 — lote consolidado de inventário e lojas

- Atual: `translations/interface-v015.json`, sobre MAP v030/layout v005 e arte v014. Iniciadores usam `work/interface-v015/MetalSaga-ptbr-interface-v015.iso`. Acrescenta 278 textos únicos da UI S_PACK (333 IDs) e um formato ELF de personagem: 920 campos/ocorrências acumulados. Manual `docs/interface-v015.md`, único relatório resumido `reports/interface-v015.json`.
- Opt-in `spack-ui-counted-alias-preserving-repack-v001` em `tools/spack_ui.py`: somente 0x35070..0x37070, mesmo tamanho de 8.192 bytes, 378 IDs, 317 alvos, 61 aliases preservados. Offsets relativos são reconstruídos dentro da tabela; SDA pai, arquivo/extents e outros recursos imutáveis. Resultado ocupa 7.956 bytes. Hashes de origem, janelas de instruções, controles printf/pipes, prefixo `%%I%02d%s`, números e espaços de concatenação vinculados. Guarda por entrada `max(original,31)` é conservadora, não prova geral de buffer. Não liberar outras tabelas S_PACK por semelhança.
- A carga da entrada raiz 1/SDA interna 0 e o ponteiro VA 0x475B18 foram rastreados. Probes de instruções originais verificam os 378 IDs, aliases e contador de comprimento; o caminho comum observado aloca pelo comprimento e converte pipe para LF. Isso não executa alocador/I/O/GPU nem comprova todos os consumidores. A v015 aguarda teste manual no PCSX2; não navegar autonomamente.
- 39 alvos permanecem preservados: nomes/termos, símbolos/valores estáveis, nativos 826E/8277, marcador e composição `%screased` com `in`/`de`. Não traduzir os três componentes por substituição simples. Grand Master e Rent-a-Tank conservam proteção nominal; Drive acompanha tutoriais existentes. Tabelas gerais de nomes/descrições de itens não foram alteradas.
- `character-status-single-multiline-v001` autoriza somente ELF 0x32B6A0, 51 bytes, consumidor 0x118A20..0x118A88; nova string 50 bytes, mesmos parâmetros/quebras/NUL. Catálogo/regex geral intactos; Coat continua dependente de contexto.
- `--compact-output` no construtor mantém apenas ISO e relatório por construção, com receitas Unicode/caminhos/hashes preservados; modo histórico sem flag continua reproduzível. Preparar-Interface usa a flag. O planejamento atualiza o mesmo `work/planejamento-interface.json`, agora sobre v015. Evitar duplicar relatórios/rascunhos por tela; preservar todo o histórico anterior.
- 87 testes de interface e seis de planejamento passaram. Delta integral contra v014: 6.818 bytes em dois patches; fonte, título, demais textos e diretório ISO idênticos. Manter alpha, dez ISOs de trabalho e OneDrive/desligamento somente por novo pedido.

## Interface v016 — correio Satcom e procurados

- Atual: `translations/interface-v016.json`, manual `docs/interface-v016.md`, relatório consolidado `reports/interface-v016.json`. Preserva integralmente a v015, MAP v030/layout v005 e arte v014. Acrescenta 119 campos: 41 corpos e 38 assuntos de mensagens, mais 40 descrições de procurados. Total 1.039 ocorrências de interface. Iniciadores apontam para `work/interface-v016/MetalSaga-ptbr-interface-v016.iso`.
- Política opt-in `spack-satcom-mail-wanted-bounded-v001`, em `tools/spack_satcom.py`. Somente entradas 13/14 do SDA S_PACK em 0x35000: mail 0x86700/0x1F10/count41, wanted 0x88610/0x1960/count40. Tabelas/offsets/limites de registros imutáveis; nenhum crescimento de campo frente à origem. Não liberar outros recursos por semelhança.
- Mensagem: metadados de quatro bytes, remetente/assunto/corpo NUL. Assunto e corpo podem ser recompostos dentro do próprio registro porque o getter 0x71AE0..0x71B6C percorre os dois NULs por strlen e devolve ponteiros; manter remetente e cauda. O último registro possui `00 00 00 C1` opaco: posição e bytes preservados, sem usar como capacidade. Não interpretar metadados 0–3 como personagem/estado canônico.
- Procurado: preservar primeiros 44 bytes (metadados, nome e seu padding); editar somente descrição em +44, dentro do comprimento original. Recompensas e nomes intactos. Remetentes genéricos também permanecem em inglês nesta política, além dos nomes próprios; não afirmar que todos os rótulos do correio estão traduzidos.
- Tokens locais `%N0`/`%B0` e pipes mantêm sequência e quantidade por campo, assim como números literais. Esta política não altera as liberações específicas dos controles MAP. Conservar linhas e máximo de colunas do próprio original; não confundir colunas com medição exata de pixels ou limites gerais dos buffers de expansão.
- O getter original foi executado para os 41 registros originais/traduzidos em RAM sintética; strlen usa o probe limitado existente. Isso não executa PCSX2, GPU, I/O ou expansor completo. Validação visual continua pendente do usuário, em passagem conjunta, sem navegação automática.
- O mesmo catálogo local `work/planejamento-interface.json` agora inclui 203 campos Satcom, com 119 traduzidos e 84 preservados (41 remetentes, 40 nomes, três assuntos). Não contar preservados como tradução nem generalizar a cobertura para todo o jogo. Manter saídas compactas, alpha e limite de dez ISOs; nenhuma transferência automática ao OneDrive.
- Passaram 96 testes de interface e seis de planejamento (102 distintos); delta integral v015→v016 de 10.962 bytes somente nos 81 registros previstos. Iniciador conferido sem abrir PCSX2. A imagem conserva tamanho/diretório e todos os outros bytes da v015; não declarar execução funcional ou validação visual realizada.

## Limpeza e interface v017 — regra atual de retenção

- Por novo pedido do usuário, manter **cinco**, não dez, ISOs de trabalho em work/. Esta regra substitui os limites anteriores; alpha permanente em dist/ continua protegida e fora da fila. `tools/iso_retention.py` aplica limite padrão/máximo 5. Não apagar originais, BIOS, saves, anexos, recursos gráficos aprovados, receitas ou recuperação pendente.
- Permanecem somente cinco CMD na raiz: Iniciar-Teste, Preparar-Interface, Extrair-Dialogos, Reinserir-Dialogos e Auditar-Traducao. Dez wrappers duplicados/experimentais foram removidos; seus scripts e documentação histórica continuam reproduzíveis. Referências históricas aos CMD removidos não indicam iniciadores atuais. README atualizado explica o uso.
- Atual: `translations/interface-v017.json`, manual `docs/interface-v017.md`. Acrescenta 114 descrições de equipamentos, usadas por 126 IDs, sobre toda a v016 intacta. Total 1.153 campos/ocorrências de interface; MAP v030/layout v005 e arte v014 intactos. Não traduz nomes de itens. Validação visual pendente do usuário.
- Política `spack-item-description-original-slots-v001`: SDA raiz 0 → 0x800; registros de itens na entrada 0, 0x820, 1.349 × 128 bytes; pool na entrada 1, 0x2AAA0/0x4EC0, strings NUL variáveis. Offset de descrição em item +24; 927 referências para 567 alvos. Nomes/atributos/registros e offsets permanecem imutáveis. Não presumir slots de 64 bytes ou confundir com tabela em 0x37070.
- Somente textos ASCII de origem, sem variáveis, dentro do comprimento original; fonte PT-BR compatível, mesmos números/linhas/máximo de colunas. Hashes do ELF/S_PACK/pool/texto e todos os registros compartilhados vinculados. Não expandir slots, liberar bytes nativos ou atualizar referências por semelhança.
- Inicializador 0x70A68..0x70B98 e consumidor 0x118CB4..0x118CD0 conferidos; probe executa apenas encaminhamento 0x118CC4..0x118CD0, getters SDA e contador limitado, sem renderização/PCSX2. Não declarar menu completo emulado.
- Das 175 descrições revistas, 114 aplicadas e 61 adiadas por espaço; propostas pendentes preservadas em `description_review` da mesma receita, sem compilação. Outras 392 ainda não revistas. O catálogo local único passa a incluir os 567 alvos com essas classes. Respeitar a orientação do usuário: adiar itens difíceis, sem empobrecer texto/remover acentos para fazê-los caber.
- Passaram 103 testes de interface, seis de planejamento, cinco de retenção e três de alpha (117 distintos). Delta integral de 4.125 bytes em 114 intervalos, sem qualquer outra mudança frente à v016. A alpha foi reconferida por hash e somente leitura. Manter nova retenção de cinco; não confundir essas verificações com execução PCSX2.

## Interface v018 — revisão ampla do pool de descrições

- Atual: `translations/interface-v018.json`, manual `docs/interface-v018.md`, relatório único `reports/interface-v018.json`. Acrescenta 239 descrições à v017 sem alterar suas 114 anteriores. Total 353 descrições, usadas por 602 IDs; 1.392 campos de interface. Nomes, atributos, preços e dados de itens intactos; MAP v030, layout v005 e arte v014 preservados.
- Os 567 alvos do pool receberam propostas/revisão inicial: 353 aprovados binariamente, 212 adiados por espaço/linhas, um por controle e um marcador ??? preservado. Não há alvos não revistos nesse catálogo; isso não significa catálogo completo do jogo, aprovação editorial final ou teste visual realizado. As 61 pendências anteriores não foram retomadas nesta rodada.
- Perfil binário continua `spack-item-description-original-slots-v001`, sem repack, referências novas ou crescimento. A opção `item-description-unique-name-references-v002` valida nomes únicos citados em componentes/projetos. Receitas anteriores não ativam a opção retroativamente. Preservar também MAIN/SUB/SE, C Unit, Max Load e HP/SP.
- `tools/prepare_item_batch.py` prepara textos Unicode explicitamente revistos, sem IA/API/rede ou edição binária. Faz quebras entre palavras, preserva aprovados e arquiva recusados na mesma receita. Saída nova apenas; `--resume-deferred` autoriza somente reavaliar IDs pendentes explicitamente listados, nunca sobrescrever aprovados/preservados. A ferramenta não traduz nem libera formatos.
- Ledger opt-in `item-review-ledger-v002` conferido no compilador/planejador: classes disjuntas, contagens e hashes. Não classificar marcador original como tradução nem trocar atenção/provocação por deslocamento do inimigo. Guardas de bytes/linhas/colunas e caracteres continuam conservadoras.
- `item.description.03226` contém 80%% e continua bloqueado. Não liberar percentual por semelhança com ELF/ajuda. Próximo passo: agrupar causas dos 212 casos de espaço e provar referências/limites dos consumidores antes de reorganizar o pool; folgas de strings curtas não são capacidade autorizada automaticamente.
- Manter os cinco CMD atuais e cinco ISOs de trabalho, além da alpha protegida. Validar visualmente em conjunto pelo usuário, sem obter cada item autonomamente e sem transferir ao OneDrive por padrão.
- Passaram 111 testes de interface, seis de planejamento, cinco de retenção e três de alpha (125 distintos). Delta integral v017→v018 de 6.932 bytes em 239 intervalos; demais bytes e diretório idênticos. O iniciador usa `work/interface-v018/MetalSaga-ptbr-interface-v018.iso`. Não declarar execução PCSX2 ou validação visual com base nesses testes.

## Interface v019 — recuperação ampla de adiamentos

- Atual: `translations/interface-v019.json`, manual `docs/interface-v019.md`, relatório único `reports/interface-v019.json`. Recupera 142 descrições antes adiadas, usadas por 230 IDs. São 495/567 descrições traduzidas (832 IDs) e 1.534 campos de interface; toda v018, MAP v030, layout v005 e arte v014 preservados.
- Mantém a política `spack-item-description-original-slots-v001` sem relaxamento. Não há repack, novas referências ou expansão. Restam 70 adiamentos de espaço, um percentual bloqueado e um marcador preservado. Esses 71 adiamentos mantêm integralmente os dados e propostas da v018; não arquivar tentativas encurtadas que percam efeitos, categorias ou preposições de nomes de armas.
- `diagnose_budget` no preparador e no planejador existente separa excesso de bytes, quebra entre palavras, linhas, colunas, controles e glifos. As restrições podem se sobrepor; não somar como textos distintos. Saída continua no mesmo `work/planejamento-interface.json`. Ajuste de orçamento não comprova semântica, largura em pixels ou edição autorizada.
- Iniciadores apontam para `work/interface-v019/MetalSaga-ptbr-interface-v019.iso`. 117 testes de interface, seis de planejamento, cinco de retenção e três de alpha passaram (131 distintos). Delta integral v018→v019: 4.702 bytes somente em 142 intervalos, diretório e demais bytes idênticos. Não declarar teste PCSX2: usuário verifica visualmente em partida normal.
- Manter cinco ISOs de trabalho e alpha permanente protegida. Não enviar ao OneDrive nem desligar sem novo pedido. Próximas pendências: provar limites/referências antes de repack de descrições; esclarecer composição `%screased`, Coat e TITLE/BACK. Fragmentos MAP continuam posteriores.

## Interface v020 — três blocos, nomes genéricos e composição

- Atual: `translations/interface-v020.json`, manual `docs/interface-v020.md`, relatório único `reports/interface-v020.json`. Acrescenta 238 campos/ocorrências em uma imagem: 189 nomes genéricos/habilidades (183 rótulos distintos), 41 descrições retomadas e oito campos de interface. Total 1.772; MAP v030, layout v005 e arte v014 mantidos. São 536/567 descrições traduzidas, usadas por 883 IDs; 29 adiamentos de espaço, um percentual bloqueado e um marcador preservado.
- `spack-reviewed-generic-item-names-original-slots-v001` em `tools/item_names.py`: 1.349 registros ×128 em 0x820, nome NUL antes de +24, offsets/atributos/IDs intactos. O maior nome original tem 16 bytes; a janela de 24 não autoriza crescimento. Cada alvo respeita o próprio comprimento original. Fonte/código/SDA/extents não crescem. Preservar armas humanas, motores/C Units, LOVE machine, componentes e nomes únicos; não promover os 239 nomes pendentes automaticamente.
- Getter 0x6D938..0x6D950 executado em memória sintética para todos os 1.349 IDs, retornando base 0x475AE8 + ID×128; consumidor 0x1B34D0..0x1B3530 encaminha nome ao texto em VA 0x2967C8 (arquivo 0x1977C8). Ordenação 0x705A8..0x70610 usa nomes: ordem alfabética pode mudar. Isto não prova todos os consumidores nem executa o PS2. Rótulos iguais nessa tabela têm tradução idêntica em todos os IDs.
- Validar marcadores EX/I/II/III no Unicode, nunca nos bytes GFI: um byte de ô parece ASCII I. Regressão explícita com Maiô. Não remover acentos nem ampliar o repertório silenciosamente. Ó/Â e a proteção contextual de Fang seguem entre as recusas das propostas de nomes; resolver com políticas específicas.
- `spack-in-de-cremento-preview-v001` libera somente o rótulo 142 da UI, com incremento/decremento. Mantém in/de nos aliases 143/145 e 144/146, printf, nome/número de item e atributos. Hashes do trecho 0x1F0320..0x1F040C e das tabelas 0x349FB8/0x349FC0 vinculados. Probe de 16 combinações somente no encaminhamento 0x1F038C..0x1F03E8; não executar nem alegar sprintf/transação/PS2. Não desbloquear outros compostos ou os prefixos compartilhados.
- A descrição continua em `spack-item-description-original-slots-v001`; seu relatório distingue nomes intactos pelos patches de descrição dos nomes genéricos autorizados separadamente. Os 30 adiamentos restantes preservam integralmente a v019. Os sete literais ELF novos são Dir./Esq., três Saldo e duas capitalizações MAIN/SUB. Não declarar cobertura completa de menus por essas contagens.
- Queda de energia interrompeu os testes antes do build. V019 reconferida por hash/tamanho, JSONs recuperados e nenhum parcial/transação v020 encontrado. Log interrompido não conta como aprovação. Depois passaram 135 testes de interface, seis de planejamento, cinco de retenção e três de alpha (149 distintos); composição reconferida por quatro testes sem duplicar a contagem. Delta integral de 7.882 bytes em 238 intervalos; demais bytes/diretório idênticos. Nenhuma navegação PCSX2.
- Iniciadores usam `work/interface-v020/MetalSaga-ptbr-interface-v020.iso`. Planejador mantém o mesmo arquivo local, agora com todos os registros de nomes e classes. Manter cinco ISOs, alpha protegida, OneDrive/desligamento só por novo pedido. Próximos alvos: limites de nomes/descrições, Coat e TITLE/BACK; fragmentos MAP continuam posteriores.

## Interface v021 — teto observado de nomes e instalação

- Atual: `translations/interface-v021.json`, manual `docs/interface-v021.md`, relatório único `reports/interface-v021.json`. São 285 ocorrências novas: 268 nomes (37 equipamentos, 105 consumíveis/materiais, 56 móveis/acessórios, 51 habilidades, 19 objetos genéricos) e 17 mensagens de sistema. Total 2.057; 457 nomes traduzidos, 536 descrições/883 IDs e MAP v030 mantidos. Fontes/layout v005 e arte v014 intactos.
- Novo opt-in `spack-reviewed-generic-names-observed-ceiling-v002`: teto de 16 bytes mais NUL, máximo original testemunhado no ID 954; todos os tails originais até +24 são zero. Encaminhamento comum 0x1B34EC..0x1B3504 até VA 0x2967C8 e desenho 0x1977C8..0x197910 vinculados por hash. Getter e encaminhamento executados para todos os 1.349 índices em RAM sintética, sem invocar formatação/GPU. Não alegar todos os consumidores ou largura visual comprovados.
- Os bytes +17..+127 permanecem intactos em todos os registros; 264 nomes novos usam preenchimento do próprio campo. Não expandir para 17..23 bytes ou para outra string. O perfil histórico v001 mantém o próprio comprimento original e rejeita a opção nova. Perfis/receitas anteriores continuam reproduzíveis e seus patches idênticos. Aliases protegidos e nomes únicos permanecem bloqueados; os aliases editáveis mantêm a mesma tradução em todos os IDs.
- 47 propostas de nomes seguem pendentes. Preservar seus motivos/hashes históricos; `current_validation` do planejador é diagnóstico individual, não autorização. Quatro passam nas guardas individuais mas dependem de revisão editorial/aliases (Sugar Pill, Dance Earrings, Dance Shoes, Grenade Gun). Não promover automaticamente nem remover proteção de Repair Kit/Fang/Bus Stop Sign para caber. Ó/Í ainda não foram liberados no repertório.
- `ndata-install-crlf-original-loaded-region-v001` libera somente entrada 12 de NDATA em 0x96800, leitura de 875 bytes (descritor 0x348ED0), 17 linhas CRLF. Alvos usam 804 bytes, NUL apenas dentro da leitura; SDA, descritor e padding externo intactos. %INSTALLSIZE% e pipes preservados. Caller 0xBD8B4..0xBD914 chega ao leitor/CRLF existente; substituição em 0xBEEC4..0xBEEEC/0x95E50 vinculada, mas não executada. Não instalar/formatar HDD ou habilitar recursos do PCSX2 para validar textos. Perfil de recursos legado continua rejeitando entrada 12.
- TITLE/BACK foram investigados via construtor 0x10AB40/tabela virtual 0x3061C8, sem conclusão suficiente para editar. Coat continua pendente. Não repetir suposições de caixa/voltar por nomes dos botões. Sem repack de descrições ou nova liberação MAP.
- Passaram 153 testes finais de interface, seis de planejamento, cinco de retenção e três de alpha (167 distintos). Auditoria de nomes nos diálogos usa herança resolvida e segmentos string/dicionário, não só campos chamados translation. Procurou 416 rótulos exatos >=6 bytes em 5.183 segmentos canônicos, sem correspondências; não generalizar para contexto/sinônimos/aliases. Delta integral v020→v021: 4.103 bytes em 269 intervalos, demais bytes/diretório idênticos. Nenhuma execução PCSX2.
- Iniciadores usam `work/interface-v021/MetalSaga-ptbr-interface-v021.iso`. Manter cinco ISOs de trabalho, alpha protegida e transferências/desligamento só por novo pedido. Teste visual consolidado das listas/nomes e mensagens continua pendente.


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


## Planejamento após v025

Consultar `docs/proximos-passos-v025.md` e `reports/progresso-v025.json`. Planejamento somente, sem nova tradução/ISO: a base continua v025. MAP 5892/7231 (81,48%), descrições 541/567 (95,41%), nomes fora das categorias protegidas 516/565 (91,33%); não chamar essas métricas de porcentagem de todo o jogo. Restam 23 propostas nominais e 26 nomes não revisados, nem todos a traduzir; 24 descrições de espaço, uma de controle e um marcador preservado. Próximo reforço planejado: hash/tamanho/journal antes de abrir/entregar a ISO; ainda não implementado nesta rodada. Depois revisar nomes, provar capacidade/consumidores, fechar lacunas de interface e só então fragmentos MAP. Evitar repetir tentativas curtas improdutivas ou forçar 15 nomes quando a decisão correta for preservar.


## Interface v026 — expansão de batalha e interações

Atual: `translations/interface-v026.json`, manual `docs/interface-v026.md`, relatório único `reports/interface-v026.json`. Acrescenta 1.298 campos/ocorrências: 679 ações, 248 dicas de análise, 72 nomes genéricos de inimigos, 149 reações de itens e 150 textos de bares. São 849 payloads PT-BR distintos novos e 3.419 campos acumulados. Referência numérica: maior ganho anterior de 647 registros MAP (v019), meta 1.294; não confundir campos/ocorrências com palavras, tempo ou 1.298 novas falas MAP. Compartilhamentos físicos dos pools são contados uma vez.

`spack-battle-labels-and-analysis-hints-fixed-fields-v001`: S_PACK ações 0x37070, 967×228, campo inicial 32 com alvo até 18 bytes (máximo observado incluindo nativos; ASCII original até 16); inimigos 0x6CDB0, 261×276, nome em +0/24 até 16 bytes, dica +232/44 até 43 bytes/duas linhas/19 caracteres por linha. Lista explícita de IDs genéricos; Wanted, personagens, nomes distintivos, nativos e demais IDs protegidos. Preservar atributos e trailer opaco de 12 bytes. Aliases de itens exigem redação já aprovada; MAIN/SUB/SE, Marceau e Muscle mantidos. Ponteiros/encaminhamentos foram executados em RAM sintética, não formatador/GPU/jogo.

`spack-reactions-and-bar-original-counted-pools-v001`: reações em 0x325D0/8864, 179 chaves×3 variantes, 151 alvos; 149 alterados, 8470 bytes usados, limite textual 8849 e trailer opaco de 15 bytes intocado. Bar raiz SDA 6 em 0x11C800, texto +0x20/3744, 172 IDs/166 alvos; 150 alterados, 3736 bytes usados. Repack só dentro dos pools; chaves, aliases, prefixos [n], números, pipes, espaços de extremidade e demais entradas preservados. Marcador *sg_Mx e denominações/expressões mantidos. Janelas de carga, consulta e prefixo vinculadas ao ELF original. Sem novos controles, glifos, crescimento de arquivos/extents ou edição dos recursos adjacentes não interpretados.

Revisão nominal: 566 selecionados, 516 traduções intactas, 25 pendentes e 25 preservados (inclui o ID protegido 55). No recorte não protegido: 516 traduzidos, 24 preservados, 25 pendentes, zero não selecionados. Das 26 seleções novas, 22 preservadas e quatro adiadas; 946/1035 passaram de pendência a preservação explícita. Bunny fica preservado por contexto ainda não comprovado, sem declarar que é nome próprio. Não contar preservações como traduções. Descrições continuam 541/889 referências, MAP v030 5892/123 adiados; layout v005 e arte v014 intactos.

Preflight implementado em `tools/verify_test_iso.py`, integrado ao iniciador: hash integral/tamanho/relatório concluído/journal/partial e estabilidade dos arquivos; recusa divergência, sem reparo automático. CLI padrão agora interface; `Iniciar-Teste.cmd` e `Preparar-Interface.cmd` usam v026. Planejador local inclui os novos catálogos e razões de preservação, no mesmo work/planejamento-interface.json. Nenhuma navegação PCSX2, OneDrive ou desligamento nesta rodada.

Validação: 215 testes distintos aprovados (194 de interface, sete preflight, seis planejamento, cinco retenção, três alpha). Suíte inicial: 193 com uma falha no filtro de teste, que incluía o patch legado battle.ptbr-advance como novo; corrigido o teste, código do produto inalterado, reexecutados seis casos v026 com sucesso (inclui novo teste do planejador). Não somar reexecuções. Auditoria de 67 nomes genéricos ingleses em 5183 segmentos canônicos MAP: zero ocorrências exatas; não prova semântica/flexões nem expande aliases. Delta integral v025→v026: 21162 bytes em 1001 intervalos S_PACK; diretório, demais bytes, fontes e MAP iguais. SHA-256: 58b1fa85f04fbdf9002dda7f5fafb450bd0d74d64098139a5137a109a7f8707a. Cinco ISOs e alpha protegida; validação visual pendente nos novos contextos.


## Continuidade interface v028 — descrições conhecidas concluídas

Atual: `translations/interface-v028.json`, manual `docs/interface-v028.md`, relatório `reports/interface-v028.json`. A receita intermediária v027 recupera 24 descrições de espaço; v028 acrescenta a descrição 80%% e dois literais ELF (Pelo no status canino e erro de leitura de pintura). Somente uma ISO nova, v028. São 27 campos novos, 3.446 acumulados; 566/567 descrições (99,82%), usadas por 925 IDs. O marcador ??? (dois IDs) permanece intacto; zero descrições pendentes nesse catálogo, sem comprovar todos os textos do jogo descobertos. MAP v030 5892/123 adiados, 516 nomes traduzidos/25 pendentes, batalha/bares, layout v005 e arte v014 mantidos.

`spack-item-description-original-pool-repack-v002`, em tools/description_pool.py, é opt-in. Reorganiza somente 0x2AAA0/20160 de S_PACK e atualiza u32 +24 dos registros de 128 bytes em 0x820. Preservar nomes +0..23, atributos +28..127, sentinelas FFFFFFFF, SDA/extents e aliases. São 567 alvos/927 referências; 926 ponteiros mudam, primeiro mantém zero. Usados 18425 bytes, 1735 livres. Toda fonte vinculada por hash; reconstrução original byte a byte. IDs continuam os offsets ORIGINAIS; planejador acrescenta destino relativo sem renomear IDs por offsets novos. Não inferir capacidade de outro recurso.

O pai fixo v026 é vinculado por caminho/hash. As 541 entradas anteriores são imutáveis em Unicode/bytes, embora possam mudar de posição dentro do pool. Retomadas explícitas somente entre adiamentos do pai. Novos alvos: máximo original observado de 59 bytes/29 caracteres por linha, mesma quantidade de linhas de cada origem, números, nomes e tokens preservados. Perfis antigos continuam fixos. 17 caminhos com lw 5AEC foram inspecionados e seus trechos executados para 927 referências (15759 casos) em RAM sintética. Isso não executa formatador, alocação, desenho ou PS2, nem prova censo exaustivo de aliases indiretos.

`single-80-double-percent-description-v001`, em tools/description_percent.py, libera somente item.description.03226. Manter exatamente 80%% (bytes 38 30 25 25). Probe do switch original 0x229EA4 até 0x22A418 produz um %, comprimento 1, sem ler/avançar argumentos. Raw-copy e wrapper %s conservam os dois bytes; manter esse comportamento original, sem prometer um único sinal em todas as telas. Não liberar printf/MAP/% genérico ou outros textos por semelhança.

`canine-coat-status-label-v001`, em tools/character_status_context.py: ramos originais dos dez índices; 0..5 usam Driving/+0x4C, 6..9 resolvem Dog e usam Coat/+0x58. Traduzir somente Coat: %4d para Pelo: %4d, sem mudar valor, mecânica ou classe. TITLE/BACK seguem sem semântica comprovada. Your Saves em 0x320BF0/0x321628/0x322CE0 permanece original: há uso em caminhos de icon.sys, não traduzir como simples rótulo nem migrar saves.

O comparador reconhece a transição fixo→pool somente com o pai exato, reconstruindo o overlay histórico; não autoriza apagar patches arbitrários. Iniciar-Teste.cmd e Preparar-Interface.cmd apontam para v028; preflight integral permanece obrigatório. SHA-256 da ISO: 594b1344b0088b5218795c8c3e7943b08a5d7a40514c210b19f6704644bdd32e. Comparação v026→v028: 20887 bytes em 929 intervalos autorizados; demais bytes/diretório intactos. Nenhuma navegação PCSX2; usuário verifica em partida normal. Cinco ISOs e alpha permanente protegida; sem OneDrive/desligamento automático.

Próximos alvos: nomes ainda bloqueados por 16 bytes/glifos/identificadores, TITLE/BACK e lacunas gráficas comprovadas. Não repetir tentativas nas descrições já encerradas nem cortar preposições para caber. Fragmentos MAP continuam posteriores. Testes finais registrados no relatório v028.


## Continuidade interface v029 — senha gráfica e comando BACK

Atual: `translations/interface-v029.json`, manual `docs/interface-v029.md`, relatório `reports/interface-v029.json`. Três campos gráficos novos: DESTRAVAR/TRAVAR/SAIR no painel de senha; BACK recebe VOL. nos três slots de legenda de entrada de nomes. Estes slots já pertencem a registros traduzidos: não contar revisão como novos registros. Total 3449 campos. Descrições 566/925 referências, nomes 516/25 pendentes, MAP v030 5892/123 adiados, layout v005, arte v014 e todos os textos anteriores preservados. Uma ISO consolidada, cinco ISOs de trabalho e alpha permanente protegida.

`password-panel-three-native-labels-v001`, em tools/password_graphics.py: somente textura da entrada 6 de DATA/FDATA/PASSWORD.SDA em 0x618B0/0x10410. GANM entrada 13 em 0x71D80 permanece intacto; sprites 18,1,0 recebem DESTRAVAR/TRAVAR/SAIR, nos retângulos [154,170,252,192], [154,200,252,222], [154,230,252,252]. Paleta/alpha, headers, SDA, dimensões, números/setas, seis outras texturas, comandos e validação da senha não mudam. Composição local pela GFI existente, célula 20 pixels; DESTRAVAR usa 94/98 da largura natural, demais palavras escala 1. Não alterar GFI nem arte do título para isso. SHA da textura resultante está fixado na política; divergência de raster/dependência deve falhar, não substituir silenciosamente a v001.

Ligação comprovada por arquivo/ELF original: password.sda em 0x32E120; upload 0x131A68..0x131A90; tabela de GANM 0x32E290 e teclas 0x32E2B0; encaminhamento gráfico 0x132C20..0x132C40. Foram executados um caso de upload e os 15 encaminhamentos de teclas em RAM sintética: sprites [4..15,18,1,0]. Switch original 0x32E200 liga teclas 12/13/14 a modos 0/1/saída, sem alteração de lógica. Não confundir prova de argumentos/preview com GPU ou execução do jogo.

`name-entry-back-navigation-v002`, em tools/name_back_command.py, é opt-in no compilador de legendas. Ramo original 0x10BA74..0x10BA90 zera linha +0x3020 e copia categoria +0x2700 para coluna +0x3022; encaminha redesenho a 0x10CBA8. Foram executados 42 casos de navegação (7 linhas, 3 categorias, nome vazio/preenchido), sem alteração do buffer de nome, mais oito casos de seleção de legenda em 0x10D540..0x10D584. Só BACK muda para VOL., 12 bytes no total das três legendas. Preservar espaços, ícones nativos, offsets, NULs e demais palavras. Perfil histórico continua com BACK. TITLE segue em inglês: o seletor de legenda não comprova o retorno do chamador ao título.

Iniciar-Teste.cmd e Preparar-Interface.cmd passam a v029; preflight integral obrigatório. Preview comparativo em work/password-v029-comparacao.png foi inspecionado, sem PCSX2. O planejador mantém work/planejamento-interface.json e acrescenta os três gráficos e a pendência TITLE. Resultados de testes/comparação/hash no relatório v029. Sem OneDrive, desligamento ou mudanças de saves/configurações.

Próximas pendências: TITLE no chamador e grafismos FNAME_DT/END, antes de editar bancos aparentemente inativos. F_COMMON tem superfícies e nomes físicos START/SELECT: não promover como palavras de menu sem uso comprovado. Não repetir tentativas de encurtamento nos 25 nomes nem reanalisar descrições já encerradas; não remover proteções para obter contagens. Nomes pendentes continuam por espaço/glifo/identidade; fragmentos MAP permanecem depois das lacunas de interface.


## Continuidade interface v030 / MAP v031 — serviços em lote

Atual: `translations/interface-v030.json`, base `translations/regiao-inicial-v031.json`, manual `docs/interface-v030.md`, relatório `reports/interface-v030.json`. Acrescenta 69 traduções de reparos, preços, viagens, entregas, inventário, recompensas e cenas com referências dinâmicas, além de dois gráficos END→FIM. Retoma 74 IDs explícitos: cinco permanecem intactos por conter somente nomes/marcadores e não contam como tradução. São 5961 registros MAP alterados, 49 adiados e 3451 campos de interface. Preservar integralmente as 5892 traduções MAP e os 3449 campos anteriores, nomes únicos, expressões, Hunter/Soldier/MAIN/SUB/SE, layout v005 e título v014. Descrições 566/925 referências e nomes 516/25 pendentes mantidos.

`fixed-record-reviewed-variable-selectors-slots-v012`, em tools/control_variable_refs.py, herda v011. Somente seletores adicionais explícitos: inteiros $0/2/5/10/11/12/13/14/16/17/18; I$1/2/9/10/15/19; N$1/2/6/10. Foram executados 106 casos dos handlers originais e leitor em RAM sintética: consumo, variável/contexto, inteiro com sinal, stride item128 e tabela de nomes com ponteiros de4 bytes. Não comprova identidades canônicas, limites das tabelas, emissor ou PS2. N$3 não liberado; f minúsculo permanece bloqueado. Slots fixos e nenhum crescimento por segmento, tokens/índices/quebras/spans vazios/rótulos/offsets imutáveis, sem repack, falha atômica. Lexer histórico e políticas anteriores inalterados. Não estender índices por semelhança.

`name-entry-two-finish-sprites-v001`, em tools/name_finish_graphics.py: somente textura de FNAME_DT.SDA em 0x4CC0/0x40440, 512x512/8bpp, upload0x40410. Preservar header/paleta/alpha/cauda48, GANM0x86980 e pixels externos aos interiores dos sprites14 [426,216,475,240] e34 [426,440,475,464]. FIM usa GFI existente, célula24/largura33 sem redução horizontal; raster vinculado por hash. Probes originais de upload/GANM/categorias comprovam sprites padrão32/33/34 e selecionados12/13/14; não são execução de GPU/validador de nome/PS2. TITLE e demais bancos permanecem intactos. Preview em work/nome-fim-v030-comparacao.png, separado de validação visual em jogo. Cofre v029 permanece byte a byte igual; seu preview recebeu aprovação do usuário antes desta rodada.

Iniciar-Teste.cmd e Preparar-Interface.cmd usam v030/MAPv031. Auditar-Traducao.cmd usa o relatório compacto v030; o auditor recompila o plano em memória somente se toda a cadeia de receitas e os resultados se reproduzirem. Planejador também reconhece a política v012 e os dois gráficos. Não criar arquivos volumosos de origem só para atualizar uma triagem.

Pendências em reports/plano-pendencias-v008.json: 35 opacos (19 N$3 preservados e 16 outros) e 14 nativos. Os 16 incluem 8 formatos f, 3 %, 2 %N, 1 %M_1, 1 %M_4, 1 %T0. Não confundir spans do lexer com comandos completos nem retraduzir nomes de tanques. As 160 sugestões de revisão/114 combinações não são traduções obrigatórias; preservar decisões explícitas. Próxima rodada pode abordar TITLE e os 8 formatos f como frentes independentes, com provas próprias, antes de repetir tentativas nos 25 nomes bloqueados. Usuário confere a nova versão em passagem normal, sem exigir navegação imediata. Uma ISO consolidada, teto de 5 e alpha permanente protegida; sem OneDrive/desligamento automático.

Passaram 319 testes distintos, incluindo 246 de interface e 42 de controles; reexecuções não somadas. Comparação integral v029→v030: 5845 bytes em 70 intervalos autorizados, diretório/demais bytes/fontes intactos. SHA-256: 1deb57e06fc864d13f850492e881ccc9ba72289fd3ab1e2603db1646a15370d6. Preflight, iniciador em dry-run, reconstrução do plano compacto e hash/readonly da alpha conferidos. Nenhuma execução PCSX2 nesta rodada; teste visual pendente em partida normal.


## Continuidade interface v031 / MAP v032 — rodada normal de sucata

Atual: `translations/interface-v031.json`, base `translations/regiao-inicial-v032.json`, manual `docs/interface-v031.md`, relatório `reports/interface-v031.json`. Por pedido do usuário, rodada normal, sem extensão ampla: oito diálogos de sucata/tonelagem para construção de tanques, projeto e adiamento. Preservar o tom de Dr. Palm/assistente, nomes e valores. Total 5969 traduções MAP, 41 adiamentos; todos os 5961 patches anteriores intactos. Interface 3451 campos, descrições 566/925 referências, nomes 516/25 pendentes, layout v005 e título v014 mantidos. Sem avisos novos de largura nesses oito registros; isso não comprova apresentação visual.

`fixed-record-scaled100-preserved-slots-v013`, em tools/control_scaled100.py, herda v012 e libera somente os tokens completos %$0f100, %$2f100 e %$13f100. Índice e divisor literal 100 são imutáveis, não apenas o prefixo antes de f. Leitor original 0x1B5A30..0x1B5AD0, handler 0x1B5DEC..0x1B5E84, formato %.2f em 0x349DB8. Foram executados 24 probes de instruções/leitor em RAM sintética com modelo FP32 finito; helper 0x183E38 stubado para conferir encaminhamento. Não executa helper completo, formatador, emissor ou PS2, nem comprova arredondamento em jogo. Manter separador decimal do motor, slots fixos sem crescimento por segmento, comandos/ordem/quebras/spans/rótulos/cabeçalhos/offsets/tamanhos, sem repack e com falha atômica. Políticas anteriores, lexer histórico/fingerprints, outros índices/divisores e f genérico continuam bloqueados.

Iniciar-Teste.cmd, Preparar-Interface.cmd, Auditar-Traducao.cmd e planejador usam v031/MAPv032. Relatório compacto pode reconstruir plano em memória por hashes. Triagem em reports/plano-pendencias-v009.json: 27 opacos (19 nomes N$3 preservados e oito outros: 3 %, 2 %N, 1 %M_1, 1 %M_4, 1 %T0), mais 14 nativos. Não repetir investigação dos oito formatos f já encerrados ou traduzir N$3 para inflar contagens. TITLE e nomes bloqueados continuam pendentes para rodadas próprias.

Passaram 90 testes distintos (48 controles, 12 reinserção, 3 lote, 6 cobertura, 7 preflight, 6 planejamento, 5 retenção, 3 alpha). Suíte completa de interface não repetida por não haver mudança de textos/renderizadores dessa interface; construção e comparação integral conferem os recursos. Delta v030→v031: 943 bytes em oito registros MAP, diretório e demais bytes/fontes/arte idênticos. SHA-256: 375f1dede3ffb0f7adf40affd2da934e4dfe117991e94040b12ea9edb8d9efbe. Cinco ISOs de trabalho e alpha protegida. Nenhuma execução PCSX2, OneDrive ou desligamento; usuário confere em partida normal, sem exigir alcançar Dr. Palm agora.


## Continuidade interface v032 — títulos de personagem e recompensas

Atual: `translations/interface-v032.json`, base MAP inalterada `translations/regiao-inicial-v032.json`, manual `docs/interface-v032.md`, relatório `reports/interface-v032.json`. Rodada extensa de 75 campos novos: 73 títulos da ficha e duas mensagens de prêmio do minijogo de tanques. Total 3526 campos; MAP continua com 5969 traduções/41 adiamentos. Preservar integralmente os 3451 campos anteriores, nomes de itens 516/25 pendentes, descrições 566/925 referências, layout v005 e título v014. Os títulos da ficha são distintos do comando TITLE da entrada de nomes, que continua bloqueado para tradução por falta da prova do chamador.

`character-title-original-cells-v001`, em tools/character_titles.py, permite somente 71 células de 16 bytes em 0x3198F0..0x319D60 e sete não vazias de oito bytes em 0x348BF8..0x348C38. A oitava célula é vazia e permanece original. Dez grupos em 0x264478 têm 47/7/7/8/8/1/1/1/1/1 referências; os grupos de oito são contíguos sem NUL separador. Há 82 referências, três vazias, 79 não vazias e 78 títulos únicos. Pro Mechanic compartilha uma célula entre dois grupos; manter um único patch e a redação neutra Pro de oficina. Preservações explícitas: Gamer, Moocher Breeder, Bargain Hunter, Cyber Hunter e Yokozuna. Não usar nomes de personagens presumidos para justificar tradução pelo índice do grupo.

Lookup original 0x6BB60..0x6BB84, chamador 0x118A18..0x118A34, encaminhamento 0x118A68..0x118A8C; call sites adicionais 0x1B5D64 e 0x1CD378. Foram executadas 79 combinações não vazias com lookup/caller/encaminhamento em RAM sintética. Não executa formatador completo, desenho, desbloqueio de títulos ou PS2, nem prova limites de índice no runtime. Texto pode ocupar somente 15 ou sete bytes da própria célula, com NUL final e sem consumir célula adjacente. Validar ASCII/NUL/padding original, hashes de célula, referências conhecidas exatamente nos grupos, ausência de aliases internos, termos e glifos. Ponteiros, código, células preservadas/vazias e seções imutáveis. Não transferir essa capacidade a itens ou modificar o catálogo ELF legado para liberar mais strings.

Mensagens de prêmio: ELF 0x337610/0x337628, Ganhou com %dG/%s e quatro espaços iniciais/finais originais. Argumentos conferidos por instruções originais em 0x160194..0x1601AC e 0x160268..0x160290: valor de contexto+0x1788 e nome por base+ID*128. Não altera prêmio, pagamento, identificadores ou nomes únicos. Não confundir identificadores internos de minijogos com texto visível.

Iniciar-Teste.cmd, Preparar-Interface.cmd, Auditar-Traducao.cmd e planejador usam v032. Planejador mantém um JSON e distingue hashes da célula inteira dos hashes de literal pré-NUL; não intercambiar essas provas. Delta final v031→v032: 879 bytes em 75 campos ELF; MAP/fontes/arte/diretório e demais bytes idênticos. SHA-256: a0724bee61e4bd573d07785dc9ac4ebedf209d088c796282ed1ae444176ce701. Revisão editorial ajustou quatro títulos, inclusive gênero/alias compartilhado; a imagem não publicada anterior foi descartada após conferir hash, com evidência privada em work/. Testes finais e repetições documentados no relatório da versão. Nenhuma navegação PCSX2; usuário confere em partida normal. Cinco ISOs de trabalho e alpha permanente preservadas.

O usuário pediu desligamento pelo terminal ao concluir esta rodada extensa. Executar somente após verificações, documentação, commit e push concluídos. É uma solicitação desta rodada, não autorização recorrente. Nenhuma cópia para OneDrive foi solicitada. Próximos bloqueios: comando TITLE, 25 nomes de itens, oito outros controles e 14 nativos MAP, mantendo os 19 N$3 preservados e a revisão contextual/visual acumulada.

Fechamento v032: 326 testes distintos aprovados (257 interface, 48 controles, 7 preflight, 6 planejamento, 5 retenção, 3 alpha). Os sete testes de títulos e quatro de integração passaram novamente após a revisão final, sem somar repetições. Relatório do compilador atual reproduz exatamente os metadados da imagem final; preflight, dry-run do iniciador, retenção de cinco imagens e hash/readonly da alpha conferidos.


## Continuidade diálogos v033 — prioridade voltou ao MAP.MCT

Por pedido do usuário, priorizar os diálogos pendentes e sua infraestrutura. Atual: `translations/regiao-inicial-v033.json`, consolidada por `translations/interface-v033.json`, manual `docs/dialogos-v033.md`, relatório `reports/interface-v033.json`. Recuperados 14 registros: oito com variantes/lexemas de controle e seis com bytes nativos revisados. São 5983 traduções MAP e 27 adiamentos (19 N$3 preservados e oito ocorrências nativas idênticas ainda sem contexto suficiente). Todos os 5969 patches anteriores e os 3526 campos de interface permanecem intactos; fontes/layout v005 e título v014 não mudam. Não recomeçar os N$3 ou declarar os oito nativos como debug/falsos positivos sem evidência.

`fixed-record-reviewed-dialogue-quirks-v014` herda v013. `tools/control_dialogue_quirks.py` libera somente %M_1, %M_4, %T0, %NO e quatro lexemas de preço %500/%5000/%8000/%1000 seguidos de G nos contextos observados. M lê argumento omitido zero e o segundo literal 1/4, produzindo tipo8/valor empacotado; T0 é literal, distinto de T$0. %NO contém O, não zero: o leitor não consome a letra e o caminho inspecionado mantém resíduo literal. Dígitos de preço seguem o dispatch padrão no formatador genérico; o renderizador completo de escolhas não foi executado. Preservar todos esses bytes e resíduos, sem substituir %NO por %N0, remover %, trocar preços ou alegar bug corrigido. Correções futuras exigem prova específica do consumidor e conferência visual. Não liberar outras variantes por semelhança. Slots fixos, sem crescimento por segmento, sem repack; ordem/controles/quebras/spans/rótulos/cabeçalhos/offsets/tamanhos e transação atômica mantidos. Lexer/fingerprints históricos e políticas anteriores inalterados.

`tools/dialogue_native_review.py` vincula seis IDs/hashes integrais: msg07B264E0, 128226B4, 128226FC, 12822744, 12822790, 13709CC0. Somente estes registros podem substituir conteúdo nativo por PT-BR. Preservar ☆/8199 no sufixo de Syd e 。/8142 antes da primeira quebra no aviso do trem, uma ocorrência cada. Codec global continua estrito; não inserir CP932/UTF-8/japonês arbitrário nem usar esses símbolos em outros registros. Verificados os glifos das origens nas duas GFI; não colidem com a linha PT-BR0x23 e nenhuma fonte foi alterada. Bar e trem foram contextualizados por mensagens vizinhas. Não assumir que validação binária/bitmap comprova exibição no PCSX2.

Auditar-Traducao.cmd agora usa `tools/audit_dialogue_backlog.py`, com um único JSON local substituível em work/dialogos-pendencias-atual.json. Originais, offsets, capacidades, hashes, contextos e agrupamentos ficam somente em work/. Resumo público em reports/dialogos-pendencias-v033.json; a ferramenta anterior de cobertura continua acessível por CLI. Reconstruir planos compactos somente por receitas vinculadas/hash, mmap no MAP e sem IA/APIs/internet. Inventário: 2741 blocos/61356 comandos SSD; varridos 54125 comandos fora dos 13 layouts conhecidos, 781072 bytes, zero candidatos pelo filtro ASCII. Isso não prova cobertura completa de textos curtos, nativos, comprimidos ou fora do índice SSD.

Rótulos de falantes: 134 únicos em 1527 referências, deduplicados mas não liberados. Há nomes próprios, marcadores e possíveis funções genéricas. Manter label/terceira string imutável nas políticas existentes; uma liberação futura exige opt-in e prova própria. Calls em 0x1C6548/0x1C6DE0 passam a origem ao setter0x1FD968; 14 words vinculam retenção do ponteiro, helpers, +4/alinhamento e escrita em objeto+0x34. É inspeção estática, não execução de instruções. A hipótese de alocação por comprimento/cópia e os helpers/desenho/vínculos com retratos ainda precisam de prova. Próxima frente recomendada: rótulos genéricos sem alterar nomes próprios/Hunter/Soldier, contexto dos oito nativos repetidos e revisão editorial das expressões. Os160 sinais de revisão/458 sugestões de nomes/603 controles-pontuação são triagem, não traduções obrigatórias.

Passaram 107 testes distintos: 53 controles, 4 codec nativo, 4 regressão real, 12 reinserção, 6 cobertura, 7 auditoria, 7 preflight, 6 planejamento, 5 retenção, 3 alpha. Repetições não somadas. Delta integral v032→v033: 917 bytes em14 registros MAP, demais bytes/diretório/fontes/arte/interface idênticos. SHA-256: 7d70d3e99632b6e8df1a7c66db1e66c4d69eaea3ceec878a037ed5b550566f9e. Preflight, dry-run, relatório final do compilador, cinco ISOs e alpha readonly/hash conferidos. Iniciar-Teste.cmd e Preparar-Interface.cmd usam v033; não exigir acesso imediato às cenas, usuário confere em partida normal. Nenhuma navegação PCSX2 ou cópia para OneDrive. O desligamento da rodada anterior foi atendido e não é recorrente; não desligar nesta rodada sem novo pedido.
## Continuidade interface/MAP v034 — funções dos falantes

Atual: `translations/interface-v034.json`, base `translations/regiao-inicial-v034.json`, manual `docs/dialogos-v034.md`. Lote de 553 rótulos em 72 funções/estabelecimentos, com todas as falas/opções v033 preservadas. São 5999 registros MAP com algum campo alterado; corpos/opções continuam em 5983. Somente 16 registros novos mudam exclusivamente pelo rótulo; não anunciar 553 novas falas. Interface mantém 3526 campos, layout v005 e título v014. Permanecem 27 adiamentos de corpos: 19 N$3 preservados e oito nativos sem contexto. Não retraduzir nomes para inflar cobertura.

Política opt-in `map-generic-speaker-label-fixed-slots-v001`, em `tools/speaker_labels.py`, aplicada após o compilador legado. Esse compilador e a extração mantêm `label.editable=false`, terceira string protegida e fingerprints históricos. A receita v034 enumera IDs/hashes integrais/hashes de rótulos/targets, vinculados a sete janelas e hash do ELF original. Somente roles do mapa editorial explícito, em msgn/smnn/2snm sem bloqueios e slots fixos. Proibir crescimento/realocação, controles injetados, alteração de corpo/opções/cabeçalho/offsets, nomes próprios/profissões protegidas, decisões de preservação e metadados adulterados. O overlay combina com patch do corpo sem duplicar IDs, reparseia a estrutura e exige leitura final independente. O campo histórico `named_choice_evidence.label_and_tail_immutable` descreve a fase legada anterior; exceções do overlay são enumeradas separadamente em `speaker_labels.results`. Não interpretar como edição geral autorizada de nomes/cauda.

Calls 0x1C6548/0x1C6DE0 → setter 0x1FD968; strlen 0x2266CC/0x2267F0 conta bytes; pedido ao alocador `(len+4)&~3`, alinhamento16; setter grava destino em objeto+0x34; strcpy escalar 0x2265B4/0x2266AC copia bytes/NUL; getter 0x1FDB00 retorna ponteiro não zero. Instruções originais executadas em memória sintética, com alocador substituído e fonte/destino desalinhados. Sentinelas, padding e origem preservados. Não foram executados cleanup, allocator, cópia SIMD alinhada, GPU, retratos ou PCSX2. Não confundir getter1FDB00 com lookup1FEB00. Validação estrutural não comprova associação visual/limites de todos os caminhos.

367 referências a funções revistas ficam adiadas por capacidade (Man/Homem, Worker/Trabalhador, Transporter/Transportador, Dog/Cão etc.). Não abreviar artificialmente nem remover acentos. Outras607 referências incluem nomes, marcadores e rótulos não selecionados. `tools/prepare_speaker_labels.py` reproduz somente a seleção editorial contra a v033 e cria saídas novas; não é tradutor heurístico/IA. `Auditar-Traducao.cmd` mantém único JSON em work/dialogos-pendencias-atual.json, agora com tradução por referência e contagem de corpos separada. Rótulos continuam sem autorização irrestrita de edição.

57 testes distintos aprovados; delta integral v033→v034:4340 bytes em553 registros MAP, demais bytes/diretório/fontes/arte/interface idênticos. SHA256 `13ecb3029d86b9d85b6dddb738816e646cb112715f5be99463cb5e5026daa2be`, tamanho1704427520. Iniciar-Teste.cmd, Preparar-Interface.cmd e Auditar-Traducao.cmd usam v034; preflight/dry-run, cinco ISOs e alpha readonly/hash conferidos. Sem execução PCSX2, OneDrive ou desligamento. Usuário confere rótulos, acentos, corte e associação com falas/retratos em partida normal. Próxima frente: remanejamento interno de rótulos com folga, somente com prova própria, e contexto das pendências; não crescer registros/SSD nem repetir investigação N$3.
## Continuidade interface/MAP v035 — folga interna dos rótulos

Atual: `translations/interface-v035.json`, base `translations/regiao-inicial-v035.json`, manual `docs/dialogos-v035.md`. Mais239 rótulos (226msgn/13smnn), acumulando792 referências traduzidas. Novos: Homem113, Trabalhador69, Transportador39, Mecânico severo6, Mercador3, Rapaz3, Técnico de manutenção2, Cozinheiro2, Ancião2 (espaço final original preservado). Não houve novo corpo traduzido: continuam5983 corpos/opções e5999 registros MAP com alguma alteração. Interface3526, layoutv005, títulov014, todos os textos/nomes/controles v034 mantidos. Os27 adiamentos de corpos permanecem (19N$3 preservados/8nativos sem contexto). Das367 funções adiadas na v034, restam128 sem folga neste mecanismo; outras607 referências incluem nomes/termos protegidos/marcadores e funções não selecionadas. Não contar rótulos como novas falas.

Política opt-in `map-generic-speaker-label-same-record-tail-borrow-v002`, em `tools/speaker_label_space.py`, aplicada após o compilador de corpos e overlay fixo v034. Hash original do registro/rótulo, hash do registro após as traduções herdadas e target_offset explícito vinculam cada alvo. Somente msgn/smnn/2snm slots sem bloqueios/preservações e roles do mapa editorial existente. Preservar metadados/fingerprints/label.editable=false. Encontrar o NUL real do segmento anterior; exigir só zeros entre ele e o rótulo original e cauda original intacta. Nova posição `(size-bytes_alvo-1)&~3` deve ficar estritamente após NUL e antes do rótulo antigo; sem folga, adiar. Manter corpo/opções/cabeçalhos/terminadores, tamanho do registro, fronteiras SSD e extents ISO. Não tomar espaço de outro registro nem encurtar a fala.

Offsets compilados ficam no wrapper `compiled_speaker_label_offsets`, separado da extração. Reparse estrutural, releitura independente e um único patch por ID. Auditor informa offset/capacidade originais e compilados separadamente. O preparador `tools/prepare_speaker_labels.py --relocate` conserva relocations herdadas e enumera pendentes, sem IA/APIs. Mudanças posteriores nos corpos podem invalidar base_record_sha256/posição: revisar e vincular explicitamente de novo, nunca ignorar a recusa. A política fixa v034 e receitas históricas continuam reproduzíveis.

Probes originais: strchr0x2262C8 com ramo escalar0x22643C..0x226468, alvoNUL e entrada sintética desalinhada; scanners msgn0x1C6508..0x1C6538 e escolhas0x1C6D9C..0x1C6DD0, com branch-likely/delay slots. Executados em memória sintética nos registros antes/depois; posição deve coincidir com a receita. Cinco janelas novas e hash ELF vinculados; probes anteriores de comprimento/alocação/cópia/getter reaplicados. Não foram executados SIMD alinhado, chamador completo, alocador/objetos/GPU/retratos/PCSX2. Não generalizar para outros formatos ou alegar validação visual.

65 testes distintos aprovados; delta integral v034→v035:2368 bytes em239 registros MAP, demais bytes/diretório/fontes/arte/interface idênticos. SHA256 `ddedfe278309fa6e7f1d22d24d08b7bdb5f7406e70b6475e11fb26deb65a8675`, tamanho1704427520. Iniciar-Teste.cmd, Preparar-Interface.cmd, Auditar-Traducao.cmd e default do auditor usamv035; preflight/dry-run aprovados. Cinco ISOs de trabalho, alpha readonly/hash preservada. Sem OneDrive/desligamento/PCSX2. Próximo avanço exige estratégia própria para128 rótulos sem espaço ou contexto das pendências; não repetir tentativas sem evidência, cortar frases para inflar números ou reinvestigar N$3.
## Continuidade interface/MAP v036 — posições de byte dos rótulos

Atual: `translations/interface-v036.json`, base `translations/regiao-inicial-v036.json`, manual `docs/dialogos-v036.md`. Mais75 rótulos (64msgn/11smnn): Homem24, Gato15, Cão11, Transportador9, Alto-falante8, Mercador5, Rapaz2, Ancião1 (espaço final preservado). Total867 referências de rótulos traduzidas. Corpos/opções continuam5983; registros com algum campo alterado6024, sendo25 novos exclusivamente por rótulo. Não contar como75 novas falas. Interface3526, fontes/layoutv005 e títulov014 inalterados. Os27 adiamentos de corpos continuam19N$3 preservados/8nativos sem contexto.

Política opt-in `map-generic-speaker-label-byte-tail-borrow-v003` em `tools/speaker_label_space.py`, campo de receita `speaker_label_byte_packing`, posterior e separado dos overlays v001/v002 herdados. Posição `size-bytes_alvo-1` sem arredondar; somente inícios não alinhados a quatro bytes e estritamente após o NUL anterior/antes do rótulo original. Exigir zeros separadores/cauda original, slots/famílias conhecidos, ausência de bloqueios/preservações, role/target editorial, hashes original/compilado/rótulo e offset final exatos. Não encurtar corpo/opções, editar nomes/controles, mudar cabeçalhos ou crescer registros/SSD/extents. V002 mantém arredondamento quatro; receitas históricas não são promovidas automaticamente. Metadados/fingerprints/label.editable=false intactos; wrapper de offsets acumula239 v002+75 v003 (314 posições), com os553 rótulos fixos na origem.

Leitores originais percorrem os separadores byte a byte, comprovados pelos mesmos probes antes/depois. Acrescentado `byte_copy_probe`: strcpy0x2265B4 escalar com destino alinhado16 e origem em cada classe não alinhada1..7mod8; bytes/NUL/origem/retorno/sentinela conferidos. Na construção, executar as duas classesmod8 compatíveis com o resíduo mod4 do alvo. Probes de comprimento/pedido de alocação/getter anteriores mantidos; SIMD alinhado, alocador, objetos/GPU/retratos/PCSX2 não foram executados. Isso não comprova apresentação visual nem libera outros formatos. `prepare_speaker_labels.py --byte-packed` reproduz a seleção e conserva entradas herdadas do perfil; incompatível com --relocate na mesma preparação. Compilador agora mostra registros alterados e contagens de corpos/opções/rótulos separadas.

Restam53 funções revistas sem folga mesmo por byte: Worker20, Man20, Transporter8 e uma Stern Mechanic/Cat/Maintenance Man/Guy/Dog. Outros607 rótulos seguem nomes/termos preservados/marcadores/funções não selecionadas. Não repetir tentativas em zeros inexistentes nem cortar artigos/acentos. Próximo avanço exige revisão contextual ou nova estrutura com prova própria; avaliar separadores de corpo/opções de escolhas remanescentes antes de cogitar crescimento externo. Não reinvestigar N$3 decidido e não presumir contexto dos oito nativos.

63 testes distintos aprovados; delta integral v035→v036:481 bytes em75 registros MAP, demais bytes/diretório/fontes/arte/interface idênticos. SHA256 `32f2769c7e5b1ef1d4a36bde78e837e74337ea5d24c71c78b4bb7616f01a0036`, tamanho1704427520. Iniciar-Teste.cmd, Preparar-Interface.cmd, Auditar-Traducao.cmd e auditor padrão usamv036; preflight/dry-run aprovados. Cinco ISOs e alpha readonly/hash preservados. Usuário confere rótulos/acentos/corte/fala/retrato em partida normal; sem navegação PCSX2, OneDrive ou desligamento nesta rodada.
## Continuidade interface/MAP v037 — contexto e separadores das opções

Atual: `translations/interface-v037.json`, base `translations/regiao-inicial-v037.json`, manual `docs/dialogos-v037.md`. Mais45 rótulos, acumulando912 referências: Musculoso19, Fiel dirigente17, Fã de ônibus3, Agente do Hunter Office2 e quatro rótulos antigos recuperados (Homem3/Mecânico severo1). Os41 primeiros foram revistos pelo contexto da catedral, do entusiasta das gravações de ônibus e do guichê; Executive Believer foi interpretado como função de organização dos fiéis, não nome de divindade. Não generalizar identidade canônica. Preservar Father Muscle/Gluteus Maximism/Hunter Office e demais nomes. Glossário atualizado. Todos45 registros já tinham falas alteradas: seguem6024 registros MAP com algum campo alterado e5983 corpos/opções traduzidos. Interface3526, fontes/layoutv005 e arte/títulov014 mantidos; os27 adiamentos de corpos permanecem19N$3/8nativos sem contexto.

Política opt-in `map-context-reviewed-speaker-layout-v004`, em `tools/speaker_label_review.py`, campo `speaker_context_review`, posterior às três políticas anteriores. São38 slots originais, três caudas por byte e quatro escolhas nomeadas com opções deslocadas para aproveitar zeros depois da pergunta. IDs smnn0BE243CC/0E76E4BC/0E76FAD4/10340A50. Pergunta na posição original e opções continuam alinhadas4; novo início `(label_start-len_opcoes-1)&~3` deve ficar após NUL da pergunta e antes do início antigo das opções. Exigir zeros dos separadores/cauda original, hashes original/rótulo/compilado, layout e offsets explícitos; preservar byte a byte perguntas/opções/controles/terminadores, cabeçalhos, tamanho e posição dos registros/SSD/extents. Não crescer, abreviar ou liberar repack genericamente. Mapa EXTRA específico das quatro funções; ROLES/políticas anteriores inalterados. Não mudar EXTRA silenciosamente para revisar traduções históricas; criar perfil/versionamento que conserve reprodução.

Nova prova executa scanner original pergunta→opções0x1C6D2C..0x1C6D68, ligado ao NUL obtido pelo helper em0x1C6CC0..0x1C6CD4. Probes de strchr escalar/zeros/rótulo antes e depois, cópia/len/alocação/getter anteriores mantidos; sete janelas e hash ELF vinculados. Handler completo das opções, SIMD alinhado, alocador/objetos/GPU/retratos/PCSX2 não foram executados. Dados de extração/fingerprints/label.editable=false imutáveis. Wrapper `compiled_dialogue_segment_offsets` contém posições compiladas destes45 IDs; acumular também wrapper anterior de rótulos, sem apagar314 posições anteriores. Leitura final independente considera ambos. Um patch por ID e recusa integral em caso de falha. Compilador legado continua recusando labels.

`tools/prepare_speaker_context.py` reproduz seleção contra v036, conserva entradas contextuais herdadas e mantém somente metadados no relatório público. Não usar heurística de nomes/IA/APIs. Mudanças nos corpos podem invalidar vínculos: rever explicitamente antes de reconstruir. Auditor mantém JSON local substituível e agora registra evidência do novo perfil. Restam49 funções antigas sem folga, todasmsgn, e566 referências fora da seleção (nomes/termos/marcadores/funções). Esses49 não têm separador de opções adicional para aproveitar: próxima frente exige revisão contextual ou armazenamento com prova própria, sem repetir zeros inexistentes/cortar frases/remover acentos. Não reinvestigar N$3 decidido nem inventar contexto dos oito nativos.

64 testes distintos aprovados; delta integral v036→v037:633 bytes em45 registros MAP, incluindo deslocamentos internos de quatro opções, demais bytes/diretório/fontes/arte/interface idênticos. SHA256 `e7e65c661409946eb81b8e185c1c71478710cf1aa1538f74a04bd5fbd4c63789`, tamanho1704427520. Iniciar-Teste.cmd, Preparar-Interface.cmd, Auditar-Traducao.cmd e auditor padrão usamv037; preflight/dry-run aprovados. Cinco ISOs e alpha readonly/hash preservados. Usuário confere opções/rótulos em partida normal; sem navegação PCSX2, OneDrive ou desligamento nesta rodada.

## Descoberta consolidada v001 — prioridade antes do próximo lote

Em 25/10/2026 o usuário pediu uma fase inteiramente de descoberta, preparando o
restante do catálogo para tradução posterior em conjunto. Consultar
`docs/descoberta-v001.md` e `reports/descoberta-v001.json`. Base segue v037;
nenhuma receita, fonte, iniciador ou ISO foi alterada. Não retomar pequenos lotes
automaticamente: preparar mecanismos e triagem gráfica por conjuntos, depois
uma tradução ampla consolidada do subconjunto seguro. Pendências inconclusivas
ficam explícitas, sem exigir cobertura absoluta para todo avanço futuro.

`python tools/discover_remaining_catalogue.py` renova somente o catálogo local
`work/descoberta-catalogo.json` e o planejamento local existente. Não usa
IA/APIs/internet. Verifica ISO/journals, hashes de 58 referências e preservação
de 84 receitas; compila validação em memória, sem criar imagem. Originais,
contextos e previews ficam em work/, metadados públicos em reports/. Os 2.838
candidatos ASCII por forma e as 119 texturas reconhecidas em 17 arquivos não são
contagens de textos faltantes. Entradas desconhecidas/comprimidas/nativas ainda
limitam a cobertura. Não declarar 100% do jogo nem promover candidatos por inglês.

Novas evidências: FD_END.SDA entrada0 em0x800 contém LZSS de dicionário zerado
1024, posição1006; 4222 bytes descomprimidos, 292 linhas/209 não vazias.
Decoder original limitado executado em memória sintética e replay exato de
tokens conferido; falta recompressor de texto editado e semântica do renderer.
S_PAINT.SDA entrada22 em0xAE6A0 tem228 registros×36, 12 legendas distintas
repetidas19 vezes. Lookup/forwarding originais conferidos para228; campo+1 de23
bytes incluiNUL, grupo+0 e parâmetros+24..35 preservados. Texturas0x34360/0xCCE0
têm10/3 rótulos observados; falta vincular recortes/uso antes de editar.
Preservar MAIN/SUB/SE. S_PACK nó0x35000 entrada3 em0x7E720 contém25 destinos,
nomes em campo32 seguidos de flags/escritas/caudas variáveis; ponteiros originais
conferidos, consumidores completos pendentes. Cidades permanecem protegidas,
inclusive Junkyard; não reempacotar como pool simples.

Nomes de motores em S_PACK0x320F0 (10×124, 26 campos não vazios) são protegidos;
consumidor não comprovado. Cauda0xF5260..0xF5800 contém cópia de registro de
batalha, mas inatividade não comprovada: não tratar como texto ativo nem folga.
TITLE tem apenas um slot5 em0x32A31E; transições internas estudadas não provam
destino externo. Os49 rótulos restantes são todosmsgn, déficit mínimo1..4bytes,
sem separador adicional. Oito nativos idênticos continuam sem interpretação
aprovada;19N$3 já estão decididos como nomes preservados.

Dos25 nomes de itens pendentes,20 propostas caberiam fisicamente em23bytes+NUL,
mas o teto16 observado continua no compilador até prova de todos os consumidores;
uma exigeÓ e quatro exigem revisão terminológica. Perfil atual tem18 códigos;
faltamÀ/Â/Ê/Í/Ó/Ô/Ú/Ü. Quatorze pares vazios comuns às duas GFI são candidatos,
não códigos liberados. Auditar uso/cache/dois caminhos de layout/métricas antes
de extensão; preservar os18 existentes e ASCII. Nenhuma fonte alterada.
34 testes distintos aprovados (19 novos e15 de preflight/retenção/alpha).
Probes originais limitados não são execução PCSX2 nem validação visual.

## Continuidade interface v038 — legendas da pintura

Usuário autorizou retomar a tradução após descoberta v001. Atual:
`translations/interface-v038.json`, base MAP v037 inalterada, manual
`docs/interface-v038.md`, relatório `reports/interface-v038.json`. Foram
traduzidas doze legendas distintas de cores/padrões, em228 referências
S_PAINT.SDA. Não contar como228 novas frases. Interface acumula3754 campos;
MAP mantém6024 registros alterados/5983 corpos-opções/912 referências de rótulos.
Todas as traduções anteriores, nomes protegidos, fontes/layoutv005 e artev014
foram preservados integralmente. Botões gráficos da pintura ainda pendentes.

Perfil opt-in `paint-caption-fixed-cells-observed-ten-byte-ceiling-v001`,
`tools/paint_captions.py`, seção `paint_captions` da receita. Exige hashes do
recurso inteiro/tabela/ELF/janelas/nomes, doze grupos completos e todos19aliases
de cada nome. Somente campo+1 de23bytes incluindoNUL; teto10bytes codificados,
maior nome observado. Nenhuma liberação de22bytes pelo espaço físico. Preservar
grupo+0, parâmetros+24..35, SDA, offsets e tamanho. Bloquear controles, glifos
desconhecidos, crescimento além do teto e seleção parcial. Não generalizar esse
teto ao nome de itens nem usar perfil para outros recursos.

Encaminhamento construtor/base0x4F810→0x3F838→0x3F910→0x3DB20 inspecionado.
Probes de registradores/strlen/cálculo de alocação `(len+32)&~3` para12origens e
12destinos; setup de registradores salvo e prólogos fornecidos pelo harness.
Não executados alocador, construtor completo, conversão/desenho ouPCSX2.
Leitura independente das228células e round-trip integral conferidos.72testes
distintos aprovados. Comparação integral v037→v038:1748bytes exclusivamente nas
legendas; todos os demais bytes idênticos. ISO1704427520bytes, SHA256
`0b4c931e141de804200d4e42c4fe125f9013707308b1e829871f5159102727c0`.

Iniciar-Teste.cmd usa aliasinterfacev038, Preparar-Interface.cmd valida UIv038
com MAPv037, auditor padrão usa construção v038. Planejador inclui campos de
pintura e contagem distinta12/ocorrências228. Cinco ISOs e alpha preservadas.
Usuário verifica pintura/seleção/acentos/largura em partida normal; não exigir
navegação imediata. Próximo alvo são os rótulos gráficos da pintura, com prova
de recortes/consumidores antes de importar, preservando MAIN/SUB/SE; créditos e
demais bloqueios continuam no mapa de descoberta. Sem OneDrive/desligamento.

## Preparação de edição v001 — correção de prioridade após v038

O usuário esclareceu que esperava mecanismos de edição e triagem gráfica,
não apenas mais legendas traduzidas. Rodada dedicada a essa preparação, sem
nova tradução/ISO/fontes. Consultar `docs/preparacao-edicao-v001.md`,
`reports/preparacao-edicao-v001.json` e `reports/triagem-grafica-v001.json`.
Base jogável segue interfacev038/MAPv037. Pacotes em
`work/preparacao-edicao-v001/`, sem novos.cmd. Imagens/originais/JSONbilíngue
permanecem fora do Git.50testes distintos passaram, onze novos.

`tools/credits_edit_pack.py`: compressor LZSS determinístico1KiB zerado,
posição1006, sobreposição/circulação e flagsLSB; 4222bytes originais recomprimem
em2348 no slot4096 e conferem com decoder original em memória sintética.
Pacote292linhas, somente49cabeçalhos e2frases selecionáveis; outras241imutáveis.
Preservar prefixos nativos opacos, staff/empresas, Atlus, CRLF/ordem/contagem.
Teto35bytes por linha e4222total decodificado,4096comprimido. Sem edição,
reproduzir exatamente o fluxo/recurso original. Não aumentar limites por caber
no disco. Inspecionados leitorCRLF, dispatch# e cópia ao buffer; renderer/fontes
nesta tela ainda não executados. Saída FD_END.SDA em cópia work/, sem ISO.

`tools/paint_button_pack.py`: doze recortes de três texturas S_PAINT,
dez editáveis e duas linhas SUB/SE protegidas. MAIN em linha mista exige revisão
semântica da arte; o importador não fazOCR nem garante texto por pixels. Índices,
paleta/alpha/tamanho, GANM/hotspots e pixels fora dos recortes imutáveis.
Forwarding limitado0x5E250..0x5E284 de textura0xCCE0/tamanho0x2410 eGANM0xF0F0
executado com base/contexto fornecidos. Demais pares são visuais/geométricos,
dispatch completo ainda pendente. Apenas cópia S_PAINT.SDA emwork, sem ISO.

`tools/interface_atlas_pack.py` acrescenta perfil explícito `remaining-v002`
(`remaining-ui-atlases-original-palette-v002`) para119texturas em14recursos,
verificando17fontes. Perfil legado69texturas preservado. Não copiar os três
arquivos sem texturas reconhecidas à saída. Importação indexada preserva todo
restante; não significa UV/uso/ISO aprovados. `tools/triage_graphic_pack.py`
gera folhas e classificação vinculada às fontes. Foram revisadas18folhas com
todos119atlas:18latinos candidatos,1nativo,1misto com categorias protegidas,
6com mecanismos existentes a revisar,6nomes/assinatura protegidos,3marcações
protegidas e84sem palavra localizável observada. São texturas, não frases.
Atlas originais podem ter texto já traduzido na receita; não somar novamente.
365entradas desconhecidas permanecem explícitas, sem cobertura total alegada.

Próximo trabalho: concluir vínculos/uso da pintura, recortes por minijogo,
carregamento/cartazes e apresentação dos créditos; então compor tradução ampla
e consolidar os subconjuntos seguros. Não editar atlas inteiros como se fossem
texto, traduzir nomes dos procurados ou promover automaticamente cópias à ISO.
TITLE, nomes de itens, destinos e nativos sem contexto conservam seus bloqueios.
Round-trips locais executados idênticos; hash ISOv038, cinco ISOs ealpha
conferidos. Sem PCSX2, OneDrive ou desligamento nesta rodada.
