# MAP v042 / interface v049 — rótulos completos e revisão de redação

Rodada de 28/10/2026. Dos 49 rótulos genéricos pendentes por espaço, foram
recuperados **36**. Os **13 restantes** ficam intactos. O perfil não aumenta
registros ou SSD, não altera fontes/ELF e não abrevia funções para fazê-las caber.

| Rótulo novo | Referências |
| --- | ---: |
| Trabalhador | 11 |
| Homem | 16 |
| Transportador | 7 |
| Técnico de manutenção | 1 |
| Rapaz | 1 |

Total de referências de falantes traduzidas: **948**, antes 912, de 1.527
referências catalogadas. As 579 restantes incluem os 13 deste recorte e 566
referências fora dele, como nomes, marcadores, profissões preservadas e funções
ainda não liberadas. Não tratá-las todas como dívida de tradução automática.

MAP continua com **6.032 registros alterados**, sendo 5.991 com corpo/opções
modificados. Os 36 registros desta rodada já tinham suas falas traduzidas;
não são 36 diálogos inéditos. A interface mantém 3.848 unidades heterogêneas,
os 541 nomes de itens e todos os gráficos da v048.

## Investigação e decisão

Os 49 casos são `msgn`, distribuídos em 31 SSD. Faltavam de um a quatro bytes
depois do corpo traduzido. A continuação dos perfis de cauda v002/v003 e das
escolhas nomeadas v004, sem outra mudança, não os recupera.

O levantamento `reports/rotulos-espaco-investigacao-v005.json` procurou apenas
padding final, além do NUL obrigatório, em outros `msg/msgn` do mesmo SSD.
Encontrou candidatos para quatro casos; um dos blocos contém somente o próprio
registro. **Não é um censo de todas as folgas internas**: não examina todos os
separadores ou outros layouts, nem prova que comandos possam ser movidos.
Esses zeros não foram promovidos a espaço livre e nenhum limite foi ampliado.

Em 36 falas, uma revisão natural libera espaço suficiente, mantendo sentido,
contexto, tom, artigos, acentos e a sequência de controles. Exemplos de redação:

- “Vou saborear a bebida.” → “Vou curtir a bebida.”, no agradecimento por bebida.
- “Muito obrigado!” → “Valeu mesmo!”, no mesmo registro informal.
- “...Wow, convencido!” → “...Wow, fechado!”, após o discurso de adesão da
  catedral. O personagem aceita a proposta; não chama o interlocutor de
  convencido. O contexto vizinho foi conferido, sem alterar as outras falas.

As decisões completas ficam em `translations/rotulos-redacao-v005.json`.
São 120 bytes a menos nos corpos somados, por substituição de redação completa,
não corte de strings. Nenhum artigo foi retirado para fechar o orçamento.
Não foi criado um compressor textual ou um algoritmo de tradução automática.

## Mecanismo seguro

Política opt-in `map-reviewed-body-and-complete-speaker-tail-v005`, em
`tools/speaker_body_review.py`, vinculada por `speaker_body_review` ao manifesto
`translations/rotulos-espaco-v005.json`. Pais vinculados por hash: MAP v041 e
interface v048. O payload autoral dos 36 IDs também possui hash fixo; não editar
os textos silenciosamente para alterar reproduções históricas.

1. Reproduzir o pai com todos os mecanismos antigos, inclusive os oito avisos
   Erro. e as 912 referências de falantes já traduzidas.
2. Compilar cada corpo revisto pelo reinseridor histórico, mantendo o rótulo
   protegido nessa primeira etapa. Os 36 registros são slots `msgn`, sem
   comandos dinâmicos novos. Hashes, capacidades, codec PT-BR, terminadores,
   controles e o parse estrutural são verificados.
3. Reaproveitar somente os zeros que passam a existir depois do NUL do corpo,
   usando o posicionamento de cauda já comprovado. O rótulo completo termina
   dentro do mesmo registro; o corpo continua em `registro+32`.
4. Executar os scanners escalares originais até o rótulo e as provas já
   existentes de comprimento, alocação, cópia/getter e resíduos de alinhamento.
5. Conferir os dois textos, cabeçalho e tamanho, e reconstruir o registro por
   parser independente com shadow neutro para os pares PT-BR.

