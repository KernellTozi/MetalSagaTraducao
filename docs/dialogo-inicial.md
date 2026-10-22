# Piloto de diálogo: pergunta sobre ser Hunter

## Resultado binário

Em 21/10/2026 foi localizada uma única ocorrência da sequência abaixo em MAP.MCT:

```text
You want to become
a hunter?
```

O texto digitado pelo usuário com espaço e “Hunter” maiúsculo não aparece literalmente;
a busca pelo prefixo levou a essa ocorrência. Foi alterada para:

```text
Quer ser um
Hunter?
```

O sentido e a quebra de linha são preservados no piloto ASCII. A forma PT-BR final
“Você quer se tornar um caçador?” fica registrada, aguardando codificação/fontes.

| Campo | Evidência |
| --- | --- |
| Recurso | DATA/MAP/MAP.MCT, 730.998.784 bytes |
| SHA-256 de origem | `06b4a68a31ceb32e9298e7550affad89152a3e44e5a61013f50023745d0000f0` |
| Início do registro | `0x1DF47F0C` |
| Tag | `6D 73 67 00` (`msg` + NUL) |
| Índice local no cabeçalho | 28 (`0x001C`), não um índice global de falas |
| Tamanho uint16 LE em +6 | 64 (`0x0040`) |
| Cabeçalho preservado | 32 bytes |
| Início do texto | `0x1DF47F2C` |
| Slot textual | 32 bytes: até 31 úteis e um NUL |
| Texto original | 28 bytes, uma quebra 0x0A, NUL e três zeros adicionais |
| Texto experimental | 19 bytes, uma quebra 0x0A e 13 zeros até o próximo registro |
| Próximo registro | `cmps`, índice 29, em `0x1DF47F4C` |
| LBA ISO de MAP.MCT | 26.258, inalterado |

O cabeçalho completo original está no relatório de validação. Campos em +8/+0x0C,
+0x10/+0x14 e +0x18/+0x1C não tiveram sua semântica interpretada; foram mantidos
byte a byte. Não foi deduzido um mapeamento geral de personagens desses valores.

Antes do alvo, foram encadeadas 25 instruções de tamanho explícito, com índices
3 a 27, até o alvo de índice 28. A exploração encontrou uma fronteira especial
antes de `iff` de índice 3 e parou ali, sem presumir o formato do cabeçalho desse
bloco. O editor exige três registros anteriores e três posteriores com fronteiras
únicas e verifica suas tags, índices e tamanhos contra o plano de edição.

Essa evidência basta para o piloto de **mesmo tamanho**: toda alteração está no
slot NUL-terminado, os cabeçalhos e posições permanecem idênticos. Não comprova
que os índices são ponteiros, nem autoriza mudar comprimentos de registros ou
reescrever tabelas/fluxo de controle. A interpretação de `msgn` e outros comandos
está fora do editor restrito.

## Ferramentas e reprodução

Sem dependências externas; usar Python 3.11+ (hashlib.file_digest).

```powershell
python tools/dialogue.py pilot --output work/dialogue-inicial-v001.json
python tools/build_dialogue_iso.py --plan work/dialogue-inicial-v001.json --output work/MetalSaga-ptbr-dialogo-inicial-v001.iso --report reports/dialogue-inicial-v001-validation.json
python -m unittest discover -s tests -v
```

Os comandos rejeitam saídas já existentes. Os artefatos desta versão já estão
gerados; não é necessário reconstruí-los para testar. Para uma nova versão, usar
outros nomes identificados. O build escreve primeiro `.iso.partial`, valida e só
então publica o nome final. A ISO original nunca é aberta para escrita.

O plano JSON identifica o registro por offset, hash e cabeçalho. Somente
`translation` é editável. O builder aplica os bytes diretamente a uma cópia nova
da ISO, sem gerar outra cópia de 731 MB de MAP.MCT. Verifica o hash do MAP na ISO
contra a extração e o inventário; compara integralmente a imagem com o resultado
esperado e exige diretório, LBAs e tamanho iguais.

Resultado: **27 bytes diferentes**, todos no slot autorizado. O hash da ISO
experimental é `30c53a9b8eb2802939b71b56b7f25becda612c39d2d7824c86eca13e061003ed`.
Detalhes reproduzíveis: `reports/dialogue-inicial-v001-validation.json`.
O teste é binário; a exibição da nova fala permanece pendente com o usuário.
Um diagnóstico curto pelo iniciador também confirmou boot da ISO nova até o aviso
inicial de ausência de cartão, sem navegação prolongada ou restauração de savestate.
Passaram 12 testes automatizados: cinco do diário e sete do editor de diálogos,
incluindo rejeição de codificação/controles desconhecidos, metadados alterados,
overflow, padding não zero e alterações inesperadas na imagem.

## Expansão controlada

```powershell
python tools/dialogue.py scan --output work/dialogue-catalog-ascii-v001.json
```

Foram obtidos **2.048 candidatos** e rejeitadas 2.715 ocorrências de assinatura
`msg\0`. O catálogo real, sem tradução, passou por `changes()` com zero patches:
o round-trip lógico preserva integralmente MAP.MCT. O catálogo contém textos do
jogo e permanece local. Apenas seu resumo é versionado.

Limites desta primeira política:

- Somente `msg\0` com tamanho alinhado, terminador NUL e padding final zero.
- Descoberta heurística, seguida de validação estrutural de vizinhos na inserção.
- ASCII imprimível e quebras LF; sem comandos `%...`, TAB, glifos especiais ou msgn.
- Contagem de LF preservada; linhas editadas não podem ficar vazias nem aumentar
  em número de caracteres em relação à respectiva linha original.
- Sem aumentar slot, mudar cabeçalho, ponteiros, IDs, offsets ou tamanho de arquivo.
- Hash de origem, registro, texto-fonte e metadados precisam coincidir exatamente.
- O limite por caracteres é uma barreira conservadora, **não substitui métricas em
  pixels**. A largura real depende da fonte e ainda requer amostragem visual.

O builder já recebe vários registros no mesmo plano. Os testes sintéticos incluem
duas mensagens alteradas em slots independentes e comparação integral. Isso
permite versões consolidadas e reversão por registro: restaurar `translation` ao
valor de `source` remove aquela edição da próxima construção a partir do original.
Manter planos separados por lote, sem deduplicar suas ocorrências físicas.

Depois da confirmação visual da amostra, ampliar gradualmente a seleção de
registros compatíveis. Para traduzir, usar contexto de cena e glossário em
`translations/glossary.json`, com revisão de comprimento e sentido. Não ativar
tradução em massa sobre o catálogo apenas por ele passar na heurística.
Registros com tokens, códigos multibyte, outras tags ou novos limites passam por
investigação separada. A ausência de confirmação visual desta frase não impede
o trabalho de fontes, parser, métricas e testes automatizados independentes.
