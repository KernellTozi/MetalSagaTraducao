# Referência indireta N0 — política v011

A política opt-in `fixed-record-n0-preserved-slots-v011` herda v010 e acrescenta somente `%N$0`. Mantém o nome resolvido pelo jogo e não atribui um personagem ou veículo fixo ao índice. O lexer histórico e os fingerprints do extrator não mudam.

## Evidência no ELF original

Offsets no arquivo `SLUS_212.93`; VA = offset + `0xFF000`:

- A entrada N da tabela em `0x33DD60` aponta para VA `0x2B4CAC`, offset `0x1B5CAC`.
- `0x1B5CAC..0x1B5CDF` avança após N e chama o leitor numérico original em `0x1B5A30`, com saída temporária em sp +`0x28`.
- Para `$0`, o leitor consulta a variável 0 do contexto. Isso é diferente de `%N0`, cuja forma literal já era reconhecida pelo lexer legado: o argumento literal é zero, não o conteúdo da variável zero.
- O handler multiplica o valor por quatro e carrega o ponteiro em VA `0x47558C` + índice ×4. Essa última leitura acontece no delay slot do salto para o emissor em `0x1B5E88`.
- O ponteiro fica em s1; s6 mantém o cursor depois do parâmetro. Não há neste handler o seletor e os accessors usados por T.

O interpretador limitado de `control_n0.py` executa as instruções originais com memória simulada e usa o interpretador existente do leitor. Testa índice, endereço consultado, leitura do ponteiro, cursor e delay slot. Os endereços dos nomes e índices dos rastros são artificiais, não offsets nem limites comprovados das tabelas do jogo.

Hash integral do ELF, handler, dispatch e dependências herdadas são obrigatórios. Evidência em `reports/controle-n0-v011-evidence.json`. A inicialização dos nomes, o emissor e o jogo completo não foram emulados. O mesmo índice de variável aparece em contextos de hospedagem, recebimento e nomeação de veículos; não comprova uma identidade canônica única.

## Política e tradução

Somente `%N$0` é promovido. `%N$00`, `%N$01`, `%N$1`, `%N-$0`, `%n$0`, variantes com underscore e outros opacos continuam bloqueados. `%N$3` permanece bloqueado para edição e seus 19 nomes de tanques continuam intactos por decisão editorial; a investigação anterior não foi repetida para aumentar contagens.

Registros com a referência exigem slots fixos e nenhum crescimento de segmento frente à origem. Preservam comandos, índices, ordem, quebras, spans vazios, rótulos, cabeçalhos, offsets e limites de execução. Não crescer registros, blocos ou extents.

As 22 traduções mantêm nomes dinâmicos, Drive, huh? e risadas. No tutorial, Drive permanece igual à interface ainda não localizada integralmente. Na fala de Dr. Palm, a construção inglesa de posse não permite simplesmente inverter os dois tokens: a redação em português associa o apelido ao tanque mantendo a ordem B15/N0. Não se gravou apelido ou nome de tanque fixo.

## Reprodução

```powershell
python -m unittest discover -s tests -p test_control_n0.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v029.json --output work/n0-repro
```

Os testes cobrem handler/reader originais em memória simulada, distinção do N0 literal, sintaxe restrita, N3 bloqueado, rótulos, round-trip, recusa de crescimento/troca de índice/repack e falha atômica. A regressão compara os 7.231 descritores com a v028, preserva suas 5.870 traduções e confere Drive, huh? e risadas. A exibição efetiva continua pendente do teste conjunto no PCSX2.
