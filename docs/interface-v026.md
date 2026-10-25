# Interface v026 — expansão consolidada de batalha e interações

A rodada acrescenta **1.298 campos/ocorrências de texto** em cinco conjuntos:

| Conjunto | Novos campos |
|---|---:|
| Rótulos de ações de batalha | 679 |
| Dicas de análise de inimigos | 248 |
| Nomes descritivos de inimigos | 72 |
| Reações ao examinar/usar itens | 149 |
| Cardápios e comentários de bares | 150 |
| **Total** | **1.298** |

Referência histórica: o maior ganho registrado nos lotes anteriores foi de
647 registros MAP, na v019; a meta numérica desta rodada foi 1.294. A medição
nova é de campos/ocorrências, não palavras: não são 1.298 falas MAP inéditas.
Nomes e dicas são campos distintos de uma mesma ficha; labels repetidos de
ações ocupam registros distintos. Aliases que compartilham o mesmo payload
dos pools são contados uma vez. Reutilizações e preservações não são traduções
novas na tabela original de itens.

Total consolidado: **3.419 campos de interface**. MAP v030 mantém 5.892
registros alterados; continuam as 516 traduções de nomes de itens e 541
descrições/889 referências. Os textos anteriores, arte v014 e fontes/layout
v005 permanecem iguais. Não medir porcentagem do jogo inteiro por essa soma.

## Execução local

Abra **Iniciar-Teste.cmd**, que aponta para:

`work/interface-v026/MetalSaga-ptbr-interface-v026.iso`

O iniciador agora confere relatório concluído, tamanho, SHA-256 integral,
ausência de transação e de construção parcial antes de iniciar o PCSX2.
Uma divergência impede a abertura; não há tentativa de adivinhar/reparar bytes.
O relatório e a imagem também não podem mudar durante a leitura. Não se usa
cache de hash para dispensar conferências futuras.

Conferência manual e reconstrução, sem IA/APIs:

