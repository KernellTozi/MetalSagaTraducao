# Interface v062 — reboque, habilidades, blindagem e música

Continuação autorizada da v061, sobre MAP v044 e fontes/layout v005.
Ferramenta tools/screen_followup.py; manifesto translations/telas-revisadas-v001.json;
receita translations/interface-v062.json. Perfil opt-in exato
screenshot-followup-exact-names-map-labels-and-stat-cells-v001.

## O que foi alterado

| Elemento observado | Tradução |
|---|---|
| Scrap Armor, item 190 | Colete avariado |
| Animal Instinct, itens 864 e 959 e ação 219 | Instinto animal |
| Jukebox, 11 rótulos de interação | Vitrola |
| Comandos da vitrola | Mover / Tocar / Parar / Sair / Percussão |
| Aviso e nome de Snake's Den | Toca da Cobra |
| SKILL LIST / ITEM LIST | HABILIDADES / ITENS |
| Towed / Tow / Stop towing | Reboque / Rebocar / Soltar reboque |
| Discard how many? | Quanto descartar? |
| Armor tiles / Load / Free na janela de descarte | Placas / Carga / Livre |

Os nomes das músicas não foram traduzidos. Crimson Manzier é o nome único
do equipamento 176, não um procurado; foi preservado. A associação inicial
do Codex a procurados foi corrigida após a consulta ao catálogo de itens.

São **25 unidades novas**: seis literais ELF, três nomes de itens, uma ação,
13 nomes de mapa e dois títulos rasterizados. Dois formatos de resultados
foram revisados, sem serem contados novamente. Interface passa de 4.317
para 4.342 unidades heterogêneas; itens de 627 para 630 campos alterados.
O catálogo de diálogos continua em 6.044 alterados/5.991 corpos ou opções/
991 referências explícitas, com 108 nomes padrão herdados. Os 13 novos nomes
de mapa são de outra estrutura; não equivalem a 13 diálogos traduzidos nem
resolvem os 13 rótulos curtos ainda pendentes.

## Nível e Prêmio: causa e correção

Os formatos de resultados em ELF+0x3239E0 e +0x323A28 tinham um espaço a menos
na tradução. O acento ocupa dois bytes e um único glifo; conservar somente
o orçamento de bytes havia reduzido uma coluna visível antes dos números.

- Original Level: cinco espaços antes de %3d. A tradução usava quatro;
  Nível agora volta a cinco espaços.
- Original Reward: dez espaços antes de %8d. A tradução usava nove;
  Prêmio agora volta a dez espaços.
- Os códigos %3d e %8d e todos os valores permanecem intactos. As células
  originais são de 16 e 24 bytes, com caudas zeradas. A edição rejeita evidência
  de referências interiores e cabe nessas células, sem ocupar o texto seguinte.
  O primeiro NUL avança um byte; o NUL final da célula permanece.

O harness existente de medição executou instruções originais com o layout
v005 para 0, 25 e 999 nos modos 0 e 2: o avanço total de Nível passa a coincidir
com Exp, e o de Prêmio com Dinheiro. A correção recupera 11 unidades de avanço
em tamanho 22 nesses modos. Isso não comprova o modo usado pela captura nem
uma composição da GPU. Conferir a tela de resultados em jogo; não alterar
o desenho dos acentos para compensar um erro de espaçamento do formato.

O comparador normaliza somente os dois intervalos autorizados para comparar
o prefixo antigo com as células finais de 16/24 bytes. Os bytes fora do patch
antigo são recuperados do original, não supostos como bytes da versão anterior.
Não liberar aumento de outros formatos ou campos com essa prova.

## Itens e habilidade

Três campos de 24 bytes e uma ação de 32 bytes no S_PACK.SDA. Alvos têm no
máximo 15 bytes, dentro do teto de 16 já provado para nomes. Fonte, IDs,
atributos e demais bytes de cada registro permanecem intactos. O lookup dos
três registros e da ação foi conferido pelo harness de instruções existente.

Animal Instinct tem duas cópias na tabela de nomes e outra na tabela de ações;
as três recebem a mesma redação. Os bloqueios globais do compilador histórico
para 864/959 permanecem: o perfil novo libera somente esses IDs e o 190, com
fonte, registros e tradução exatos no manifesto. Não estender a outros nomes
protegidos, armas ou aos 89 MANTER aprovados anteriormente.

## Vitrola, caverna e campos de mapa

A varredura encontrou 11 Jukebox no MAP.MCT, todos no início de nós tipo 6
com 204 bytes. A tradução Vitrola tem os mesmos sete bytes e preserva o NUL
original: o patch tem somente oito bytes. O exemplar de Junkyard possui um
byte FF em +31; ele é opaco e fica intacto. Uma tentativa inicial de tratar
a cauda inteira como zeros foi recusada antes de gerar ISO. A solução usa
um nome completo de igual comprimento, sem liberar a cauda desconhecida.

