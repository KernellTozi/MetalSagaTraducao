# Layout PT-BR v004 — primeiro experimento de métricas

**Retorno manual posterior: o usuário confirmou que o alargamento persistiu.** A correção desta rotina foi insuficiente para a fala de Nina. Consultar `layout-v005.md` para o segundo caminho de desenho identificado. Para reproduzir a ISO antiga, usar `python tools/start_test.py --iso layout-v004`; o iniciador de acentos passa a apontar para a v005.

## Problema confirmado e diagnóstico

Em 22/10/2026, o usuário reprovou a aparência dos acentos na versão consolidada. Nas capturas de Nina, o ê de “Você” e o É de “É um trabalho” aparecem desproporcionalmente largos. A premissa anterior de caracteres provisoriamente corretos foi retirada para este trabalho. A tipografia não está aprovada.

O perfil v002 conserva o bitmap do corpo de várias minúsculas. O patch v003 altera a largura no cache, mas não a rotina de layout dos diálogos. Foi localizada uma segunda decisão no ELF original, função em offset `0x3E520..0x3E857` (VA = offset + `0xFF000`):

- `0x3E568..0x3E59C`: um código de dois bytes recebe largura e avanço iguais ao tamanho completo, margem zero e bearing zero.
- `0x3E5A0..0x3E5C8`: ASCII recebe meia largura, margem 2 e avanço inicial de meia largura.
- `0x3E5CC..0x3E824`: o modo latino consulta tabelas de bearing/avanço para letras e ajustes de pontuação.
- Tabelas em offsets `0x316830` (22) e `0x316898` (26), com pares de bytes assinados.
- O consumidor em `0x3DF48..0x3DF98` combina a largura com a margem, ajusta o retângulo de textura pelo bearing e soma o avanço. Há outros consumidores da mesma rotina.

Exemplo medido pelo teste de instruções:

| Célula | Código | Largura | Margem | Bearing | Avanço |
| --- | --- | ---: | ---: | ---: | ---: |
| 22 | e ASCII | 11 | 2 | 0 | 11 |
| 22 | ê antes | 22 | 0 | 0 | 22 |
| 22 | ê v004 | 11 | 2 | 0 | 11 |
| 26 | E ASCII | 13 | 2 | 0 | 13 |
| 26 | É antes | 26 | 0 | 0 | 26 |
| 26 | É v004 | 13 | 2 | 0 | 13 |

Isso comprova uma diferença no layout que pode explicar o alargamento da captura. O resultado visual da correção ainda precisa ser confirmado no PCSX2.

## Correção restrita e reprodução

`tools/glyph_layout.py` gera uma substituição de 824 bytes dentro da alocação original da função, sem ampliar o ELF, usar outra região como código ou alterar extents. Apenas os 18 pares PT-BR herdam as métricas da letra ASCII correspondente; o retorno preserva o código original e o leitor continua consumindo dois bytes. A busca do bitmap acentuado continua usando esse código.

A conversão duplicada de métricas minúsculas de 19 pixels passa a usar o mesmo trecho de conversão das maiúsculas com o índice ajustado em 26. Os argumentos e resultados das chamadas soft-float permanecem idênticos no teste. O prólogo/epílogo são preservados, e o código original é guardado no espaço livre `sp+8`, entre o ra salvo e os registradores seguintes. Não se alterou o tamanho da pilha.

Os desenhos GFI v002, o mapeamento e o patch de cache v003 permanecem idênticos. Não há redução de altura nem redesenho neste experimento. Aplicar as métricas da letra-base evita tentar compensar a escala errada deformando os bitmaps.

```powershell
python -m unittest discover -s tests -p "test_g*.py" -v
python tools/validate_glyph_layout.py --output work/auditoria-layout-nova.json
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v023.json --output work/layout-rebuild --layout-profile ptbr-layout-v004 --iso-name MetalSaga-ptbr-layout-rebuild.iso --build-iso
```

Usar saídas novas. O perfil é opt-in; as construções históricas continuam com `spacing-v003`. O construtor mantém hashes de fontes, origem imutável, releitura dos textos, limites, controles, transação e comparação integral da ISO. A opção `--iso-name` altera somente o nome da imagem experimental, sem editar a receita de tradução.

## Testes e limites

Foram aprovados 16 testes de fontes, cache e layout em 11,484 segundos. Os novos testes incluem todos os 256 primeiros bytes, cinco tamanhos (12, 19, 22, 26, 32), três valores do modo latino, todos os 18 acentos, limites dos intervalos, chamadas soft-float e registradores preservados.

A auditoria adicional executou as instruções para 65.536 sequências: somente 18 mudaram, todas do mapeamento PT-BR. As outras 65.518 mantiveram os resultados anteriores. A varredura estática encontrou cinco referências diretas externas, todas à entrada da função, nenhuma ao interior substituído. Relatório: `reports/layout-v004-instructions.json`.

`tools/layout_probe.py` é um interpretador limitado desta função, com a classificação e as três rotinas soft-float modeladas nas fronteiras de chamada. Não emula o PS2 completo nem a rasterização. A varredura de referências diretas não exclui toda referência indireta. Outros textos/fontes e controles dinâmicos continuam exigindo validação própria.

## Teste visual solicitado

Abrir `Testar-Acentos-Corrigidos.cmd`. ISO: `work/fontes-layout-v004/MetalSaga-ptbr-layout-v004.iso`.

Esta imagem mantém os mesmos 5.758 registros traduzidos da v023, sem nova tradução. Fechar a sessão anterior e iniciar o jogo pela nova ISO; evitar savestate de outra versão, pois ele pode restaurar o executável/cache antigo. Saves de cartão continuam disponíveis no ambiente isolado.

No começo do jogo, conferir as mesmas falas de Nina: “Você quer mesmo ser um Hunter?” e “Eu acho uma péssima ideia. É um trabalho ingrato e sem futuro.” Observar se ê/é/É ficam com o corpo do tamanho das letras vizinhas, sem espaços extras, sobreposição ou cortes. Conferir também ç, ã e í quando aparecerem, especialmente o avanço estreito de í. A altura das letras deve permanecer preservada.

Não houve navegação nem execução desta ISO no PCSX2 pelo Codex. Não promover esta correção à ISO de desenvolvimento nem substituir a versão consolidada por presunção de sucesso visual.

## Imagem entregue e comparação com a v023

A construção final passou com zero recusas e zero violações de terminologia. O plano JSON dos 7.231 registros é idêntico byte a byte ao plano da v023. A comparação integral entre as duas ISOs encontrou somente 620 bytes diferentes dentro da janela de layout de 824 bytes. Fontes, MAP.MCT, textos, patch de cache e diretórios são idênticos entre essas imagens. Evidência: `reports/layout-v004-vs-v023.json`; construção: `reports/layout-v004-build.json`.

ISO: 1.704.427.520 bytes. SHA-256: `a6bdfb2aaf143f1b9705fb740a67c82610972a818c33336ca180b01eca15b803`.

O iniciador passou pelo `--dry-run`. A retenção removeu a ISO v014 mais antiga, preservando dez imagens de trabalho (v015 a v023 e este experimento). A ISO original não integra essa contagem. Fontes de referência, BIOS, saves e configurações foram preservados.
