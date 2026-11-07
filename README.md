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

**Pacote para compartilhar:** `dist/publicacao-v070/MetalSaga-PTBR-v070-Patch.zip`
(1,19 MiB). Contém patch e aplicador offline para Windows, sem ISO/BIOS.
O jogador fornece a ISO original exigida; o pacote confere origem e resultado.
[Instruções, hashes e publicação](docs/publicacao-patch-v070.md). Não houve
publicação automática do ZIP.

**Candidata final v070**, sobre MAP v048 e fontes/layout v005. Corrige os relatos de NOME/AJUSTES, Sem tanques/Sem navios com fade, Caverna desconhecida, Acampamento de mercadores, venda de equipamento, Sim/Não dos minigames, Binramen e gritos de negação. Categorias Máquinas/Veículos/Desconhecidos por extenso e Minério pequeno aplicados. Mantém Poker/Blackjack, nomes tradicionais das mãos e as demais traduções. A conferência em partida continua pendente; não é certificação de 100% do jogo.

São **633 campos de nomes de itens aplicados** (610 valores distintos), **4.666 unidades heterogêneas de interface**, **6.044 registros MAP de diálogo alterados**, 5.991 com corpo/opções modificados e 991 referências explícitas de falantes traduzidas. Os 108 nomes padrão e os rótulos de mapa adicionais são contados separadamente dessas referências. Restam 13 rótulos explícitos curtos bloqueados pela reserva de memória não comprovada. Dummy/UP/DOWN/Damage Override ficam por decisão contextual anterior. As contagens não representam porcentagem de todo o jogo.

ISO: `work/interface-v070/MetalSaga-ptbr-interface-v070.iso`. Abra **Iniciar-Teste.cmd**; **Abrir-Pasta-da-Ultima-Versao.cmd** abre a mesma pasta. Cópia solicitada na Área de Trabalho: `MetalSaga-PTBR-Candidata-Final-v070.iso`. Conferir os relatos corrigidos e as categorias nas diferentes telas. O perfil isolado histórico tem cartões de memória desativados. ISOs antigas são retiradas somente após as cópias novas conferidas, preservando receitas e relatórios.

A aprovação recebida e o relatório completo ficam em `work/revisao-armas-v001/`; resultado em `APLICACAO-ARMAS-APROVADAS.md`. As sugestões antigas continuam históricas. O pacote local v054 não inclui as correções posteriores.

**Manutenção:** `dist/manutencao-v070/MetalSaga-ptbr-manutencao-v070.iso`, cópia independente somente leitura. A nova ordem de remover as versões anteriores substitui o backup v059 após a conferência das cópias v070. Preservar a cópia de manutenção; nunca aplicar patches diretamente nela. [Procedimentos, entrega e limitações](docs/interface-v070.md).

- [Candidata final, correções e manutenção](docs/interface-v070.md)
- [Revisão dos nomes tradicionais dos jogos de cartas](docs/interface-v069.md)
- [Minigames: gráficos, instruções e catálogo de cobertura](docs/interface-v068.md)
- [Relatos da partida, diário, dança e MC Hamir](docs/interface-v067.md)
- [Tanque, locais, LOVE Machine e minigame de bebida](docs/interface-v066.md)
- [Legibilidade do crédito e abertura do e](docs/interface-v065.md)
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
