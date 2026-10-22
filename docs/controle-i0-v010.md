# Referência I0 — política v010

A política opt-in `fixed-record-i0-preserved-slots-v010` herda v009 e acrescenta somente `%I$0`. Não troca o nome dinâmico por um nome fixo, não modifica a tabela de origem nem amplia o lexer histórico ou os fingerprints de extração.

## Evidência no ELF original

Offsets no arquivo `SLUS_212.93`; VA = offset + `0xFF000`:

- A entrada I da tabela em `0x33DD60` aponta para VA `0x2B4D74`, offset `0x1B5D74`.
- `0x1B5D74..0x1B5DA3` avança após I e chama o leitor numérico original em `0x1B5A30`. `$0` lê a variável 0 do contexto; não representa um item fixo de ID zero.
- O handler carrega o ponteiro de base em VA `0x475AE8`, desloca o valor lido sete bits à esquerda e soma à base: endereço = base + índice ×128.
- O endereço resultante segue em s1 para o emissor em `0x1B5E88`; s6 mantém o cursor do texto após o parâmetro.

O interpretador limitado de `control_i0.py` executa as instruções originais com memória simulada e usa o interpretador existente do leitor original. Os testes conferem índice, deslocamento, leitura da base, cursor e delay slots. Os índices de prova não são limites comprovados da tabela durante o jogo.

Hash integral do ELF, intervalo do handler, dispatch e verificações herdadas são obrigatórios. Evidência em `reports/controle-i0-v010-evidence.json`. Não se executou o emissor, não se comprovou o terminador de todos os registros dessa tabela nem seu vínculo completo com um arquivo como S_PACK.SDA. O stride 128 não autoriza traduzir ou expandir esses registros.

## Política e contexto

Somente `%I$0` é liberado. `%I$00`, `%I$01`, `%I$1`, `%I0`, `%I-$0`, `%i$0`, variantes com underscore e misturas com outros opacos permanecem bloqueados. Um f literal após I0 não aciona a formatação fracionária do comando numérico `$`.

Registros com a referência exigem slots fixos e nenhum crescimento de segmento frente ao próprio comprimento original. Preservar comandos, índices, ordem, quebras, spans vazios, rótulos, cabeçalhos, offsets e limites anteriores. Não crescer registros, blocos SSD ou extents.

As 14 falas contêm dicas de combate/equipamento, proteção e agradecimentos por presentes. A redação ao redor da referência evita depender de um gênero gramatical ainda não confirmado do nome resolvido. Mantêm-se nomes únicos, `%N0`, `%W5`, pausas, risadas e expressões. Não foram traduzidos os nomes que o lookup retorna.

## Reprodução

```powershell
python -m unittest discover -s tests -p test_control_i0.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v028.json --output work/i0-repro
```

Os testes cobrem handler original com memória simulada, leitor, sintaxe exata, legado bloqueado, slots, rótulos, round-trip, recusa de crescimento/troca de índice/repack e falha atômica. A regressão do lote compara todos os 7.231 descritores com a v027 e preserva suas 5.856 traduções. A validação no PCSX2 continua para o save corrido do usuário.
