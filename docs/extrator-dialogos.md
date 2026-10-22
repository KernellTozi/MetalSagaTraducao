# Extrator local de diálogos v002

Detalhes da investigação e limites dos novos parsers: `extracao-v002.md`.

## Executar no Windows 11

Requer Python 3.11 ou superior disponível como `python`. Na pasta do projeto, dar
duplo clique em **`Extrair-Dialogos.cmd`**. A janela mostra o caminho e as contagens
e aguarda uma tecla ao terminar. Cada execução cria uma pasta nova com data/hora
em `work/extracoes/`. Não sobrescreve resultados anteriores.

Também pode executar na raiz:

```powershell
python tools/extract_dialogues.py
```

Para escolher uma pasta nova:

```powershell
python tools/extract_dialogues.py --output work/extracoes/meu-lote-001
```

O original é `JOGO/Metal Saga/DATA/MAP/MAP.MCT`. `--source` permite analisar cópias
em `work/`; outros caminhos são recusados. Não há IA, rede, API ou emulação.
A ferramenta usa apenas a biblioteca padrão do Python; não exige Pillow/Capstone.
Não traduz, não altera fontes e não gera ISOs.

## Arquivos gerados

| Arquivo | Conteúdo |
| --- | --- |
| `catalogo-consolidado.jsonl` | Todas as 6.211 ocorrências, uma por offset, com classificação e registro |
| `dialogos.jsonl` | Um objeto JSON por linha: registros do subconjunto validado |
| `identificados.jsonl` | Texto recuperado com estrutura local, mas controles, codificação ou contexto ainda limitados |
| `pendentes.jsonl` | Candidatos enquadrados, motivo da incerteza e bytes completos em hexadecimal |
| `rejeitados.jsonl` | Assinaturas que falharam em alinhamento, tamanho ou limites |
| `plano-ascii.json` | Plano compatível com o editor ASCII já existente, sem traduções |
| `relatorio.json` | Hash, revisão, contagens, motivos, tempo, comparação com catálogo anterior e integridade |

JSONL é UTF-8 e preserva quebras de linha dentro das strings como `\n` e páginas
como `\t`; cada linha física é um registro completo. Os campos `source` e
`translation` começam iguais. Não deduplicar textos iguais: offsets diferentes
são ocorrências diferentes. Os textos extraídos e bytes do jogo ficam locais,
ignorados pelo Git. Somente metadados do relatório de execução são versionados.

`relatorio.json` com `completed: true` é a indicação de execução completa. Se
ocorrer erro, a pasta parcial fica preservada para diagnóstico e não deve ser
tratada como catálogo concluído. Reexecutar usando outra pasta.

## Resultado executado sobre o MAP de referência

- 6.211 ocorrências das assinaturas `msg\0` ou `msgn` examinadas.
- **4.438 registros com extração estrutural validada**, incluindo os 2.049 da v001.
- **1.702 registros identificados, ainda bloqueados**, com texto recuperado.
- **40 candidatos de estrutura desconhecida**, com bytes preservados.
- **31 assinaturas rejeitadas** por alinhamento/localização ou tamanho inválido.

Contagens de candidatos não equivalem a quantidades comprovadas de falas; incluem
possíveis falsos positivos e estruturas que ainda precisam ser interpretadas.
Não se afirma que todas as falas do jogo estão contidas nessas assinaturas.

Os **2.049 registros da v001** foram preservados integralmente. A igualdade é
verificada pelo hash da serialização original ancorado no relatório versionado,
mesmo sem a pasta antiga. Quando os catálogos locais anteriores estão presentes,
também se comparam seus registros campo por campo. O plano ASCII mantém exatamente
seus 2.048 registros e a política original de edição.

A extração v002 levou aproximadamente 13 segundos nesta máquina. O iniciador
Windows foi executado e produz os mesmos arquivos de dados que a chamada direta.
Os 36 testes passaram. Os relatórios registram tempos próprios.

## Estrutura e contexto preservados

Cada registro validado contém ID baseado no offset físico, offset do registro e
do texto, índice local, tamanho total, capacidade útil, cabeçalho hexadecimal,
hash do registro, texto-fonte, bytes originais do texto e sequência de controles.
Quando o contexto é comprovado, inclui três instruções anteriores e três posteriores,
com offsets, tags, índices e tamanhos. Sua ausência mantém o novo registro na classe
identificada, sem promovê-lo a validado. O relatório associa o catálogo ao hash do MAP.

Em 1.415 `msgn`, recupera também a segunda string usada como rótulo de exibição.
Isso não estabelece um ID canônico de personagem, cena, missão ou ponteiro.
Índices locais não são IDs globais; palavras como “Nina” não são inferidas dos
cabeçalhos. Campos desconhecidos são preservados em bytes, sem inventar semântica.
Os vizinhos são instruções físicas, não necessariamente falas anteriores/seguintes.

Os formatos têm parsers separados, fundamentados nos carregadores do ELF. `msg`
exige padding zero após o NUL; `msgn` exige segunda string limitada e padding final
zero. Sintaxes opacas são identificadas e bloqueadas; bytes desconhecidos não passam
por decodificação com substituição ou perda. Consultar o relatório técnico v002.

## Integridade e desempenho

O MAP é aberto somente para leitura via `mmap`. A varredura e a escrita dos JSONL
são incrementais; não há cópia integral de 731 MB em um objeto `bytes` e os candidatos
pendentes não são acumulados em listas. O plano ASCII compatível mantém cerca de
2 mil registros em memória; os catálogos anteriores, quando disponíveis, são carregados
para comparação. O sistema operacional administra as páginas mapeadas; não foi
medido um limite absoluto de memória residente.

Cada registro aceito é reconstruído com cabeçalho, bytes de texto, NUL e padding;
o resultado deve ser idêntico ao registro original. O plano ASCII sem edições
passa no validador existente e deve produzir zero patches. O hash do MAP antes e
depois deve ser igual. Isso é round-trip **sem alteração**, não demonstra segurança
para qualquer tradução ou ampliação de registros. O hash do original é ancorado
no inventário. Relatório atual: `reports/extrator-v002-validation.json`.

Testes locais:

```powershell
python -m unittest discover -s tests -v
```

Cobrem extração ASCII, mensagens com controles, `msgn` com separadores de tamanhos
variados, parâmetros negativos, controles opacos, bytes nativos, round-trip exato, JSON, bytes
desconhecidos, padding inválido, truncamento, alinhamento, tamanhos inválidos,
fronteiras ambíguas, nomes inválidos, pipeline em cópia sintética e recusa de
sobrescrita. O teste real preserva os 2.049 registros da v001 e reconstrói todos os
6.140 registros textuais recuperados.

## Reinserção: disponível e pendente

O `plano-ascii.json` é compatível com `tools/build_dialogue_iso.py`, que já aceita
várias edições em slots independentes e compara a ISO inteira. Editar somente
`translation`; os limites ASCII/LF e de comprimento do editor continuam vigentes.
Nenhuma nova ISO foi criada nesta entrega.

O JSONL é um catálogo de extração, ainda não uma entrada direta do builder.
Faltam um importador/validador de lotes JSONL e uma política generalizada para
controles e acentos que associe obrigatoriamente os bytes às fontes corretas.
Relocação para traduções maiores que os slots, tabelas de ponteiros, edição genérica
de `msgn`, outras codificações e métricas em pixels permanecem fora do editor aprovado.
Essas etapas podem ser implementadas sem repetir a extração nem consumir IA para
o processamento binário. A revisão narrativa e ajustes finos de fonte ficam adiados.
