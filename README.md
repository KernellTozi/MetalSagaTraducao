# Metal Saga — tradução PT-BR para PS2

Tradução dos recursos do jogo original para execução no PCSX2, independente da recompilação nativa. Não distribui ISO, originais, BIOS ou emulador.

## O que abrir

| Arquivo na raiz | Para que serve |
|---|---|
| **Iniciar-Teste.cmd** | Abre a ISO traduzida atual |
| Preparar-Interface.cmd | Valida a receita atual, sem criar outra ISO |
| Extrair-Dialogos.cmd | Extrai o catálogo local de diálogos |
| Reinserir-Dialogos.cmd | Reinserção e simulação de lotes |
| Auditar-Traducao.cmd | Atualiza as pendências de diálogos e confere a situação das 16 revisões de nomes |

Atalhos duplicados e de experimentos antigos foram removidos. As ferramentas continuam em tools/, com procedimentos históricos em docs/ e no Git.

## Versão atual

**Interface v055**, sobre MAP v044 e fontes/layout v005. Corrige **14 rótulos da batalha real**, em dois atlas comprimidos de MMBATTLE.BIN. FBS_DATA era outro conjunto de gráficos; o usuário havia aberto corretamente a v054. MAIN/SUB/SE, ícones, retratos, fontes e todas as traduções anteriores foram preservados.

São **3.862 unidades heterogêneas de interface**, **6.044 registros MAP alterados**, 5.991 com corpo/opções modificados, 991 referências de falantes traduzidas e **541 nomes de itens aplicados**. Permanecem 13 rótulos bloqueados no recorte de espaço, 523 outras referências que incluem nomes/termos preservados e 19 adiamentos de nomes de tanques. Essas contagens não representam porcentagem de todo o jogo.

ISO: `work/interface-v055/MetalSaga-ptbr-interface-v055.iso`. Abra **Iniciar-Teste.cmd**. Integridade e delta integral verificados; a aparência dos novos gráficos depende do teste visual do usuário. O perfil isolado histórico tem cartões de memória desativados.

Foi preparada uma revisão de **175 armas**, com anexo de 15 munições, em `work/revisao-armas-v001/ARMAS-PARA-REVISAR.md`. As novas sugestões aguardam revisão humana e não foram aplicadas. Para regenerar: `python tools/weapon_name_review.py`; revisões locais diferentes são preservadas. O pacote local v054 é histórico e não contém os gráficos v055.

- [Lote atual e limites](docs/interface-v055.md)
- [Revisão das armas](docs/revisao-armas-v001.md)
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
- dist/alpha-v001/: alpha permanente, somente leitura, fora da retenção.

Manter **cinco ISOs de trabalho**, as mais recentes. O construtor remove as antigas elegíveis antes de criar outra. Não apaga original, alpha, arquivos desconhecidos ou imagens com recuperação pendente. Conferir com `python tools/iso_retention.py`.

Construções novas produzem somente ISO e relatório. Receitas, fontes editáveis aprovadas, evidências e recursos necessários à reprodução são preservados. Não apagar work/ indiscriminadamente. OneDrive somente mediante pedido expresso.

Extração/reinserção são locais, sem IA ou APIs. Requerem Python; dependências gráficas de construção estão documentadas nos manuais correspondentes. Não acessar arquivos de outros projetos.
