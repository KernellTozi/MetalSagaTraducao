# Metal Saga — tradução PT-BR (PS2)

Tradução por modificação dos recursos do jogo original para execução no PCSX2.
Projeto independente de recompilação nativa. Não distribui arquivos do jogo, BIOS ou emulador.

Prioridade atual: **HUD, Satcom, mensagens e menus**, depois itens; os pequenos
fragmentos restantes de MAP.MCT ficam para o final. O lote atual de interface
soma **573 campos de texto e 40 rótulos gráficos de interface** à base de diálogos v030, mantendo o layout v005.
**`Preparar-Interface.cmd`** valida localmente; **`Testar-Interface.cmd`** ou
**`Iniciar-Teste.cmd`** abre a imagem consolidada. A execução visual dessa nova
interface está pendente. O lote inclui mensagens de Memory Card, diário e estatísticas.
A v008 mantém a fonte recuperada do atlas original e corrige o alinhamento vertical
das letras pela referência Remote.
Alguns títulos são imagens e ainda permanecem em inglês.
[Escopo, reprodução e roteiro de teste](docs/interface-v008.md).

A **alpha v001 está preservada** em `dist/alpha-v001/MetalSaga-ptbr-alpha-v001.iso`,
fora da retenção, somente leitura e conferida por hash. Ela contém a interface v001
e não é substituída por lotes posteriores. [Manifesto e regras](docs/alpha-v001.md).

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
7.231 registros localmente, sem gerar outra ISO. São 5.892 registros traduzidos e
1.339 preservados, incluindo 123 adiados mantidos no original.
O rascunho PT-BR está em `translations/regiao-inicial-v029.json`, com herança dos
lotes anteriores. **`Testar-Regiao-Inicial.cmd`**
abre a ISO consolidada com textos v029, fontes v002 e layout v005,
confirmado visualmente pelo usuário nas falas de Nina. [Manual e limites](docs/regiao-inicial-v029.md).
[Glossário e regras de preservação](docs/glossario.md).

O recorte atual abrange todo o catálogo conhecido do MAP.MCT; isso não significa
100% de tradução. **`Auditar-Traducao.cmd`** separa alterações, bloqueios, pausas,
sugestões de nomes/expressões e preservados a revisar em `work/auditorias/`.
[Manual da auditoria](docs/auditoria-cobertura.md). A v023 traduz 91 escolhas nomeadas mediante uma [política específica de slots fixos](docs/reinsercao-v005.md), com rótulos protegidos e verificação do ELF original. A política legada permanece inalterada.

- [Ambiente de teste, iniciador e roteiros](docs/ambiente-de-testes.md).
- [Piloto de diálogo e expansão em lotes](docs/dialogo-inicial.md).
- [Pesquisa dos quatro projetos públicos](docs/referencias-tecnicas.md).
- [Experimento de acentuação, mapeamento e teste manual](docs/acentuacao.md).

Imagens históricas podem já ter sido removidas pela retenção das dez mais recentes.
Se a imagem histórica do primeiro diálogo ainda estiver presente, na raiz:

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


Correção da largura dos acentos confirmada pelo usuário na cena de Nina: **`Testar-Acentos-Corrigidos.cmd`**
abre uma cópia da v023 com métricas PT-BR v005, mantendo os mesmos textos e
bitmaps. [Diagnóstico, reprodução e roteiro visual](docs/layout-v005.md).
O iniciador habitual abre o lote atual com esse mesmo perfil de correção. A aprovação cobre a cena
testada; outros contextos continuam sujeitos a verificação.


Próximas etapas: [plano de conclusão](docs/plano-conclusao.md). A v029 acrescenta
22 registros de hospedagem, recebimento e nomeação de veículos com [referência N0 preservada](docs/controle-n0-v011.md).
Drive continua igual ao comando da interface; nomes, apelidos e risadas permanecem intactos.
O perfil de acentos v005 continua vinculado à receita. O usuário fará a conferência conjunta em um save corrido.

**Preparar-Atlas.cmd** prepara 69 texturas dos próximos cinco conjuntos de interface,
com previews e PNGs indexados em work/. A reconstrução local preserva os recursos
originais e não altera ISO. [Manual dos atlas](docs/atlas-interface-v001.md).
A imagem de teste atual é interface v010: cabeçalho e instruções da nomeação,
preservando a tela inicial traduzida e o alinhamento Satcom corrigido.
[Manual da v010](docs/interface-v010.md). Abrir pelo **Iniciar-Teste.cmd** na raiz.
