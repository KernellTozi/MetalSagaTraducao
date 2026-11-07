# Como contribuir

## Relatar um problema

Use o formulário de problema nas Issues e informe:

- Versão da tradução e versão do PCSX2, quando utilizado.
- Local, personagem, item ou menu envolvido.
- Passos para reproduzir, texto observado e resultado esperado.
- Captura de tela e, se possível, a fala anterior para contextualizar.
- Se houve restauração de save state ou inicialização limpa pelo memory card.

Não anexe ISO, BIOS, emulador, dumps, saves pessoais ou credenciais.
Capturas devem mostrar somente o necessário, sem dados pessoais.

## Sugerir uma tradução

Informe a frase atual, sua sugestão e o contexto da cena. Antes de propor
trocas de nomes próprios, consulte o [glossário](docs/glossario.md).
Limites de bytes e largura visual podem exigir adaptação; não remova artigos
ou acentos apenas para fazer uma frase caber.

## Contribuir com ferramentas

As ferramentas são locais, preferencialmente em Python. Preserve fontes
originais e produza alterações em cópias. Uma mudança binária precisa de
evidências de formato, limites e ponteiros, além de testes apropriados.
Validação binária não substitui teste visual no jogo.

Descreva o problema resolvido, o comportamento final e as verificações
executadas no pull request. Não inclua binários do jogo, fontes comerciais,
ISOs, BIOS, recursos extraídos ou resultados volumosos. As regras técnicas
detalhadas estão no [AGENTS.md](AGENTS.md).
