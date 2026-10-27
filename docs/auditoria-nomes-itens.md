# Auditoria humana completa de nomes de itens

O usuário pediu revisar todos os nomes, incluindo os já traduzidos, em
26/10/2026. Prioridade atual: preparar e discutir a auditoria com ele antes
de aplicar novos nomes. A exportação não muda receitas, políticas, originais
ou ISO. Não considerar propostas anteriores como escolhas aprovadas.

## Lista entregue

`work/auditoria-itens-v040/auditoria-completa.md`, em tabelas Markdown no
formato ID / Original / Tradução aplicada / Bytes, com seções separadas:

- 516 nomes traduzidos e aplicados;
- 25 propostas pendentes, explicitamente não aplicadas;
- 500 nomes mantidos no original, com o motivo disponível;
- 308 campos vazios, incluídos para conferir a tabela inteira.

Total principal: **1.349 IDs, 1.041 nomes preenchidos**, sem deduplicar nomes
iguais. A tabela também inclui habilidades e marcadores técnicos; isso não
significa 1.041 itens obtíveis. Um apêndice inclui todos os 50 campos conhecidos
de variantes de dez motores, 26 preenchidos. Não contar esses campos como
50 itens novos. Motores e demais nomes protegidos continuam preservados.

`revisao-editavel.json` contém os mesmos registros, IDs, hashes, offsets,
traduções aplicadas, propostas separadas, limites, motivos e descrições atuais
disponíveis para contexto. `review_translation` e `review_decision` começam
como null. Nenhum importador/aplicação automática foi acrescentado. O usuário
pode responder no chat por ID ou anotar esse arquivo; a próxima aplicação
deverá validar escolhas e políticas explicitamente.

## Regras de tamanho e qualidade

Teto atual 16 bytes de texto, terminador reservado. ASCII/espaço/pontuação
ASCII usam um byte; cada acento/cedilha mapeado usa dois. Ó maiúsculo ainda
não existe no perfil. O campo físico de 24 bytes não libera crescimento a
23 bytes. Tamanho em bytes não garante que qualquer combinação caiba
visualmente em todas as telas. Não suprimir acentos/artigos ou aceitar nomes
ruins para encerrar a auditoria. Preservações podem ser discutidas com o
usuário, mas não liberar categorias inteiras por inferência.

## Ferramenta e conferência

```powershell
python tools/export_item_name_audit.py --recipe translations/interface-v040.json --output work/minha-auditoria-itens
python -m unittest discover -s tests -p test_item_name_audit.py
```

Usar pasta nova. Funciona localmente sem IA, APIs, internet ou emulador.
O exportador compila a política atual dos nomes, confere a contabilidade de
revisão e aplica os patches somente em memória. Faz preflight integral da
ISO correspondente e compara **cada um dos 1.349 campos de nome** e os
50 campos de variantes com os bytes efetivamente presentes na imagem.
Confere fonte e receita novamente antes de gravar os arquivos de auditoria.

Somente os metadados próprios ficam em `reports/auditoria-itens-v040.json`.
Originais, descrições e revisão bilíngue permanecem em work/, fora do Git.
Oito testes verificam cobertura, contagens, separação proposta/aplicação,
campos preservados/vazios, variantes, Markdown completo, codec e detecção de
divergência de campo em ISO fictícia isolada. A exportação foi conferida
contra a v040 real; nenhum teste visual novo foi realizado.
