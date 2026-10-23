# Interface v001 — Satcom, mensagens e menus

## Mudança de prioridade

Por solicitação do usuário: trabalhar primeiro no HUD/Satcom/mensagens/menus, depois nos itens e deixar os pequenos registros restantes do MAP.MCT para o final. As 5.892 traduções v029 e os 123 adiamentos permanecem intactos. Este lote acrescenta **88 strings do executável**, sem contar essas strings como novos diálogos.

O lote cobre seletores e avisos de pastas/mensagens, descrições das funções do Satcom, controles/atalhos, navegação e seletores do diário/monstros. Não representa a tradução completa desses sistemas. O corpo das mensagens e as entradas de DIARY.DAT não foram alterados. O título de uma entrada do diário, por exemplo, não muda por traduzir seu seletor.

## Execução local

- `Preparar-Interface.cmd`: compila e valida sem construir ISO; relatórios e revisão bilíngue ficam em uma pasta nova de `work/pilotos/`.
- `Testar-Interface.cmd` ou `Iniciar-Teste.cmd` sem argumentos: abre a ISO consolidada de interface no ambiente isolado de teste existente. Não restaura savestate. A ferramenta recusa uma segunda instância compartilhando esse ambiente.
- `Testar-Regiao-Inicial.cmd` continua apontando à base histórica v029, sem o lote de interface.

