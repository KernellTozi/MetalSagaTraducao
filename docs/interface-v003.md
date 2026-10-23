# Interface v003 — sistema, diário e estatísticas

## Resultado e escopo ampliado

Esta rodada acrescenta **200 campos**, chegando a **473 textos de interface** acumulados. Mantém integralmente as 273 entradas anteriores, os 5.892 diálogos traduzidos v029 e o layout v005. O volume de origem tratado é 13.949 bytes, contra 2.746 na rodada anterior: **5,08 vezes mais texto**. Contagens de campos não são porcentagem de tradução do jogo.

| Recurso | Novos campos traduzidos | Escopo |
|---|---:|---|
| NDATA.SDA | 98 | Memory Card, verificação, salvar/carregar, formatação, erros, espaço livre, pinturas, HD e confirmações |
| DIARY.DAT | 100 | 65 corpos e 35 títulos, em 65 registros do diário |
| SLUS_212.93 | 2 | Quadro de seis estatísticas e cabeçalho de veículos alugados |

No diário, nomes de personagens, cidades, veículos, procurados e itens únicos permanecem. Montanha de Sucata e Grande Destruição seguem o glossário; Junkyard permanece em inglês como cidade. O ferro-velho de Newfolk é uma referência genérica distinta da cidade Junkyard. Os controles `%N1` a `%N9` existentes são preservados literalmente; isto **não libera** comandos N de outras famílias no MAP.MCT.

Os corpos 16 e 31 do diário contêm bytes nativos desconhecidos e continuam intactos. O corpo 62 é uma expressão de silêncio, também preservada. Existem títulos mantidos no original por nomes próprios ou por permanecerem fora do lote; não declarar o diário 100% traduzido. Em NDATA, são 99 linhas originais nas duas tabelas; a linha que contém somente ponto permanece igual e não conta como tradução.

## Como usar

`Preparar-Interface.cmd` compila e valida localmente sem criar uma ISO nova. `Testar-Interface.cmd` ou `Iniciar-Teste.cmd` abre:

`work/interface-v003/MetalSaga-ptbr-interface-v003.iso`

