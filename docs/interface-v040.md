# Interface v040 — Carregando

Atualização de 26/10/2026. O usuário definiu o novo escopo gráfico:
pôsteres wanted intactos, títulos de cassino/minijogos como WIN/LOSE/ROUND
dispensados, trabalho já feito preservado e Now Loading traduzível como
Carregando. Essas regras substituem o planejamento anterior de cartazes
genéricos e títulos gráficos de minijogos. Menus/instruções em texto continuam
no escopo. Os créditos entregues na v039 permanecem iguais.

## Alteração isolada

A receita `translations/interface-v040.json` herda integralmente a v039 e
acrescenta somente um rótulo gráfico: **Carregando**. São **3.805 campos de
interface**, sem alegação de porcentagem global. MAP v037, layout/fontes v005,
arte inicial v014, legendas de pintura e demais traduções são preservados.
As seis propostas de pintura continuam separadas, sem aprovação presumida.

`tools/loading_graphics.py` implementa a política opt-in
`loading-carregando-original-palette-fixed-sprite-v001`. Alvo único:

| Campo | Valor |
| --- | --- |
| Recurso | DATA/RDATA/RLOADING.SDA |
| Entrada de textura | 2, offset 0x8D0, tamanho 0x1050 |
| Imagem | 256×32, 4 bits por pixel |
| Plano de pixels alterável | 0x920, 4.096 bytes |
| GANM preservado | entrada 3, 0x1920, um único sprite |
| Retângulo/hotspot | 0,0–256,32; 128,16 |

Nada é realocado ou expandido. Paleta, alpha, cabeçalho, outra textura,
descritores, GANM, hotspot e código ELF ficam intactos. A receita vincula
hashes de fonte, janelas do ELF e textura resultante; qualquer alteração do
desenho exige nova revisão/receita, sem mudar silenciosamente a reprodução.

## Desenho e comparação visual

Imagem apresentada no chat e salva em:
`work/carregamento-v001/comparacao-final.png`.
Original acima e tradução abaixo, ambos em ampliação 3x sem suavização.
Trata-se de preview do atlas, não de captura do PCSX2.

As letras são desenhadas por retângulos inteiros: hastes de quatro pixels,
travessas de um pixel, maiúscula com 19 pixels de corpo e minúsculas com
11. Linha de base 23 e descendente até 28, como no original. Cinco máscaras
paramétricas (`a`, `d`, `g`, `n`, `o`) conferem **pixel a pixel** com a geometria
de tinta original; `C`, `r`, `e` foram construídas na mesma grade. Não foi
usada fonte instalada, escala horizontal, colagem ou alteração de GFI.

A palavra ocupa 176 pixels, com intervalo de três pixels entre letras,
mantendo o centro do conjunto de tinta anterior. As cores vêm da própria
tinta original na mesma linha; para posições antes vazias usa-se a amostra
mais próxima daquela linha. Paleta e valores de alpha não são recalculados.
O resultado gráfico ainda precisa de conferência em jogo pelo usuário.

## Evidência de uso e limites

O nome original embutido no ELF em 0x33ADA8 corresponde a
`\data\rdata\rLoading.sda`. Foram executados oito encaminhamentos inteiros
originais em memória sintética:

- Nome do recurso no chamador 0x17524C–0x175250.
- Dois descritores, stride 56, da tabela ELF 0x268788: argumentos de textura
  em 0x1752DC–0x175324 e de GANM em 0x17532C–0x175338.
- Seleção do objeto de textura em owner+0x9A0 (0x175650–0x175658), do
  gerenciador GANM em owner+0xB30 (0x175678) e do ponteiro para o primeiro
  sprite desse gerenciador (0x17571C).

Bases de objetos/stack, fonte carregada e ponteiro do gerenciador foram
fornecidos pelo harness. Não foram executados carregamento completo, upload,
GPU, animação de FPU ou PCSX2. O recorte é uma palavra inteira, sem substituir
sprites individuais ou alterar temporização da tela.

## Testes e execução

Passaram **40 testes distintos**, oito novos: correspondência das cinco
máscaras nativas, argumentos originais, hashes, fronteiras e corrupção,
reversão, paleta/alpha, tradução exata, hash do raster, preservação integral
da receita v039 e proteção da saída de previews. Inclui regressões dos
créditos e propostas de pintura, preflight, retenção e alpha.

```powershell
python -m unittest discover -s tests -p test_loading_graphics.py
python tools/loading_graphics.py --preview work/minha-comparacao-carregando.png
```

Para reconstruir em pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v037.json --interface-draft translations/interface-v040.json --compact-output --build-iso --output work/minha-v040
```

`Iniciar-Teste.cmd` aponta para a ISO consolidada v040 e
`Preparar-Interface.cmd` valida a receita correspondente. No teste manual,
observar uma tela que antes mostrava Now Loading: legibilidade, recorte,
posição, cores e comportamento do carregamento. Não é necessário repetir
navegação longa ou testes dos créditos.

Metadados finais da ISO e comparação integral com a v039 ficam em
`reports/interface-v040.json` e `reports/interface-v040-delta.json`.
Somente depois da comparação concluída o iniciador passa para a nova imagem.
Máximo de cinco ISOs de trabalho; alpha permanece fora da retenção.

Comparação integral concluída: **2.368 bytes diferentes**, todos nos 4.096
bytes autorizados de pixels RLOADING. Os demais bytes e o diretório ISO são
idênticos à v039. A conferência integral de tamanho/hash da v040 passou:
1.704.427.520 bytes, SHA-256
`e035aa3a4cdb50aab56509ba0aad04fb9d85a5ebd0bbf7b6a3d2963cea363ae1`.
Cinco ISOs de trabalho e hash da alpha conferidos. Nenhuma navegação PCSX2,
transferência OneDrive ou desligamento foi executado nesta etapa.

Próximos trabalhos: menus/instruções em texto ainda pendentes, composição dos
botões de pintura após revisão da arte e demais elementos de interface úteis.
Não buscar mais diálogos indiscriminadamente, nem recriar títulos dispensados
dos minijogos ou rótulos de pôsteres wanted.
