# Interface v016 — mensagens do Satcom e fichas de procurados

Lote consolidado sobre a v015: **119 campos novos**, sendo os corpos das **41
mensagens** conhecidas desta tabela do Satcom, **38 assuntos** e as descrições
das **40 fichas de procurados**. São **1.039 campos/ocorrências de interface**,
sem contar nomes preservados como tradução. MAP v030, layout v005 aprovado,
arte do título v014 e todas as traduções da v015 permanecem idênticos.

## Conteúdo e contexto

As mensagens incluem os desafios de Lloyd/Duke/Guermo, convites de Scarlet e
Rosa Beldaire, correspondência de Eddy, dicas de garagem de Nina, construção
de tanques com Dr. Palm, tutoriais Hunter, avisos de reboque/ferrovia e eventos
da campanha. Cada mensagem foi revista com remetente, assunto e corpo juntos.
Os textos formais de serviços e o tom familiar de Eddy foram tratados separadamente.

Os nomes dos procurados permanecem em inglês; suas descrições, rumores,
localizações e avisos agora estão em português. Preservar as distinções entre
rumor e fato, direções geográficas e instruções de missão. Junkyard continua
em inglês mesmo quando aparece em minúsculas no original. Montanha de Sucata,
Grande Destruição, Ferrovia Continental, Mar de Areia, Toca da Cobra e cortina
de areia acompanham o glossário e os diálogos existentes. MAIN/SUB/SE e Hunter
são preservados, assim como nomes próprios e termos únicos.

Dos **203 campos identificados** nessas tabelas, 119 são traduzidos e 84
permanecem intactos: 41 remetentes, 40 nomes de procurados e três assuntos
(`Arthur Beldaire`, `Fire Truck`, `SOS!`). Isso preserva também remetentes
genéricos, como serviços, ainda em inglês. Não significa que todos os recursos
de correio ou de interface do jogo tenham sido descobertos.

## Estruturas comprovadas e política

Opt-in `spack-satcom-mail-wanted-bounded-v001`, em `tools/spack_satcom.py`.
A receita Unicode está no único `translations/interface-v016.json`; textos
originais, revisão e bytes completos ficam somente em `work/`.

| Recurso em S_PACK.SDA | Entrada do SDA em 0x35000 | Offset | Tamanho | Registros |
|---|---:|---:|---:|---:|
| Mensagens | 13 | 0x86700 | 0x1F10 | 41 |
| Procurados | 14 | 0x88610 | 0x1960 | 40 |

Ambos começam por count e offsets relativos de 32 bits, estritamente crescentes
e alinhados a quatro bytes. Não alterar contagens, offsets das tabelas, limites
dos registros, SDA pai, comprimento do arquivo ou extents ISO.

**Mensagem:** quatro bytes de metadados imutáveis, remetente NUL, assunto NUL
e corpo NUL, seguidos por cauda preservada. Os metadados observados são 0–3;
não foram interpretados como identidade de personagem ou estado canônico.
O último registro termina numa cauda `00 00 00 C1`, de significado desconhecido.
O C1 e a posição da cauda não são modificados nem usados como capacidade extra.

O leitor percorre remetente e assunto por strlen. Assim, assunto/corpo podem
ser recompostos **dentro do mesmo registro**, após o remetente intacto. Cada
campo fica limitado ao próprio comprimento original em bytes; o fim do espaço
editável continua sendo o fim original do corpo com NUL. Sobras recebem zeros,
sem invadir a cauda. A posição do corpo pode recuar, mas o leitor comprovado
a recalcula. Não se trata de realocação geral ou de autorização para outros SDA.

**Procurado:** metadados nos primeiros 16 bytes, nome no slot 16..43 e descrição
em +44 (0x2C). Só a descrição é editada, sem crescer frente ao próprio texto
original. Metadados, nome completo, terminador e padding do nome são imutáveis.
Os valores de recompensa não mudam.

Guardas comuns: hash integral de S_PACK e ELF, hashes das duas tabelas e de cada
registro/campo, IDs únicos, leitura de volta, identidade sem edição e reversão
binária. Não aceitar bytes nativos como ASCII nem introduzir NUL/TAB/CR/LF.
Codificação pela extensão GFI PT-BR existente, com encode/decode reversível.

Os únicos tokens variáveis observados/liberados aqui são **%N0 e %B0**, além de
pipe como quebra. Sequência e quantidade exatas são preservadas por campo,
assim como números literais. Isso **não libera** `%N$0`, `%B$0` ou outros controles
MAP por semelhança. Não foi alterado nenhum handler de variáveis.

Mantêm-se quantidade de linhas e limite máximo de caracteres por linha do
próprio original, sem corte de palavras ou retirada de acentos. Essa guarda
de colunas não é medição exata de pixels. Os consumidores usam expansão em
buffers de pilha; o lote não presume capacidade geral desses buffers e não
aumenta os campos ou a quantidade de tokens que podem expandir.