Reconstrução a partir dos originais, usando uma pasta de saída nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v029.json --interface-draft translations/interface-v003.json --output work/interface-v003 --build-iso
```

Novo exportador local dos recursos comprovados:

```powershell
python tools/interface_resources.py --output work/interface-recursos-novo.json
```

Exporta 99 mensagens do sistema e 136 campos de diário com IDs, offsets de origem, capacidades, hashes, controles e bytes originais. Os dois corpos nativos ficam marcados como não editáveis. O arquivo com textos originais deve permanecer em work/, fora do Git. A exportação não traduz nem altera a ISO e não usa internet, IA ou APIs.

## Evidência de NDATA.SDA

O SDA raiz tem 203 entradas. Somente duas tabelas foram liberadas nesta versão:

| Entrada | Offset no SDA | Tamanho lido pelo jogo | Linhas | Descritor no ELF |
|---|---:|---:|---:|---:|
| 186 | 0x110D800 | 0x1357 (4.951) | 79 | 0x320B00 |
| 200 | 0x1344800 | 0x43B (1.083) | 20 | 0x348FF0 |

Os pares offset/tamanho no executável coincidem com as posições das entradas e com os comprimentos dos textos, sem zeros de alinhamento. Os consumidores formam os endereços dos descritores em `0xC11E8/0xC11EC` e `0xCDDB0/0xCDDB4`, carregam os recursos pela chamada em VA `0x195968` e passam o buffer/tamanho ao leitor em VA `0x194B10` nas chamadas `0xC125C` e `0xCDE00`. Os PCs documentados são offsets de arquivo, salvo quando explicitamente marcados como VA.

O leitor está no arquivo em `0x95B10`: conta CR/LF no intervalo `0x95B68..0x95BB4`, pula o LF de um par CRLF e aloca tabelas de ponteiros. O processamento seguinte reconhece os delimitadores, copia pares multibyte e converte `|` em quebra de linha na memória. O buffer temporário começa no stack frame antes de `0x200`; a política conservadora limita cada linha a **511 bytes**, incluindo os separadores internos. As janelas de instruções e seus hashes estão vinculados em `tools/interface_resources.py` e no relatório de evidência.

`execute_count` executa **as instruções originais do contador** em memória simulada, incluindo delay slots e branch-likely. Os testes conferem CR, LF, CRLF, bytes de acentos e zeros ao final, com 79/20 registros antes e depois. Não executa I/O, alocação, classificador de fontes ou o jogo completo; os resultados não substituem o PCSX2.

A política `ndata-crlf-and-diary-fixed-v003` recompõe cada uma dessas duas tabelas dentro do **mesmo intervalo originalmente lido**. Pode variar o comprimento das linhas, pois os ponteiros são construídos pelo leitor; ordem, IDs, quantidade e CRLF permanecem. Não utiliza os bytes extras do slot SDA. Completa o intervalo com NULs, que não acrescentam registros ao contador. Conserva a ordem exata de `|`, `$MD$`, `$MP$`, `$MEM$` e `$HDD$`. Assim, “No” pode virar “Não” neste formato sem depender do slot ELF de dois bytes ou de remover acentos.

As demais entradas de NDATA não foram liberadas por semelhança. A tabela de instalação de HD da entrada 12, páginas de ajuda em HTML e texturas continuam pendentes de seus próprios perfis.

## DIARY.DAT e literais do ELF

Reaproveita `diary.fields` para os 68 registros/136 campos originais. O compilador novo aplica o codec do projeto somente a campos ASCII revisados, dentro dos slots comprovados, com NUL/padding e metadados fixos. Mantém cabeçalhos, tabela de offsets, rótulos preservados e bytes nativos intactos. O editor legado ASCII não foi alterado. A receita vincula a fonte/layout v005 compatíveis com os pares PT-BR; não é CP932 comum. A política terminológica compartilhada é conferida também nestes campos. Nomes próprios exigem caixa exata aqui para distinguir junkyard genérico da cidade Junkyard; profissões e expressões mantêm as regras existentes.

As estatísticas em `0x32C6C0` e o cabeçalho em `0x32C810` não tinham NUL imediatamente antes, razão pela qual não entravam no catálogo anterior. A hipótese anterior de um wrapper consumido junto do texto não é necessária para estes dois casos: as instruções originais passam **diretamente o endereço do literal** ao método formatador em VA `0x20D608`, em `0x122328` e `0x122560`. Os bytes anteriores permanecem intocados, sem atribuir-lhes uma estrutura não comprovada.

O perfil opt-in `two-proven-format-literals-v003` admite somente esses dois offsets, verificando as janelas de consumidor, referências e ausência de aliases interiores reconhecidos. Mantém os seis `%4d` na mesma ordem e as seis quebras do quadro de estatísticas. O cabeçalho passa a “Nome”, SP e “Obus”; os nomes dos veículos não mudam. O catálogo legado de 4.297 candidatos permanece igual; não houve relaxamento global da regex. A nomeação em `0x33B3B8` continua fora do perfil.

## Integridade e validação visual

- **37 testes direcionados passaram**, sem falhas/erros/skips. Incluem regressão v002, diário legado, fontes/layout, proteção da alpha, retenção, round-trip e casos negativos de IDs, fontes, delimitadores, controles e orçamentos.
- A exportação local também foi executada: 99 mensagens e 136 campos, com dois corpos bloqueados.
- A ISO tem 1.704.427.520 bytes; SHA-256 `f3fd86e2df37ff6fb7bf77d18fc39afd7bc776f9828f426029651e59787eccc1`.
- Comparação integral com v002: **13.285 bytes diferentes**, somente nos 104 patches correspondentes aos 200 novos campos. Os patches de tabela agrupam várias mensagens; não confundir número de patches com número de traduções.
- MAP.MCT, fontes e todos os bytes fora dos intervalos revisados permanecem idênticos à v002. Diretórios ISO9660, extents e tamanho mantidos. A alpha foi novamente conferida pelo hash e continua somente leitura.
- Mantidas dez ISOs sob work/; a imagem experimental de layout v004 foi removida como a mais antiga elegível. A alpha permanece adicionalmente em dist/, fora da retenção. Receitas/relatórios históricos preservados.

Evidências: `reports/interface-v003-validation.json`, `reports/interface-v003-format-evidence.json` e `reports/interface-v003-tests.json`. Não foi executado o PCSX2 nesta rodada. O iniciador foi conferido em dry-run.

Roteiro consolidado: fechar a instância anterior, iniciar esta ISO sem restaurar savestate e conferir os avisos normais de verificação/carregamento, escolhas Sim/Não, seleção de slot, diário (primeira página esperada: “Tarefas”), estatísticas e aluguel de veículos. Verificar acentos, número de linhas, cortes, colunas, valores variáveis e nomes. Não é necessário provocar formatação de cartões, falta de espaço ou corrupção para testar; BIOS, cartões e saves existentes foram preservados. A aprovação das fontes nas falas de Nina não comprova a renderização desses novos contextos.

Próximos conjuntos: ajuda e conteúdo de mensagens, título/legendas de nomeação e demais textos desenhados em imagens, mantendo a prioridade de interface antes de itens. Os pequenos controles MAP continuam pausados. Nenhuma cópia para OneDrive é feita sem pedido explícito.
