# Missão 03 — consolidação avançada

## Entrega e preservação

O extrator v003 continua offline e usa `Extrair-Dialogos.cmd`, Python 3.11+.
O catálogo entregue fica em `work/extracoes/catalogo-v003-final/`.
Nenhuma tradução, alteração de fonte, navegação no PCSX2 ou ISO nova foi produzida.

| Classe | v002 | v003 |
| --- | ---: | ---: |
| Extração estrutural validada | 4438 | 5369 |
| Texto identificado, edição bloqueada | 1702 | 1862 |
| Estrutura desconhecida no conjunto examinado | 40 | 0 |
| Ocorrência rejeitada como instrução textual | 31 | 71 |
| Total de registros com texto recuperado | 6140 | 7231 |

Foram recuperados **1.091 registros novos**, contendo **1.685 segmentos textuais**.
Uma pergunta e suas opções são um único registro com segmentos distintos, não
ocorrências duplicadas. O consolidado contém 7.302 offsets: as 6.211 ocorrências
anteriores mais os 1.091 registros adicionais, todos provenientes de instruções
enquadradas. Textos iguais em endereços diferentes continuam separados.

Os 6.140 registros textuais da v002 são preservados campo por campo. Dois hashes
versionados da v002 verificam a serialização desses registros; o fingerprint dos
2.049 da v001 também permanece obrigatório. As capacidades e IDs antigos não mudam.
O registro original fica em `record`; evidência adicional fica em `validation`
no consolidado e em `contexto-ssd.jsonl`, sem reescrever os dados antigos.
Os motivos em `record.reason` e nas contagens `reasons` do relatório permanecem
históricos quando vêm da v002; `reasons_provenance` esclarece essa compatibilidade.

## Limites SSD comprovados e os 40 desconhecidos

O executável verifica a assinatura SSD e a versão `0x469` em VA `0x2BC8C8..2BC924`.
Em `0x2BCFE4`, a primeira instrução é posicionada em base + `0x0C`. Em
`0x2BD00C..2BD014`, o campo uint32 em `+8` é somado à base para estabelecer o limite.
Portanto o tamanho **inclui o cabeçalho de 12 bytes**; não é o tamanho após ele.
Offsets ELF desses endereços: subtrair `0xFF000`.

`SsdIndex` percorre cada bloco por tamanhos de instrução, exige que nenhuma
instrução atravesse o fim e que a caminhada termine exatamente no limite. Recusa
blocos sobrepostos, instruções duplicadas, tamanhos inválidos e truncamento.
No original, os **2.741 blocos** passaram integralmente, totalizando **61.356
instruções**, sem erros. Isso resolve a incerteza da v002 sem relaxar o parser
de seis vizinhos: há agora uma prova independente das fronteiras do bloco inteiro.

Todos os 40 desconhecidos anteriores ficam fora do fim declarado de um desses
blocos: 16 no próprio limite, 13 em limite +4 e 11 em limite +8. Seus supostos
registros atravessavam dados seguintes e, por isso, pareciam conter `ssd` no
cabeçalho ou no texto. Não são inícios de instrução `msg/msgn` daquele fluxo.
São classificados como ocorrências falsas da busca de assinaturas, mantendo
seus bytes e evidência de origem. A semântica da região adjacente não foi inventada:
o extrator só prova a exclusão do fluxo executável, sem chamá-la de tabela de
ponteiros ou dar significado aos seus campos.

Exemplos: `0x057CEA28`, `0x0DB1092C`, `0x1DF6A308`. Decisões individuais de todos
os 40 estão em `reports/dialogue-advanced-v003.json`.

## Reavaliação das 31 rejeitadas

Trinta ocorrências estão fora de todos os fluxos SSD verificados e falham no
enquadramento básico como instruções. A outra, em `0x10CF57ED`, começa dentro de
uma instrução `smsg` válida em `0x10CF57EC`. O texto desta instrução maior foi
recuperado pelo parser novo, sem promover a assinatura interna desalinhada.

São 71 ocorrências rejeitadas como inícios de instruções textuais, sustentadas
pelo enquadramento e pelos limites do leitor. Isso não prova que regiões inteiras
fora de SSD não contenham qualquer outro tipo de texto. O relatório registra
offset, assinatura, bloco ou instrução que sustenta cada decisão, sem distribuir
os recursos originais.

## Formatos adicionais e cobertura fora de msg/msgn

Os novos parsers usam cabeçalhos indicados por carregadores do ELF, seguidos por
strings NUL-terminadas. Preservam separadores zero, offsets e segmentos. Opções
separadas por TAB continuam juntas na string original. Não há normalização.

| Tag | Cabeçalho | Strings | Registros recuperados | Evidência principal (VA) |
| --- | ---: | ---: | ---: | --- |
| `smsg` | 40 | 2 | 315 | `0x2C5920`: 4 parâmetros; tratamento `0x2C5940` |
| `sel` | 16 | 1 | 27 | `0x2C5630`: 1 parâmetro; separação TAB em `0x2C5788` |
| `smnn` | 40 | 3 | 83 | Mesmo loader de 4 parâmetros; strings delimitadas no corpus; papel da terceira bloqueado |
| `2smg` | 48 | 2 | 55 | `0x2C5BA0`: 5 parâmetros |
| `2snm` | 48 | 3 | 29 | `0x2C5E30`: 5 parâmetros; papel da terceira bloqueado |
| `2sel` | 24 | 1 | 12 | `0x2C58A0`: 2 parâmetros |
| `msgb` | 24 | 1 | 155 | `0x2C5F58`: ponteiro de texto em registro +24 |
| `supr` | 48 | 1 | 390 | `0x2CBB98`: ponteiro de texto em registro +48 |
| `MC` | 24 | 1 | 18 | `0x2BA2E8`: copia string de registro +24 |
| `SP` | 32 | 1 | 6 | `0x2BAD38`: copia string de registro +32 |
| `ST` | 32 | 1 | 1 | Mesmo carregador de `SP` |

