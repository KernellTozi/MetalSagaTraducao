# Controle B15 — política de reinserção v006

## Evidência

O catálogo v023 contém 35 registros com o span `%B$15`. Em 32, ele é o único controle opaco; três continuam com outros bloqueios. Esses 32 pertencem a um conjunto coerente de construção/reforma de tanques e fabricação de C Unit, com referência recorrente a um apelido. Não se converteu essa referência em nome fixo.

No ELF original reconhecido, offsets no arquivo (VA = offset + `0xFF000`):

- `0x1B5A30..0x1B5ACF`: leitor numérico. Reconhece sinal, `$` opcional e dígitos; `$` faz leitura uint32 em contexto + índice ×4. Retorna o cursor no primeiro byte não numérico. Para `$15`, o índice é 15 decimal, não hexadecimal.
- `0x33DD60`: tabela de dispatch dos comandos; a entrada B aponta para VA `0x2B4CE0`.
- `0x1B5CE0..0x1B5D2B`: B chama esse leitor, usa o resultado numa tabela de int16 em VA `0x43CE30` e obtém uma string por offsets do recurso apontado em VA `0x475B18`.
- O processamento posterior em `0x1B5E88..0x1B5EF7` percorre a string obtida e emite caracteres. Isso não torna o índice uma identidade canônica de personagem.

A rotina de leitura foi executada por um interpretador limitado, incluindo delay slots, branch-likely e MULT com destino do R5900. Foram conferidos índice variável, sinal, consumo dos dígitos e parada antes do sufixo. Hashes do ELF, do leitor e do handler e alvo do dispatch são verificados a cada compilação opt-in. Não foi emulado o lookup completo de recursos ou todo o motor.

## Política restrita

`fixed-record-b15-preserved-slots-v006` herda a política de escolhas nomeadas e reconhece somente o token exato `%B$15`. Não libera `%B$14`, `%B$150`, `%N$...`, `%$...` ou outros controles. O extrator e o lexer históricos continuam inalterados.

O comando é imutável: remoção, troca de índice, duplicação ou mudança na sequência de controles recusa o lote. Mantêm-se quebras, páginas, spans vazios, bytes de origem, hashes, cabeçalhos, offsets, nomes/rótulos e tamanho do registro.

Registros com B15 exigem `slots`, sem repack. Cada segmento traduzido deve ter no máximo a quantidade de bytes do próprio texto original, mesmo se houver padding adicional. Essa restrição reduz o risco de crescimento junto da substituição dinâmica; não equivale a uma validação de todos os estados de execução. A expansão dinâmica usa a mesma referência original.

## Reprodução

```powershell
python -m unittest discover -s tests -p test_control_b15.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v024.json --output work/b15-repro
```

Os testes verificam o leitor real, token exato, preservação do lexer legado, round-trip, recusa de crescimento, mudança de referência, repack, controles adicionais e ELF divergente. A regressão integral da v024 preserva os 5.758 registros traduzidos anteriores.

As traduções do grupo estão na v024. A exibição da referência dinâmica, largura e fluxo das decisões precisam de teste manual quando essa parte do jogo estiver acessível. A correção de acentos v005 continua aplicada e teve aprovação visual nas falas de Nina; isso não comprova toda a cena de construção de tanques.
