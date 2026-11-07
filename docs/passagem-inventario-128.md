# Metal Saga PS2 — passagem para o projeto de inventário 128

## Pedido e autorizações do usuário

Este documento é uma passagem técnica para outro projeto, não uma ordem para
alterar a tradução. O usuário pediu um patch independente para aumentar o
inventário relatado de 64 para 128 espaços, sobre o jogo original em inglês.

Workspace de destino: `C:\Projetos\MetalSagaInventario`.

O usuário autorizou expressamente nesta passagem:

- Consultar, em modo de leitura, as outras pastas dentro de `C:\Projetos`,
  incluindo a tradução e outros projetos, quando houver relação técnica útil.
- Consultar o repositório público da tradução:
  https://github.com/KernellTozi/MetalSagaTraducao
- Criar um novo repositório no GitHub para o projeto de inventário.

Essa autorização substitui, **no projeto de inventário**, a proibição inicial
de consultar outros projetos. Não concede autorização para modificar esses
projetos, seus repositórios, configurações globais, BIOS ou saves originais.
Se o AGENTS.md inicial do inventário ainda proibir leitura de outros projetos,
atualizá-lo para refletir esta instrução mais recente do usuário.

A consulta é permitida, não obrigatória. Começar pelas evidências PS2 abaixo.
Código de eventual recompilação nativa pode servir como hipótese, mas não
comprova layout, endereço, capacidade, salvamento ou comportamento do ELF PS2.
Não atribuir descobertas de outro executável ao original sem validação.

## Missão inicial para o novo Codex

Continue este projeto com autonomia. Não prometa que basta trocar 64 por 128.
Confirme a estrutura, implemente ferramentas locais e desenvolva uma prova
controlada do aumento. O jogador fará a navegação e testes prolongados.

1. Leia o AGENTS.md e este documento no novo workspace. Confira arquivos
   existentes e trabalho em andamento antes de escrever.
2. Atualize as regras de consulta conforme a autorização acima.
3. Inicialize Git local, se necessário. Use o GitHub autenticado para criar
   `KernellTozi/MetalSagaInventario`, se esse nome estiver disponível.
   Crie-o **privado inicialmente** como escolha conservadora desta passagem;
   não é uma exigência do usuário. Não transforme ou sobrescreva outro repo.
   Se já existir, confira titularidade, remoto e conteúdo antes de reutilizar.
4. Configure `.gitignore` antes do primeiro commit. Versione somente código,
   documentação, decisões e evidências próprias apropriadas. Não envie ISO,
   BIOS, emulador, saves, recursos extraídos ou fontes comerciais.
5. Confirme a origem original. Pode copiar a ISO e extraídos de referência
   da tradução para o novo projeto, sem modificar ou mover a fonte. Confirme
   hashes após a cópia e evite duplicações desnecessárias.
6. Faça a investigação e entregue relatório, ferramentas e, quando houver
   prova suficiente, uma ISO experimental identificada. Não publique um
   patch incompleto como funcional. Não faça uploads de binários/Releases
   automaticamente por causa da autorização de criar o repositório.

## O que ainda NÃO foi descoberto

- O limite 64 é uma observação do usuário, não prova binária desta passagem.
- Não sabemos ainda se o alvo é inventário humano, de veículo, depósito ou
  mais de um deles, nem se o limite corresponde a entradas distintas/pilhas.
- Não foram localizados, para esse objetivo, o array real, alocador, stride,
  campo de contagem, referências, serialização ou checksum do save.
- Não há patch 128, experimento executado ou compatibilidade comprovada.
- Não inferir capacidade de inventário a partir das tabelas de nomes de itens.

Antes de pedir esclarecimentos ao usuário, examine os menus e estruturas
disponíveis. Se existirem inventários diferentes, documente a distinção e
delimite explicitamente o primeiro alvo; não amplie todos por suposição.

## Base original comprovada no projeto de tradução

| Propriedade | Valor |
|---|---|
| Plataforma/edição | PS2, USA / NTSC-U |
| Serial/executável | SLUS-21293 / `SLUS_212.93` |
| ISO original local | `C:\Projetos\MetalSagaTraducao\JOGO\Metal Saga.iso` |
| Tamanho ISO | 1.704.427.520 bytes |
| SHA-256 ISO | `ef8405bf9e34bffd7846bcf3386a73464864823e20cd46ee9dacec514028b403` |
| Extraídos originais | `C:\Projetos\MetalSagaTraducao\JOGO\Metal Saga` |
| SHA-256 ELF original | `25756885a1a01a4ddd82045fd78e1928c09873f810cf182b99b248914fb1ea71` |
| ELF | ELF32, little endian, MIPS, entrada `0x27FD58` |
| ISO9660 | Setores lógicos de 2.048 bytes, PVD no setor 16 |

