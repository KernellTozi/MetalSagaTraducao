# Auditoria local de cobertura

Execute `Auditar-Traducao.cmd` na raiz. A ferramenta lê o plano e o relatório
compilados da versão padrão, sem acessar IA, APIs ou o emulador. Não altera o
MAP.MCT, traduções ou ISOs. É necessário ter a pasta da compilação local; caso
esteja ausente, recompilar com o construtor e o caminho indicado no manual do lote.

A cada execução, cria uma pasta nova em `work/auditorias/`:

- `resumo.json`: contagens, hashes e limites da classificação; sem textos do jogo.
- `deferred.jsonl`: registros adiados, com metadados originais.
- `controls_or_punctuation.jsonl`: registros sem letras após retirar comandos reconhecidos.
- `name_or_expression_candidate.jsonl`: sugestões de nomes ou expressões preservadas.
- `review_unchanged.jsonl`: demais registros intactos, para revisão humana contextual.

Os JSONL contêm textos originais e ficam fora do Git. Labels protegidos de msgn
não são tratados como diálogo editável na triagem. Nomes e expressões só recebem
uma sugestão quando o texto visível completo coincide com a lista explícita da
política; isso não é reconhecimento automático de entidades. Falas compostas,
nomes em sequência, gritos e onomatopeias podem continuar em revisão por cautela.

A ferramenta confere validade da compilação, hash de origem, IDs únicos,
adiamentos conhecidos e contagens. Remove da visão de triagem somente os tokens
reconhecidos pelo parser existente. Um controle opaco sem adiamento explícito
provoca erro. Nenhuma classificação libera edição ou comprova execução no PCSX2.

Na v021: 5.636 alterados, 349 adiados, 599 de controles/pontuação, 458 sugestões
de nomes/expressões e 189 preservados a revisar. Estes últimos contêm 117
combinações textuais distintas. Há muitos gritos, sons, risadas, nomes e marcas
de atuação; também há títulos genéricos como Transport Pod e Trader Camp que
merecem revisão posterior. As contagens não são porcentagem de palavras nem
indicam 189 diálogos obrigatoriamente não traduzidos.

A auditoria foi executada sobre a compilação final, com resumo próprio em
`reports/regiao-inicial-v021-coverage.json`. Seu resultado orienta a próxima
revisão e não altera o lote atual.

```powershell
python tools/audit_translation_coverage.py --build-dir work/regiao-inicial-v021 --output work/auditoria-v021-repro
```

Três testes cobrem triagem conservadora, comandos, labels somente de leitura,
entradas inconsistentes, IDs duplicados e controles opacos sem adiamento.


## Ampliação v022

O resumo passa a incluir bloqueios por família, por motivo e por sintaxe opaca
reconhecida pelo parser. A lista de sintaxes representa os spans encontrados,
não uma gramática comprovada: por exemplo, um sufixo após `%$15` pode fazer parte
do formato em execução e não estar incluído nesse span. Não remover ou corrigir
comandos com base nessa classificação.

Depois da revisão dos títulos: 5.667 alterados, 349 adiados, 599 de controles ou
pontuação, 458 sugestões de nomes/expressões e 158 preservados a revisar. O resumo
final está em `reports/regiao-inicial-v022-coverage.json`. Os relatórios da v021
permanecem como evidência histórica. Os testes adicionais verificam que a
classificação de sintaxes não promove registros nem concede aprovação de edição.
