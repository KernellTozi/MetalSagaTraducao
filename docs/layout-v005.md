# Layout PT-BR v005 — desenho de caracteres individuais

## Retorno do usuário e segundo caminho

O usuário testou o experimento v004 e informou que todos os acentos continuavam largos e com aparência de baixa resolução. A captura do ê de “Você” confirma a persistência visual. A hipótese de que somente a rotina `0x3E520` governasse essa fala não foi confirmada; os testes anteriores comprovavam apenas o comportamento da função substituída. O resultado v004 não é aprovação tipográfica.

Foi identificado outro caminho: o loop de texto em `0x3E1A8..0x3E2DB` chama o desenho individual em `0x3E2E0..0x3E51F` (endereços no arquivo ELF, VA = offset + `0xFF000`). Essa função contém outra decisão independente:

- `0x3E354..0x3E374`: classifica o byte alto do código; caracteres de dois bytes recebem largura inteira e margem zero; ASCII recebe meia largura e margem 2.
- `0x3E378..0x3E390`: obtém o retângulo do glifo pelo código original.
- `0x3E394..0x3E4C8`: calcula avanço e ajustes de textura por letra/pontuação.
- `0x3E4CC..0x3E4E4`: envia as dimensões para o desenho; a imagem ainda podia ser ampliada horizontalmente, mesmo com o cache v003 e a função v004 corrigidos.

No teste de instruções com cache v003 modelado, fonte 22 e modo latino 1:

| Código | Retângulo de origem | Largura de desenho | Altura | Avanço |
| --- | --- | ---: | ---: | ---: |
| e ASCII | 13×22 | 13 | 22 | 12 |
| ê antes | 13×22 | 22 | 22 | 23 |
| ê v005 | 13×22 | 13 | 22 | 12 |

A fonte 26 passa de desenho 26 para 15, como o ASCII da mesma fonte. O í herda também bearing e avanço de i. Esses valores vêm de um teste limitado de instruções, não de uma captura do GS/PCSX2. A relação com a fala de Nina ainda precisa de confirmação visual da v005.

## Implementação

`tools/glyph_single.py` substitui 576 bytes dentro da função existente, sem crescer o ELF. A consulta ao cache ocorre com o código acentuado original. Depois dela, somente os 18 pares PT-BR usam a letra-base para os cálculos de layout. Isso conserva a seleção do bitmap e permite reutilizar as tabelas originais de cada letra.

A implementação compacta o lookup duplicado de métricas maiúsculas/minúsculas e usa a tabela de mapeamento já contida na função adjacente v004. Portanto, depende explicitamente do patch v004 adjacente, vinculado por hash, além do cache v003. O perfil `ptbr-layout-v005` aplica os três juntos. Não usar o patch individual sozinho.

Os bitmaps continuam idênticos ao perfil v002, sem redução de altura ou nova reamostragem. Os textos continuam sendo os da v023. O perfil novo é opt-in e não modifica o padrão histórico do construtor nem a ISO de desenvolvimento.

## Reprodução

```powershell
python -m unittest discover -s tests -p "test_g*.py" -v
python -m unittest discover -s tests -p test_edit_font_pack.py -v
python tools/validate_glyph_single.py --output work/auditoria-desenho-nova.json
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v023.json --output work/layout-v005-rebuild --layout-profile ptbr-layout-v005 --iso-name MetalSaga-ptbr-layout-v005-rebuild.iso --build-iso
```

Usar nomes novos. A auditoria lê somente o ELF original imutável e não usa IA, internet ou APIs. O interpretador `tools/layout_probe.py` agora cobre os dois caminhos, com fronteiras simuladas de classificação, cache, textura, desenho e soft-float. Não emula rasterização nem comprova execução no PS2.

Os testes específicos comparam ASCII, pontuação, códigos vizinhos, quatro tamanhos e três modos. Conferem dimensões de desenho, retângulo de textura, próximo x, preservação de registradores e manutenção do código na chamada ao cache. Os testes da v004 e do cache v003 continuam executados.

## Arquivos de fonte editáveis

Pacote local: `work/fontes-editaveis-ptbr.zip`; pasta: `work/fontes-editaveis-ptbr/`.

Há 18 PNGs para cada fonte, nos tamanhos nativos 22×22 e 26×26, e referências ASCII para comparação. `MAPEAMENTO.txt` identifica cada arquivo. `U00EA.png` é ê; `U00C9.png` é É. Editar com zoom, mantendo dimensões e tons de cinza. Preto corresponde a transparência do glifo; branco à intensidade máxima. Evitar redimensionamento ou suavização automática do editor.

```powershell
python tools/edit_font_pack.py export --output work/novo-pacote-fontes
python tools/edit_font_pack.py import --pack work/fontes-editaveis-ptbr --output work/fontes-editadas
```

A importação confere origem, dimensões e formato antes de escrever cópias de GFI em `work/`. Só altera as 18 células reservadas; os originais ficam intactos. Ela não modifica ISOs automaticamente. O round-trip sem edição reproduz as fontes v002 byte a byte. Os PNGs, referências, ZIP e GFI ficam fora do Git.

## Teste visual

Executar `Testar-Acentos-Corrigidos.cmd`, agora apontando para `work/fontes-layout-v005/MetalSaga-ptbr-layout-v005.iso`. Fechar a sessão anterior e iniciar pela nova imagem, evitando savestate de outra versão. Conferir no PCSX2 o nome da ISO carregada.

Rever a fala de Nina “Você quer mesmo ser um Hunter?” e o trecho “péssima ideia. É um trabalho”. Comparar o corpo de ê/é/É com as letras vizinhas: largura, espessura, altura e nitidez. Observar também ç/ã/í, espaços, sobreposição e avanço de páginas. Não houve execução nem navegação desta ISO no PCSX2 pelo Codex. A aparência permanece pendente de confirmação manual.

## Resultados da entrega

Foram aprovados 20 testes de fontes/cache/layout e três testes de exportação/importação de fontes (23 no total). O round-trip do pacote sem edição reproduz as GFI v002 exatamente. A importação recusa dimensões, modo de cor ou vínculo de origem incorretos antes de escrever as fontes.

A auditoria percorreu 65.536 códigos de 16 bits: apenas os 18 PT-BR mudaram de comportamento no desenho individual; 65.518 mantiveram os resultados anteriores. Referências diretas externas apontam somente para a entrada da função. O modelo de cache respeita a classificação nativa de ASCII/kana e o flag v003 dos 18 pares; chamadas de desenho são registradas, sem rasterização real. Evidência: `reports/layout-v005-instructions.json`.

A construção consolidou os mesmos 5.758 registros alterados, com zero recusas. O plano JSON é idêntico ao da v004/v023. A comparação integral entre v005 e v004 encontrou somente 316 bytes diferentes, dentro da função de desenho individual de 576 bytes. Fontes, MAP.MCT, textos e diretórios são idênticos entre essas duas ISOs. Relatórios: `reports/layout-v005-build.json` e `reports/layout-v005-vs-v004.json`.

SHA-256 da ISO: `92ebfcd0a98ced0301740aefaf3fee96f6b7c7c780d005c3d7ba381618ac108d`. Tamanho: 1.704.427.520 bytes. O iniciador passou pelo `--dry-run`, sem execução do emulador.

A retenção preserva dez ISOs de trabalho: v016 a v023 e os experimentos de layout v004 e v005. A v015 mais antiga foi removida; receitas e relatórios permanecem. A original em `JOGO/` é preservada fora da contagem. Não houve alteração de saves, BIOS ou configurações.
