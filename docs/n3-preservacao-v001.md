# Análise de N3 — preservar nomes de tanques

O próximo grupo da triagem v025 era `%N$3`, com 19 registros exclusivos. A inspeção dos corpos encontrou a referência entre aspas, uma quebra de linha e nomes de tanques, como Buggy, Demag, Panzer, Maus e Type 90. Esses nomes devem permanecer em inglês conforme orientação expressa do usuário. Não há motivo contextual para reescrever esses registros nesta fase.

## Evidência binária

No ELF original, a entrada N da tabela `0x33DD60` aponta para VA `0x2B4CAC`, offset `0x1B5CAC`. O handler até `0x1B5CDF` avança após N, chama o leitor numérico compartilhado e usa o resultado multiplicado por quatro para carregar um ponteiro da tabela em VA `0x47558C`. O cursor retornado pelo leitor fica em s6; a string obtida segue para o emissor em `0x1B5E88`.

Para `$3`, o leitor consulta a variável 3, não um nome fixo de índice 3. O interpretador limitado confirmou o consumo e a leitura dessa variável. O conteúdo completo da tabela em execução e os valores fornecidos pelos chamadores não foram rastreados; não chamar essa referência de ID canônico de personagem, cidade ou cena.

O relatório `reports/n3-preservation-v001.json` contém hash do ELF/handler, alvo do dispatch, sondagens do leitor e os 19 IDs/fingerprints. A análise foi feita sobre o original e o plano local, sem modificar recursos.

## Decisão

Preservar integralmente os 19 registros e os nomes de tanques. Não criar traduções cosméticas ou promover esses nomes para aumentar contagens. A decisão editorial está definida, mas a edição de N continua tecnicamente bloqueada no compilador; por isso esses 19 ainda aparecem entre os adiados da auditoria conservadora.

Se uma fala real precisar usar N futuramente, investigar os chamadores, valores e limites do lookup antes de uma política própria. Não generalizar a análise desses nomes a `%N$0`, combinações com T ou outras variáveis.

O trabalho seguinte passou ao grupo `%$15`. Após a v026, priorizar `%T$0`, não repetir a investigação dos nomes N3 sem evidência nova.
