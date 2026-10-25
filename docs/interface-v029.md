# Interface v029 — painel de senha e navegação na entrada de nomes

Uma versão consolidada com duas frentes de interface:

| Recurso | Alteração |
|---|---|
| Botão gráfico UNLOCK | DESTRAVAR |
| Botão gráfico LOCK | TRAVAR |
| Botão gráfico EXIT | SAIR |
| BACK nas três legendas de entrada de nomes | VOL. |

São **três campos gráficos novos** e **três slots de legenda revisados**. Os
slots pertencem a registros já traduzidos; não contam como três registros
inéditos. O acumulado passa de 3.446 para **3.449 campos/ocorrências**.

Todos os diálogos MAP v030, 566 descrições/925 referências, 516 nomes de itens,
textos de batalha/bares, fontes/layout v005 e arte do título v014 permanecem
iguais. Continuam 25 nomes pendentes; não foram encurtados perdendo sentido ou
alterando identificadores para aumentar contagens. Isso não é porcentagem
de todas as telas do jogo.

## Uso e conferência visual

Abra `Iniciar-Teste.cmd`, apontando para:

`work/interface-v029/MetalSaga-ptbr-interface-v029.iso`

Na entrada de nomes, conferir `VOL.` junto ao botão correspondente ao BACK
original. Ele deve continuar movendo a seleção da grade de caracteres para a
linha de categorias, sem apagar o nome. `TITLE` permanece em inglês: o destino
final do encerramento no chamador ainda não está comprovado.

No painel de senha M.M.S.S., conferir os três botões à direita, o botão
selecionado e a legibilidade. Números, setas, teclas, senha e ações permanecem
originais. Não é necessário alterar uma senha, abrir um save existente ou
modificar dados pessoais apenas para testar a tradução.

O preview comparativo foi inspecionado localmente e fica em
`work/password-v029-comparacao.png`: original à esquerda, resultado à direita.
Isso não é captura do PCSX2. O agente não executou o emulador nesta rodada;
validação visual em jogo permanece pendente para o usuário.

## Botões gráficos de senha

Ferramenta local `tools/password_graphics.py`; política opt-in
`password-panel-three-native-labels-v001`.

- Original: `DATA/FDATA/PASSWORD.SDA`. Textura da entrada **6**, offset
  **0x618B0**, extensão **0x10410** (66.576 bytes): cabeçalho de 16 bytes,
  paleta RGBA original de 1.024 bytes e 65.536 índices, 256×256/8 bpp.
- GANM da entrada **13**, offset **0x71D80**, 19 registros de 16 bytes.
  Só os pixels dos três retângulos abaixo são alterados; o GANM é imutável.

| Sprite | Retângulo [x0,y0,x1,y1), em pixels | Texto |
|---:|---|---|
| 18 | [154,170,252,192) | DESTRAVAR |
| 1 | [154,200,252,222) | TRAVAR |
| 0 | [154,230,252,252) | SAIR |

Composição de palavras completas com a GFI existente, pelo mesmo renderizador
local já usado na interface. Nenhuma fonte GFI é alterada. Altura de célula de
20 pixels, centralização no hotspot original (49,11) e margem horizontal.
DESTRAVAR ocupa 94 pixels contra 98 naturais (escala horizontal 0,95918);
TRAVAR e SAIR mantêm escala horizontal 1. Isso não muda as escalas de desenho
do jogo, nem reduz todos os caracteres para acomodar a palavra longa.

A paleta e o alpha brutos são preservados: índice zero transparente, demais
índices com alpha 127. Somente cores da própria paleta são usadas. Header,
SDA, dimensões, seis outras texturas, registros GANM, índices das teclas numéricas e
demais pixels permanecem intactos. Não se edita comparação de senha, estados,
armazenamento, colisões, áudio ou comandos do controlador.

### Evidências do carregamento e uso

Offsets abaixo são do ELF original. Cada janela está vinculada por SHA-256,
além do hash integral do ELF e do recurso original.

- `0x32E120`: literal `password.sda`; carga em `0x131950..0x131964`.
- `0x131A68..0x131A90`: envia base+0x618B0 e tamanho 0x10410 ao upload da
  textura `password_panel07.imd`, contexto +0x820.
- `0x32E290`: offsets dos GANM; `0x32E2B0`: sequência de 15 sprites de teclas
  `[4..15,18,1,0]`. São doze teclas numéricas/setas e três ações.
- `0x132C20..0x132C40`: encaminha contexto +0x820, base+0x71D80 e sprite
  da tabela ao método gráfico. As instruções originais foram executadas em
  RAM sintética para **todas as 15 teclas**, além do caso de upload da textura.