O inventário técnico da tradução conferiu 58 arquivos extraídos contra os
extents da ISO. A árvore de referência é imutável. `SYSTEM.CNF` aponta para
o ELF acima. Não usar a ISO traduzida v071, manutenção v070 ou patch PT-BR
como base para este novo projeto.

## Formatos e pistas relevantes

### ELF, endereços e instruções

- A tradução já analisou instruções MIPS do ELF original e possui sondas
  limitadas para funções específicas. Elas não são um emulador PS2 completo.
- Vários trechos examinados usam VA = offset de arquivo + `0xFF000`.
  Isso não autoriza aplicar a diferença globalmente: confira os segmentos
  carregáveis e a região de cada endereço.
- A rotina identificada como getter de registro de item está em
  **VA `0x16C938`**. O censo histórico encontrou 190 chamadas diretas;
  elas podem ler atributos ou encaminhar ponteiros, não necessariamente nomes
  ou entradas do inventário. É uma raiz de investigação, não solução pronta.
- O scanner em `tools/item_name_capacity.py` encontrou 54 candidatos de `lw`
  com imediato `0x5AE8` e pesquisou o endereço `0x475AE8`. A origem/base e os
  aliases precisam de rastreamento em cada uso. Não assumir 54 consumidores
  comprovados nem ausência de escrita por não encontrar `sw` semelhante.
- Endereços LUI/ADDIU têm parte baixa assinada; registrar delay slots, contexto
  e registradores. Um LUI pode ser compartilhado por várias instruções.
  Scanner de janelas curtas pode perder referências reais.

### Tabela de itens versus inventário

- `S_PACK.SDA` contém tabelas de recursos, incluindo nomes de equipamentos.
- Registros de item estudados pela tradução têm stride de **128 bytes**;
  o campo de nome ocupa 24 bytes, com atributos/ponteiros a partir de +24
  nos registros examinados. **128 bytes por definição de item não significam
  128 espaços disponíveis no inventário.**
- Consulte `tools/item_names.py`, `tools/item_name_capacity.py` e
  `docs/capacidade-nomes-v001.md` antes de usar esses dados.
- Investigações de buffers de nomes em `docs/buffers-nomes-v002.md` tratam
  formatação de texto. Buffers de 128/1.024 bytes citados ali também não
  comprovam armazenamento de inventário.

### Contêineres e ISO

- SDA observado: magic `73 64 61 00`, tamanho uint32 LE em +4, quantidade
  em +8, tabela de offsets uint32 LE a partir de +0x0C.
- Há contêineres aninhados. Extensões DAT/MCT também podem conter SDA.
- `S_PACK.SDA` possui sete entradas externas em `0x800`, `0x35000`,
  `0x8C800`, `0xB4000`, `0xF5800`, `0x11A000`, `0x11C800`.
- Intervalo até próximo offset é slot, não necessariamente tamanho lógico.
  Padding aparente não é automaticamente espaço disponível para expansão.
- As ferramentas da tradução fazem alterações comprovadas, usualmente
  mantendo tamanhos/extents. Elas não demonstram reconstrução segura com
  arquivos maiores nem expansão de heap/segmentos do executável.

### Textos, fontes e gráficos

- ASCII original e formatos de controle devem ser preservados neste patch.
- O suporte PT-BR usa extensão própria de fonte/codificação e patches de
  métricas/layout. Não é UTF-8 nem suporte direto genérico de CP932.
- **Não importar os patches de acentos, as fontes modificadas ou as receitas
  de tradução**: o objetivo aqui é o jogo original em inglês.
- Alguns títulos/botões são texturas, outros são strings ELF. A aparência
  da tela não identifica sozinha o armazenamento.
- Se a expansão exigir novas páginas/scroll, investigar limites e índices
  dos menus; não redesenhar recursos gráficos sem necessidade.

## Estratégia recomendada de investigação

### A. Demonstrar o limite e rastrear consumidores

Mapear a ligação entre uma entrada visível no inventário, o ID da definição
do item e os dados mutáveis da partida. Separar ID, quantidade, slot, flags,
equipado, destino e tipo de inventário. Distinguir capacidade por personagem
de armazenamento compartilhado e de veículos.

Busca por literais 64/0x40 pode ajudar na triagem, mas não prova o limite.
Rastrear checagem de inventário cheio, inserção, remoção e enumeração;
documentar chamadores e referências, inclusive indiretas.

### B. Memória e salvamento antes da expansão

Provar reserva e ciclo de vida do armazenamento, stride e campos vizinhos.
Verificar buffers temporários de ordenação, transferência e seleção,
máscaras de bits e tipos assinados. **128/0x80 pode cruzar o limite positivo
de um campo assinado de oito bits**; isso é hipótese de risco a verificar,
não uma característica já encontrada no jogo.