Construção reproduzível, na raiz, com Python 3.11+ e as dependências locais das fontes já instaladas:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v029.json --interface-draft translations/interface-v001.json --output work/interface-v001 --build-iso
```

A saída deve ser nova; para reconstruir, escolha outra pasta sob work/. O comando não sobrescreve uma imagem existente. Resultado desta versão: `work/interface-v001/MetalSaga-ptbr-interface-v001.iso`. O processo usa somente arquivos locais, sem IA/APIs. O compilador verifica o vínculo à v029 e ao layout `ptbr-layout-v005` e inclui as fontes compatíveis. A retenção mantém no máximo dez ISOs geradas mais recentes; receitas e relatórios permanecem.

## Evidências do executável

Fonte: `SLUS_212.93`, SHA-256 `25756885a1a01a4ddd82045fd78e1928c09873f810cf182b99b248914fb1ea71`. Offsets abaixo são do arquivo, não da ISO. Nas regiões examinadas o endereço virtual corresponde ao offset + `0xFF000`.

| Região | Offset | Tamanho | Uso na análise |
|---|---:|---:|---|
| .text | 0x1000 | 0x25A108 | Instruções que formam endereços |
| .data | 0x263B80 | 0xAEF50 | Referências diretas |
| .rodata | 0x312B00 | 0x35BC8 | Literais |
| .sdata | 0x348800 | 0x1870 | Literais curtos e tabelas |

`tools/interface_text.py` encontra 4.297 strings ASCII terminadas em NUL nas duas seções de literais. Há nomes internos, caminhos, debug e textos que não são interface. Apenas as 88 entradas revisadas da receita recebem patch; referências são evidência de endereço, sem provar todas as telas e caminhos de execução.

Exemplos de consumidores conferidos no original:

- Seletor de pasta em `0x32CA00`: LUI `0x123718`, ADDIU `0x123724` no delay slot de JAL `0x123720` ao método em VA `0x22BB80`. Seletor de mensagem em `0x32CA10`: par `0x12381C`/`0x123828` e chamada `0x123824` ao mesmo método.
- Seletor de nota em `0x32D188`: par `0x128D94`/`0x128DA0` e chamada `0x128D9C` ao mesmo método. Aviso sem notas em `0x32D198`: par `0x1294FC`/`0x129500`, chamada `0x129504` a VA `0x20ED40`.
- Tabela em `0x3497F0` aponta para `0x32D160` e `0x32D178`; o código forma seu endereço em `0x128C0C`/`0x128C24`.
- Tabela de doze descrições em `0x32DB78`, referenciada em `0x12F74C`/`0x12F768`, reúne as funções do Satcom.

O catálogo conserva referências de ponteiros alinhados, GP+ADDIU e pares LUI+ADDIU/ORI. É uma análise conservadora e parcial, não uma prova completa de fluxo ou ausência de aliases dinâmicos. Um alias interno encontrado em `0x349820` impede sua edição; `0x32C000`, sem referência reconhecida, também continua pendente. Não relaxar esses bloqueios para aumentar contagens.

## Política de reinserção

`elf-ui-fixed-original-string-v001` exige hash do ELF inteiro e de cada origem, ID único e grupo contextual, referência reconhecida e nenhum alias interior reconhecido. Não altera código ou ponteiros. O orçamento é **somente o comprimento original**, sem aproveitar alinhamento/padding. A tradução termina em NUL e recebe zeros até o NUL final original; o intervalo total permanece idêntico. Preserva os espaços iniciais, sequência exata de parâmetros printf (incluindo `%s`), `|`, `;`, tabulações e quebras. Percentuais desconhecidos são recusados.

Os caracteres usam o mapeamento próprio de `gfi.py` e as fontes compatíveis, não UTF-8/CP932 comum. Exemplos: ç=`82 40`, é=`82 45`, í=`82 47`, ê=`82 46`. O custo de um acento é dois bytes. Rótulos pequenos usam abreviações como Msgs, Hab., Veíc. e Depós.; textos que exigirem crescimento ficam para investigação de referências/realocação, sem cortar artigos de frases para caber. Drive permanece igual ao tutorial/interface existente. Não modifica nomes de itens ou entidades.

Validações: orçamento por string, controles, round-trip Unicode, tamanho/seções do ELF, releitura de patches e restauração byte a byte ao original. A construção verifica também offsets de cada recurso, diretórios ISO9660 e todas as diferenças contra o conjunto esperado de patches. Testes e evidência da compilação ficam em `reports/interface-v001-tests.json` e `reports/interface-v001-validation.json`.

## O que é imagem no HUD

Previews das três primeiras entradas de cada um de FBS_DATA.SDA/F_COMMON.SDA foram exportados e inspecionados. Observações verificadas nas imagens extraídas, ainda sem edição:

- **FBS_DATA.SDA, entrada 0, offset 0x40:** botões de batalha com palavras desenhadas, incluindo Weapon, Skill, Equip, Item e Drive.
- **Entrada 1, offset 0x10450:** peças de moldura do Satcom.
- **Entrada 2, offset 0x20860:** Satcom, BS-Controller, From, Title e Playing Time desenhados. Eles **continuam em inglês nesta ISO**.
- **F_COMMON.SDA, entrada 0:** ícones de botões/analógicos e START/SELECT. Entradas 1/2: fundos, sem texto de menu identificado nesses previews.

Nas seis entradas examinadas: cabeçalho `<HHIII>` (largura, altura, profundidade dos índices, offset da paleta e dos pixels), paleta de 16/256 cores RGBA e pixels indexados de 4/8 bits; nos de 4 bits, nibble baixo primeiro. A visualização linear produziu imagens legíveis. Isso não libera todas as entradas ou outros recursos; não inferir formato pelo nome SDA. Animações e outras estruturas não são tratadas por este exportador.

```powershell
python tools/interface_text.py --output work/interface-catalog-novo.json
python tools/interface_textures.py --output work/interface-previews-novos
```

O exportador aceita somente seis entradas inspecionadas, confere hashes de origem e cria PNGs **de visualização RGB**, com manifesto de offsets/tamanhos/hashes. Não preserva alpha/índices no PNG e **não oferece importação ou round-trip de PNG**. Não usar esses previews como se fossem assets reinseríveis. Os binários/fontes/imagens extraídos ficam em work/, fora do Git. A triagem adicional de FDATA está em `reports/interface-resource-triage-v001.json`; ausência de uma busca ASCII não prova ausência de texto.

## Roteiro manual e próximos passos

Não foi realizada navegação no PCSX2 nesta etapa. Na ISO identificada, abrir Satcom e observar descrições inferiores das funções, menu de mensagens (pastas/seleção/aviso sem mensagens), diário (seleção de notas) e configurações de controle. Exemplos esperados: “Escolha a pasta”, “Leia as mensagens”, “Consulte o diário”. Verificar acentos, truncamento, quebras, seleção/volta e comportamento dos atalhos. Em frases parametrizadas, verificar que o nome/posição variável permanece visível. Alguns componentes gráficos e o corpo das mensagens continuam originais.

O layout v005 aprovado nas falas de Nina foi mantido; essa aprovação não garante todas as fontes/contextos do Satcom. Registrar a versão e tela se aparecerem quadrados, espaçamento anormal ou cortes.

Próxima etapa: ampliar o catálogo por telas e localizar a origem dos corpos das mensagens/ajuda; preparar exportação/importação fiel dos rótulos gráficos com paleta, alpha, índices e metadados preservados antes de desenhá-los em PT-BR. Resolver a interface de forma coerente antes de começar os dados de itens. Os 123 adiamentos do MAP continuam congelados.


## Resultado desta construção

- 28 testes direcionados passaram; zero falhas/erros. Os dois testes de regressão v029/layout fazem parte desse total; não foi executada toda a suíte histórica.
- 88 strings novas; 5.892 diálogos traduzidos preservados, nenhum novo diálogo traduzido nesta etapa.
- Comparação da ISO inteira com v029: exatamente 1.272 bytes diferentes, todos dentro dos 88 patches revisados de UI. MAP.MCT, fontes e todos os demais recursos permanecem idênticos à v029; ELF idêntico fora dessas strings. Diretórios, extents e tamanho ISO9660 mantidos.
- ISO: 1.704.427.520 bytes; SHA-256 `f928e0c375db669e16f078d6a0b7a4bd053ab3e933e7732e3772f14beb00bc58`.
- Dez ISOs de trabalho após construir; v022 removida pela retenção, receitas/relatórios preservados. Original intacto.
- Iniciador conferido por `--dry-run`, sem abrir o PCSX2. A interface nova ainda depende do teste visual manual.
