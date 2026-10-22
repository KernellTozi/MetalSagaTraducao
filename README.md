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

Lote atual da região inicial: **`Preparar-Regiao-Inicial.cmd`** recompila e valida
7.231 registros localmente, sem gerar outra ISO. São 5.758 registros traduzidos e
1.473 preservados, incluindo 258 adiados mantidos no original.
O rascunho PT-BR está em `translations/regiao-inicial-v023.json`, com herança dos
lotes anteriores. **`Testar-Regiao-Inicial.cmd`** ou **`Iniciar-Teste.cmd`**
abre a ISO consolidada, com fontes v002 e espaçamento v003 assumidos
provisoriamente corretos pelo usuário. [Manual e limites](docs/regiao-inicial-v023.md).
[Glossário e regras de preservação](docs/glossario.md).

O recorte atual abrange todo o catálogo conhecido do MAP.MCT; isso não significa
100% de tradução. **`Auditar-Traducao.cmd`** separa alterações, bloqueios, pausas,
sugestões de nomes/expressões e preservados a revisar em `work/auditorias/`.
[Manual da auditoria](docs/auditoria-cobertura.md). A v023 traduz 91 escolhas nomeadas mediante uma [política específica de slots fixos](docs/reinsercao-v005.md), com rótulos protegidos e verificação do ELF original. A política legada permanece inalterada.

- [Ambiente de teste, iniciador e roteiros](docs/ambiente-de-testes.md).
- [Piloto de diálogo e expansão em lotes](docs/dialogo-inicial.md).
- [Pesquisa dos quatro projetos públicos](docs/referencias-tecnicas.md).
- [Experimento de acentuação, mapeamento e teste manual](docs/acentuacao.md).

Para abrir a ISO histórica do primeiro diálogo, na raiz:

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