Snake's Den aparece como nome do mapa (tipo 2) em 0x852E800 e como aviso de
entrada/saída (tipo 7, 216 bytes) em 0x852DFDC. Os dois recebem Toca da Cobra,
conforme o glossário, em prefixos de 14 bytes com NUL. O campo reconhecido
comporta 32 bytes; somente os dois zeros necessários ao novo nome são usados,
sem alterar os metadados posteriores, nós, referências ou tamanhos de blocos.
As outras ocorrências em falas/scripts não recebem substituição cega.

Os getters nativos 0x79EB8, 0x7E5C0 e 0x7E988 devolvem o ponteiro já existente
no objeto. As sondas executam esses getters em memória simulada, sem escritas.
Não executam o carregador completo, scripts de interação ou o emulador.
Cada patch de mapa vincula o nó e o registro de origem por hash.

## Comandos e descarte de placas

Os ícones de controle da vitrola em ELF+0x331CD0 permanecem byte a byte,
inclusive direcional, X, triângulo, círculo e L1/L2/R1/R2. Rótulos completos
sem dois-pontos cabem na string original, como nos comandos de venda v061.
Identificadores técnicos texJukebox/classes não são traduzidos. Nenhum atlas
de nomes de músicas ou outro recurso NDATA é modificado nesta versão.

Reboque usa as strings do painel TANK ONOFF em 0x315E90/A0/F10.
Espaços finais mantêm o tamanho dos rótulos de largura fixa. A mensagem de
log minúscula towed., em outro contexto, permanece intacta; não é a linha
Towed da captura.

O descarte usa 0x32AED0 e 0x32AF00. Título, Placas, Carga e Livre
mantêm parâmetros, quebras de linha e setas nativas 81 A8. Os formatos numéricos
e as posições das setas no formato de dados não mudam. SP, unidades t,
quantidades, sinais negativos e cálculo de carga permanecem originais.

A validação de integração recusou três adições que coincidiam com literais
já traduzidos em contextos relacionados. Foram retiradas do lote: Dirigir ou
rebocar?, Desembarcar e Quantos largar? permanecem como no pai. A tentativa
foi bloqueada antes de criar ISO; não se relaxou o teste de sobreposição para
aplicar o mesmo texto duas vezes ou inflar a contagem de traduções novas.

## Títulos gráficos

Somente mais duas células do atlas S_PACK+0x8C830. ITENS ocupa [4,84,106,96];
HABILIDADES, [4,144,118,156]. A altura das letras continua em dez pixels,
com a mesma linha de base, paleta, cabeçalhos e UVs. Não houve resampling.

HABILIDADES usa intervalo de um pixel entre as letras. O espaço interno dos
dois D foi estreitado em uma coluna para o título ocupar 113 pixels, mantendo
as hastes e altura originais. ITENS conserva o espaçamento nativo de três.
As três células traduzidas na v061 e todos os pixels fora das duas novas
áreas são preservados. Comparação em work/interface-v062-previews/titulos.png.

## Reprodução e roteiro visual

```powershell
python tools/screen_followup.py
python tools/screen_followup.py --previews
python -m unittest discover -s tests -p test_screen_followup.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v062.json --compact-output --build-iso --output work/interface-v062-reproducao
```

Conferir inventário de proteções, habilidades e ação Instinto animal, entrada
de Toca da Cobra, nome/comandos da Vitrola, títulos de habilidades/itens,
seleção de reboque e a janela de descarte. Nos resultados, conferir os números
de Nível contra Exp/Total e Prêmio contra Dinheiro/Despesa. Não foram alterados
valores numéricos ou regras do jogo. Os nomes de músicas devem permanecer iguais.

O usuário faz a navegação. Testes binários e sondas não comprovam execução
no PCSX2; os novos elementos aguardam validação visual. As capturas recebidas
já mostram MEMBROS/FROTA da arte v061, sem validar todos os demais elementos.
Backup v059 permanece protegido. As categorias abreviadas e os 13 rótulos
explícitos curtos continuam numa investigação independente.


## Verificação da entrega

Passaram 60 testes distintos: 16 novos e 44 de regressão. Preflight com hash
integral, tamanho, recibo e ausência de transação pendente aprovado. A comparação
integral v061→v062 confirmou 1.268 bytes em 26 patches previstos, sem diferenças
extras ou alterações de diretório/fontes/layout. Fora das revisões explícitas
os patches anteriores permanecem iguais.

ISO: work/interface-v062/MetalSaga-ptbr-interface-v062.iso, 1.704.427.520 bytes.
SHA-256: `c000755d8447b157eae3ed5674b69a70fb223b4c813f5e9c43144fe57b4ec232`.
Iniciar-Teste.cmd e Abrir-Pasta-da-Ultima-Versao.cmd já apontam para essa pasta;
ambos foram conferidos sem executar PCSX2. Resumo reports/interface-v062.json
e comparação reports/interface-v062-delta.json.

Cinco ISOs de trabalho, dentro do limite. Backup v059 teve hash integral e
atributo somente leitura reconferidos; a v061 também permanece disponível.
Nenhuma cópia para OneDrive ou desligamento nesta rodada.
