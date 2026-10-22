# Metal Saga — tradução PT-BR (PS2)

Tradução por modificação dos recursos do jogo original para execução no PCSX2.
Projeto independente de recompilação nativa. Não distribui arquivos do jogo, BIOS ou emulador.

O reconhecimento inicial está em [docs/reconhecimento.md](docs/reconhecimento.md).
Há experimentos separados de diário, diálogo inicial e acentuação. A fala ASCII
inicial foi confirmada visualmente pelo usuário; os dois grupos de acentos receberam
validação visual preliminar, com limitações tipográficas ainda abertas.

Para extrair os diálogos localmente, dar duplo clique em **`Extrair-Dialogos.cmd`**.
Os resultados ficam em uma pasta nova de `work/extracoes/`. Não usa IA, APIs,
emulador nem dependências externas. [Manual do extrator](docs/extrator-dialogos.md).
Na v003: 5.369 registros com extração validada, 1.862 identificados e bloqueados,
zero desconhecidos no conjunto examinado e 71 rejeitados. São 7.231 registros com
texto recuperado em 13 famílias. [Evidências e limites](docs/extracao-v003.md).

Reinserção v004: dar duplo clique em **`Reinserir-Dialogos.cmd`** para exportar,
simular e aplicar lotes. A política binária cobre 6.882 registros em onze famílias;
349 continuam bloqueados. ISO de desenvolvimento reutilizável, snapshots e
recuperação transacional. [Manual e teste visual preparado](docs/reinsercao-v004.md).

- [Ambiente de teste, iniciador e roteiros](docs/ambiente-de-testes.md).
- [Piloto de diálogo e expansão em lotes](docs/dialogo-inicial.md).
- [Pesquisa dos quatro projetos públicos](docs/referencias-tecnicas.md).
- [Experimento de acentuação, mapeamento e teste manual](docs/acentuacao.md).

Para abrir a ISO do diálogo, dar duplo clique em `Iniciar-Teste.cmd`. Na raiz:

```powershell
.\Iniciar-Teste.cmd dialogue
```

Fechar a cópia de teste e usar `.\Iniciar-Teste.cmd diary` para testar o diário.
Para o novo experimento separado, usar `.\Iniciar-Teste.cmd accents`.

Requer Python 3.11 ou superior. As ferramentas originais usam a biblioteca padrão;
a composição de acentos usa as dependências locais descritas no relatório acima.
Execute na raiz do projeto:

```powershell
python tools/recon.py
python tools/probe_resources.py
python tools/disc.py 'JOGO/Metal Saga.iso' --source 'JOGO/Metal Saga' --report reports/disc.json
python -m unittest discover -s tests -v
```

Os relatórios versionados contêm metadados, hashes e offsets; extrações de texto e cópias
modificadas ficam em `work/`, ignorado pelo Git. `JOGO/` é somente leitura por política.
