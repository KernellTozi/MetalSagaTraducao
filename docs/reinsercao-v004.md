# Missão 04 — reinserção em lotes v004

## Resultado e níveis de validação

A ferramenta local exporta planos Unicode/UTF-8 associados aos IDs da v003,
simula e combina lotes, valida todos os registros e atualiza uma ISO de
desenvolvimento transacional. Não usa IA, APIs ou rede. Não houve tradução em massa.

Dos 7.231 registros recuperados, **6.882 são elegíveis pela política binária**,
em onze famílias, contra os 2.048 do editor ASCII inicial. Todos os 6.882 passaram
por um ensaio determinístico de edição de um byte em memória, preservando controles,
registros e as fronteiras dos 1.580 blocos SSD afetados. Esse ensaio troca caixa ou
pontuação e **não é tradução**, nem foi aplicado à ISO. O catálogo completo sem
edições passou com zero patches.

**Isso não comprova execução de milhares de textos no PCSX2.** A edição binária,
a extração, o round-trip sem alterações e a exibição são níveis distintos.
O experimento de três registros descrito abaixo está preparado para teste visual
manual. Repack e os demais formatos continuam sem aprovação visual específica.

## Executar no Windows

Dar duplo clique em **`Reinserir-Dialogos.cmd`** na raiz do projeto. O menu oferece:

1. Exportar catálogo editável.
2. Simular um ou mais lotes.
3. Aplicar lotes na ISO de desenvolvimento.
4. Criar a ISO base uma única vez.
5. Restaurar a ISO de desenvolvimento ao original.
6. Recuperar uma transação interrompida.

O catálogo já exportado está em `work/traducoes/catalogo-v004-final.json`.
Fazer uma cópia para trabalhar. Editar **somente `translation`** nos segmentos
editáveis e, quando apropriado, `mode`: `slots` ou `repack`. Todos os outros campos
são vínculos com o original e sua alteração é recusada. Rótulos de `msgn` ficam
protegidos. Registros bloqueados podem permanecer sem tradução no arquivo.

Pode manter apenas as entradas desejadas em cada lote, mas não alterar seus IDs
ou metadados. Não é preciso extrair o MAP novamente a cada revisão. Salvar os JSON
em UTF-8 dentro de `work/`. Arquivos com BOM UTF-8 também são aceitos.

Comandos equivalentes na raiz:

```powershell
python tools/reinsert_dialogues.py export --output work/traducoes/meu-lote.json
python tools/reinsert_dialogues.py dry-run --plan work/traducoes/meu-lote.json
python tools/reinsert_dialogues.py init
python tools/reinsert_dialogues.py apply --plan work/traducoes/meu-lote.json
```

`init` já foi executado nesta entrega. Não executar novamente para cada lote.
A inicialização interrompida pode ser retomada pelo mesmo comando: o prefixo da
cópia `.partial` é comparado integralmente ao original antes de continuar. Prefixos
divergentes são recusados, não truncados. Um ambiente já inicializado não é sobrescrito.

Para combinar lotes:

```powershell
python tools/reinsert_dialogues.py dry-run --plan work/traducoes/lote-a.json work/traducoes/lote-b.json
python tools/reinsert_dialogues.py apply --plan work/traducoes/lote-a.json work/traducoes/lote-b.json
```

Edições em campos diferentes são combinadas. Traduções diferentes para o mesmo
campo, metadados conflitantes ou modos incompatíveis bloqueiam a operação inteira.
Uma entrada sem tradução não apaga a tradução explícita de outro lote.

**Os lotes informados representam o estado desejado completo**, não apenas um
incremento da ISO anterior. O que estava modificado e não estiver nos lotes volta
ao original. O relatório lista esses IDs em `previous_entries_restored_to_original`.
Para acumular traduções, manter o plano completo ou informar todos os lotes ativos.

## Políticas por família

