# Reconhecimento técnico — 21/10/2026

## Resultado e limites

Foi comprovada a extração e reinserção de campos do diário sem realocação, com geração
de uma ISO experimental de tamanho idêntico. Isso comprova a operação binária, mas
**não comprova execução, renderização ou compatibilidade de acentos no PCSX2**.
Não foi iniciada tradução em massa.

## Fontes e inventário

- ISO: `JOGO/Metal Saga.iso`, 1.704.427.520 bytes.
- SHA-256: `ef8405bf9e34bffd7846bcf3386a73464864823e20cd46ee9dacec514028b403`.
- Árvore extraída: `JOGO/Metal Saga`, 58 arquivos, 1.703.631.558 bytes.
- Todos os 58 arquivos da árvore correspondem em tamanho e SHA-256 aos respectivos
  extents ISO9660. Nenhum arquivo de referência foi escrito pelas ferramentas.
- Sistema de arquivos ISO9660 com setor lógico de 2.048 bytes, descritor primário no setor 16.
- Executável `SLUS_212.93`: assinatura ELF, classe 32 bits, little endian, máquina 8
  (MIPS), tipo 2, entrada `0x27FD58`. `SYSTEM.CNF` aponta para esse executável.
- Três IRX com assinatura ELF: ATAD, DEV9 e USBMOUSE; imagem IOP `IOPRP300.IMG`
  começa por `RESET`/`ROMDIR`. Não foram alterados.
- Extensões: 35 SDA, 7 DAT, 4 BIN, 3 IRX, 2 GFI, e um de cada LDT, MCT, PTD,
  STM, IMG, CNF e executável `.93`. Extensão não determina formato.
- Diretórios de dados: ADATA, COMMON, FDATA, MAP, MMBATTLE, MOVIE, NDATA, RDATA,
  S, SOUND, SYS e TANK. Inventário completo: `reports/inventory.json`.
- Maiores recursos: MAP.MCT (730.998.784), BGM.SDA (358.459.392),
  MMBATTLE.BIN (321.731.584), DEMO.STM (95.670.704 bytes).
- `DEMO.STM` possui assinaturas `MSTM` e `MPEGPCM` no início; o codec e a estrutura
  dos streams ainda não foram determinados.

## Contêiner SDA

39 arquivos, inclusive DAT e MCT, passaram pela validação estrutural abaixo:

| Offset | Estrutura observada |
| --- | --- |
| 0x00 | quatro bytes `73 64 61 00` |
| 0x04 | tamanho declarado, uint32 little endian, igual ao arquivo |
| 0x08 | quantidade de entradas, uint32 little endian |
| 0x0C | tabela de offsets uint32 little endian |

Os offsets são crescentes, ficam depois da tabela e dentro do tamanho declarado.
Os intervalos até o próximo offset são slots; podem conter padding. Não devem ser
confundidos automaticamente com o tamanho lógico do recurso.

`S_PACK.SDA` tem sete entradas em `0x800`, `0x35000`, `0x8C800`, `0xB4000`,
`0xF5800`, `0x11A000`, `0x11C800`. Cada uma contém outro SDA válido cujo tamanho
declarado cabe no slot externo. O primeiro SDA interno declara `0x34070` bytes,
dentro de um slot de `0x34800` bytes. Foram reconhecidos oito nós SDA nesse arquivo.
Isso demonstra acesso direto a esses recursos, sem precisar descomprimir o contêiner.
Não significa que todos os seus recursos estejam descomprimidos.

## Recursos textuais prioritários

