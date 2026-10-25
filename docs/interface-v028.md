# Interface v028 — conclusão das descrições conhecidas

Rodada com duas etapas técnicas e **uma única ISO consolidada**. A receita
v027 registra a recuperação das 24 descrições bloqueadas por espaço. A v028
acrescenta a descrição com `80%%`, esclarece `Coat` e traduz o erro de leitura
de pintura. Não foi criada uma ISO v027.

| Entrega | Resultado |
|---|---:|
| Descrições novas | 25 |
| Descrições traduzidas no catálogo conhecido | 566 de 567 (99,82%) |
| Itens que usam essas descrições | 925 |
| Marcador original preservado | 1 descrição, usada por 2 itens |
| Rótulos/mensagens ELF novos | 2 |
| Campos novos nesta rodada | 27 |
| Interface acumulada | 3.446 |

O marcador `???` foi preservado, sem contar como tradução. Não há descrições
pendentes nesse catálogo. Isso não comprova que todos os recursos descritivos
do jogo foram descobertos. Os 516 nomes traduzidos, 25 nomes pendentes,
preservações nominais, MAP v030 (5.892 traduções e 123 adiamentos), textos de
batalha/bares, fontes/layout v005 e arte v014 continuam com a redação anterior.

## Como testar

Abra `Iniciar-Teste.cmd`. A imagem atual é:

`work/interface-v028/MetalSaga-ptbr-interface-v028.iso`

O iniciador confere tamanho, SHA-256 integral e ausência de transação/arquivo
parcial antes de abrir. Não houve execução do PCSX2 nesta rodada. Em uma partida
normal, conferir descrições nas lojas, inventário e equipamentos; lentes corpo
a corpo, componentes nomeados, reparos e acessórios são amostras úteis. Conferir
acentos, quebras, última linha e se a seleção continua mostrando o item correto.
No status dos cães, `Coat` passa a `Pelo`; o número original não muda.

A pintura recebe a mensagem `Falha ao ler pintura.|Confira a conexão|de %s|com
o console.` com os três pipes e o parâmetro na mesma ordem original. Não
provocar falhas de armazenamento nem desconectar cartões para obter essa tela.
Os rótulos e atributos podem ser conferidos durante o uso normal.

## Reorganização das descrições

O novo opt-in `spack-item-description-original-pool-repack-v002` fica em
`tools/description_pool.py`. O perfil histórico de slots permanece disponível
e continua rejeitando crescimento. Não há aumento de arquivo, SDA, RAM alocada
por esse carregamento ou extensão da ISO.

- Pool original: S_PACK.SDA `0x2AAA0`, **20.160 bytes**, entrada 1 do SDA em
  `0x800`. Conteúdo original: 20.155 bytes, seguidos por cinco zeros. A
  reconstrução sem tradução deve reproduzir integralmente esses bytes.
- Tabela de itens: `0x820`, **1.349 registros de 128 bytes**. Somente o u32 em
  **+24** contém a referência relativa da descrição e recebe atualização.
  Nomes em +0..+23, atributos em +28..+127 e sentinelas `FFFFFFFF` são imutáveis
  por este mecanismo. Os patches de nomes existentes são separados.
- São **567 alvos distintos e 927 referências**. Cada grupo de itens que
  compartilhava uma descrição continua compartilhando o mesmo alvo. Não há
  deduplicação por igualdade de texto nem mudança dos IDs lógicos.
- A v028 utiliza **18.425 bytes**, deixando **1.735 bytes** no mesmo pool.
  Foram atualizadas 926 referências; a primeira continua no offset zero.
- Todos os 541 textos aprovados anteriormente permanecem idênticos em Unicode
  e bytes codificados. Seus endereços físicos podem mudar dentro do pool.
  O pai fixo `interface-v026.json` é vinculado por SHA-256; mudanças nesses
  textos, fontes de referência ou metadados são recusadas.
- As 25 retomadas têm IDs explícitos e devem pertencer aos adiamentos do pai.
  As demais descrições mantêm os bytes originais, inclusive o marcador.
- Novas descrições respeitam o máximo original observado de **59 bytes e 29
  caracteres por linha**, mantendo a quantidade de linhas de cada origem.
  Mantêm números, nomes únicos, tokens e o repertório aprovado. São guardas
  conservadoras; não demonstram largura em pixels ou todas as telas possíveis.

O planejador mantém os IDs derivados dos offsets **originais**, acrescentando
`original_offset` e `planned_pool_relative_offset`. Não usar offsets relocados
como se fossem IDs de outro original. O catálogo continua no mesmo arquivo
`work/planejamento-interface.json`; não é necessário exportar cópias por item.

## Evidência dos consumidores

Offsets abaixo são do ELF original, não endereços virtuais. Os trechos são
vinculados por hash, além do hash do ELF inteiro.

- `0x70A98..0x70B9C`: diferenças entre entradas SDA, alocação e cópias. Em
  `0x70B88..0x70B98`, a descrição é copiada na extensão delimitada pela entrada
  seguinte. Os descritores e o tamanho carregado não mudam.
- `0x6D938..0x6D950`: getter de registro de item, stride 128.
- Foram encontrados **17 `lw` com imediato `5AEC`** no intervalo de código
  `0x1000..0x25B108`. Cada janela foi inspecionada: a base `0x475AEC` recebe a
  referência do item, com encaminhamento para três tipos de consumidor.
  Esse censo local não é uma prova exaustiva de todos os aliases indiretos.