| Família | Elegíveis | Bloqueados | Cabeçalho | Campos e política |
| --- | ---: | ---: | ---: | --- |
| `msg` | 4567 | 158 | 32 | Corpo; slots fixos |
| `msgn` | 1384 | 31 | 32 | Corpo editável, rótulo preservado; slots ou repack |
| `smsg` | 272 | 43 | 40 | Pergunta e opções; slots ou repack |
| `sel` | 26 | 1 | 16 | Opções; slots fixos |
| `2smg` | 53 | 2 | 48 | Pergunta e opções; slots ou repack |
| `2sel` | 12 | 0 | 24 | Opções; slots fixos |
| `msgb` | 155 | 0 | 24 | Corpo; slots fixos |
| `supr` | 388 | 2 | 48 | Título; slots fixos |
| `MC` | 18 | 0 | 24 | String; slots e limite conservador de cópia |
| `SP` | 6 | 0 | 32 | String; slots e limite conservador de cópia |
| `ST` | 1 | 0 | 32 | String; slots e limite conservador de cópia |
| `smnn` | 0 | 83 | 40 | Terceira string ainda não liberada |
| `2snm` | 0 | 29 | 48 | Terceira string ainda não liberada |

Os 349 bloqueados são: 223 somente por controles opacos, 91 somente pelo papel
da terceira string, 21 pelos dois motivos e 14 por bytes nativos na origem.
Esses dados podem permanecer no plano sem alterações; não são reencodificados.

O compilador deriva os vínculos do MAP original e do índice SSD, sem confiar em
metadados editados no JSON. Verifica hash do MAP, hash do registro, cabeçalho,
índice, offset, segmentos e fronteiras SSD. Cabeçalhos, tamanho total de cada
registro, índices, blocos, tamanho do MAP e LBAs ficam invariáveis.

LF, TAB e comandos reconhecidos precisam manter os mesmos bytes e ordem.
Spans vazios e adjacência de comandos também são preservados: um prefixo
`%F1%M0_5` não pode ser deslocado para depois do texto. Isso preserva inclusive
o número de opções. Sintaxes opacas, comandos novos e quebras/páginas extras são
recusados. Uma política futura poderá permitir redistribuir linhas, mas a atual
não presume segurança para isso.

O compilador também respeita limites de cópia de execução. O helper de opções
em VA `0x2C5788` usa uma região temporária de 256 bytes e acrescenta **dois NULs**
(`0x2C5824`); portanto são permitidos até **254 bytes** na string de opções,
mesmo quando o slot tem mais espaço. Para `MC`, a cópia começa no objeto +`0x1C`
e há campo em +`0x3C`, limitando a string a 31 bytes mais NUL. `SP/ST` usam o
limite conservador de 31 bytes, além do slot original. Não se infere espaço livre
somente a partir do tamanho de uma alocação C++.

## Expansão comprovada e limites

`slots` mantém os offsets de todas as strings. A tradução pode ocupar o padding
zero comprovado do próprio segmento, mantendo pelo menos um NUL. O padding livre
medido nos segmentos exercitados foi: zero bytes em 1.749, um em 2.046, dois em
1.586 e três em 1.501. Os valores são bytes, não caracteres Unicode.

No piloto inicial, o texto passou de **28 para 31 bytes**, usando o limite útil
de 31 bytes no slot de 32, sem mover qualquer instrução.

`repack` reconstrói somente o payload do registro, alinhando as próximas strings
a quatro bytes. Permite redistribuir espaço entre as strings, ainda dentro do
mesmo tamanho total. Está limitado a `msgn`, `smsg` e `2smg`: os carregadores
posicionam o texto por cabeçalho e encontram as strings seguintes percorrendo NUL
e zeros, conforme os caminhos comprovados em `0x2C5410` e `0x2C5940`, com helper
`0x2C5248`. Não se substituem supostos ponteiros por busca de inteiros.

Ensaio no `smsg` real em `0x11620`:

- Pergunta: 47 → **51 bytes**, excedendo seu slot original de 47 úteis.
- Opções: 18 → 6 bytes; quantidade de opções e TAB preservados.
- Segunda string: offset `0x11678` → `0x1167C`.
- Registro inteiro: **108 bytes, inalterados**; cabeçalho e bloco SSD preservados.
- O modo `slots` recusou esse caso; `repack` o compilou e releu corretamente.

