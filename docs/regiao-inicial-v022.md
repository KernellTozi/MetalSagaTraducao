# Revisão consolidada v022

## Resultado

Esta versão mantém o catálogo completo conhecido de 7.231 registros do MAP.MCT
e revisa 31 títulos genéricos preservados. São 5.667 registros alterados, contra
5.636 na v021: ganho de 31 registros, sem aumentar artificialmente elegibilidade.
São 5.961 segmentos traduzidos e aproximadamente 78,37% dos registros catalogados.
A proporção não mede palavras nem representa a tradução completa do jogo.

As receitas anteriores permanecem intactas. O filho v022 altera cinco raízes de
tradução e suas ocorrências idênticas, com os 31 IDs explicitamente listados em
`reviewed_changes`. A regressão verifica todos os demais registros por identidade
e compara metadados dos títulos depois de retirar somente a tradução revisada.

| Título | Tradução | Ocorrências |
| --- | --- | ---: |
| Transport Pod | Transportador | 19 |
| Trader Camp | Acampamento | 9 |
| Lake Bridge | Ponte do lago | 1 |
| Junk Mountain | Montanha de Sucata | 1 |
| Impound Lot | Apreensões | 1 |

São títulos genéricos de dispositivos ou locais. Não houve alteração de nomes
de cidades, personagens, tanques ou equipamentos únicos. Traços decorativos
foram retirados quando necessário para manter português natural e o slot original.

## Investigação e auditoria

Os 349 bloqueios permanecem. A auditoria agora discrimina família, motivos e
sintaxes opacas por spans do parser. São 223 casos apenas de controles opacos,
91 apenas da terceira string, 21 com ambos e 14 de bytes nativos. A triagem
reproduz as contagens já conhecidas, sem sugerir que sejam novas descobertas.

A investigação no ELF confirmou o caminho da terceira string de escolhas
nomeadas até o método de rótulo. Foram conferidos 112 registros, 83 smnn e 29
2snm. Desses, 91 não têm outros bloqueios conhecidos. Isso prepara uma política
específica de slots fixos; não libera edição nesta versão. Evidências, comandos
e limites estão em `docs/escolhas-nomeadas-investigacao-v001.md`.

A auditoria final separa 5.667 alterados, 349 adiados, 599 de controles/pontuação,
458 sugestões de nomes/expressões e 158 preservados a revisar. Os candidatos não
são aprovados automaticamente. A ferramenta local continua em
`Auditar-Traducao.cmd`; os detalhes com textos ficam somente em `work/`.

## Integridade e teste manual

A compilação revisada tem zero recusas e zero violações de terminologia. Os
slots, cabeçalhos, offsets, blocos SSD e extents permanecem invariáveis. Há 1.595
grupos SSD e 619 avisos conservadores de largura, sem medição em pixels.
A exceção ASCII `nao` permanece apenas em `map.msg.1df8bec0`.

A suíte completa passou: 125 testes em 422,049 segundos. Ela inclui a
comparação integral dos registros não revisados, o detalhamento dos bloqueios e
a evidência de escolhas nomeadas, com recusa de executável alterado.

Fontes v002 e espaçamento v003 continuam assumidos provisoriamente corretos
pelo usuário. Esta versão não foi executada no PCSX2 pelo Codex. No teste manual,
observar os títulos Transportador, Acampamento e Montanha de Sucata quando os
locais estiverem acessíveis, verificando acentos, largura e enquadramento.

## Uso

- `Preparar-Regiao-Inicial.cmd`: recompila e valida a v022 sem gerar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a versão atual.
- ISO: `work/regiao-inicial-v022/MetalSaga-ptbr-regiao-inicial-v022.iso`.
- Revisão, plano e relatório: `work/regiao-inicial-v022/`.
- Auditoria: `Auditar-Traducao.cmd`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v022.json --output work/reconstrucao-v022 --build-iso
python tools/investigate_named_choices.py --output work/escolhas-nomeadas-repro.json
python -m unittest discover -s tests
```


## Construção e retenção verificadas

A ISO possui 1,704,427,520 bytes. A comparação integral confirmou que os
468,143 bytes diferentes correspondem exatamente aos patches
previstos, incluindo fontes e espaçamento. O diretório do disco permaneceu
idêntico. Originais, BIOS, saves e configurações não foram alterados.

SHA-256: `dd6f7f7ba0374591ab5311a5d1f7570693e345f0aae86612f5839940011f6650`.

A auditoria final está em `work/auditoria-v022-final/`, com resumo próprio em
`reports/regiao-inicial-v022-coverage.json`. As evidências do executável ficam
em `reports/named-choice-evidence-v001.json`.

A retenção removeu a ISO v012, a mais antiga elegível. Receitas e relatórios
permanecem. Há dez imagens de trabalho, v013 a v022; a original em `JOGO/`
fica fora da contagem. O atalho histórico v012 exige reconstrução.
