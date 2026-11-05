# Interface v067 — relatos da partida e MC Hamir

Receita `translations/interface-v067.json`, sobre v066 integral, com MAP
`translations/regiao-inicial-v047.json` sobre v046. Perfil `ptbr-layout-v005`.
Ferramenta local `tools/screenshot_backlog.py`, manifesto vinculado
`translations/relatos-pos-v066-v001.json`. O pedido de iniciar a tradução
encerrou a pausa de recepção dos relatos.

## Traduções

| Elemento | Redação aplicada |
|---|---|
| Tank Stop | Sem tanques |
| Diário My Arm! | Meu braço! |
| Retirement Compound | Vila dos Aposentados |
| First Continental RR Tunnel | Túnel 1 - Ferrovia Continental |
| Land Battleship Tiamat | Encouraçado Tiamat |
| TIME da dança | TEMPO |
| Dance / Exit / Help | Dançar / Sair / Ajuda |
| Confirmação de pintura | Carregar esta pintura? / (A pintura anterior será perdida) |

As redações dos locais acompanham a terminologia já usada nos diálogos.
O nome do túnel ocupa exatamente 31 bytes no codec do projeto e seu NUL
completa o campo físico de 32. A hifenização acomoda o nome completo da
ferrovia. A tradução de Tiamat também alcança os dois literais ELF vinculados.

As duas falas de MC Hamir recebem português coloquial, com hesitação e
reação de susto preservadas. A primeira passa a “E agora? / Isso não é bom...
/ Cadê aquilo!?”. A segunda inclui “P-Pra que falar / comigo assim, do nada!?
/ Meu coração não aguenta!”, seguida por “Que susto!” em outra página.
Os comandos `%F1`, `%M0_8`, as reticências, Ack!!, quebras e separações de
páginas continuam vinculados ao registro de origem. O personagem mantém
seu nome. A segunda fala recebe um aviso conservador de largura e exige
conferência da margem em partida.

## Limites e evidências

### Diário

Somente registro 31 de `DATA/FDATA/DIARY.DAT`, título em 0x17EC
e corpo em 0x1814, capacidades 39/79 bytes. O corpo conserva a sequência
nativa `81 63`, uma reticência representada por … na receita de autoria.
A rotina aceita essa sequência exclusivamente nesse campo original.
O resto do texto usa ASCII e os pares PT-BR do projeto, com os quatro
separadores `|` na ordem original.

O corpo passa a “E agora?||Dr. Mortem não pode ajudar…||Talvez o Professor
Grey possa.”. Cabeçalho, índice, offsets, nomes e campos vizinhos são
preservados. O teste reabre as fronteiras do diário e desfaz os patches
em memória até recuperar integralmente a origem. Essa exceção específica
permite trabalhar em torno da reticência existente sem liberar outros
campos nativos na política histórica de interface.

### Nomes de locais

O parser de cenas confere os 300 mapas e 839 campos tipo 2/3 da origem.
São seis ocorrências adicionais, em nós tipo 2/7 existentes, com os
descritores e registros vinculados por hash.

| Nome | Mapa | Offsets no MAP.MCT |
|---|---|---|
| Encouraçado Tiamat | 11 | 0x4C3800 |
| Vila dos Aposentados | 143 | 0x10CE27DC, 0x10CE3000 |
| Túnel 1 - Ferrovia Continental | 153 | 0x122E4FDC, 0x122E50B4, 0x122E5800 |

Os literais de Tiamat em ELF 0x31B858 e 0x31B940 recebem a mesma redação
nos intervalos originais. Referências existentes e ausência de aliases
interiores são conferidas. Os títulos supr já traduzidos dessas regiões
continuam usando a terminologia anterior.

### Pintura e controles

Literal de pintura em ELF 0x342180, limitado à string original com NUL.
A quebra entre pergunta e aviso é conservada. A legenda da dança fica
em 0x338B18, em célula de 32 bytes com cauda original zerada e ausência
de referências interiores. Conserva os três tokens de botões, a associação
às ações e a string Pose imediatamente seguinte.

