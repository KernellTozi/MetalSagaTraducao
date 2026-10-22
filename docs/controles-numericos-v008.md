# Variável numérica 15 — política v008

A política `fixed-record-numeric15-preserved-slots-v008` herda integralmente a v007 e acrescenta somente `%$15` inteiro. Não amplia o lexer histórico nem modifica fingerprints de extração. Evidências anteriores: [controle numérico v007](controles-numericos-v007.md).

## Evidência e limites

O ELF original reconhecido usa o mesmo dispatch `$`, leitor `0x1B5A30..0x1B5ACF` e handler `0x1B5DEC..0x1B5E83`. O leitor efetivamente executado pelo interpretador limitado consome os três bytes de `$15`, lê um uint32 no contexto +60 e para antes de G ou F. O handler inteiro usa `%d`, offset `0x349DC0`, tratando o valor como inteiro de 32 bits com sinal. O índice é 15 decimal.

O hash integral do ELF, hashes dos handlers/leitor, dispatch e formato continuam obrigatórios. Provas com valores extremos e sufixos estão em `reports/controle-numerico15-v008-evidence.json`. Não foi emulado o jogo inteiro nem a função completa de formatação.

F maiúsculo é sufixo literal; f minúsculo abre o caminho fracionário com outro argumento, que permanece bloqueado. Não liberar `%$150`, `%$155`, `%$14`, `%$015`, índices negativos ou outros comandos por semelhança. Misturas com controles desconhecidos continuam bloqueadas.

Preservar o token, sequência, quebras/páginas, spans vazios, nomes, rótulos e limites de execução. Registros com referências dinâmicas liberadas exigem slots fixos e cada segmento deve ter no máximo seu tamanho original em bytes, mesmo se existir padding adicional. Nenhum registro, bloco ou extent cresce. Isso é validação binária; as substituições dinâmicas e o fluxo das escolhas precisam de conferência no jogo.

## Casos preservados

`map.supr.01deb784` contém somente um marcador com `%$15` e F maiúsculo. Foi retomado para classificação, mas seus bytes permanecem idênticos e ele não aumenta o total de traduções. Não se traduziu F nem se afirmou comprovação visual da tela a que pertence. A intenção consta em `preservation_decisions` da receita; o compilador rejeita uma decisão de preservação vinculada a registro alterado, adiado ou inexistente. Decisões são herdadas nos lotes seguintes.

O grupo anterior de 19 `%N$3` não foi liberado para edição. Seus nomes de tanques são preservados por decisão contextual; ver [análise de N3](n3-preservacao-v001.md).

## Reprodução

```powershell
python -m unittest discover -s tests -p test_control_numeric15.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v026.json --output work/numeric15-repro
```

Os testes cobrem leitor original, limites inteiros, sufixos, índices parecidos, legado bloqueado, rótulos, round-trip, recusa de crescimento/repack/troca de índice e falha atômica. A regressão do lote compara todos os descritores com a v025, preserva as 5.821 traduções anteriores e distingue os 17 registros alterados do marcador intacto.
