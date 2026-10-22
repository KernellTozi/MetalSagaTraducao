# Experimento de acentuação v001

## Estado e finalidade

ISO separada: `work/MetalSaga-ptbr-acentos-v001.iso`. Validação binária concluída;
**validação visual preliminar realizada manualmente pelo usuário** nas telas A e B
de Nina. Os grupos minúsculos e maiúsculos apareceram, permaneceram dentro da caixa
e não houve travamento relatado. Não constitui aprovação de toda a tipografia,
de ambas as fontes individualmente ou de todos os contextos. Não contém a edição
do diário. Não altera as ISOs anteriores. A fala ASCII “Quer ser um / Hunter?”
foi confirmada pelo usuário em captura de tela; a evidência dos acentos é o teste
posterior separado, identificado em `reports/acentos-v001-validation.json`.

As capturas mostram marcas visíveis e espaçamento largo. Deslocamentos aparentes
podem envolver o desenho composto dos glifos e seu avanço de célula inteira;
não foi isolada a causa por caractere. As maiúsculas usam corpos comprimidos
verticalmente para reservar o topo, diferentemente de várias minúsculas. O mesmo
mapeamento funcionou nos dois grupos, mas a qualidade de cada diacrítico ainda
não foi aprovada. Não é possível identificar somente pelas capturas qual das duas
GFI foi usada. Menus, diário e outros leitores continuam sem validação equivalente.
Nenhuma fonte foi alterada após esse retorno. A investigação tipográfica fica
adiada: não existe impedimento de fontes para extrair os bytes originais.

Não foi identificado suporte nativo seguro aos 18 caracteres solicitados. Foi
construída uma extensão experimental de fontes, usando códigos cujo caminho até
os bitmaps foi identificado no executável. Não inserir bytes de UTF-8 ou CP1252.
O codec CP932 do Python rejeita todos os 18 caracteres; isso, isoladamente, não
seria prova da codificação do jogo. As evidências abaixo vêm do leitor do ELF.

## Evidências de codificação e fontes

ELF de referência `SLUS_212.93`: SHA-256
`25756885a1a01a4ddd82045fd78e1928c09873f810cf182b99b248914fb1ea71`.
Nos trechos analisados, endereço virtual = offset no arquivo + `0xFF000`.

| Offset no ELF | Evidência |
| --- | --- |
| `0x197098` | Inicializa classificação de bytes em VA `0x484660` |
| `0x197858` | Leitor distingue caracteres de um byte e pares; combina primeiro byte << 8 com o seguinte |
| `0x197EE8` | Conversão aritmética de pares Shift-JIS para linha/coluna JIS |
| `0x197218` | Busca bitmap pela tabela de linhas GFI ou banco ASCII |
| `0x1971A8` | Relocação dos offsets do cabeçalho e das 94 linhas GFI |

A classificação marca `20..7F` como 1, `A0..DF` como 2,
`80..9F/E0..EF` como -1 e `F0..F9` como -2. Não se generalizou a semântica de
todas essas classes. O ramo de dois bytes e a conversão foram rastreados para
os pares deste experimento. Exemplo: `82 40` → JIS `23 21`.
Capstone ajudou a inspecionar instruções MIPS básicas; não foi tratado como
decodificador completo das extensões R5900. Hashes dos trechos analisados estão
em `reports/gfi-encoding-analysis.json`; nenhum trecho binário foi versionado.

Ambas as fontes usam pixels lineares de 4 bits, primeiro nibble baixo, depois alto.
O cabeçalho contém stride em `0x10`, início dos pixels em `0x14`, tabela de códigos
extras em `0x18`, banco extra em `0x1C`, kana em `0x20`, fallback em `0x24`,
contagens em `0x28/0x2C` e 94 offsets de linhas em `0x30`.

| Fonte | Tamanho | Célula | Bytes/glifo | Linha JIS 23 |
| --- | ---: | ---: | ---: | ---: |
| SUC20I22.GFI | 874126 | 22×22 | 242 | `0x5BC8` |
| SUC24I26.GFI | 1220590 | 26×26 | 338 | `0x7F08` |

As duas têm 32 células totalmente zeradas nessa linha: colunas JIS `21..2F`,
`3A..40`, `5B..60`, `7B..7E`. Foram selecionadas as primeiras 18. A busca em
6.180 candidatos enquadrados por cabeçalhos msg/msgn no MAP não encontrou esses
pares. É uma verificação heurística local; não comprova ausência de usos em todos
os recursos ou em textos construídos dinamicamente.

## Mapeamento experimental

ASCII continua com os mesmos bytes e bitmaps. Cada caractere abaixo ocupa dois
bytes na mensagem. São códigos próprios do projeto, **não codificação CP932 padrão**.

| Caractere | Bytes hex | Índice JIS |
| --- | --- | --- |
| ç | 82 40 | 23 21 |
| á | 82 41 | 23 22 |
| à | 82 42 | 23 23 |
| ã | 82 43 | 23 24 |
| â | 82 44 | 23 25 |
| é | 82 45 | 23 26 |
| ê | 82 46 | 23 27 |
| í | 82 47 | 23 28 |
| ó | 82 48 | 23 29 |
| ô | 82 49 | 23 2A |
| õ | 82 4A | 23 2B |
| ú | 82 4B | 23 2C |
| ü | 82 4C | 23 2D |
| Ç | 82 4D | 23 2E |
| Á | 82 4E | 23 2F |
| É | 82 59 | 23 3A |
| Ã | 82 5A | 23 3B |
| Õ | 82 5B | 23 3C |

