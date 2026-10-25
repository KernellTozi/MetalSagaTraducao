# Metal Saga — tradução PT-BR para PS2

Tradução dos recursos do jogo original para execução no PCSX2, independente da recompilação nativa. Não distribui ISO, originais, BIOS ou emulador.

## O que abrir

| Arquivo na raiz | Para que serve |
|---|---|
| **Iniciar-Teste.cmd** | Abre a ISO traduzida atual |
| Preparar-Interface.cmd | Valida a receita atual, sem criar outra ISO |
| Extrair-Dialogos.cmd | Extrai o catálogo local de diálogos |
| Reinserir-Dialogos.cmd | Reinserção e simulação de lotes |
| Auditar-Traducao.cmd | Consolida pendências e rótulos de falantes em um JSON local |

Atalhos duplicados e de experimentos antigos foram removidos. As ferramentas continuam em tools/, com procedimentos históricos em docs/ e no Git.

## Versão atual

**Interface v033**, sobre MAP v033 e fontes/layout v005. Rodada focada nos diálogos: **14 registros recuperados** por investigação de controles e seis origens nativas revisadas. Mantém todas as traduções anteriores, os 73 títulos da ficha, botões do cofre e FIM, além das **566 de 567 descrições traduzidas**, usadas por **925 itens**. A tabela de nomes continua com **516 registros traduzidos** e 25 pendentes. Hunter, Soldier, nomes próprios e MAIN/SUB/SE permanecem protegidos.

São **3.526 campos/ocorrências de interface** e **5.983 registros de diálogo alterados**. Restam **27 adiamentos MAP**: 19 nomes de tanques preservados e oito ocorrências nativas repetidas ainda sem contexto suficiente. A auditoria local reúne também 134 rótulos únicos de falantes em 1.527 referências, mantendo-os não editáveis. Isso não representa porcentagem de todo o jogo. O catálogo conhecido de descrições tem **99,82%** traduzido. O comando TITLE continua preservado; `%NO` e preços com `%` mantêm os bytes originais e exigem conferência específica, sem correção silenciosa.

ISO: `work/interface-v033/MetalSaga-ptbr-interface-v033.iso`. Abra **Iniciar-Teste.cmd**, que confere tamanho/hash/transações e usa inicialização limpa em vez de save state antigo. O usuário realiza os testes visuais durante a partida; verificações binárias não substituem execução no PCSX2.

- [Lote atual e limites](docs/dialogos-v033.md)
- [Plano de conclusão](docs/plano-conclusao.md)
- [Glossário](docs/glossario.md)
- [Extrator local](docs/extrator-dialogos.md)
- [Reinserção e integridade](docs/reinsercao-v004.md)

## Organização

- JOGO/: ISO original e extraídos imutáveis.
- PCSX2/ e ambiente isolado de teste: preservar BIOS, cartões e configurações.
- translations/: receitas Unicode e propostas pendentes, versionadas.
- tools/ e tests/: ferramentas locais e testes.
- docs/ e reports/: procedimentos e evidências próprias.
- work/: resultados e recursos de construção, fora do Git.
- dist/alpha-v001/: alpha permanente, somente leitura, fora da retenção.

Manter **cinco ISOs de trabalho**, as mais recentes. O construtor remove as antigas elegíveis antes de criar outra. Não apaga original, alpha, arquivos desconhecidos ou imagens com recuperação pendente. Conferir com `python tools/iso_retention.py`.

Construções novas produzem somente ISO e relatório. Receitas, fontes editáveis aprovadas, evidências e recursos necessários à reprodução são preservados. Não apagar work/ indiscriminadamente. OneDrive somente mediante pedido expresso.

Extração/reinserção são locais, sem IA ou APIs. Requerem Python; dependências gráficas de construção estão documentadas nos manuais correspondentes. Não acessar arquivos de outros projetos.