Outro ensaio reposicionou o rótulo preservado de um `msgn` real em `0x1139C`,
reduzindo o corpo de 125 para 106 bytes, sem mudar o registro de 176 bytes.
Esses são testes binários sobre dados reais em memória, **não testes de execução**.

Crescer além do registro continua bloqueado. O MAP possui contêineres e tabelas
externas já observadas; mudar apenas tamanho SSD e tamanho de instrução não prova
que referências externas continuem válidas. Os bytes depois do SSD não são
declarados espaço livre por serem zero. Não houve realocação entre registros,
expansão do MAP ou atualização de diretórios ISO de tamanho variável.
Essas limitações são explícitas; não há truncamento, abreviação ou remoção de acentos.

## Unicode, fontes e layout

`tools/gfi.py` centraliza os 18 caracteres PT-BR do experimento preliminar.
Planos ficam em Unicode; a conversão para pares binários próprios do projeto
ocorre só ao compilar. Caracteres ausentes, formas Unicode decompostas não
mapeadas, NUL ou controles não aprovados são recusados, sem substituição silenciosa.
O repertório atual ainda não inclui todas as maiúsculas acentuadas do português.

Se houver acentos, a ISO recebe **exatamente as fontes v001 já testadas**, ancoradas
nos hashes de `reports/acentos-v001-validation.json`. As células ASCII não mudam.
As fontes podem ser lidas da ISO local `work/MetalSaga-ptbr-acentos-v001.iso`;
se ela não existir, a composição determinística usa o Pillow local já preparado
em `work/python-deps`, verificando os mesmos hashes. Não baixa dependências durante
a reinserção. Preparação opcional, quando necessária: consultar `acentuacao.md`.
O fluxo com a ISO de acentos existente usa só a biblioteca padrão.

O parser estrutural original reconhece bytes nativos, não a extensão PT-BR.
Por isso, a releitura estrutural usa uma cópia em memória na qual cada par novo
vira dois bytes ASCII, preservando posições. Separadamente, os bytes reais de
cada segmento e seu round-trip no codec do projeto são conferidos. Essa cópia
não é gravada no jogo nem serve para afirmar que o motor aceita CP932 padrão.

Métricas de pixels continuam sem aprovação geral. Linhas maiores geram avisos,
não são cortadas para caber no inglês. Bytes válidos e controles preservados não
garantem legibilidade; layouts novos precisam de amostragem visual manual.

## ISO de desenvolvimento, segurança e recuperação

Imagem: `work/desenvolvimento/MetalSaga-ptbr-desenvolvimento.iso`.
Ela foi copiada uma vez da ISO original; atualizações posteriores modificam somente
os registros/células aprovados e preservam seus tamanhos. A implementação compara
a imagem inteira ao original mais os patches esperados antes e depois de escrever.
Confere extents, hashes, LBAs, diretório e comprimentos. A ISO e a extração originais
sempre são abertas somente para leitura.

No Windows, `CreateFileW` com compartilhamento zero impede a abertura de escrita
quando já existe leitor e impede novos leitores enquanto a atualização mantém o
arquivo aberto. Isso inclui o PCSX2 mantendo a imagem aberta. Não se depende de
adivinhar nomes de processos. Foi testado com leitores reais de arquivo, inclusive
na ISO de desenvolvimento. Em outros sistemas, o fallback usa flock consultivo;
a garantia de compartilhamento aqui foi validada no Windows.

Arquivos de controle, somente em `work/desenvolvimento/`:

- `estado.json`: geração, hash atual e patches necessários ao estado ativo.
- `transacao.json`: journal preparado antes das escritas. Sua presença bloqueia novas aplicações.
- `lotes/<hash>.json`: snapshot Unicode independente dos binários, só com as edições ativas.
- `ultima-transacao.json` e `ultima-recuperacao.json`: evidências da última operação.

Metadados usam gravação temporária, flush/fsync e troca atômica. Uma transação
interrompida mantém o journal. **Não abrir a ISO pendente no emulador**; o iniciador
`Iniciar-Teste.cmd development` também recusa esse estado.

