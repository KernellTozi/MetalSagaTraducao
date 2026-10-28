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

**Interface v047**, sobre MAP v040 e fontes/layout v005. Última rodada: **cinco painéis de instruções de minigames e três rótulos de pintura**, preservando os seis botões anteriormente aprovados. Hunter, Soldier, nomes próprios, MAIN/SUB/SE, pôsteres Wanted e títulos decorativos permanecem protegidos.

São **3.848 unidades de interface** (métrica heterogênea que inclui painéis completos) e **6.024 registros MAP alterados**, sendo 5.983 com corpo/opções modificados. Há **541 nomes de itens aplicados**, zero pendentes naquele recorte genérico e 500 preservados; 16 revisões editoriais anteriormente bloqueadas continuam separadas. Restam oito ocorrências MAP nativas sem contexto, 49 rótulos sem orçamento e um painel japonês de regras sem uso demonstrado na edição inglesa. Isso não representa porcentagem de todo o jogo.

ISO: `work/interface-v047/MetalSaga-ptbr-interface-v047.iso`. Abra **Iniciar-Teste.cmd**, que confere tamanho/hash/transações e usa inicialização limpa em vez de save state antigo. O usuário realiza os testes visuais durante a partida; 133 testes automatizados e a comparação integral de ISOs não substituem execução no PCSX2.

- [Lote atual e limites](docs/interface-v047.md)
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