Localizar gravação/leitura do save e respectivos comprimentos/checksums,
caso existam. Não inferir formato de save pela estrutura em RAM. Escolher
explicitamente a política para saves antigos: compatibilidade comprovada,
migração controlada ou exigência de nova partida documentada. Nunca editar
o cartão original do usuário para realizar experimentos.

### C. Implementação mínima e testes de fronteira

- Prova reversível, com manifesto dos bytes originais e alterados.
- Estados com 0, 1, 63, 64, 65, 127, 128 e tentativa de 129 entradas.
- Verificar que a 65ª/128ª entrada permanece utilizável após outras operações.
- Testar pilhas repetidas separadamente de itens distintos.
- Compra, loot, uso, descarte, venda, equipar/desequipar, ordenação,
  transferência, itens importantes e avisos de inventário cheio.
- Página/rolagem/seleção da última entrada e retorno aos menus.
- Salvar, encerrar, iniciar limpo e carregar; validar contagens, IDs,
  quantidades, flags, equipamento e dados adjacentes.
- Se usar instrumentação em RAM ou cheats para investigar, identificá-los
  como ferramentas de diagnóstico, não como patch permanente na ISO.

## Ferramentas existentes que podem ajudar

Todas as referências abaixo são relativas à raiz da tradução. Antes de
reutilizar código, conferir imports, caminhos fixos e efeitos colaterais.
Não executar compiladores da tradução apontando para a pasta nova esperando
que sejam genéricos. Copiar/adaptar somente módulos úteis para o novo repo,
registrando procedência, e mudar raízes/guardas para o novo workspace.

| Referência | Utilidade / limite |
|---|---|
| `reports/inventory.json`, `docs/reconhecimento.md` | Arquivos, tamanhos, formatos e hashes; documento antigo tem hipóteses já superadas por manuais posteriores |
| `tools/interface_text.py` | Leitura de seções ELF e scanner conservador de referências, não disassembler completo |
| `tools/item_names.py`, `tools/item_name_capacity.py` | Tabelas/getter de itens, censos e sondas locais |
| `tools/item_name_buffers.py`, `tools/item_name_stream.py` | Exemplos de execução limitada e sentinelas; específicos de texto |
| `tools/build_dialogue_iso.py` | ISO original vinculada por hash e comparação integral com delta esperado |
| `tools/development_iso.py` | Exemplo de controle de acesso/journal; não editar seu estado manualmente |
| `tools/verify_test_iso.py` | Exemplo de preflight ligado a receita/relatório; adaptar ao formato do novo projeto |
| `tools/iso_retention.py`, `tests/test_iso_retention.py` | Retenção de cinco ISOs, proteção de originais, não atravessar links/junctions; fixtures isoladas |
| `tools/start_test.py`, `docs/ambiente-de-testes.md` | Iniciador e ambiente de emulação; não herdar perfil que desative memory card em teste de salvamento |
| `tools/build_public_patch.py`, `release/Aplicar-Patch.*` | Exemplo de distribuição xdelta; adaptar nome, serial, manifestos e estado do novo patch |
| `tests/test_public_patch_applier.py` | Testes de recusa e preservação de partial existente |

O GitHub público permite consultar esses arquivos sem acessar recursos locais.
O código foi publicado sem escolha de licença geral; o usuário autoriza esta
reutilização no seu próprio projeto de inventário. Dependências externas
continuam com suas licenças próprias.

## Construção e entrega do patch

- Aplicar a modificação sempre contra a origem imutável com SHA verificado.
- Recusar bytes de origem inesperados, sobreposição e saída existente.
- Comparar integralmente a ISO gerada, permitindo apenas diferenças previstas.
- Não misturar patch de tradução com patch de inventário nesta fase.
- Guardar receitas/relatórios e limitar ISOs de trabalho a cinco, sem apagar
  originais, saves, backups independentes ou arquivos desconhecidos.
- Depois de validar o mecanismo: VCDIFF/xdelta3 com origem original exata,
  manifesto de origem/resultado e reconstrução integral por hash.
- A tradução usou xdelta oficial 3.2.2, `-a -A= -S none` e decoder oficial,
  com licenças e dependências. Consulte `docs/publicacao-patch-v071.md`.
- Aplicador offline deve preservar original, recusar destino/partial já
  existentes e remover somente temporários criados pela própria execução.
- Teste automatizado, execução limitada e hash correto não substituem teste
  real no jogo, sobretudo salvar/carregar inventário expandido.

## Primeira entrega esperada

Relatório que comprove o limite e identifique a estrutura/consumidores;
scripts de análise reproduzíveis; decisão fundamentada de viabilidade para
128; plano de compatibilidade de save. Se ainda não houver prova suficiente,
entregar descobertas e bloqueios concretos sem forçar um patch inseguro.

Esta passagem não contém testes de inventário novos. Os hashes, formatos
e ferramentas citados vêm do trabalho anterior da tradução; a aplicação
ao aumento de capacidade ainda precisa ser demonstrada.