- Switch em `0x1321C4..0x1321E4`, tabela `0x32E200`: teclas 12/13/14 chegam
  aos blocos `0x132300`, `0x132314`, `0x132328`. Os primeiros encaminham modos
  0/1 à rotina existente; o último retorna o resultado de saída. Esses blocos
  não são modificados.

A investigação liga explicitamente textura, GANM, teclas e ações; não infere
uso apenas por proximidade de arquivos ou compatibilidade geométrica. O probe
não executa carregador completo, GPU, validação de senha ou PS2.

## BACK na entrada de nomes

`tools/name_back_command.py` prova a navegação pelo perfil
`name-entry-back-navigation-v002`. O compilador histórico de legendas continua
reproduzindo BACK; somente a receita v029 opta por `VOL.`.

- Consulta do botão e ramo: `0x10BA5C..0x10BA90`.
- A partir de `0x10BA74`, se a linha em +0x3020 não é zero, o código zera essa
  linha e copia o seletor +0x2700 para a coluna +0x3022. Encaminha o redesenho
  a `0x10CBA8`; não chama a rotina de exclusão e não altera o buffer do nome.
- A prova executa **42 casos**: sete linhas, três seletores e nome vazio ou
  preenchido. Quando já está na linha zero, não muda a seleção.
- A seleção de legenda em `0x10D540..0x10D584` também foi executada em **oito
  casos** de nome vazio/preenchido, flag e modo. Ela distingue as variantes
  TITLE/CANCEL/DELETE. Isso ajuda a separar funções, mas não comprova o destino
  de TITLE no fluxo externo; ele não foi traduzido por hipótese.

Somente os quatro bytes de BACK em cada uma das três legendas recebem `VOL.`:
**12 bytes diferentes**, com os mesmos offsets, NUL, ícones nativos, espaços,
cabeçalho e demais palavras. Não se amplia a liberação dos bytes nativos dessas
legendas nem do texto digitado pelo jogador.

## Reprodução local

```powershell
python tools/plan_interface_menus.py
python tools/password_graphics.py --output work/senha-comparacao-nova.png
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v029.json --output work/interface-reproducao-v029 --compact-output --build-iso
python tools/verify_test_iso.py work/interface-v029/MetalSaga-ptbr-interface-v029.iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

O preview exige um caminho novo e não altera a ISO. A construção é inteiramente
local, sem IA, API ou internet; usa os originais e dependências já documentados.
O perfil vincula também o SHA-256 exato da textura produzida: uma divergência
de renderização/dependências interrompe a construção, em vez de mudar
silenciosamente o resultado da mesma versão.
O planejador mantém o mesmo `work/planejamento-interface.json`, agora com os
três rótulos gráficos e a pendência de TITLE, sem produzir catálogos por botão.

Validação binária, hash e comparação integral ficam no relatório próprio
`reports/interface-v029.json`. Manter cinco ISOs de trabalho e a alpha permanente
protegida; sem envio OneDrive ou desligamento automático.

## Continuidade

O recorte conhecido de descrições está concluído. Os 25 nomes ainda exigem
espaço/glifos ou decisão de identidade: não sacrificar significado, artigos ou
nomes protegidos. TITLE continua dependente do chamador, e FNAME_DT contém
grafismos de bancos/END cujo uso deve ser ligado às variantes corretas antes
de editar. F_COMMON também contém nomes físicos de botões START/SELECT e
superfícies, não um lote de palavras novas a traduzir. A auditoria não autoriza
alterar grafismos japoneses de bancos aparentemente inativos.

Depois das lacunas reais de interface, retomar os controles MAP restantes em
famílias e acumular revisão contextual/visual em partida normal. Não declarar
cobertura completa da interface ou de todo o jogo com base nesses catálogos.


## Resultado final executado

**258 testes distintos aprovados**: 237 de interface (464,669 s), sete de integridade do iniciador, seis de planejamento, cinco de retenção e três da alpha. Após fixar o hash da textura, os oito casos gráficos foram reexecutados, incluindo recusa de raster divergente, sem somá-los novamente. A validação final do compilador produziu o mesmo relatório de interface da construção da imagem.

Comparação integral v028→v029: **3.638 bytes diferentes em quatro intervalos autorizados** — uma textura e três legendas. Diretório ISO e todos os demais bytes idênticos; tamanho 1.704.427.520 bytes. SHA-256 da ISO:

`f6d5bde30abbda60206a4434663e717e6735c71c7c92f90b260514a250254ca3`

Preflight real e iniciador em dry-run aprovados, sem abrir PCSX2. Cinco ISOs de trabalho confirmadas, alpha conferida por hash/atributo somente leitura.
