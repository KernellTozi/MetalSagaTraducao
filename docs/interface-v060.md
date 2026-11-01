# Interface v060 — nomes padrão de NPCs e alinhamento das escolhas

Sobre a v059 completa, com MAP v044 e fontes/layout v005. Backup protegido
em dist/backup-v059/ permanece intacto. A rodada aplica **108 campos de nomes
padrão de modelos**, com 55 traduções distintas, e substitui a medição de
largura de uma classe de opções. Não há novas falas, itens ou glifos.

## Por que Boy não aparecia na lista dos 13

Os 13 casos pendentes são rótulos explícitos gravados no fim de registros
msgn. Boy não está entre os rótulos desse catálogo. A pesquisa dirigida
encontrou o nome em outro recurso: **entrada externa 2 do MAP.MCT**, em
0x202B7000, com 409 registros de 44 bytes. Cada registro contém 12 bytes
de atributos/offsets e um nome padrão de **32 bytes**, incluindo o NUL.
Todos os 409 campos têm terminador e cauda zerada; 19 contêm bytes nativos
e foram preservados integralmente.

A tabela termina em 0x202BB650, antes do primeiro payload em 0x202BB800.
Não foi necessário aumentar o arquivo, deslocar modelos ou aproveitar
caudas desconhecidas. A regra aceita no máximo 31 bytes de texto mais NUL.
Os três valores anteriores a cada nome, índices, ordem e dados dos modelos
ficam intactos.

O carregador em ELF+0x328D0 calcula a alocação por contagem×44 e copia os
registros em 0x3299C–0x32A28. O método de nome em 0x7D530 segue o objeto de
modelo e retorna registro+12; o descritor virtual correspondente está em
VA 0x403F28+0x48/+0x4C. A rotina de diálogo em 0x1FDB00 usa esse caminho
quando não há nome explícito. A sonda executa a seleção do caminho e o
getter virtual originais, com a busca do ator na coleção modelada; não
executa alocador, carregamento completo, GPU ou PCSX2.

Foram traduzidos somente papéis genéricos revisados: **Boy → Menino** nas
duas entradas encontradas, Girl → Garota, Man → Homem, Woman → Mulher,
Worker → Trabalhador, além de funcionários, comerciantes, serviços e outros
papéis. Os alvos seguem o glossário anterior quando disponível. Nomes
próprios de personagens, tanques, procurados, inimigos únicos e termos
Hunter/Soldier/Punk permanecem; títulos ambíguos também não foram promovidos.
A lista bilíngue completa está somente em work/npc-menus-v001/revisao-local.json.

**Isso não resolve nem esconde os 13 rótulos explícitos curtos.** Se um
diálogo fornece seu próprio nome, ele continua tendo prioridade sobre o
nome padrão traduzido. A sonda verifica separadamente esse caminho para
Worker, Nina, Hunter e Soldier. O protótipo de lookup permanece bloqueado
até a reserva de memória comprovada; ver docs/falantes-lookup-v001.md.
Outras ocorrências de Boy em nomes de cena/modelagem não foram substituídas
por busca textual indiscriminada.

## Causa reproduzida de Sim/Não

A tela de Memory Card encaminha as linhas NDATA 186/12 e 186/13 para a
classe de itens de escolha em 0xC4B04–0xC4B60 e em 0xC7604–0xC766C. O
construtor 0x99EA8 conta bytes e grava `strlen >> 1`; a atualização herdada
0x4F898 calcula a largura como tamanho da fonte×esse número.

Com fonte de tamanho 22:

| Opção | Bytes | Largura anterior | Avanço medido, modo 1 |
|---|---:|---:|---:|
| Sim | 3 | 22 | 30 |
| Não | 4 | 44 | 33 |

O ã usa dois bytes, embora continue sendo um glifo. Assim, as caixas usadas
no alinhamento têm larguras diferentes das letras desenhadas. A evidência
reproduz o sentido do deslocamento visto na captura; não é uma nova captura
do jogo. Modos 0/2 medem 33 para Sim e Não. Os três modos foram verificados.

## Correção de largura

