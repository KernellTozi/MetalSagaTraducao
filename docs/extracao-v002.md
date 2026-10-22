# Consolidação da extração MAP.MCT — v002

## Resultado e significado das classes

O iniciador continua sendo `Extrair-Dialogos.cmd`, Python 3.11+, sem rede, IA,
APIs ou bibliotecas externas. Nesta entrega não houve tradução, edição de fontes,
execução do PCSX2 nem criação de ISO.

| Classe | v001 | v002 | Garantia |
| --- | ---: | ---: | --- |
| Extração validada | 2049 | 4438 | Perfil de texto reconhecido, enquadramento e seis vizinhos verificados; round-trip exato |
| Identificado, bloqueado para edição | 0 | 1702 | Layout local e texto recuperados sem perda; controles, codificação ou contexto exigem cautela adicional |
| Estrutura desconhecida | 4131 | 40 | Não foi comprovado um payload textual pelo parser; bytes completos preservados |
| Assinatura rejeitada | 31 | 31 | Falha objetiva em alinhamento/localização/tamanho; não equivale a provar que todo o recurso é falso |

Foram recuperados **4.091 registros adicionais**: 2.389 na classe validada e 1.702
na identificada. São **6.140 ocorrências com texto recuperado**, dentro das 6.211
assinaturas da varredura anterior. Os 2.049 registros da v001 permanecem exatamente
iguais, inclusive IDs, textos, controles, cabeçalhos e metadados dos vizinhos.

“Validado” nesta tabela se refere à **extração estrutural**, não à aprovação visual
de cada fala nem à existência de um editor genérico para os novos perfis. Todos os
perfis v002 têm `editable: false` e política de edição ainda não implementada. Não
foram relaxadas as verificações de seis vizinhos do perfil validado. Registros sem
esse contexto ficam identificados e bloqueados, mesmo quando seu texto é legível.

## Evidência do executável e parsers distintos

ELF de referência: `SLUS_212.93`, SHA-256
`25756885a1a01a4ddd82045fd78e1928c09873f810cf182b99b248914fb1ea71`.
Nos trechos examinados, offset no ELF = endereço virtual − `0xFF000`.

| Endereço virtual | Offset ELF | Evidência |
| --- | --- | --- |
| `0x2BD4B4` | `0x1BE4B4` | Comparação fourcc `msg` |
| `0x2BE134` | `0x1BF134` | Comparação fourcc `msgn` |
| `0x40A884` / `0x40A84C` | `0x30B884` / `0x30B84C` | Entradas dos dois carregadores apontam para `0x2C5228` |
| `0x2C5228` | `0x1C6228` | Passa três parâmetros ao carregador compartilhado |
| `0x2C5248` | `0x1C6248` | Copia parâmetros, calcula `3 × 8 + 8` e armazena ponteiro de texto em `+0x20` |
| `0x2C23A0` | `0x1C33A0` | Copia unidades de oito bytes após o cabeçalho inicial de oito bytes |
| `0x2C548C` | `0x1C648C` | Tratamento `msgn`: procura TAB e NUL, percorre zeros e encaminha a segunda string à interface |

O ramo `msg` usa o tratamento em `0x2C5298`; `msgn` usa `0x2C5410`.
A análise inicial usou Capstone local para instruções MIPS básicas, reconhecendo
que ele não decodifica corretamente todas as extensões R5900. A ferramenta de
reprodução usa somente a biblioteca padrão e verifica words/opcodes específicos,
destinos JAL e hashes das janelas, sem depender do disassembler.

`parse_msg` exige cabeçalho de 32 bytes, texto não vazio terminado em NUL e zeros
até o fim do registro. `parse_msgn` exige o mesmo início textual, mas interpreta
separadamente o NUL, o intervalo de zeros, a segunda string terminada e o padding
final zero. O intervalo não é presumido como alinhamento de quatro bytes. Tudo
é reconstruído preservando inclusive esse intervalo.

Exemplos reproduzíveis de `msgn`: `0x1139C` (176 bytes), `0x11474` (164 bytes),
`0x11548` (192 bytes). A segunda string foi recuperada em **1.415 registros**.
Três assinaturas `msgn` não passaram nesse parser e ficaram desconhecidas.
Offsets, hashes de registros representativos e contagens estão em
`reports/dialogue-formats-v002.json`; textos e bytes extraídos ficam em `work/`.

## Controles e codificação

O texto continua ancorado em bytes originais, sem remoção ou normalização. TAB
`09` e LF `0A` têm posição registrada. As sintaxes numéricas observadas de
`%F`, `%N`, `%W`, `%P` e `%M` recebem tokens com offsets e bytes; `%M` permite
parâmetros negativos, como `%M-1_5`. Isso identifica a sintaxe, não demonstra todos
os efeitos de cada comando. Não se move, interpreta ou executa o comando.

Formas como `%N$0`, `%I$0`, `%B$15`, `%$15`, `%M_1` e `%NO` ficam opacas e
bloqueadas. O tokenizador marca o prefixo reconhecível; o texto-fonte e os bytes
completos preservam também qualquer sufixo cuja gramática não foi resolvida.
Não se deve usar esses tokens parciais como política de edição ou de tradução.

