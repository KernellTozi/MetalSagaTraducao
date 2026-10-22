# Referência T0 — política v009

A política opt-in `fixed-record-t0-preserved-slots-v009` herda a v008 e acrescenta somente `%T$0`. O lexer histórico e os fingerprints do extrator permanecem inalterados. A variável e o texto que o jogo resolve não são substituídos por um nome fixo.

## Evidência no ELF original

Offsets no arquivo `SLUS_212.93`; VA = offset + `0xFF000`:

- A entrada T da tabela em `0x33DD60` aponta para VA `0x2B4D2C`, offset `0x1B5D2C`.
- `0x1B5D2C..0x1B5D73`: avança após T e chama o leitor numérico original. `$0` lê a variável 0; não significa automaticamente uma entidade de ID zero.
- Multiplica o resultado por `0x240` e soma ao ponteiro em VA `0x475570`. O MULT com destino é uma instrução R5900, não deve ser interpretado como MULT convencional sem registrador de destino.
- O accessor em `0x7F698..0x7F69F` lê o ponteiro em estrutura +`0x228`.
- O handler lê o seletor no objeto +`0x6C` e chama o accessor em `0x6BB60..0x6BB83`. Este lê `table[index]` na tabela de ponteiros VA `0x363478`, depois a string em tabela selecionada + seletor ×4.
- O retorno segue em s1 para o emissor de strings em `0x1B5E88`; s6 mantém o cursor retornado pelo leitor.

O interpretador limitado de `control_t0.py` executa as instruções desses três intervalos com memória simulada. Chamadas ao leitor usam o interpretador já existente do leitor original. Foram exercitados índices/seletor diferentes, stride, ponteiros, consumo, chamadas e delay slots, inclusive o retorno que define s1. Isso não executa o emissor nem comprova o conteúdo das tabelas durante o jogo.

O hash integral do ELF, os três intervalos, dispatch e verificações herdadas são obrigatórios. Evidência e rastros em `reports/controle-t0-v009-evidence.json`. A análise não estabelece uma identidade canônica de personagem, cidade ou cena.

## Política e tradução

Somente `%T$0` é reconhecido; `%T$00`, `%T$01`, `%T$1`, `%T0`, `%T-$0`, `%t$0`, `%N$3` e variantes com underscore continuam bloqueados. Um f literal depois de T0 não aciona o caminho fracionário exclusivo do comando numérico `$`; não confundir os handlers.

Mantêm-se tokens, ordem, quebras/páginas, spans vazios, nomes/rótulos e limites de execução. Registros que contenham a referência exigem slots fixos, sem crescimento de nenhum segmento frente ao próprio comprimento original. Cabeçalhos, offsets, registros, blocos e extents não crescem.

As 18 despedidas usam três variantes de redação/quebras. A tradução mantém a cortesia e verte o tratamento Mr. como sr., preservando o lookup. Outros comandos opacos, inclusive combinações de N com T, continuam bloqueados.

## Reprodução e limites dos testes

```powershell
python -m unittest discover -s tests -p test_control_t0.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v027.json --output work/t0-repro
```

Os testes conferem instruções originais com memória simulada, sintaxe exata, legado bloqueado, rótulos, round-trip, recusa de crescimento, mudança de índice, repack e falha atômica. A regressão integral do lote compara os 7.231 descritores com a v026 e preserva suas 5.838 traduções. A validação no PCSX2 continua para a passagem conjunta do usuário.