O wrapper de atualização da classe, **ELF+0x99F78–0x99FA8**, tem 48 bytes.
Ele passa a encaminhar por tail-call o objeto de texto já existente para
a rotina nativa de medição em **0x3DD60**, que usa os avanços da rotina
0x3E520 com o layout v005. A rotina nova ocupa exatamente os mesmos 48 bytes;
não há novo segmento, code cave, tabela de nomes, reserva de heap ou mudança
de cabeçalho ELF. Altura da fonte de desenho, escala 0.9, estilo, SP e
registradores preservados são conferidos nas sondas.

O escopo é a classe de linhas de escolha usada por essas caixas, inclusive
outras listas que compartilhem a mesma classe. Não é um deslocamento fixo
somente de Sim. Os textos Sim/Não, fontes GFI e os patches v005 permanecem
iguais. Glifos ASCII, acentos, pares nativos de largura completa, nomes
vazios, três modos, tamanhos 19/22/26 e quebra de linha foram testados.
Isso não comprova todos os layouts/listas/ícones no jogo: conferir também
outras escolhas e listas durante a partida.

## Ferramentas e reprodução

- tools/npc_default_names.py: diretório e nomes padrão, sem editar atributos.
- tools/choice_text_metrics.py: wrapper e sondas de largura nativa.
- tools/npc_menu_revision.py: sobreposição exata do pai v059.
- translations/npc-menus-v001.json: nomes, hashes, janelas e casos de medição.
- translations/interface-v060.json: receita consolidada.

```powershell
python tools/npc_menu_revision.py
python -m unittest discover -s tests -p test_npc_menu_revision.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v060.json --compact-output --build-iso --output work/interface-v060-reproducao
```

Todos os 108 nomes, os metadados de origem, os casos de medida e o pai inteiro
são vinculados por hash. Mudanças não relacionadas são recusadas. A primeira
preparação foi bloqueada porque intervalos de escrita da sonda usavam tuplas
na memória e listas após serialização JSON. A representação foi uniformizada,
sem relaxar a comparação; nenhuma ISO foi produzida na tentativa bloqueada.

## Roteiro visual

Iniciar-Teste.cmd e Abrir-Pasta-da-Ultima-Versao.cmd já acompanham a v060. ISO em work/interface-v060/.

Na mesma tela da captura, conferir o centro de Sim e Não em relação à caixa
e à faixa de seleção; testar ambas as seleções. Conferir também outro aviso
de confirmação e outras listas, sem provocar corrupção/formatação de saves.
Observar os NPCs que antes apareciam como Boy, bem como demais papéis,
acentos e identificação correta dos personagens.

Não há confirmação visual nova no PCSX2 nesta rodada. O uso anterior de
Decoy→Isca foi relatado pelo usuário na v059 e não valida esta alteração.
Backup, BIOS, cartões de memória, configurações e saves não foram alterados.
Não houve OneDrive ou desligamento.

## Verificação da entrega

Passaram 56 testes distintos: 11 novos e 45 de regressão. A comparação integral
v059→v060 confirmou 929 bytes diferentes em 109 patches previstos (108 campos
de nomes e um wrapper ELF). Diretório ISO, fontes/layout e patches anteriores
permanecem iguais. Preflight com hash integral e os dois atalhos foram conferidos
sem abrir o emulador. Há três ISOs de trabalho, dentro do limite de cinco.

ISO: work/interface-v060/MetalSaga-ptbr-interface-v060.iso, 1.704.427.520 bytes.
SHA-256: `89a5adba72ff73985e0a322bbe3fab682a49424a8db6a1b997644974d553bb64`.
O backup v059 teve hash integral e atributo somente leitura reconferidos.
Relatórios próprios: reports/interface-v060.json e reports/interface-v060-delta.json.

## Retorno visual posterior do usuário

Em 01/11/2026, o usuário confirmou que o nome Menino funcionou perfeitamente.
É uma validação pontual de Boy→Menino em jogo, sem identificação de qual das
duas entradas foi observada. Os demais nomes e o alinhamento Sim/Não continuam
sem confirmação geral. Evidência própria em reports/interface-v060-visual-user.json.
Não houve nova execução pelo Codex ou alteração da ISO para registrar o retorno.
