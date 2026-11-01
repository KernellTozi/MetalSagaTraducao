# Interface v061 — lacunas observadas durante a partida

Sobre a v060 integral, com MAP v044 e fontes/layout v005. O usuário informou
que não encontrou defeitos na ISO até o momento e autorizou aplicar os textos
das capturas. Isso revoga a espera por aplicação daqueles avisos; não comprova
todos os caminhos de execução da v060 ou a solução geral de Sim/Não.

## Alterações

| Tela | Tradução aplicada |
|---|---|
| Aviso do tanque | Sobrepeso; Sem motor; Sem C Unit; imóvel |
| Outras causas do mesmo aviso | Chassi falhou; Motor falhou; C Unit falhou |
| Detalhes do save | Nome; Nível; Tempo; Salvo |
| Espaços vazios do cartão | Vazio, no literal compartilhado NO DATA |
| Equipamento | Equipamento; Comparar; MEMBROS; FROTA |
| Teletransporte | CIDADES |
| Máquina de venda, comandos | Mover + direcional; Comprar + X; Sair + círculo |
| Máquina de venda, instrução | Acenda o centro / e ganhe um prêmio! |

São 20 unidades heterogêneas: 15 literais ELF, três títulos rasterizados e
duas linhas de instrução. Eles produzem 18 patches físicos. Interface passa
de 4.297 para 4.317 unidades; itens 627, MAP 6.044 alterados/5.991 corpos ou
opções/991 referências explícitas e os 108 nomes padrão continuam iguais.
Não há tradução de cidades, veículos, personagens ou nomes únicos nesta rodada.

## Literais e controles

Ferramenta tools/observed_menu_translation.py, perfil opt-in
observed-save-vehicle-vending-and-headers-fixed-v001. Manifesto
translations/menus-observados-v001.json, sobreposição exata ao pai v060.

- Save em ELF+0x3211F0/0x321200/0x321210/0x321240. A leitura original mostra
  formatos com oito bytes de prefixo, dois bytes nativos 81 46 de separador
  e %s/%d. Os novos prefixos mantêm oito caracteres visíveis, incluindo espaços.
  Nível exige nove bytes nesse prefixo, pois í ocupa dois. As quatro células
  têm 16 bytes, caudas zeradas e referências aos respectivos inícios. O leitor
  de printf recebe a string até NUL, sem deslocamento fixo para o parâmetro.
  Foi autorizado somente esse espaço de cada célula, após conferir a cauda e
  rejeitar evidência de referências interiores. O separador e parâmetro são
  preservados, deslocados um byte somente em Nível; o início da célula seguinte
  e o último NUL de cada célula ficam intactos. Não transferir essa capacidade
  aos campos Machine/Vehicle/Unknown. Nível usa o codec PT-BR existente, não UTF-8.
  A fonte do motor, valores, localização e data/hora não são alterados.
- Causas do tanque em 0x32ED10/20/30/48/58/70 e formato em 0x32ED80.
  Quebras LF e os dois %s do formato permanecem na mesma ordem. A função
  em 0x13B058 limpa uma área de 0x80 bytes e acrescenta as causas; os 64
  subconjuntos dos seis textos foram verificados em concatenação Python.
  Nenhum cresce frente à origem ou alcança 128 bytes com o NUL. Isso não é
  execução da função completa nem comprovação da causa de sobrepeso.
- Equipamento em 0x32B110 e 0x32B250. Equipamento é o título completo escolhido
  para essa tela; Comparar é uma ação completa, sem abreviar a palavra peças.
  O literal Status/Equip de outro contexto em 0x32CE80 não foi substituído
  indiscriminadamente.
- NO DATA em 0x348F78 passa a Vazio. A referência em dados é compartilhada;
  conferir tanto a linha vazia quanto o painel de detalhes no jogo.
- Comandos em 0x32FF38: os três códigos originais de ícones são preservados
  exatamente e em ordem: 24 81 81, 24 81 7E e 24 81 9B. Foram omitidos somente
  os dois-pontos dos rótulos para manter os verbos completos no espaço original.
  Mover descreve o uso do direcional para mudar a seleção.

Todos os 15 patches mantêm tamanho físico, posição e NUL final do intervalo
autorizado. O primeiro NUL do formato Nível avança um byte dentro de sua
célula existente; os outros literais conservam o NUL original como limite.
Não houve realocação de strings ou aumento de buffers. As referências candidatas do
catálogo e janelas de instruções ficam vinculadas no manifesto; não representam
um censo completo de consumidores ou liberação genérica de bytes nativos.

## Títulos gráficos e instrução da máquina

Os três títulos estavam na entrada 0 da subárvore 2 do S_PACK.SDA: textura
em 0x8C830, 256×256, 8 bpp. CIDADES ocupa o retângulo [4,108,114,120], FROTA
[4,156,146,168] e MEMBROS [4,168,144,180]. As letras usam a mesma fonte raster
maiúscula do atlas, na altura e linha de base originais, sem escala. A letra F
foi construída do E nativo retirando somente a barra inferior; as demais são
extraídas de amostras desse alfabeto. Nenhum UV ou dimensão foi ampliado.
O GANM de ícones em 0xB3BA0 pertence a outro atlas e não foi confundido com
descritores destes títulos. A identificação aqui é pela inspeção do atlas e
correspondência com as capturas; o uso integral dos seletores não foi executado.

