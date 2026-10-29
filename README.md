# Metal Saga — tradução PT-BR para PS2

Tradução dos recursos do jogo original para execução no PCSX2, independente da recompilação nativa. Não distribui ISO, originais, BIOS ou emulador.

## O que abrir

| Arquivo na raiz | Para que serve |
|---|---|
| **Iniciar-Teste.cmd** | Abre a ISO traduzida atual |
| Preparar-Interface.cmd | Valida a receita atual, sem criar outra ISO |
| Extrair-Dialogos.cmd | Extrai o catálogo local de diálogos |
| Reinserir-Dialogos.cmd | Reinserção e simulação de lotes |
| Auditar-Traducao.cmd | Atualiza as pendências de diálogos e o diagnóstico dos 16 nomes bloqueados |

Atalhos duplicados e de experimentos antigos foram removidos. As ferramentas continuam em tools/, com procedimentos históricos em docs/ e no Git.

## Versão atual

**Interface v050**, sobre MAP v043 e fontes/layout v005. Última rodada: **32 rótulos de função do grupo BB**, incluindo os numerados e o ex-integrante. Soldado BB traduz Trooper; a classe Soldier continua preservada. Os corpos e opções permanecem iguais à v049. Hunter, nomes próprios, MAIN/SUB/SE, pôsteres Wanted e títulos decorativos continuam protegidos. O painel japonês do minigame de cães permanece original por decisão do usuário.

São **3.848 unidades de interface** (métrica heterogênea que inclui painéis completos) e **6.043 registros MAP alterados**, sendo 5.991 com corpo/opções modificados. Os novos rótulos não são novos corpos traduzidos. Há **980 referências de falantes traduzidas**, 13 bloqueadas no recorte de espaço e outras 534 fora dessa seleção, incluindo nomes e termos preservados. Mantêm-se **541 nomes de itens aplicados**, 16 revisões editoriais bloqueadas e a revisão em partida normal. Os oito adiamentos nativos foram resolvidos; os 19 restantes são nomes de tanques preservados. Essas contagens não representam porcentagem de todo o jogo.

ISO: `work/interface-v050/MetalSaga-ptbr-interface-v050.iso`. Abra **Iniciar-Teste.cmd**, que confere tamanho/hash/transações e usa inicialização limpa em vez de save state antigo. O usuário realiza os testes visuais durante a partida; 199 testes automatizados e a comparação integral de ISOs não substituem execução no PCSX2.

- [Lote atual e limites](docs/dialogos-v043.md)
- [Plano de conclusão](docs/plano-conclusao.md)
- [Investigação dos nomes bloqueados](docs/capacidade-nomes-v001.md)
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