Foram recuperados **14 registros com sequências nativas de dois bytes**,
incluindo japonês e um símbolo estrela. Exemplos: `0x040EF0EC`, `0x07B264E0`,
`0x128226B4`. O decoder segue as formas de bytes do leitor já investigado e usa
CP932 estrito para representar em Unicode apenas sequências que reencodam nos
mesmos bytes. Preserva ainda cada sequência, offset relativo e índice JIS.
Isso não afirma que o arquivo inteiro é CP932 nem que exista suporte nativo a
acentos PT-BR. Bytes UTF-8 podem coincidir com sequências válidas de outro código;
não há tentativa de “detectar automaticamente” UTF-8. Os 14 registros continuam
identificados, sem aprovação de cobertura dos glifos em cada fonte/contexto.

## O que ainda bloqueia a promoção

| Motivo exclusivo na classe identificada | Quantidade |
| --- | ---: |
| Contexto completo de instruções não comprovado | 1513 |
| Sintaxe opaca de controles | 150 |
| Sintaxe opaca e contexto incompleto | 25 |
| Bytes nativos, cobertura/execução não validada | 7 |
| Bytes nativos e contexto incompleto | 7 |

A classe identificada inclui os 403 casos de fronteira anterior ambígua e os 235
com problemas em tags/tamanhos dos vizinhos da v001. Também inclui diálogos curtos
próximos às fronteiras de blocos, sobretudo `msgn`. O parser de payload foi
comprovado independentemente, mas não se inventou um enquadramento global para
transformar esses casos em registros editáveis.

Os **40 desconhecidos** têm marcadores `ssd` dentro do intervalo que seria seu
suposto registro: 37 assinaturas `msg` e 3 `msgn`. Exemplos: `0x057CEA28`,
`0x0DB1092C`, `0x1DF6A308`. Há ocorrências nas quais `msg` é imediatamente seguido
por `ssd`, fazendo os bytes do marcador parecerem índice/tamanho. O parser de
cabeçalho fixo falha corretamente. Foram examinados o payload, as fronteiras,
os marcadores e o despacho do ELF; não foi comprovada uma gramática completa
do contêiner ou das tabelas adjacentes. Não se afirma que os 40 são falsos positivos.

As 31 rejeitadas mantêm os motivos anteriores: 19 de localização/alinhamento e
12 de tamanho. Uma ocorrência não alinhada em `0x10CF57ED` está contida na tag
`smsg` iniciada um byte antes; isso comprova que aquela ocorrência não começa
uma instrução `msg`, mas não resolve o formato `smsg`. Outras ocorrem em regiões
com dados não enquadrados como instruções. Não foram reclassificadas só pela aparência.

Próxima investigação recomendada: gramática de limites dos blocos `ssd`, tabelas
adjacentes e variantes como `smsg`. Isso poderá recuperar contexto sem reduzir o
rigor dos parsers. Os números atuais não são uma contagem de 100% dos textos do jogo.

## Catálogo e contexto

`catalogo-consolidado.jsonl` contém exatamente uma linha por ocorrência/offset,
com `classification` e `record`. Os arquivos de cada classe são visões separadas,
não novos IDs nem duplicações internas do consolidado. Ocorrências de textos
iguais em offsets diferentes permanecem distintas. Os 6.140 registros textuais
não se sobrepõem fisicamente; IDs/offsets duplicados ou sobreposição impedem
a conclusão da extração.

Os novos itens preservam parâmetros brutos de oito bytes, cabeçalhos, índices,
capacidades, bytes do diálogo, nomes, sufixos, controles e offsets. O rótulo de
`msgn` fornece contexto útil, mas pode ser genérico e não é um identificador
canônico do falante. Não foi estabelecido um mapeamento de cena ou retratos.
Os 2.049 itens antigos não recebem campos novos para preservar igualdade exata.

## Reprodução e validação

```powershell
python -m unittest discover -s tests -v
python tools/extract_dialogues.py --output work/extracoes/minha-consolidacao-v002
python tools/probe_dialogue_formats.py --catalog work/extracoes/minha-consolidacao-v002 --output reports/formatos-minha-execucao.json
```

O mesmo `Extrair-Dialogos.cmd` chama automaticamente a versão atual. O catálogo
entregue está em `work/extracoes/catalogo-v002/`. Novas execuções sem argumentos
usam pastas datadas. Nenhuma saída existente é sobrescrita.

Foram aprovados 36 testes, incluindo parsers separados, strings nomeadas com
diferentes intervalos, padding/terminadores inválidos, controles, parâmetros
negativos, sequências nativas estritas e bloqueio de contextos ambíguos. Na execução
real, todos os 6.140 registros textuais tiveram reconstrução binária idêntica,
os 2.049 anteriores passaram na comparação integral/fingerprint, o plano ASCII
sem edição produziu zero patches e o hash do MAP permaneceu inalterado. O fingerprint
v001 usa explicitamente a representação JSONL Windows CRLF registrada no relatório
antigo, inclusive quando o script é executado em outro sistema.

A memória continua usando `mmap`, saída incremental e metadados dos subconjuntos;
não se copia o MAP inteiro para um buffer Python. Relatório de execução atual:
`reports/extrator-v002-validation.json`. As limitações de reinserção descritas no
manual permanecem; a nova contagem não autoriza tradução em massa.