Os parâmetros comuns são unidades de oito bytes após oito bytes de cabeçalho.
O parser exige o número de strings esperado, terminadores, separadores e ausência
de conteúdo extra. O tamanho de uma assinatura textual isolada não basta: os novos
formatos só são enumerados em fronteiras reais do índice SSD. Os perfis com terceira
string permanecem identificados/bloqueados; não foi presumido que ela seja sempre
um nome de personagem.

Os novos textos incluem perguntas e respostas, avisos, títulos de lugares e nomes.
Isso comprova que `msg/msgn` não cobriam o conteúdo textual completo do MAP.
Os 13 grupos conhecidos (11 novos + `msg/msgn`) somam **7.231 instruções** no índice,
e todos têm extração sem perda nesta revisão do arquivo.

Foi feita uma auditoria adicional das outras instruções SSD: busca de sequências
com pelo menos 15 caracteres de um conjunto restrito de letras, pontuação e espaços,
sempre dentro de instruções reais e fora dos 13 grupos. Não restaram candidatos
nesse critério. Essa busca é um controle de cobertura, **não uma prova de 100%**:
textos curtos, tabelas externas aos fluxos, compressão e referências indiretas
podem escapar. Não foi feita uma recompilação ou engenharia reversa integral do jogo.

## Registros bloqueados e níveis de validação

O índice prova fronteiras para todos os 6.140 registros antigos, incluindo **1.545**
com `context_error` na v002. Esse campo é preservado como evidência histórica;
o estado atual do enquadramento está em `validation.ssd_instruction_boundary`
e no arquivo de contexto. Não se alterou a classificação antiga só para aumentar
a coluna de validados, pois os editores genéricos desses perfis continuam ausentes.

Os 160 novos identificados incluem 112 perfis de três strings com papel adicional
não totalmente comprovado e casos de controles opacos. Junto aos 1.702 antigos,
são 1.862 na classe identificada. Preservação de controles não implica compreensão
de todos os efeitos: `%N$...`, `%I$...`, `%B$...`, `%$...` e variantes incompletas
permanecem bloqueadas para edição generalizada. Os parâmetros brutos não foram
convertidos em retratos, falantes ou ponteiros por suposição.

Foram consultadas as duas GFI originais somente para inventariar as sequências
nativas já extraídas: 25 pares possuem glifos não vazios; `81 40` é espaço de
largura inteira e sua célula vazia é esperada. Não houve edição de fonte nem
validação de execução desses textos nativos. Isso não transforma a codificação
original em UTF-8 ou Windows-1252 e não libera reinserção de quaisquer caracteres.

Há três níveis distintos no catálogo: extração, reconstrução binária sem alterações
e edição. O editor genérico aprovado continua restrito aos **2.048 registros ASCII**;
há ainda o piloto controlado específico de Nina. Os outros **5.182 registros** não
têm edição geral aprovada, inclusive novos perfis estruturalmente validados.
Faltam políticas para os controles dinâmicos, limites por segmento e nomes,
métricas reais e atualização de tamanhos/ponteiros caso a tradução exceda os slots.
Nenhuma dessas validações foi simulada por um round-trip sem edição.

## Execução e verificação

Dar duplo clique em `Extrair-Dialogos.cmd`, sem comandos adicionais. Para reprodução:

```powershell
python -m unittest discover -s tests -v
python tools/extract_dialogues.py --output work/extracoes/minha-extracao-v003
python tools/probe_dialogue_advanced.py --catalog work/extracoes/minha-extracao-v003 --output reports/minha-auditoria-v003.json
```

O índice usa metadados de instruções e `mmap` somente de leitura; não copia os
731 MB do MAP para um buffer Python. O consumo cresce com o número de instruções,
não com a soma dos conteúdos binários. O JSONL é escrito incrementalmente.
Relatório sem `completed: true` não representa execução concluída.

Foram aprovados **45 testes**, incluindo os onze layouts, intervalos de zeros,
escolhas/TAB, limites SSD, instrução atravessando limite, truncamento, contexto,
bytes nativos, tokens opacos e reconstrução de cada segmento. Na extração real,
os 7.231 registros textuais são reconstruídos byte a byte, não se sobrepõem,
o plano ASCII sem alterações produz zero patches e o hash do MAP é preservado.
Os fingerprints v001 e v002 são obrigatórios para o original reconhecido.
O iniciador Windows e as comparações entre execuções fazem parte do relatório
`reports/extrator-v003-validation.json`.

Foi atingida uma cobertura completa dos 13 layouts textuais identificados nos
fluxos SSD desta revisão. A cobertura absoluta de todos os recursos de MAP.MCT
continua desconhecida. O próximo avanço útil é a política de edição por segmento
e de controles dinâmicos; não é produtivo continuar procurando um formato novo
nos 40 casos já comprovados fora dos fluxos.
