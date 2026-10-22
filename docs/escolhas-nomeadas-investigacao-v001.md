# Escolhas nomeadas — investigação v001

## Resultado e limite

Foi conferido no ELF original o caminho que encaminha a terceira string dos
formatos nomeados ao método de rótulo `0x2FC968`, também presente no caminho de
msgn já estudado. A inspeção do corpus encontrou 112 registros: 83 smnn e 29
2snm. Em 91 não existem outros bloqueios conhecidos; 21 também têm controles
opacos. Essas contagens já eram compatíveis com a classificação v004; a evidência
nova é o caminho do argumento de rótulo no executável.

**Nenhuma edição foi liberada por esta investigação.** O compilador legado
continua recusando alterações desses formatos, mantendo os 349 adiamentos.
O rótulo de exibição não é um ID canônico de personagem e não comprova sozinho
retrato, falante ou condição de roteiro. Não houve execução no PCSX2.

## Evidência no executável

O relatório `reports/named-choice-evidence-v001.json` vincula o SHA-256 do ELF e
do MAP, os words exatos das instruções, os IDs, hashes dos registros e hashes e
offsets das terceiras strings. Não contém os textos originais.

| Caminho | Evidência |
| --- | --- |
| `0x2C14BC` | A construção associada a smnn fornece a tabela `0x40A718` |
| `0x40A72C`, `0x40A734` | Entradas para o tratamento `0x2C5C20` e loader `0x2C5920` |
| `0x2C5928`, `0x2C592C` | Loader compartilhado `0x2C5248`, com quatro parâmetros de oito bytes |
| `0x2C20CC` | A construção de 2snm fornece a tabela `0x40A6E0` |
| `0x40A6F4`, `0x40A6FC` | Tratamento `0x2C5E58` e loader `0x2C5E30` |
| `0x2C5E3C`, `0x2C5E40` | Mesmo loader compartilhado, com cinco parâmetros |
| `0x2C5E90` | O wrapper de 2snm chama `0x2C5C20` |
| `0x2C5D68` | A string de opções passa pelo helper `0x2C5788` |
| `0x2C5D90`, `0x2C5D94` | Busca NUL após as opções, com o argumento de busca zerado |
| `0x2C5DB8..0x2C5DCC` | Percurso pelos zeros separadores após as opções |
| `0x2C5DD4..0x2C5DE4` | Obtém o objeto de UI e passa a terceira string ao método `0x2FC968` |

Foi usada a revisão original com delta VA/arquivo `0xFF000`, já vinculado nos
relatórios anteriores. Os testes verificam words e hash completos. A saída de
um disassembler MIPS32 genérico não foi tratada como prova para instruções R5900:
alguns words de registradores e salvamento de contexto são interpretados como
instruções de outras extensões. Não foram inferidas semânticas a partir desses
nomes incorretos.

As 112 terceiras strings foram conferidas contra o MAP original, incluindo NUL,
offset, hash e marca somente de leitura. A investigação não reescreve registros,
ponteiros, fontes ou imagens de disco.

## Reproduzir

```powershell
python tools/investigate_named_choices.py --output work/escolhas-nomeadas-repro.json
```

O comando usa Python e biblioteca padrão, sem capstone, IA, rede ou emulador.
Recusa outra revisão do executável e saídas já existentes. Dois testes cobrem
o corpus real e a recusa de um ELF alterado.

## Próxima implementação

Criar uma política opt-in de slots fixos para smnn e 2snm, mantendo o rótulo,
seus zeros, offsets e metadados imutáveis. Vincular a nova política às evidências
da revisão do ELF e preservar a política legada para reproduzir versões antigas.
Testar pergunta, opções, limite temporário de opções, controles e leitura após
reinserção. Não liberar repack ou os 21 casos opacos por analogia.

Para os controles opacos, a triagem atual aponta `%B$15` em 35 registros e
`%$1` em 32, além de outras sintaxes. Essas são contagens de spans do parser;
não comprovam substituição de nomes, preços ou limites dos buffers do motor.
A gramática completa e os efeitos precisam ser rastreados antes de editar.