```powershell
python tools/reinsert_dialogues.py recover
python tools/reinsert_dialogues.py restore
```

`recover` restaura o estado anterior da transação; verifica o hash original e
recusa danos fora das faixas esperadas, sem gravar. `restore` remove todos os
patches e devolve a ISO de desenvolvimento ao hash original. Nenhum deles apaga
os arquivos de tradução. Não editar estado ou journal manualmente. Guardar os
snapshots de lotes; podem ser reaplicados diretamente com `--plan`.
Reaplicar a mesma receita verifica a imagem e evita regravá-la.

Os relatórios ficam em `work/relatorios-reinsercao/`; pode escolher um novo nome
com `--report`. Aplicações têm `apply_state`: `validated_prepared` ou `committed`.
O journal/estado são a referência de recuperação se houver interrupção. O modo
dry-run escreve somente seu relatório, sem gravar binários ou snapshots.

## Experimento preparado para o usuário

Plano: `work/traducoes/experimento-v004-final.json`.
Iniciar sem savestate, navegando manualmente até Nina. Usar:

```powershell
.\Iniciar-Teste.cmd development
```

Na pergunta originalmente sobre tornar-se Hunter, aparecerá:

```text
Teste expandido:
Mesmo registro
```

A mensagem seguinte terá sua primeira página alterada, com comandos preservados:

```text
Teste: ação.
á é í ó ú
Ç Á É Ã Õ
```

A segunda página inglesa permanece original. Avançando na conversa até a escolha,
as duas opções serão `Vou ser Hunter.` e `Vou ser mecânico.`. O TAB e a quantidade
de opções são preservados. Nenhuma lógica de escolha foi modificada.

Observar cortes na fala ampliada, renderização dos acentos, avanço de páginas,
legibilidade e seleção das duas opções. Não é necessário repetir o teste do diário:
ele não foi incorporado a esta ISO. As frases são amostras técnicas, não redação
final de tradução. Não houve navegação automática no PCSX2 nesta missão.

ISO final: 1.704.427.520 bytes, SHA-256
`051ddeef5f12a30a15f0052ef31ae68a829e039ccf0a3b6c74c00638e63d8477`.
São 4.339 bytes diferentes do original, incluindo as células de fonte v001.

## Testes executados e continuidade

Foram aprovados **65 testes automatizados**, incluindo os 45 anteriores: onze
famílias editáveis, tamanhos menores/iguais/maiores, empréstimo entre strings,
preservação de rótulo, codec, comandos e prefixos, conflitos, origem incorreta,
buffers, atomicidade do lote, ISO sintética, interrupção/torn write, recuperação,
recusa de dano externo, hardlink, leitor Windows e retomada de cópia parcial.
Falhas de energia não foram provocadas no computador; interrupções foram injetadas
em fixtures. Não se apresentam esses testes como execução do jogo.

Na ISO real foram realizados: criação única, aplicação, restauração ao hash
original, reaplicação com resultado idêntico, replay do snapshot sem regravação
e bloqueio por leitor aberto. O iniciador `.cmd` de reinserção foi executado em
dry-run; o de PCSX2 foi somente preparado/verificado com `--dry-run`.

```powershell
python -m unittest discover -s tests -v
python tools/validate_reinsertion.py --report work/relatorios-reinsercao/nova-validacao.json
```

Relatórios próprios versionados: `reports/reinsertion-v004-validation.json` e
`reports/reinsertion-v004-experiment.json`. Textos, receitas completas, fontes,
journals e ISOs permanecem locais e ignorados pelo Git.

Próximo passo: validação visual das três alterações; depois, amostragem de repack
e avanço dos controles dinâmicos. Expansão entre registros exige investigação
das referências externas antes de qualquer reconstrução de blocos.

## Extensão posterior opt-in

A política v004 acima permanece disponível e conservadora. A [v005](reinsercao-v005.md) acrescenta slots fixos para escolhas nomeadas; não habilita repack, controles opacos nem bytes nativos.
