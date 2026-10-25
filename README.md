# Metal Saga — tradução PT-BR para PS2

Tradução dos recursos do jogo original para execução no PCSX2, independente da recompilação nativa. Não distribui ISO, originais, BIOS ou emulador.

## O que abrir

| Arquivo na raiz | Para que serve |
|---|---|
| **Iniciar-Teste.cmd** | Abre a ISO traduzida atual |
| Preparar-Interface.cmd | Valida a receita atual, sem criar outra ISO |
| Extrair-Dialogos.cmd | Extrai o catálogo local de diálogos |
| Reinserir-Dialogos.cmd | Reinserção e simulação de lotes |
| Auditar-Traducao.cmd | Confere a cobertura dos diálogos |

Atalhos duplicados e de experimentos antigos foram removidos. As ferramentas continuam em tools/, com procedimentos históricos em docs/ e no Git.

## Versão atual

**Interface v025**, sobre MAP v030 e fontes/layout v005. Acrescenta 17 nomes de equipamentos, acessórios, componentes genéricos e habilidades, mantendo os identificadores próprios e os textos anteriores. São **516 registros de nomes traduzidos** e **541 descrições**, usadas por 889 IDs. Nomes únicos, motores, LOVE machine, personagens e tanques continuam preservados; atributos, preços e IDs não mudam.

São **2.121 campos/ocorrências de interface** acumulados e 5.892 registros de diálogo alterados. Isso não representa porcentagem de todo o jogo. O pool conhecido de descrições mantém 95,41% dos 567 alvos traduzidos: 24 adiados por espaço, um por controle e um marcador original. O novo perfil de nomes permite no máximo os 16 bytes observados no original, usando somente o preenchimento zerado do próprio registro. Há validações visuais pendentes.

ISO: `work/interface-v025/MetalSaga-ptbr-interface-v025.iso`. Abra **Iniciar-Teste.cmd**, usando inicialização limpa em vez de save state antigo. O usuário realiza os testes visuais durante a partida; verificações binárias não substituem execução no PCSX2.

- [Lote atual e limites](docs/interface-v025.md)
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
