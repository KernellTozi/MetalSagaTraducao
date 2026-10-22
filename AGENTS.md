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
- Prioridade atual: avançar em lotes maiores por cenas/regiões, com tradução contextual, validação local e uma ISO consolidada por lote. O Codex decide a ordem técnica sem perguntar qual recurso traduzir primeiro. O lote atual está em `translations/regiao-inicial-v007.json`; consultar `docs/regiao-inicial-v007.md`. Preservar integralmente os prefixos anteriores; a v007 tem 511 registros e mantém quatorze bloqueios, sem liberar controles opacos. Preservar nomes e enganos intencionais como Dr. Martin na fala de Biff.
- Regras de tradução do usuário: preservar Hunter e Soldier; mecânico pode ser traduzido. Preservar personagens, tanques, cidades, procurados/wanted e nomes únicos de equipamentos, motores, componentes e inimigos. Locais genéricos podem ser traduzidos, exceto a primeira cidade, que fica em inglês. Traduzir junk como sucata, não lixo; manter expressões/risadas e empréstimos usuais como punk e upgrade. Adiar itens/inimigos se o espaço criar dificuldade. Contexto e naturalidade têm prioridade; nunca omitir artigos para caber. Glossário em `docs/glossario.md`, verificações em `translations/politica.json`.
- Manter no máximo dez ISOs de trabalho sob `work/`; `tools/iso_retention.py` remove as mais antigas elegíveis antes de novas construções. Não tocar na ISO original, links, arquivos desconhecidos, recursos de recuperação ou ISOs fixadas pela política. Preservar receitas e relatórios quando uma ISO antiga for removida.
- Testes com ISOs fictícias devem simular a retenção global e executar remoções reais somente em raízes temporárias isoladas. Consultar `reports/iso-retention-test-isolation.json`. A ISO experimental ASCII v001 foi removida antecipadamente por uma contagem de fixture já corrigida; plano e relatório históricos foram preservados.
- O experimento do diário permanece preservado mesmo enquanto sua exibição não estiver confirmada. O piloto atual de diálogos é a fala sobre tornar-se Hunter.