Os fingerprints e offsets de extração continuam originais, com
`label.editable=false`. As posições finais ficam nos wrappers
`compiled_speaker_label_offsets` e `compiled_dialogue_segment_offsets`.
Não há liberação geral do reinseridor legado para mudar nomes próprios.
As duas referências por alias continuam vinculadas aos mesmos pais; foi
conferido que nenhum alias fora dos 36 muda de valor.

Uma falha bloqueia o lote inteiro. O perfil não reutiliza cabeçalhos,
parâmetros, padding externo, outros registros, fontes ou código do jogo.
Os probes não executam o renderizador completo, SIMD alinhado, objetos,
retratos ou PCSX2. Não equivalem a validação visual desses contextos.

## O que continua bloqueado

Os 13 IDs e hashes estão no campo `remaining` do manifesto. Incluem vocalizações
de gato/cão, silêncio, brindes, interjeições e formulações curtas como os
agradecimentos com baby e a citação sobre gelo. Suas falas e seus rótulos
permanecem byte a byte iguais aos da v048.

Não foram selecionadas revisões equivalentes que cumprissem simultaneamente
o orçamento e a preservação dessas formulações. Isso não significa impossibilidade
teórica de tradução. Significa que os mecanismos atuais não acomodam os rótulos
completos sem tocar nessas falas. Uma próxima investigação pode examinar outro
armazenamento ou reconstrução limitada com provas próprias; não voltar a
procurar indefinidamente os mesmos zeros nem cortar sons/bordões para inflar
a contagem. Alterar fronteiras de registros/SSD ou criar redirecionamento no
ELF exige evidência adicional e perfil separado.

Os 19 adiamentos do catálogo de corpos continuam sendo nomes de tanques
preservados. Não se somam nem se confundem com estes 13 rótulos. Os oito avisos
nativos continuam resolvidos; o painel japonês dos cães permanece excluído.
As 16 revisões de itens e a revisão contextual/visual em partida normal seguem
em filas distintas. Sinais editoriais do auditor não são traduções pendentes
obrigatórias confirmadas.

## Validação e entrega

- **190 testes passaram**, incluindo 12 novos e os testes históricos dos
  rótulos, caudas, escolhas, codec nativo, fontes e políticas de preservação.
- Delta integral v048 → v049: **843 bytes em 36 registros MAP**, todos previstos.
  Os demais bytes, inclusive os 13 casos preservados, ELF, fontes, gráficos,
  diretório, extents e tamanho da ISO são idênticos.
- Zero avisos de largura pelo compilador de corpos neste lote. Isso não
  confirma clipping/espacamento no renderizador; conferir durante a partida.
- Auditoria de nomes: 65 usos classificados para preservação, zero sem decisão.
- Preflight integral de tamanho/hash/transações aprovado; cinco ISOs de trabalho
  e alpha independente conferidos. Originais intactos; sem OneDrive.
- Nenhum PCSX2 foi executado. Não exigir alcançar cada ocorrência agora.

ISO: `work/interface-v049/MetalSaga-ptbr-interface-v049.iso`, 1.704.427.520 bytes.
SHA-256: `a22abc7d29ac8f41453cd0fbbbc03d55f9fe7282208c0943e7d22ed4e239941d`.
Relatórios em `reports/interface-v049.json` e `reports/interface-v049-delta.json`.

Abra **Iniciar-Teste.cmd**. **Preparar-Interface.cmd** valida v049/MAP v042 sem
gerar outra ISO; **Auditar-Traducao.cmd** atualiza as pendências locais da v049.
Em partida normal, conferir rótulos completos, acentos, avanço das falas e
quebras de página, especialmente nos brindes e serviços. Fontes/layout v005
e o processo de inicialização limpa continuam preservados.

Reprodução local, sem IA ou APIs e usando novas pastas/arquivos de saída:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v042.json --interface-draft translations/interface-v049.json --compact-output --build-iso --output work/minha-v049
python tools/speaker_body_review.py --survey-output work/levantamento-caudas-v005.json
python -m unittest discover -s tests -p test_speaker_body_review.py
```

O segundo comando reproduz o levantamento restrito sobre o pai v041; não
modifica nem autoriza edição do jogo. Sem desligamento solicitado nesta rodada.
