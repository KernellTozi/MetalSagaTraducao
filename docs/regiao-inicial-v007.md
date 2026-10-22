# Região inicial — lote consolidado v007

O intervalo `0x1DF47F0C..0x1DF6AA20` contém 511 registros: 442 traduzidos
e 69 preservados, incluindo quatorze bloqueados. São 474 segmentos traduzidos
em 98 grupos SSD. Comparada à v006, são 67 ocorrências e 58 traduções adicionais.
Os 444 registros anteriores permanecem integralmente iguais no plano compilado.

## Conteúdo

O lote acrescenta desafios de Lloyd, Duke e Guermo, reações dos companheiros,
intervenções do bar e falas dos espectadores. Há caminhos de aceitação, recusa,
vitória e derrota; não correspondem a uma única sequência de jogo.

São 58 alvos únicos revisados e seis aliases propostos por identidade de todos
os segmentos originais. Os nomes nas strings protegidas de `msgn` permanecem
inalterados. Hunter, Soldier, punk e as expressões de riso foram mantidos.
`Ace Hunter` permanece como título; a referência adjetiva a um Hunter de elite
não estabelece uma tradução global para títulos de classificação.

As três ocorrências `map.smnn.1df674f0`, `map.smnn.1df68898` e
`map.smnn.1df69d28` ficam intactas: o papel da terceira string ainda não foi
liberado para edição. Os onze bloqueios anteriores também foram preservados.
Não houve relaxamento dos parsers, alteração de ponteiros ou ampliação de slots.

## Validação

90 testes automatizados passaram. O teste da v007 compara integralmente o
prefixo v006, as contagens e todos os segmentos não editáveis do novo recorte.
Cinco excessos de bytes foram corrigidos reformulando as frases. A compilação
final não teve recusas nem violações da política terminológica.

A construção verifica hashes, leitura de retorno, limites SSD, extents e
diferenças integrais da ISO. Todos os registros modificados usam slots, sem
realocação. Avisos conservadores de largura permanecem no relatório; métricas
em pixels e execução no PCSX2 não foram validadas nesta entrega.

## Uso local

- `Preparar-Regiao-Inicial.cmd`: compila a v007 sem gerar outra ISO.
- `Testar-Regiao-Inicial.cmd` ou `Iniciar-Teste.cmd`: abre a ISO consolidada atual.
- ISO: `work/regiao-inicial-v007/MetalSaga-ptbr-regiao-inicial-v007.iso`.
- Plano, revisão bilíngue e relatório completo: `work/regiao-inicial-v007/`.
- Evidências publicáveis: `reports/regiao-inicial-v007-validation.json`.

```powershell
python tools/build_translation_pilot.py --output work/reconstrucao-v007 --build-iso
python -m unittest discover -s tests
```

No próximo teste manual, observar falas dos desafiantes e espectadores, nomes,
opções, passagem de páginas, acentos e largura. A tipografia mantém o perfil
autorizado provisoriamente, sem nova comprovação visual. Não é necessário jogar
para alcançar todos esses eventos em uma sessão.

A retenção removeu o experimento antigo `MetalSaga-ptbr-espacamento-v003.iso`
para manter dez imagens de trabalho. Receitas, relatórios e o mesmo patch de
espaçamento nas versões consolidadas continuam preservados. O atalho histórico
`--iso spacing` exige reconstrução do experimento; o iniciador padrão abre a
v007 existente. A ISO original, BIOS, saves e configurações foram preservados.
