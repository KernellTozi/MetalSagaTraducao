# Lote ampliado v015

## Escopo e ganho efetivo

O recorte passa a `0x169B91DC..0x1FF30844`, acrescentando oitocentas ocorrências,
o dobro da ampliação v014. Foram revisados 469 alvos próprios, trezentas
reutilizações por identidade de todos os segmentos originais e 31 bloqueios.
Pausas, nomes, latidos e registros preservados não entram no ganho de traduções.

| Lote | Registros no recorte | Registros traduzidos | Segmentos traduzidos |
| --- | ---: | ---: | ---: |
| v014 | 1.963 | 1.572 | 1.652 |
| v015 | 2.763 | 2.165 | 2.275 |

São **593 registros traduzidos adicionais**, contra 331 na rodada anterior.
O total corresponde a aproximadamente 29,94% dos 7.231 registros textuais
catalogados no MAP.MCT. Não é uma medição por palavras, apenas de diálogos ou
da tradução completa do jogo. O nome histórico do lote não significa cobertura
integral de uma região: o intervalo inclui diferentes cenas, variantes e serviços.

Os 1.963 registros anteriores permanecem iguais em texto e metadados. O teste
compara a lista inteira anterior com o sufixo da lista nova, após os oitocentos
registros acrescentados. Não houve deslocamento físico de registros.

Dos 598 registros sem alteração, 120 são adiamentos. Os 31 novos casos são:

- Quinze com terceira string sem papel liberado para edição.
- Quatorze com controles opacos.
- Dois que reúnem ambas as condições.

Não houve redução das verificações para liberar esses casos. Permanecem em inglês
até existir evidência suficiente para a edição segura.

## Cenas e critérios de tradução

| Intervalo do novo recorte | Conteúdo e decisões |
| --- | --- |
| `0x169B91DC..0x169C4B1C` | Father Muscle, sermão, treino, teste de dirigentes e Marco/Elena. Conservar a falsa cordialidade do culto, a sátira muscular e a mudança para ameaças aos apóstatas |
| `0x176A601C..0x176AB7A4` | Caverna e sequência repetida de desafios contra procurados. Reutilizar somente mensagens idênticas e manter nomes dos adversários |
| `0x1773EACC..0x177555BC` | Lorelei Bay, serviços, rumores, gangues, Oliver, Marilyn Grey, reparos, memória e variantes das conversas. Manter gagueira, fala estrangeira, impaciência profissional e pesar nas respectivas cenas |
| `0x1857C10C..0x1857D73C` | Ruínas submersas e acesso por escada. Preservar instruções de veículos e alternativas de interação |
| `0x19F521AC..0x19F589AC` | Laboratório, cães, avisos, notas de pesquisa e exploradores. Manter latidos, números das unidades e fragmentação das notas |
| `0x1AEFD0DC..0x1C649EA0` | Veículo enterrado, acampamento atacado, intervenção na batalha, Rosa e Mosquito, ruínas e desafio de Man o' War. Distinguir ameaça, deboche e cortesia do duelo |

As sequências e respostas foram lidas junto dos alvos reutilizados. A identidade
binária permite sugerir reutilizações, mas não prova por si só o mesmo tom.
Falantes sem rótulo comprovado continuam inferidos do contexto, sem alegar
identificação automática de retratos ou de todas as condições do roteiro.

Gluteus Maximism, Father Muscle, St. Arnold e Turboflex ficam preservados.
Muscle Cathedral recebe Catedral Muscular; executive believer, fiel dirigente.
Preservar os nomes não exige conservar cargos genéricos em inglês: Professor Grey
recebe Professora Grey. O glossário detalha os tons de Oliver e Marilyn Grey.

As direções de caça conservam noroeste junto às montanhas e deserto ao sul.
Tin Tunas, Mosquito, Armored 8-Wheeler, Manhunter e Alpha Unit não foram renomeados.
Não houve tradução em massa de tabelas de itens, armas ou inimigos.

O final do culto mantém seis libras de carne e cinco milhas; não houve conversão
arredondada das unidades. A nota sobre pombos mantém 300 objetos, e as unidades
do laboratório continuam na ordem 1, 3, 4, 2.

Na reação curta `map.msg.1afd9694`, `Não...` ocupa exatamente sete bytes e mantém
o acento e a hesitação. A exclamação foi retirada para caber, sem remover artigos,
alterar o slot ou introduzir outra exceção ASCII. O único `nao` sem acento continua
sendo o registro anteriormente autorizado `map.msg.1df8bec0`.

## Verificação e limites

109 testes automatizados passaram. O teste novo reproduz o recorte de oitocentos
registros, confere a preservação integral da v014, bloqueios, aliases, nomes,
direções, números e a exclusividade da exceção ASCII. A suíte também verifica
extração, reinserção, controles, fontes, instruções do patch de espaçamento,
construção e retenção isolada de ISOs.

As recusas das primeiras revisões foram corrigidas nos textos, preservando a
quantidade e a ordem de quebras, páginas, comandos e spans vazios. A compilação
final não tem recusas nem violações da política terminológica. Os registros
modificados usam slots existentes; não houve realocação de registros ou extents.

A ISO tem 1.704.427.520 bytes. A comparação integral confirmou que os 169.631
bytes diferentes correspondem exatamente aos patches previstos, incluindo fontes
e espaçamento, e que o diretório do disco permanece idêntico. O lote abrange
563 grupos SSD. O relatório mantém 261 avisos conservadores de largura.

A validação de largura continua conservadora e não mede pixels. Nenhum teste
binário substitui a leitura na tela. Esta versão não foi executada no PCSX2 pelo
Codex; a avaliação visual permanece pendente. No próximo teste manual, observar
uma conversa disponível de Lorelei Bay ou uma das cenas do novo recorte, além
das falas iniciais: acentos, alinhamento, largura, passagem de páginas, escolhas
e nomes dinâmicos. Não é necessário alcançar todas as variantes numa sessão.

## Reprodução local

- `Preparar-Regiao-Inicial.cmd`: compila e valida a v015 sem gerar nova ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada atual.
- ISO: `work/regiao-inicial-v015/MetalSaga-ptbr-regiao-inicial-v015.iso`.
- Plano, revisão bilíngue e relatório: `work/regiao-inicial-v015/`.
- Metadados próprios: `reports/regiao-inicial-v015-validation.json`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v015.json --output work/reconstrucao-v015 --build-iso
python -m unittest discover -s tests
```

Preparação reproduzível do intervalo, sem tradução automática nem ISO:

```powershell
python tools/prepare_translation_lot.py --parent translations/regiao-inicial-v014.json --start-offset 169b91dc --lot-id regiao-inicial-v015 --output work/preparacao-v015-repro
```

A retenção removeu a ISO experimental v008 para manter o limite de dez imagens.
Sua receita e relatórios permanecem; o atalho histórico exige reconstrução se for
usado novamente. A v014 continua disponível. Originais, BIOS, saves e configurações
foram preservados.

SHA-256 da ISO:
`122544ce539707fc39f103620312c5fb8d3a504c93c1cb036054eff49214c1f2`.
