# Reinserção v005 — escolhas nomeadas

Política explícita: `fixed-record-named-choice-slots-v005`. A política v004 continua sendo o padrão do compilador genérico e dos lotes antigos. Somente a receita v023 seleciona a extensão.

## Evidência e limites

A [investigação v001](escolhas-nomeadas-investigacao-v001.md) demonstrou o caminho da terceira string até o método de rótulo no ELF original. Cada compilação opt-in verifica o SHA-256 completo do ELF e 22 instruções/palavras. Uma revisão divergente aborta a operação. O relatório registra o hash e a quantidade de verificações.

Foram catalogados 112 registros: 83 smnn (cabeçalho de 40 bytes) e 29 2snm (48 bytes). Destes, 91 não possuem outros bloqueios; 21 preservam controles opacos e continuam adiados. Corpo e opções são editáveis somente em slots fixos. A terceira string continua somente leitura: bytes, offset, terminador e padding até o final do registro são conferidos integralmente.

Não há realocação, crescimento de registro ou repack dessas famílias. O buffer temporário de opções continua limitado a 254 bytes, além do limite individual do slot. Quebras de linha, páginas, opções e comandos devem preservar sequência e spans vazios. Nenhum controle opaco ou byte nativo foi liberado.

## Reprodução

```powershell
python -m unittest discover -s tests -p test_named_choice_policy.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v023.json --output work/validacao-v023-nova
```

Usar um diretório de saída novo. Sem `--build-iso`, a compilação apenas gera plano e relatórios locais. O lote possui 91 IDs explícitos em `resume_deferred`; cada retomada exige tradução própria e um adiamento existente no pai. O lote é aplicado integralmente ou recusado.

Os testes cobrem round-trip, cabeçalhos, slots, offsets, rótulo e cauda, limite de opções, recusa de metadados alterados, modo repack, controles modificados e transação parcial. Uma regressão integral compara os 7.231 registros com a v022, permitindo apenas as 91 traduções e a atualização justificada de bloqueios em 112 descritores.

A validação visual deste mecanismo continua pendente. Não se deve confundir a evidência binária com teste no PCSX2. A receita atual mantém fontes v002 e espaçamento v003, no estado anteriormente assumido pelo usuário.

## Perfis de fonte e construção

Para o lote v023, usar o construtor `build_translation_pilot.py` e os iniciadores da região. Ele integra explicitamente fontes v002 e espaçamento v003. O iniciador genérico de reinserção continua associado à ISO de desenvolvimento com fontes v001; não usá-lo para substituir a construção consolidada deste lote.