## Evidências dos consumidores

As janelas de instruções são vinculadas por hash na receita e no relatório.
O disassembly genérico foi usado apenas para investigação: as operações de
salvamento R5900 LQ/SQ são tratadas por opcode no probe, sem aceitar os aliases
de outras arquiteturas sugeridos pelo disassembler.

- `0x6CEF4..0x6CF10`: seleciona as entradas SDA 13/14 e guarda seus ponteiros em
  VA **0x475B2C/0x475B34**. O helper SDA original também confirma os offsets.
- Getter de mensagem `0x71AE0..0x71B6C`: resolve
  `base + u32(base+4+ID*4)`, copia metadados e entrega remetente em saída +8,
  assunto em +12 e corpo em +16. Os dois strlen percorrem as strings NUL.
- `0x124128..0x124134`: a tela pede o registro ao getter. `0x124244..0x124264`
  prepara o cabeçalho, e `0x12430C..0x124324` encaminha o corpo da saída +16
  ao expansor VA 0x20D0E8, depois ao consumidor VA 0x20D608.
- `0x123F44..0x123F7C`: a lista lê remetente/assunto das saídas do mesmo getter.
- Expansor em `0x10E0E8..0x10E250`: mantém os dois bytes dos caracteres,
  resolve N/B conforme argumentos existentes e converte pipe em LF. A tradução
  preserva os tokens; não simula todos os nomes/estados possíveis da partida.
- `0x1D7A08..0x1D7A40`: seleção do registro de procurado por ponteiro relativo.
  `0x12C138..0x12C150` usa nome +16 e recompensa +12;
  `0x12C1F4..0x12C20C` encaminha descrição **+44** ao expansor e consumidor.

O probe executa o getter original das 41 mensagens antes/depois, em RAM sintética,
com delay slots e salvamento/restauração dos registradores. As duas chamadas
a strlen usam o probe limitado já existente do caminho não alinhado do contador
original. Não se executam I/O, GPU, alocador, expansão completa ou o jogo.

## Executar e testar

Abra `Iniciar-Teste.cmd` ou `Testar-Interface.cmd`. A ISO consolidada é
`work/interface-v016/MetalSaga-ptbr-interface-v016.iso`.

O usuário faz a validação visual, em inicialização limpa, sem carregar save
state antigo: abrir mensagens já recebidas, conferir lista, assunto, remetente,
quebras e acentos; abrir as fichas disponíveis e conferir nome, descrição e
recompensa. Quando aparecerem naturalmente, conferir mensagens com nome variável
e apelido dado por Dr. Palm. Não é necessário atingir todas as cenas imediatamente.

Reprodução inteiramente local:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v016.json --output work/interface-reproducao-v016 --compact-output --build-iso
python tools/plan_interface_menus.py
python -m unittest discover -s tests -p "test_interface*.py" -v
```

Só uma ISO e `relatorio.json` na pasta da construção. O planejamento atualiza
o mesmo JSON local, agora incluindo os 203 campos de Satcom; não gera arquivos
por mensagem. A alpha e a retenção de dez ISOs de trabalho permanecem.
Sem cópia para OneDrive ou execução do PCSX2 nesta rodada.

Próximos alvos: composição bloqueada de melhoria, lacunas contextuais da interface
e preparação das tabelas de nomes/descrições de itens para lote amplo. Não editar
outras entradas S_PACK automaticamente por semelhança com estes registros.

## Validação executada

- **96 testes de interface** passaram em 276,865 s, incluindo os nove testes
  novos de Satcom. **Seis testes de planejamento** passaram: 102 testes distintos.
- Leitura de volta dos campos, identidade/reversão, metadados/nomes/offsets,
  cauda C1, tokens/linhas/números, hashes, IDs, limites e recusa de bytes nativos.
  Getter original das 41 mensagens antes/depois e contador original para todos
  os textos de ambas as tabelas, nos probes limitados descritos acima.
- Comparação integral v015→v016: **10.962 bytes diferentes em 81 patches de
  registros**; todos os bytes restantes e o diretório ISO são idênticos.
  Foram traduzidos 11.596 bytes de conteúdo de origem em 9.734 bytes de destino,
  mantendo todos os limites; esses números não são porcentagem do jogo.
- ISO de **1.704.427.520 bytes**, SHA-256
  `61243a5795a907aac9f235431c6da3da508780aa7750d4e47bccf1e8a3a1929e`.
- Iniciador conferido sem executar o emulador. Dez ISOs de trabalho após a
  retenção; alpha preservada. Resumo/evidências/delta no único relatório
  `reports/interface-v016.json`. A validação visual permanece pendente.