Os novos bitmaps foram compostos a partir das letras ASCII da própria fonte e
diacríticos desenhados com antialiasing. O ponto de í foi removido; as maiúsculas
foram reduzidas verticalmente para reservar espaço superior; cedilhas receberam
espaço inferior. São protótipos tipográficos para validação, sem qualidade final
presumida. O banco ASCII original e todas as demais células ficaram intactos.
Os acentos usam o avanço da célula de largura inteira; métricas proporcionais e
espaçamento óptico ainda precisam de investigação. O ELF não foi modificado.

## Mensagens e limites

Os offsets seguintes são relativos a `DATA/MAP/MAP.MCT`, não à ISO.

**A:** pergunta de Nina originalmente “You want to become / a hunter?”, índice
local 28, registro em `0x1DF47F0C`, cabeçalho 32 bytes, slot 32 bytes.
São 26 bytes úteis mais NUL e padding; uma quebra LF preservada:

```text
A: ç á à ã
â é ê í
```

Bytes úteis: `41 3a 20 82 40 20 82 41 20 82 42 20 82 43 0a 82 44 20 82 45 20 82 46 20 82 47`.

**B:** próxima mensagem de Nina, índice local 31, registro em `0x1DF47F9C`,
cabeçalho 32 bytes, slot 120 bytes, originalmente começa com
`%F1%M0_5(Why's he thinking`. Sua primeira página passa a:

```text
Teste B:
ó ô õ ú ü
Ç Á É Ã Õ
```

Prefixo preservado: `%F1%M0_5` = `25 46 31 25 4d 30 5f 35`.
Bytes da primeira página após o prefixo:
`54 65 73 74 65 20 42 3a 0a 82 48 20 82 49 20 82 4a 20 82 4b 20 82 4c 0a 82 4d 20 82 4e 20 82 59 20 82 5a 20 82 5b`.
São 108 bytes úteis no slot de 120 bytes. O TAB `09` e toda a segunda página inglesa (“Well, I think it's a bad…”)
permanecem iguais. A sequência total de comandos e LF/TAB é exigida pelo builder.
A cadeia completa de bytes, tamanho útil e vizinhos de cada registro estão em
`reports/acentos-v001-validation.json`.

Não se aumentaram registros, arquivos ou extents. Não há relocação de ponteiros.
O limite de largura conta ASCII como uma unidade e acentos como duas, comparando
com a maior linha da página original; é uma barreira conservadora, não medição
real em pixels. O texto solicitado foi dividido para preservar os slots.

## Reprodução e testes executados

Python 3.11+; Pillow somente para composição e prévia. Dependências instaladas
localmente em `work/python-deps`, sem alterar configurações globais:

```powershell
python -m pip install --target work/python-deps -r tools/requirements-font-analysis.txt
python tools/analyze_gfi.py --preview
python -m unittest discover -s tests -v
python tools/build_accent_experiment.py
python tools/start_test.py --iso accents --dry-run
```

O builder rejeita saídas existentes; para reproduzir usar novos nomes com
`--output work/MetalSaga-ptbr-acentos-rebuild.iso --report reports/acentos-rebuild-validation.json`.
Verifica hashes de origem, slots, controles, round-trip do codec e células vazias;
escreve cópia `.iso.partial`; compara integralmente os bytes com os patches
esperados antes de publicar a ISO. Diretório ISO, tamanhos, LBAs e executável
permanecem iguais. Foram aprovados 19 testes, incluindo os dois grupos, preservação
de página e comandos, rejeição de overflow, bytes desconhecidos e ordem de nibbles.

ISO: 1.704.427.520 bytes; 4.284 bytes diferentes do original.
SHA-256: `b1c2e1a5723de76e8952ff3993968b0a7d1481fd524d86b1beb863ad366636a5`.
Uma releitura independente da ISO confirmou as duas mensagens, hashes das fontes,
36 células novas não vazias (18 em cada fonte) e hash do ELF. Os 58 arquivos
extraídos de referência também mantêm todos os hashes do inventário original.
Geração e integridade binária não equivalem a execução validada no PCSX2.

## Roteiro visual manual

Fechar a sessão anterior e executar `Iniciar-Teste.cmd accents` na raiz do projeto,
ou selecionar a ISO de acentos no PCSX2 usado pelo usuário. Iniciar o jogo de novo,
sem carregar savestate, e navegar até a pergunta inicial de Nina. Verificar A,
avançar normalmente e verificar a primeira página B da mensagem seguinte.

Observar cada um dos 18 caracteres, cortes em cima/baixo, cedilhas, ponto de í,
til versus circunflexo, maiúsculas, espaçamento, sobreposição e glifos vazios ou
japoneses. Confirmar que a página inglesa seguinte e os textos ASCII continuam
legíveis e que o diálogo avança normalmente. As capturas de A e B recebidas do
usuário sustentam a validação preliminar, sem exigir nova navegação nesta etapa.
O iniciador usa o ambiente isolado existente;
o dry-run foi executado, sem iniciar o emulador nesta etapa.

O roteiro acima fica registrado para testes futuros; não foi repetido pelo Codex.
A prioridade atual é o extrator offline descrito em `extrator-dialogos.md`.
Tipografia/métricas e ampliação do repertório ficam para etapa posterior.