A instrução da máquina cruza duas texturas da NDATA.SDA: entradas 13 e 14,
offsets 0x97000 e 0xD7800, com larguras 512 e 128 e altura 512. A edição
restringe-se a x global 453..605, y 312..347, sem tocar no selo BONUS, na
máquina ou na borda direita. As duas linhas usam os glifos GFI existentes,
altura 16, larguras 117 e 134, sem estreitamento. Não são fontes novas no jogo.

As paletas e seus alphas originais permanecem byte a byte. O fundo usa índice
transparente e a tinta índices existentes de alpha 128. Uma primeira prévia
local selecionou só índices transparentes, deixando a instrução invisível;
isso foi detectado na inspeção e corrigido antes da construção. Os testes
conferem a seleção de tinta opaca, contenção por retângulo e retorno exato
ao registro original por substituição inversa dos índices. Não confundir esse
retorno binário com renderização no PS2.

Comparações locais em work/interface-v061-previews/cabecalhos.png
e work/interface-v061-previews/maquina.png. São previews RGB,
sem composição da GPU, para revisar a arte; imagens derivadas ficam fora do Git.

## Limites ainda pendentes

Máquinas, Veículos e Desconhecidos continuam exigindo 9/9/13 bytes contra
campos atuais de sete, no ELF. Esta versão não promete expansão: os campos
adjacentes já contêm outros textos, e não há destino carregado/reserva e todos
os leitores comprovados para redirecionar esses nomes. Não usar padding/BSS
como espaço livre ou transferir provas de buffers de itens para essas tabelas.
As dez ocorrências e a estratégia continuam em docs/menus-equipamento-limites-v001.md.
Bio/Cyber também ficam para revisão contextual. Os 13 falantes explícitos
curtos continuam pendentes conforme docs/falantes-lookup-v001.md.

Uma alternativa mais estreita foi identificada para investigar antes de ampliar
o ELF: o intervalo 0x349248..0x349290 contém nove strings de oito bytes cada.
Desconhecidos/Bio/Cyber/Máquinas/Veículos/Alvos/Normal/Furtivo/Abrigo, com NULs,
somam exatamente os mesmos 72 bytes se compactados. Isso é só uma conta de
capacidade: exigiria mover os textos dentro do banco e redirecionar todas as
referências, inclusive as de Normal/Furtivo/Abrigo e aliases. Não há nove slots
independentes maiores, nem prova de que o scanner tenha encontrado todos os
leitores. Essa alternativa ainda não foi aplicada ou validada por execução.

BONUS e títulos de minigames dispensados pelo usuário permanecem como estão.
Não foram alterados nomes de armas, itens, Wanted/posters, MAIN/SUB/SE,
configurações, BIOS ou saves. Backup v059 e ISO v060 permanecem preservados.

## Reprodução e teste visual

```powershell
python tools/observed_menu_translation.py
python tools/observed_menu_translation.py --previews
python -m unittest discover -s tests -p test_observed_menu_translation.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v061.json --compact-output --build-iso --output work/interface-v061-reproducao
```

Ao abrir a versão consolidada pelo Iniciar-Teste.cmd, conferir:

1. Aviso do tanque sem motor/C Unit: causas legíveis e nome do tanque intacto.
2. Equipamento: título, ação Comparar e cabeçalhos MEMBROS/FROTA.
3. Teletransporte: CIDADES e nomes de cidades intactos.
4. Salvamento: Nome/Nível/Tempo/Salvo, espaços vazios e painel Vazio, sem
   sobrescrever saves pessoais para provocar testes. Só a interface foi editada.
5. Máquina de venda: ambas as linhas visíveis através da emenda da textura,
   comandos/ícones corretos e BONUS intacto.

O usuário realiza a navegação. Nenhuma execução de PCSX2 foi realizada pelo
Codex nesta rodada; confirmação visual dos novos elementos continua pendente.

## Construção consolidada

ISO final: work/interface-v061-final/MetalSaga-ptbr-interface-v061.iso.
Tamanho: 1.704.427.520 bytes.
SHA-256: `6cfc373bacb4064b8068fef00dd6c4bfa6b0c4af831ea9088e8d3aff3e099a73`.
Iniciar-Teste.cmd e Abrir-Pasta-da-Ultima-Versao.cmd acompanham essa pasta;
ambos foram conferidos em modo de simulação, sem iniciar o emulador.

Passaram 44 testes distintos: 13 novos e 31 de regressão (nomes padrão,
preflight, retenção e métricas/layout das fontes). O preflight verificou
tamanho, hash integral, recibo e ausência de transação pendente da nova ISO.
O backup v059 teve hash integral e atributo somente leitura reconferidos.

A construção preliminar em work/interface-v061/ foi substituída pela final
para conservar oito caracteres visíveis no prefixo Nível. Seu hash era
b5ff1fbc2c314e4aa78fa0073144ec72d4c888b04a78d1adca87fb9f417aa8ed; não usar
essa imagem como entrega atual. O comparador da entrega é executado novamente
contra v060, usando a receita final. Relatórios históricos da tentativa ficam
em work/, sem promover a imagem preliminar ou contar duas versões entregues.

A comparação integral final v060→v061 confirmou 4.865 bytes diferentes em 18
patches previstos; diretório ISO, fontes/layout e todos os patches herdados
permanecem iguais. A ISO preliminar foi removida após conferir seu hash exato,
preservando relatórios locais. Restam quatro ISOs de trabalho, dentro do
limite de cinco. Resumo em reports/interface-v061.json e delta no relatório
homônimo. Não houve OneDrive ou desligamento.