- O compilador executa os trechos inteiros de encaminhamento para as **927
  referências × 17 caminhos = 15.759 casos**, em RAM sintética. Confere o
  endereço resultante antes da chamada ao formatador/texto. Não executa
  alocação, formatação completa, desenho ou o PS2.
- `0x1B1890..0x1B19E0`: consumidor que copia texto e converte pipes em LF.
- `0x10E608..0x10E7A0`: consumidor com formatação e separação de linhas;
  `0xE1C3C`/`0xE1F8C` encaminham a descrição como argumento de `%s`.

## O caso exato de 80%%

`tools/description_percent.py` libera somente
`item.description.03226`, pelo perfil
`single-80-double-percent-description-v001`. A tradução é:

`Impede a fuga de inimigos|em 80%% das vezes.`

O número 80 e os dois bytes `25 25` permanecem intactos. Não há liberação
geral de `%`, argumentos printf, comandos MAP ou sintaxe nativa.

A chamada em `0x10E6B8` chega a `0x227C18`, que encaminha ao dispatcher em
`0x228930`. O caso literal no formatador inteiro usa o switch em
`0x229EA4..0x229ED4`; a entrada para `%` em `0x347CB4` aponta para
`0x22A3F4`. O probe executa as instruções originais até `0x22A418`: produz
um byte `%`, comprimento 1, consome o segundo caractere e **não lê nem avança
argumentos**. Para antes da saída, padding e restante do formatador.

Há uma diferença original entre consumidores: os caminhos que formatam a
descrição interpretam `%%`; os que a copiam literalmente ou a recebem como
argumento de `%s` conservam ambos os bytes. A tradução preserva esse comportamento,
sem prometer que todos os menus exibem um único sinal. Conferência visual pendente.

## Contexto de Coat e dados que não são rótulos

O perfil `canine-coat-status-label-v001`, em
`tools/character_status_context.py`, executa os ramos originais de
`0x118990..0x118A18` para os dez índices da tabela de classes. Os índices
0..5 usam `Driving` e o campo +0x4C; 6..9 resolvem o nome `Dog` e usam
`Coat`, lendo +0x58. Por isso `Coat: %4d` recebe `Pelo: %4d`. Valor,
classe, posição, NUL, ponteiro e lógica permanecem intactos. Não se atribui
um novo efeito mecânico ao atributo apenas por esse nome.

As três strings `Your Saves` em `0x320BF0`, `0x321628` e `0x322CE0` continuam
em inglês. Não foram promovidas como rótulos visíveis: em `0xC1C2C..0xC1C58`,
por exemplo, a primeira compõe `%s/%s/icon.sys`. A outra ocorrência também é
encaminhada ao fluxo de ícones. Alterar nomes de caminhos de saves exigiria
investigação/migração própria; não faz parte da tradução desta rodada.

## Reprodução e validação

```powershell
python tools/plan_interface_menus.py
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v028.json --output work/interface-reproducao-v028 --compact-output --build-iso
python tools/verify_test_iso.py work/interface-v028/MetalSaga-ptbr-interface-v028.iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

O comparador `tools/verify_interface_revision.py` reconhece a migração somente
quando o pai fixo corresponde à receita comparada. Reconstrói os patches de
descrições anteriores dentro do pool, preserva seu resultado e exige exatamente
os patches históricos esperados. Não libera remoção arbitrária de patches.

Comparação integral v026→v028 aprovada: **20.887 bytes diferentes em 929
intervalos autorizados**, sendo o pool, 926 referências e dois literais ELF.
Todos os demais bytes e o diretório ISO são idênticos. Imagem com
**1.704.427.520 bytes**, SHA-256:

`594b1344b0088b5218795c8c3e7943b08a5d7a40514c210b19f6704644bdd32e`

Resultados finais da regressão, preflight e retenção ficam no relatório próprio
`reports/interface-v028.json`. Originais/revisões bilíngues, imagens e logs
permanecem somente em work/. Cinco ISOs de trabalho e alpha permanente protegida;
nenhuma cópia OneDrive, navegação PCSX2 ou alteração de saves/configurações.

## Próximas etapas

As descrições desse catálogo estão encerradas tecnicamente; não repetir
tentativas nos 25 adiamentos antigos. Os **25 nomes** continuam com a decisão
anterior: limites de 16 bytes, um glifo maiúsculo não disponível e proteções de
identificadores/aliases. Não cortar preposições nem alterar fontes para caber.
TITLE/BACK ainda exigem o encadeamento entre legenda, eventos e ação efetiva;
nenhuma tradução desses comandos foi aplicada por hipótese. Acumular teste
visual dos menus e da nova reorganização, auditar lacunas gráficas reais e só
depois retomar as pequenas famílias MAP.


## Regressão final executada

Passaram **241 testes distintos**: 220 de interface em 438,149 s, sete de integridade do iniciador, seis de planejamento, cinco de retenção e três da alpha. Incluem as 15.759 execuções de encaminhamento por compilação, aliases/sentinelas/atributos, legado fixo, retomadas explícitas, recusas de overflow/controles, migração do comparador, percentual literal e os dez ramos de status. Reexecuções não foram somadas. O iniciador foi conferido em dry-run, sem abrir o PCSX2. A alpha foi reconferida por hash e atributo somente leitura; cinco ISOs de trabalho confirmadas.