```powershell
python tools/verify_test_iso.py work/interface-v026/MetalSaga-ptbr-interface-v026.iso
python tools/plan_interface_menus.py
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v026.json --output work/interface-reproducao-v026 --compact-output --build-iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

O planejador continua usando apenas **work/planejamento-interface.json**.
Exporta agora os novos catálogos e as decisões de preservação; bytes e textos
originais permanecem em work/. Somente ferramentas, receitas próprias e
metadados são versionados. A conferência exige o relatório de construção
`relatorio.json`; experimentos históricos sem esse manifesto não são abertos
silenciosamente pelo novo preflight.

## Ações e fichas de inimigos — formato comprovado

Implementação opt-in: `tools/spack_battle.py`, perfil
`spack-battle-labels-and-analysis-hints-fixed-fields-v001`.

- Segundo SDA de S_PACK: **0x35000**, com 22 entradas. Entrada 1 em **0x37070**
  contém **967 registros de 228 bytes** e quatro bytes finais preservados.
  Os primeiros **32 bytes** são o rótulo NUL, com preenchimento original zero;
  atributos começam em +32. As ações aprovadas usam no máximo **18 bytes**,
  maior comprimento observado incluindo rótulos nativos. O máximo original
  apenas em ASCII é 16. As 66 entradas nativas não foram liberadas ou editadas.
- Entrada 2 em **0x6CDB0**: **261 registros de 276 bytes**, mais um trailer de
  **12 bytes não interpretados**, preservado. Nome NUL em +0, campo de 24 bytes;
  informação NUL em **+232**, campo de 44 bytes. Todos os atributos intermediários
  +24..+231 permanecem intactos.
- Nomes genéricos usam teto de **16 bytes**, máximo ASCII original observado.
  Apenas uma lista explícita de IDs revisados pode ser editada. Não se promove
  um inimigo por regex/palavra genérica. Procurados são também cruzados com a
  tabela original de Wanted e bloqueados. A lista não autoriza qualquer chefe,
  personagem, nome distintivo ou outro ID.
- Dicas: **248 campos não vazios**, todos traduzidos; 13 vazios preservados.
  Máximo de 43 bytes mais NUL, duas linhas e 19 caracteres por linha, conforme
  o repertório/limites observados no conjunto original. Não há crescimento de
  registros, ponteiros ou extents.

Evidências vinculadas ao ELF original por SHA-256:

- **0x6CE04..0x6CE70**: seleção do SDA de batalha e obtenção das entradas,
  incluindo divisão do tamanho de inimigos pelo stride **0x114**.
- **0x11D358..0x11D380**: índice ×**0xE4**, base global **0x475B10**, envio
  do nome ao formatador com `%s` de **0x3495D0**.
- **0x12B45C..0x12B488**: índice ×**0x114**, base **0x475B08**, obtenção
  do registro de inimigo. **0x12B594..0x12B5A4** encaminha o nome;
  **0x12B648..0x12B664** encaminha +232 com `INFO\n%s` de **0x349870**.

As janelas inteiras relevantes são conferidas por hash. Um executor limitado
interpreta as instruções inteiras dos cálculos/encaminhamentos em RAM sintética,
incluindo o destino GPR de MULT no R5900 e delay slots. Não executa o jogo,
alocadores, formatadores ou GPU; não é prova de todos os consumidores possíveis.

Rótulos que coincidem com nomes de itens já traduzidos precisam usar a mesma
redação aprovada. Se o nome original do item está protegido/preservado, o
rótulo correspondente não pode ser traduzido por este caminho. Repetições
dentro de cada tabela mantêm redação igual. MAIN/SUB/SE permanecem explícitos;
nomes de personagens/facções dentro das ações, como Marceau e Muscle, são
preservados. Missile Fish permaneceu original pela proteção nominal existente.

## Reações de itens — três variantes e trailer preservado

Implementação: `tools/spack_interactions.py`, perfil
`spack-reactions-and-bar-original-counted-pools-v001`.

Primeiro SDA em 0x800, entrada 4: **0x325D0**, extent de **8.864 bytes**.
O u32 inicial declara **179 registros de 16 bytes**: chave imutável seguida
por três offsets relativos de texto. São **537 referências** para **151 alvos**.
O primeiro offset é **0xB34**, exatamente 4 + 179×16. Os 149 alvos traduzidos
ocupam **8.470 bytes com o cabeçalho**, abaixo do limite textual de **8.849**.

O fim contém **15 bytes opacos**, incluindo palavras não zero. Essa área inteira
fica intacta; não foi tratada como folga nem incorporada à capacidade textual.
O repack modifica somente os offsets das três variantes e seus textos dentro
do pool existente. Contagem, chaves, seleção das variantes e grafo de aliases
são preservados. Dois alvos permanecem originais por conterem fragmento
numérico ou apenas nomes de componentes que já devem continuar em inglês.

Código **0x70BC4..0x70BD8** copia essa entrada ao objeto cujo campo corresponde
a **0x475AF8**. O leitor **0x709C8..0x70A64** busca a chave e seleciona uma das
três variantes; o cálculo final **0x70A38..0x70A58** foi executado para os
179×3 pares sobre o pool reconstruído. A busca completa e a escolha aleatória
não foram executadas; suas instruções e metadados permanecem vinculados.

O texto mantém quantidades, unidades, direções, personagens e piadas deliberadas.
Exemplos de contexto: legendas de fotos, receitas de peças, mapas/tesouros e
reações a roupas. Norman, Michael, Isaac, Pamela, Arthur, Helga, Disassembler
e Father Muscle mantêm os nomes. Listas de componentes acompanham somente os
aliases já traduzidos na tabela de itens; nomes únicos continuam intactos.
Montanha de Sucata e os códigos **2946**, **2** e **946** são preservados em
seus respectivos registros, sem inventar/reunir fragmentos de combinação.

## Bares — cardápios e comentários

S_PACK raiz, entrada **6**, em **0x11C800**. SDA interno com três entradas:
texto em **+0x20 / 0x11C820**, tamanho **3.744 bytes**; os outros dois recursos
internos não são alterados. O texto contém **172 IDs**, **166 alvos
distintos** e seis aliases. São 150 traduções, **3.736 bytes usados** e oito
bytes livres. Dezesseis alvos ficam preservados: nomes/denominações, expressões,
reticências e o marcador opaco `*sg_Mx`, sem interpretação ou tradução automática.

- **0x1E26AC..0x1E273C**: carga por offset/tamanho dos campos +0x988/+0x98C
  do objeto global; base carregada em +0xF10 e ponteiros internos fixos
  +0x20, +0xEC0, +0x2590. As divisões do recurso continuam iguais.
- **0x1E2ED4..0x1E2EF8**: consulta base + u32(base + 4 + índice×4).
  O cálculo de endereço foi executado para todos os 172 IDs.
- **0x1E33B4..0x1E33EC**: outro encaminhamento por índice ao texto.
- **0x1E35E8..0x1E3664**: leitura do prefixo numérico entre colchetes e
  avanço do ponteiro antes de exibir o nome. Prefixos `[n]`, números e
  delimitadores permanecem exatamente iguais; o parser inteiro não foi emulado.

Os pools só usam posições comprovadas e lacunas zeradas. Comprimento/colunas
não ultrapassam os máximos observados no próprio conjunto; quebras `|`, espaços
das extremidades e prefixos permanecem vinculados. Nenhuma expansão de arquivo,
alteração de valor numérico ou novo formato de controle foi liberado.

## Revisão dos nomes restantes

Foi classificado o recorte inteiro que estava aberto: das 26 seleções novas,
22 foram preservadas e quatro adiadas; duas propostas antigas também passaram
a preservação explícita. A tabela original de nomes
continua com **516 traduções**, sem aumento artificial por essas decisões.
Ledger: **566 selecionados**, 516 aceitos, **25 pendentes**, **25 preservados**.
Um preservado (ID 55) pertence à categoria protegida, de modo que o recorte
não protegido de 565 se divide em 516 traduzidos, 25 pendentes e 24 preservados.
Não restam nomes não selecionados nesse recorte conservador.

Hawk Eye/Cluster Gun/Grenade Gun mantêm aliases de armas/componentes protegidos.
Curry Lunch e nomes distintivos continuam em inglês; Radar e Sensor já têm
grafia portuguesa. Bunny permanece por cautela, com contexto ainda não comprovado,
não como conclusão de que é um nome próprio. As quatro propostas novas de
aramida, sucata cibernética, porcelana e cinto de campeão ficam adiadas por
espaço. As 25 descrições pendentes e os 123 adiamentos MAP não foram liberados.

## Testes e validação visual

As verificações cobrem fonte/hash, limites SDA, campos NUL, atributos, nomes
protegidos, aliases, números, prefixos, pools, trailer opaco, recusa de overflow,
leitura de volta e round-trip. O relatório final registra contagens dos testes
executados e o delta integral da imagem. Não somar execuções repetidas como
testes distintos. Preflight possui fixture de corrupção de um bit que impede
a chamada do emulador, além de casos de truncamento, transação e relatório alterado.

O usuário testa em uma passagem normal: nomes/ações no combate, dicas de análise,
examinar itens/fotos/mapas e opções/comentários em bares. Conferir cortes,
acentos, largura, seleção, prefixos e efeitos. O layout aprovado em Nina não
comprova automaticamente estes novos contextos. Nenhuma navegação PCSX2 foi
executada pelo agente; validação visual segue pendente. Não é necessário obter
todos os itens ou alcançar Dr. Palm imediatamente.

Uma ISO consolidada por rodada, cinco ISOs de trabalho, alpha permanente fora
da retenção. Sem envio OneDrive ou desligamento nesta solicitação.


## Resultado final executado

- **215 testes distintos aprovados**: 194 de interface, sete do preflight,
  seis de planejamento, cinco de retenção e três da alpha. A suíte inicial
  executou 193 casos em 365,270 s; um filtro de teste incluiu o patch legado
  battle.ptbr-advance como se fosse novo. O filtro foi corrigido sem mudança
  no produto; seis testes v026 passaram em 20,215 s, incluindo um novo caso do
  planejador. Execuções preliminares/repetidas não foram somadas à contagem.
- Auditoria das traduções MAP após resolver herança: 67 nomes ingleses genéricos
  em 5.183 segmentos canônicos, sem correspondências exatas. Isso não comprova
  contexto, flexões ou sinônimos e não expande aliases de diálogo.
- Comparação integral v025→v026: **21.162 bytes diferentes em 1.001 intervalos**,
  todos autorizados em S_PACK; diretório ISO e demais bytes idênticos. Os 1.298
  campos são consolidados em 999 slots fixos e dois patches de pools.
- ISO de **1.704.427.520 bytes**, SHA-256
  `58b1fa85f04fbdf9002dda7f5fafb450bd0d74d64098139a5137a109a7f8707a`.
- Preflight real e iniciador sem abrir emulador passaram; retenção confere cinco
  imagens. A alpha foi conferida e continua protegida. Nenhum teste visual novo
  foi realizado pelo agente.
