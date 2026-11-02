# Metal Saga — tradução PT-BR para PS2

Tradução dos recursos do jogo original para execução no PCSX2, independente da recompilação nativa. Não distribui ISO, originais, BIOS ou emulador.

## O que abrir

| Arquivo na raiz | Para que serve |
|---|---|
| **Iniciar-Teste.cmd** | Abre a ISO traduzida atual |
| **Abrir-Pasta-da-Ultima-Versao.cmd** | Abre no Explorador a pasta da mesma versão usada pelo iniciador |
| Preparar-Interface.cmd | Valida a receita atual, sem criar outra ISO |
| Extrair-Dialogos.cmd | Extrai o catálogo local de diálogos |
| Reinserir-Dialogos.cmd | Reinserção e simulação de lotes |
| Auditar-Traducao.cmd | Atualiza as pendências de diálogos e confere a situação das 16 revisões de nomes |

Atalhos duplicados e de experimentos antigos foram removidos. As ferramentas continuam em tools/, com procedimentos históricos em docs/ e no Git.

## Versão atual

**Interface v064**, sobre MAP v045 e fontes/layout v005. Traduz **VENDAS**, recria **CARREGAR** e separa o crédito do botão: **tradução: Kernell Tozi** passa ao recurso do bloco oficial. Preserva integralmente os itens, falas e demais traduções v063. A troca para Minério pequeno continua aguardando liberação. Aparência, animação e alcance das novas telas aguardam conferência em partida.

São **633 campos de nomes de itens aplicados** (610 valores distintos), **4.363 unidades heterogêneas de interface**, **6.044 registros MAP de diálogo alterados**, 5.991 com corpo/opções modificados e 991 referências explícitas de falantes traduzidas. Os 108 nomes padrão e os rótulos de mapa adicionais são contados separadamente dessas referências. Armas aprovadas e Mundo aberto permanecem iguais; 13 rótulos explícitos curtos e a ampliação das categorias abreviadas continuam pendentes. As contagens não representam porcentagem de todo o jogo.

ISO: `work/interface-v064/MetalSaga-ptbr-interface-v064.iso`. Abra **Iniciar-Teste.cmd**; **Abrir-Pasta-da-Ultima-Versao.cmd** abre a mesma pasta. Conferir título, crédito e fade, VENDAS e os elementos v063/v062 ainda pendentes. O perfil isolado histórico tem cartões de memória desativados. Backup v059 protegido; as antigas cópias de trabalho e de investigação v059 foram removidas pela retenção, preservando o backup independente e todos os relatórios/receitas.

A aprovação recebida e o relatório completo ficam em `work/revisao-armas-v001/`; resultado em `APLICACAO-ARMAS-APROVADAS.md`. As sugestões antigas continuam históricas. O pacote local v054 não inclui as correções posteriores.

**Backup atual:** `dist/backup-v059/MetalSaga-ptbr-backup-v059.iso`, cópia independente somente leitura, com o mesmo hash da v059. Por nova ordem do usuário, foram retiradas as ISOs antigas v055–v058 e a antiga alpha, preservando receitas/relatórios. A base isolada v059 da investigação foi removida pela retenção ao construir v064; pode ser recriada a partir do backup protegido quando necessário. [Estado do método e limites](docs/falantes-lookup-v001.md).

- [Carregar, Vendas e crédito no bloco oficial](docs/interface-v064.md)
- [Capturas, Renascimento, minerais e Primeiro golpe](docs/interface-v063.md)
- [Reboque, habilidades, música e alinhamento dos resultados](docs/interface-v062.md)
- [Menus e avisos observados durante a partida](docs/interface-v061.md)
- [Nomes padrão de NPCs e alinhamento de Sim/Não](docs/interface-v060.md)
- [Efeitos de batalha, desenho e pendências](docs/interface-v059.md)
- [Lote de armas aplicado e limites](docs/interface-v058.md)
- [Satcom e Mundo aberto](docs/interface-v056.md)
- [Batalha corrigida na v055](docs/interface-v055.md)
- [Pendências atuais e conferência em partida](docs/pendencias-atuais.md)
- [Patch local: gerar, aplicar e verificar](docs/patch-local-v001.md)
- [Plano de conclusão](docs/plano-conclusao.md)
- [Investigação dos nomes bloqueados](docs/capacidade-nomes-v001.md)
- [Buffers e expansão dos nomes](docs/buffers-nomes-v002.md)
- [Entradas, emissor e páginas com nomes](docs/fluxo-nomes-v003.md)
- [Origens dos nomes e formatador adicional](docs/fontes-nomes-v005.md)
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
- dist/backup-v059/: backup atual somente leitura, fora da retenção. A alpha antiga foi substituída por ordem do usuário.

Manter **cinco ISOs de trabalho**, as mais recentes. O construtor remove as antigas elegíveis antes de criar outra. Não apaga original, backup protegido, arquivos desconhecidos ou imagens com recuperação pendente. Conferir com `python tools/iso_retention.py`.

Construções novas produzem somente ISO e relatório. Receitas, fontes editáveis aprovadas, evidências e recursos necessários à reprodução são preservados. Não apagar work/ indiscriminadamente. OneDrive somente mediante pedido expresso.

Extração/reinserção são locais, sem IA ou APIs. Requerem Python; dependências gráficas de construção estão documentadas nos manuais correspondentes. Não acessar arquivos de outros projetos.
