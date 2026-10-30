# Interface v056 — lacunas observadas no Satcom e nas saídas

Correções motivadas pelas quatro capturas enviadas pelo usuário:

| Elemento observado | Resultado |
|---|---|
| Select a shop | Qual loja? |
| Current | Atual |
| Target | Meta |
| Overworld Map, aviso de saída | Mapa do mundo |
| Tempo de jogo | Mantido em português, redesenhado no estilo nativo do Satcom |

Não foram aplicadas as sugestões de nomes das armas. A lista entregue na
v055 continua disponível e aguarda a revisão humana.

## Por que esses textos ficaram de fora

**Lojas.** O literal de ELF+0x32CB78 tem referência real em 0x1253B8–0x1253EC.
O carregamento LUI de seu endereço fica no delay slot de um branch; o scanner
conservador anterior não atravessava esse caminho. Executou-se o encaminhamento
de instruções originais com modo 1 em RAM simulada: A1 = 0x42BB78 na chamada
para o método VA 0x22BB80. Este cria o componente textual e encaminha a string
em 0x12CC04–0x12CC18. O catálogo genérico não foi relaxado.

O original tem 13 bytes; “Escolha a loja” precisaria de 14. Foi adotado
“Qual loja?”, dez bytes, uma pergunta natural no contexto de seleção,
sem suprimir um artigo de uma frase para forçar sua inserção.

**Meta financeira.** Os formatos ficam em ELF+0x32C1C0 e +0x32C248. O primeiro
é precedido por metadados não NUL; o segundo contém LF. Assim, não entram na
varredura antiga de literais ASCII isolados. Os encaminhamentos originais foram
conferidos até a chamada do formatador: ponteiros 0x42B1C0/0x42B248, argumentos
modelados 200/500. O caso Current inclui a leitura no delay slot da chamada.
Não foi executado o formatador completo ou seu desenho no jogo.

Os novos prefixos são `Atual:        %8dG` e `Meta:         %8dG\n`.
As larguras `%8d`, o sufixo G, o LF e a posição do parâmetro após 14 bytes
foram preservados. Slots, endereços e NUL final original não mudam.

**Mapa do mundo.** O literal correspondente do ELF já estava traduzido.
As capturas revelaram outros rótulos no MAP.MCT: **113 prefixos**, em
**8 nós tipo 6 e 105 nós tipo 7**, dentro das 300 árvores maps já estudadas.
Os payloads têm exatamente 204/216 bytes. Foram aproveitados o parser e a
validação de árvores de `tools/scene_name_fields.py`, sem promover os 839
nomes de tipos 2/3 para edição.

Os construtores de tipo 6/7 estão nos offsets de ELF 0x7E408/0x7E7E0;
instalam as vtables VA 0x403ED0/0x403E78. Os loaders em 0x44F74 e 0x45064
copiam a string inicial com strcpy, e preservam os demais campos separadamente.
Os getters virtuais +0x4C são VA 0x17D5C0/0x17D988 e retornam o payload
armazenado em objeto+0x3C. Os dois getters foram exercitados com memória
modelada; o carregador e uma transição real de cenário não foram executados.

A edição é restrita ao prefixo exato de 13 bytes: Overworld Map → Mapa do mundo.
O NUL em +13 permanece. **86 registros têm bytes não zerados no restante
da janela de 32 bytes:** eles são metadados opacos, não padding ou espaço
livre. Todos os bytes desde +13 até o fim de cada registro são preservados,
assim como nós, IDs, referências, destinos, geometria e scripts. Os hashes
de cada nó e payload completo ficam vinculados no manifesto.

Todas as 113 ocorrências ASCII exatas do original MAP coincidem com esses
prefixos tipados, sem duplicação com os payloads-pais que os contêm.
Isso não autoriza traduzir outros nomes de nós nem comprova ausência de
texto comprimido ou de grafia diferente em outros recursos.

## Cabeçalho Tempo de jogo

A célula GANM 21 da textura 2 de FBS_DATA.SDA ocupa [104,232,248,248].
O desenho anterior usava glifos de diálogo reduzidos e preservava linhas
residuais do letreiro original acima da área interna limpa.

Agora o letreiro inteiro, dentro dessa célula, usa o alfabeto raster nativo
do Satcom já reconstruído e alinhado. A letra p vem de Shops; T vem de Title,
com um pixel de prolongamento do traço para alinhar a linha de base. A máscara
tem 101×15 pixels, sem redimensionamento. As cores e o alpha vêm da paleta
original. Nenhuma fonte GFI, métrica ou perfil de acentos foi alterado.
Não mudar os outros rótulos do atlas junto desta revisão.

Comparação local: work/interface-v056-previews/tempo-comparacao.png.
O resultado ainda depende da avaliação visual do usuário no PCSX2.

## Política, reprodução e versão de teste

Política exata `satcom-observed-gaps-and-fixed-exit-labels-v001` em
`tools/satcom_observed_gaps.py`; manifesto
`translations/satcom-lacunas-v001.json`. O filho v056 valida o pai v055
integralmente e acrescenta 116 patches: três ELF e 113 de navegação. Revê
somente o patch existente da textura 2 de FBS. Os atlas de batalha v055
e todas as traduções anteriores são preservados.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v056.json --compact-output --build-iso --output work/interface-v056-reproducao
python -m unittest discover -s tests -p test_satcom_observed_gaps.py -v
python tools/start_test.py --dry-run
```

Abrir **Iniciar-Teste.cmd**; ISO:
`work/interface-v056/MetalSaga-ptbr-interface-v056.iso`.

SHA-256: `16a3369fd5170260623b1a029db9f43b85b98d9bb0747edc093882673fc271c1`.
Tamanho: 1704427520 bytes. A interface passa a 3978 unidades heterogêneas.
Os números dos diálogos MAP não são inflados pelos novos rótulos de saída:
continuam 6044 registros alterados, 5991 corpos/opções, 991 referências de
falantes e 541 nomes de itens. Essa contagem não é porcentagem do jogo.

Teste visual solicitado ao usuário: abrir Lojas e a meta financeira no Satcom,
conferir os rótulos/valores, observar Tempo de jogo e aproximar-se de uma
saída para o mapa externo. Confirmar também que a transição funciona como
antes. PCSX2 não foi executado nesta rodada. Relatórios de integridade e
delta integral ficam em reports/interface-v056.json e interface-v056-delta.json.
O pacote de distribuição local v054 é histórico e não inclui essas correções.
