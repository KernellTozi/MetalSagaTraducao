# Metal Saga — tradução PT-BR (PS2)

Tradução por modificação dos recursos do jogo original para execução no PCSX2.
Projeto independente de recompilação nativa. Não distribui arquivos do jogo, BIOS ou emulador.

O reconhecimento inicial está em [docs/reconhecimento.md](docs/reconhecimento.md).
Há experimentos separados de diário e diálogo inicial; ambos têm validação binária,
mas sua tradução na tela ainda aguarda confirmação visual.

- [Ambiente de teste, iniciador e roteiros](docs/ambiente-de-testes.md).
- [Piloto de diálogo e expansão em lotes](docs/dialogo-inicial.md).
- [Pesquisa dos quatro projetos públicos](docs/referencias-tecnicas.md).

Para abrir a ISO do diálogo, dar duplo clique em `Iniciar-Teste.cmd`. Na raiz:

```powershell
.\Iniciar-Teste.cmd dialogue
```

Fechar a cópia de teste e usar `.\Iniciar-Teste.cmd diary` para testar o diário.

Requer Python 3.11 ou superior, sem dependências externas. Execute na raiz do projeto:

```powershell
python tools/recon.py
python tools/probe_resources.py
python tools/disc.py 'JOGO/Metal Saga.iso' --source 'JOGO/Metal Saga' --report reports/disc.json
python -m unittest discover -s tests -v
```

Os relatórios versionados contêm metadados, hashes e offsets; extrações de texto e cópias
modificadas ficam em `work/`, ignorado pelo Git. `JOGO/` é somente leitura por política.
