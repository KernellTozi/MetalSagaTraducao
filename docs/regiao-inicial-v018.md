# Lote ampliado v018

## Escopo e resultado

O recorte `0x0BE1FD64..0x1FF30844` reúne 5.163 registros. A expansão acrescenta
800 ocorrências: 444 alvos próprios, 282 reutilizações por identidade dos
segmentos originais e 74 adiamentos. As reutilizações foram revisadas nas
sequências disponíveis; igualdade de bytes não comprova identidade de contexto.

| Versão | Registros no recorte | Traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v017 | 4.363 | 3.432 | 3.611 |
| v018 | 5.163 | 4.034 | 4.251 |

São 602 registros traduzidos adicionais. Os 4.363 registros anteriores são
preservados integralmente, incluindo metadados. Os dez nomes franceses da coleção
de tanques permanecem intactos e não contam como novas traduções.

A cobertura chega a aproximadamente 55,79% dos 7.231 registros textuais
catalogados no MAP.MCT. Essa medida inclui escolhas e mensagens de sistema;
não representa percentual de palavras nem da tradução completa do jogo.

## Contexto trabalhado

- Beldaire (`0x0BE1FD64..0x0BE2DBB4`): oficinas, C Units, mansão, coleção de
  tanques, agricultores e Hunters. Preservar condições de serviços e modelos.
- Scavenger Isle (`0x0DB0A9BC..0x0DB1AAE8`): trabalhadores, pesca, serviços,
  plataforma, abastecimento, poluição e histórias de patrulha. Manter humor,
  diferenças sociais e gravidade dos relatos de ferimentos e mortes.
- `0x0E55103C..0x0E5524BC`: avaliação de sucata, comércio e ruínas do ponto
  de ônibus. Bus Stop Sign permanece como nome de item.
- Alice One (`0x0E76738C..0x0E77A090`): recrutamento, memórias da casa, Banjo,
  Leon, Eddy/Explorer, Crazy Wayne, transporte e informações de caça. Preservar
  nomes dinâmicos, direções e diferenças nas reações dos companheiros.

São agrupamentos inferidos pela sequência disponível, não identificação
comprovada de todos os falantes ou condições de roteiro. Não houve tradução
em massa de tabelas de equipamentos e inimigos.

## Limites e integridade

Dos 1.129 registros preservados, 265 estão adiados. Os 74 novos adiamentos são
52 com controles opacos, 18 com terceira string sem edição liberada e quatro
com ambas as condições. Nenhuma verificação foi relaxada para aumentar contagens.

A compilação tem zero recusas e zero violações de terminologia. Controles,
páginas, escolhas, offsets e limites continuam vinculados aos originais. A
exceção ASCII `nao` permanece restrita a `map.msg.1df8bec0`. O recorte reúne
1.125 grupos SSD e mantém 416 avisos conservadores de largura. Esses avisos
não medem pixels e precisam de observação manual em amostras acessíveis.

A suíte completa passou: 113 testes em 185,680 segundos.
O teste de regressão reproduz a preparação, verifica a preservação completa da
v017, os adiamentos, os nomes intactos da coleção e a exceção ASCII autorizada.
Fontes v002 e espaçamento v003 continuam assumidos provisoriamente corretos
pelo usuário; a aprovação binária não equivale a validação visual desta ISO.

## Uso

- `Preparar-Regiao-Inicial.cmd`: recompila e valida a v018 sem criar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO atual.
- ISO: `work/regiao-inicial-v018/MetalSaga-ptbr-regiao-inicial-v018.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v018/`.
- Metadados próprios: `reports/regiao-inicial-v018-validation.json`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v018.json --output work/reconstrucao-v018 --build-iso
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v017.json --start-offset 0be1fd64 --lot-id regiao-inicial-v018 --output work/preparacao-v018-repro
python -m unittest discover -s tests
```

Não foi realizada navegação no PCSX2 nesta entrega. No teste manual, observar
acentos, espaçamento, limites das caixas, escolhas e passagem de páginas em
conversas acessíveis de Beldaire, Scavenger Isle ou Alice One.


## Construção verificada

A ISO possui 1,704,427,520 bytes. A comparação integral confirmou que os
333,067 bytes diferentes correspondem exatamente aos patches
previstos, incluindo fontes e espaçamento; o diretório do disco permaneceu
idêntico. Não houve realocação de registros, aumento de extents ou alteração de
originais, BIOS, saves e configurações.

SHA-256: `efb39df0a6f4f874161d892b7b7dc469da12ea20d53b840ae846b04eef0d1d2a`.

A retenção removeu `work/MetalSaga-ptbr-experimento.iso`, a imagem gerada mais
antiga, correspondente ao experimento do diário. Sua receita e seus relatórios
permanecem preservados. Há dez ISOs de trabalho após a construção; a original
em `JOGO/` fica fora dessa contagem. O atalho histórico do diário exige
reconstrução para voltar a ser utilizado.