| Recurso | Evidência | Prioridade |
| --- | --- | --- |
| DIARY.DAT | 68 registros, títulos e corpos legíveis; round-trip binário comprovado | primeiro piloto |
| S_PACK.SDA | nomes de equipamentos em ASCII, exemplo em 0x8A0; SDA aninhado | menus e itens |
| MAP.MCT | diálogos legíveis com tags msg/msgn e cabeçalhos estruturados | narrativa |
| SLUS_212.93 | mensagens de interface próximas a 0x32D160 e referências a recursos | interface |
| SYS/*.GFI | nomes referenciados junto de DNS FONT TEX/CODE no ELF | fontes |

### Diário

Arquivo com 11.252 bytes; SHA-256 em `reports/diary-validation.json`.
`uint32` em 0x00 vale 68; os 68 offsets em 0x04 terminam exatamente em 0x114,
início do primeiro registro. Todos os registros passaram pelas mesmas verificações:

| Offset relativo | Conteúdo |
| --- | --- |
| +0x00 | uint32 de metadados, significado ainda não determinado |
| +0x04 | uint32 de metadados, significado ainda não determinado |
| +0x08 | título terminado em NUL, slot de 40 bytes |
| +0x30 | corpo terminado em NUL, até o próximo registro/fim do arquivo |

O primeiro título inicia em `0x11C`, o corpo em `0x144`. Todo o padding depois do
terminador é zero nos campos observados. Texto predominantemente no subconjunto ASCII;
os corpos dos registros 16 e 31 (índices a partir de zero) contêm `81 63`.
Essa sequência é preservada como `\x81c` no JSON; **a codificação geral não foi identificada**.
`|` aparece entre trechos de texto e `%N1`/`%N2` em referências a personagens:
prováveis controles de linha e substituição; confirmar no emulador e no leitor do ELF.

O editor mantém tamanho, offsets e metadados; limita o título a 39 bytes úteis e o
corpo ao slot original menos o NUL. Rejeita overflow, alteração de tokens `%...`,
metadados, hash de origem incorreto e mudança na sequência de bytes acima de 0x7F.
Não oferece suporte novo a UTF-8, acentos ou expansão. `\xHH` representa byte literal.

### MAP.MCT

Cinco entradas externas: `0x800`, `0x1FFC4000`, `0x202B7000`, `0x26D25800`, `0x2B922000`.
A primeira começa por `maps`. Há diálogo confirmado por inspeção em `0x038DB014`
(tag `msgn` em `0x038DAFF4`) e `0x057CE63C` (tag `msg\0` em `0x057CE61C`).
Nesses exemplos, o texto começa em tag+0x20 e o uint16 little endian em tag+6
delimita o registro, incluindo cabeçalho. Há controles 0x09 e 0x0A nos diálogos.

Uma busca heurística por esse padrão encontrou 6.131 candidatos com texto ASCII e
tamanho múltiplo de quatro. **Não é uma contagem definitiva de diálogos**: pode omitir
mensagens com bytes especiais ou incluir coincidências. Amostras de offsets ficam em
`reports/structures.json`. Não editar o script narrativo até validar tamanhos,
referências, fluxo de controle e fronteiras dos blocos que o contêm.

### Fontes e gráficos

`SUC20I22.GFI` (874.126 bytes) e `SUC24I26.GFI` (1.220.590 bytes) são candidatos
fortes a fontes: o ELF contém os nomes em `0x33C360` e `0x33C380`, perto dos rótulos
`DNS FONT TEX`, `DNS FONT CODE`, `DNS FONT 22` e `DNS FONT 26`.
O cabeçalho e as regiões de dados diferem entre os dois arquivos. Tabela de glifos,
packing de pixels, métricas e mapeamento de caracteres ainda não foram decodificados.
As referências são evidência mais forte que a extensão isolada.

Recursos RDATA/RTITLE, FDATA/F_COMMON, PASSWORD e outros SDA contêm dados não textuais
e são candidatos a gráficos de interface por contexto/nome, ainda sem confirmação visual.
Sequências imprimíveis em texturas geram falsos positivos: a contagem de strings do
inventário serve para triagem, nunca como classificação automática de conteúdo.

## Experimento executado

1. Extrair os 136 campos do diário para JSON local.
2. Reinserir sem edição: igualdade integral com o arquivo de referência.
3. Alterar apenas o primeiro título para `Tarefas`, sem acentos.
4. Preservar 11.252 bytes e todos os offsets; nove bytes diferentes em
   `0x11D`–`0x125`, dentro do slot do primeiro título.
5. Criar `work/MetalSaga-ptbr-experimento.iso` como cópia separada da ISO.
6. Substituir apenas o extent do diário: LBA 643, offset absoluto `0x141800`.
7. Comparar integralmente as imagens: todos os bytes fora do extent são idênticos.

A substituição de mesmo tamanho evita reconstruir tabelas ISO e preserva os LBAs.
Expansão de arquivos exigirá investigação de referências a setores, alinhamentos e
reconstrução do disco. A ferramenta atual rejeita substituições de tamanho diferente.

## Reprodução

Na raiz do workspace, com Python 3.11+:

```powershell
python tools/recon.py
python tools/probe_resources.py
python tools/disc.py 'JOGO/Metal Saga.iso' --source 'JOGO/Metal Saga' --report reports/disc.json
python -m unittest discover -s tests -v
python tools/diary.py extract 'JOGO/Metal Saga/DATA/FDATA/DIARY.DAT' work/diary.en.json
```

Copiar o JSON para `work/diary.pt-test.json`, editar somente `text` do primeiro
campo para `Tarefas` e executar (os arquivos de saída precisam ser novos):

```powershell
python tools/diary.py insert 'JOGO/Metal Saga/DATA/FDATA/DIARY.DAT' work/diary.pt-test.json --output work/DIARY.DAT
python tools/disc.py 'JOGO/Metal Saga.iso' --replace DATA/FDATA/DIARY.DAT --payload work/DIARY.DAT --output work/MetalSaga-ptbr-experimento.iso
```

Cinco testes automatizados com fixture sintética passaram: round-trip, edição
preservando estrutura, rejeição de overflow/tokens/metadados, hash incorreto e preservação de bytes especiais.
O round-trip com o diário real e a comparação integral das ISOs também foram executados.

## Pendências e sequência recomendada

1. Executar a ISO experimental no PCSX2 e abrir o diário para verificar `Tarefas`.
   Preparar ambiente de teste isolado antes de executar, preservando cartões, BIOS,
   saves e configurações existentes. Nesta fase apenas foi identificada a instalação
   portátil; a consulta `-help` não produziu saída e não constitui teste de jogo.
2. Investigar no ELF o leitor de GFI e a sequência `81 63`; só então definir a
   codificação editável e o suporte a á/ã/ç e demais caracteres PT-BR.
3. Modelar os registros msg/msgn e as tabelas de S_PACK com testes de round-trip.
4. Definir regras de largura visual, tokens e glossário após validação no jogo.
5. Expandir textos somente quando os limites estruturais estiverem comprovados.

Não há comprovação de um algoritmo de compressão específico, de capacidade para
textos maiores nem de suporte atual a acentos. Não foram usados outros projetos,
dependências externas ou código de recompilação nativa.