### Ícones e rótulos gráficos

`DATA/MAP/HMAPAC.SDA`, textura 0 em 0x80, 256×256/8 bpp. “Sem tanques”
altera somente [90,44,192,70], dentro do sprite 0 do GANM em 0x10500,
cujo recorte é [4,4,196,70]. O símbolo de proibição permanece pixel a pixel.
Usa Arial Bold local 14, desenhada no tamanho final, com contorno cinza e
tons originais da textura. Os índices de transparência e a paleta são
preservados.

`DATA/RDATA/RMGDANCE.SDA`, entrada 17 em 0x130E00, 512×128/8 bpp.
“TEMPO” altera somente [34,5,100,27], dentro do sprite 3 do GANM em
0x141210, recorte [0,0,456,32]. Usa Arial Bold 17 no tamanho final para
caber entre o símbolo à esquerda e a barra. Números, estrelas, barra e
demais rótulos mantêm seus pixels. As duas edições reutilizam a paleta
original, lida com a permutação CLUT CSM1 já usada nas ferramentas do projeto.

A fonte instalada fica vinculada por hash no manifesto. O preparo e a
compilação funcionam localmente. Previews comparativos ficam em
`work/interface-v067-investigacao/tank-comparacao.png` e
`work/interface-v067-investigacao/dance-comparacao.png`.

### Diálogos

Revisões exclusivas dos registros `map.msgn.1774327c` e
`map.msgn.17743328`. O compilador existente aplica slots de corpo
63/103 bytes e preserva os rótulos em slots próprios. Alvos de 43/99
bytes. Cabeçalhos, registros de 108/148 bytes, controle de expressão,
quebras, rótulos e offsets são conferidos pela reinserção existente.

## Reprodução

```powershell
python tools/screenshot_backlog.py
python -m unittest discover -s tests -p test_screenshot_backlog.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v047.json --interface-draft translations/interface-v067.json --compact-output --build-iso --output work/interface-v067
```

Usar diretório de saída novo, conforme o construtor. O comparador integral
de versões exige a v066 exata como pai. São 14 unidades novas de interface,
além de duas revisões de diálogos. O catálogo alcança 4.393 unidades
heterogêneas de interface. As contagens MAP continuam em 6.044 registros
alterados, 5.991 corpos/opções e 991 referências explícitas.

## Conferência em partida

O usuário verifica Sem tanques com o ícone completo, os três locais,
título/corpo da entrada Meu braço!, legenda e tempo da dança, confirmação
de pintura e as duas falas de MC Hamir. Verificar especialmente a margem
da fala sobre o coração. A validação visual desses novos elementos está
pendente. Os testes desta rodada verificam estruturas e pixels localmente.
Minério pequeno segue aguardando a liberação específica do usuário.

## Entrega verificada

Passaram 34 testes distintos, sendo dez novos e 24 de regressão. A compilação
aceitou os 6.044 registros MAP e 4.393 unidades de interface. Preflight
conferiu tamanho, SHA-256 integral, recibo e ausência de transação pendente.
Os dois atalhos foram conferidos em simulação. O auditor das 16 revisões
históricas de itens retornou zero bloqueadas.

A comparação integral v066→v067 confirmou 3.358 bytes diferentes em 16
patches previstos, com diretório ISO, fontes e layout preservados.
Relatórios `reports/interface-v067.json` e `reports/interface-v067-delta.json`.

ISO `work/interface-v067/MetalSaga-ptbr-interface-v067.iso`, 1.704.427.520 bytes.
SHA-256 `5f12a2a766900bbf17c57b0f904945a115379634428660346611c62bffc53c0d`.
Backup independente v059 teve hash integral e atributo somente leitura
conferidos. A retenção manteve cinco ISOs de trabalho e retirou a antiga
v062. Relatórios e receitas históricas foram preservados.
