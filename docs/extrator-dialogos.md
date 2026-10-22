# Extrator local de diálogos v001

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
| `dialogos.jsonl` | Um objeto JSON por linha: registros do subconjunto validado |
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
- **2.049 registros extraídos pelo subconjunto comprovado:** os 2.048 ASCII já
  catalogados e a mensagem de Nina com controles `%F1%M0_5`, testada no experimento.
- **4.131 candidatos pendentes**, incluindo 1.418 `msgn`, 2.038 com controles ou
  codificações fora do perfil ASCII, 403 com fronteira anterior ambígua, 235 com
  problemas de enquadramento dos vizinhos e 37 com terminador/padding incompatível.
- **31 assinaturas rejeitadas** por alinhamento/localização ou tamanho inválido.

Contagens de candidatos não equivalem a quantidades comprovadas de falas; incluem
possíveis falsos positivos e estruturas que ainda precisam ser interpretadas.
Não se afirma que todas as falas do jogo estão contidas nessas assinaturas.

Os 2.048 registros do perfil ASCII foram comparados com o catálogo anterior:
**igualdade exata de todos os campos e textos**. Não foi reiniciada a investigação
de formatos. O perfil controlado permanece separado, para não ampliar implicitamente
a política de reinserção do editor ASCII.

A execução direta levou aproximadamente oito segundos nesta máquina. Uma segunda
execução pelo iniciador Windows produziu os quatro arquivos de dados idênticos,
byte por byte; os relatórios registram tempos próprios. Os 28 testes passaram.

## Estrutura e contexto preservados

Cada registro validado contém ID baseado no offset físico, offset do registro e
do texto, índice local, tamanho total, capacidade útil, cabeçalho hexadecimal,
hash do registro, texto-fonte, bytes originais do texto e sequência de controles.
Inclui três instruções anteriores e três posteriores, com offsets, tags, índices
e tamanhos. O relatório associa o catálogo ao hash de todo o MAP e ao recurso.

Não há mapeamento confiável de personagem, cena, missão ou referência de ponteiro.
Índices locais não são IDs globais; palavras como “Nina” não são inferidas dos
cabeçalhos. Campos desconhecidos são preservados em bytes, sem inventar semântica.
Os vizinhos são instruções físicas, não necessariamente falas anteriores/seguintes.

O formato `msg\0` aceito tem cabeçalho de 32 bytes e slot terminado em NUL com
padding zero, fronteiras e vizinhos verificados. `msgn` não herda esse formato por
suposição. Candidatos ASCII legíveis com controles não aprovados recebem apenas
`readable_candidate`/`assumed_text_offset`, continuam pendentes e não editáveis.
Bytes desconhecidos não passam por decodificação com substituição ou perda.

## Integridade e desempenho

O MAP é aberto somente para leitura via `mmap`. A varredura e a escrita dos JSONL
são incrementais; não há cópia integral de 731 MB em um objeto `bytes` e os candidatos
pendentes não são acumulados em listas. O plano ASCII compatível mantém cerca de
2 mil registros em memória; o catálogo anterior, quando disponível, é carregado
para comparação. O sistema operacional administra as páginas mapeadas; não foi
medido um limite absoluto de memória residente.

Cada registro aceito é reconstruído com cabeçalho, bytes de texto, NUL e padding;
o resultado deve ser idêntico ao registro original. O plano ASCII sem edições
passa no validador existente e deve produzir zero patches. O hash do MAP antes e
depois deve ser igual. Isso é round-trip **sem alteração**, não demonstra segurança
para qualquer tradução ou ampliação de registros. O hash do original é ancorado
no inventário. Relatório: `reports/extrator-v001-validation.json`.

Testes locais:

```powershell
python -m unittest discover -s tests -v
```

Cobrem extração ASCII, mensagem controlada, round-trip exato, JSON, bytes
desconhecidos, padding inválido, truncamento, alinhamento, tamanhos inválidos,
fronteiras ambíguas, exclusão de `msgn`, pipeline em cópia sintética e recusa de
sobrescrita. O teste real também compara todos os 2.048 registros ao catálogo base.

## Reinserção: disponível e pendente

O `plano-ascii.json` é compatível com `tools/build_dialogue_iso.py`, que já aceita
várias edições em slots independentes e compara a ISO inteira. Editar somente
`translation`; os limites ASCII/LF e de comprimento do editor continuam vigentes.
Nenhuma nova ISO foi criada nesta entrega.

O JSONL é um catálogo de extração, ainda não uma entrada direta do builder.
Faltam um importador/validador de lotes JSONL e uma política generalizada para
controles e acentos que associe obrigatoriamente os bytes às fontes corretas.
Relocação para traduções maiores que os slots, tabelas de ponteiros, `msgn`,
outras codificações e métricas em pixels permanecem fora do subconjunto aprovado.
Essas etapas podem ser implementadas sem repetir a extração nem consumir IA para
o processamento binário. A revisão narrativa e ajustes finos de fonte ficam adiados.
