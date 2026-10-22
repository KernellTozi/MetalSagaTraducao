# Variável numérica 1 — política v007

## Evidência no executável original

A política `fixed-record-numeric1-preserved-slots-v007` herda escolhas nomeadas v005 e B15 v006. Acrescenta somente `%$1`, preservado literalmente. O lexer e os fingerprints do extrator histórico não mudam.

Offsets no arquivo `SLUS_212.93` original reconhecido; VA = offset + `0xFF000`:

- A entrada `$` da tabela em `0x33DD60` aponta para VA `0x2B4DEC`, offset `0x1B5DEC`.
- `0x1B5DEC..0x1B5E83`: handler numérico. Passa o cursor começando no `$` ao leitor `0x1B5A30`, com resultado em `sp+0x38` e contexto de variáveis em `s5`.
- O leitor original, executado pelo interpretador limitado de `control_b15.py`, consome os dois bytes de `$1`, lê contexto +4 e retorna o cursor no sufixo. Isso distingue índice 1 de 10 ou 15.
- `0x1B5E04..0x1B5E28` compara o sufixo com `0x66`, **f minúsculo**. Esse caminho lê outro argumento e faz divisão/formatação fracionária. Continua bloqueado, inclusive quando incompleto. F maiúsculo não aciona esse caminho.
- O caminho inteiro em `0x1B5E68..0x1B5E80` carrega o valor de 32 bits de `sp+0x38` e chama VA `0x326A28`, com destino em `sp` e formato `%d`, VA `0x448DC0` / offset `0x349DC0` (`25 64 00`). Um inteiro com sinal de 32 bits requer no máximo 11 caracteres, além do NUL. Não se emulou a função completa de formatação ou o motor PS2.

O hash integral do ELF, o leitor e handler B15 herdados, o hash do handler numérico (`34410c8529e2e6613013f4f1a831fd9f3c1d44312a47e588cc81aabeebc038e9`), dispatch e formato são conferidos em cada compilação v007. Essas verificações vinculam o diagnóstico à revisão exata do jogo.

## Limites da edição

Não se traduz nem se substitui a variável por um preço fixo. Tokens, sequência, quebras, escolhas e spans vazios permanecem vinculados à origem. A moeda G e os nomes protegidos permanecem.

Registros com a nova referência exigem slots fixos e nenhum segmento pode ultrapassar o próprio comprimento original em bytes. Cabeçalhos, offsets, rótulos, caudas, registro, bloco SSD e extents ISO não crescem. O limite também continua aplicado aos registros B15 herdados. Demais famílias conservam suas políticas anteriores.

`%$10`, `%$15`, `%$-1`, `%$1f...`, outros índices e comandos opacos não são liberados. Misturas com controles desconhecidos continuam bloqueadas. A v007 não aumenta automaticamente a cobertura do extrator, nem modifica as receitas antigas.

## Reprodução e validação

```powershell
python -m unittest discover -s tests -p test_control_numeric1.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v025.json --output work/numeric1-repro
```

Os testes cobrem índice e cursor do leitor original, valores extremos de 32 bits, reconhecimento restrito, rejeição do sufixo f, imutabilidade do lexer legado, round-trip de slots, rótulo protegido, crescimento, troca de índice, repack, falha atômica e ELF divergente. A regressão do lote compara todos os 7.231 descritores e preserva as 5.790 traduções da v024.

A exibição efetiva dos números, preço cobrado e seleção das opções ainda precisam de conferência no jogo. O usuário fará isso em uma passagem contínua pelo save, incluindo a cena de Dr. Palm; não é necessário alcançar essa cena para continuar etapas técnicas independentes.
