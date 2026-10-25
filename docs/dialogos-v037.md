# Diálogos v037 — revisão de funções e separadores de escolhas

**45 rótulos adicionais**, acumulando **912 / 1.527 referências** do catálogo.
São 41 referências de funções revistas por contexto e quatro recuperadas da
lista de 53 adiamentos de espaço da v036. Restam **49** dessa lista, todos msgn.
Outras 566 referências incluem nomes, profissões preservadas, marcadores e funções
ainda não selecionadas; não representam 566 traduções automaticamente necessárias.

| Tradução nova | Referências | Justificativa |
|---|---:|---|
| Musculoso | 19 | Guia e participantes da catedral; Father Muscle permanece como nome |
| Fiel dirigente | 17 | Fiel que organiza grupos, orienta iniciados e atende o líder |
| Fã de ônibus | 3 | Interlocutor interessado nas gravações dos anúncios do ônibus |
| Agente do Hunter Office | 2 | Funcionário do guichê; nome completo do estabelecimento preservado |
| Homem | 3 | Rótulos antes bloqueados por posição das opções |
| Mecânico severo | 1 | Rótulo antes bloqueado por posição das opções |

Executive Believer foi interpretado como título funcional pelo contexto de suas
falas, sem inventar uma divindade Executive. A classificação não estabelece ID
canônico nem libera títulos similares. As falas da catedral, seu humor e os nomes
Father Muscle/Gluteus Maximism continuam iguais aos da v036. Ver glossário.

Todos os 45 registros já tinham falas alteradas. Permanecem **6.024 registros MAP
com algum campo alterado**, dos quais **5.983 têm corpo/opções traduzidos**, no
catálogo de 7.231. Não contar os novos rótulos como novas falas. Os 27 adiamentos
de corpos continuam: 19 nomes N$3 preservados e oito ocorrências nativas sem contexto.

## Uso e reprodução

Abra **Iniciar-Teste.cmd**. A imagem atual é:

`work/interface-v037/MetalSaga-ptbr-interface-v037.iso`

SHA-256: `e7e65c661409946eb81b8e185c1c71478710cf1aa1538f74a04bd5fbd4c63789`

Tamanho: 1.704.427.520 bytes. Interface com os mesmos 3.526 campos, fontes/layout
v005 e título/arte v014. `Preparar-Interface.cmd` valida sem criar ISO;
`Auditar-Traducao.cmd` atualiza o catálogo local substituível em
`work/dialogos-pendencias-atual.json`. Sem IA, APIs ou rede no processamento local.

Para construir em uma pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v037.json --interface-draft translations/interface-v037.json --output work/interface-v037-reproducao --compact-output --build-iso
```

Para reproduzir a seleção em arquivos novos:

```powershell
python tools/prepare_speaker_context.py --parent translations/regiao-inicial-v036.json --output translations/regiao-inicial-v037-reproducao.json --report reports/rotulos-falantes-v037-reproducao.json
```

O preparador conserva entradas contextuais herdadas, sem substituir as políticas
anteriores. A seleção limita-se às quatro funções explicitamente revistas e às
funções antigas ainda pendentes. Não traduz nomes por heurística. Fonte dos
contextos/revisão bilíngue somente em work/; o relatório público registra IDs,
hashes e decisões. Alterações futuras nos corpos podem invalidar seus vínculos:
revisar e vincular novamente os casos afetados, sem ignorar a recusa.

## Política específica v004

`map-context-reviewed-speaker-layout-v004`, em `tools/speaker_label_review.py`,
aplicada após os três perfis de rótulos anteriores. O campo de receita é
`speaker_context_review`. Cada alvo vincula ID, hash original do registro/rótulo,
hash do registro após compilar as traduções herdadas, layout e offsets finais
explícitos. Hash integral do ELF original e sete janelas de instruções vinculados.

Três layouts neste lote:

- **38 slots originais:** apenas novos rótulos contextuais que cabem na cauda
  original. Não mudam posições nem outros bytes.
- **3 caudas por byte:** Fã de ônibus usa zeros depois do texto/opções, segundo
  o percurso já comprovado; corpo/opções continuam nas mesmas posições.
- **4 escolhas nomeadas:** as opções são deslocadas para trás, aproveitando
  zeros depois do NUL da pergunta. O início da pergunta fica intacto e as opções
  continuam alinhadas a quatro bytes; o novo rótulo termina no limite do registro.

IDs do terceiro caso: smnn 0x0BE243CC, 0x0E76E4BC, 0x0E76FAD4 e 0x10340A50.
Antes da mudança, cada um carecia de espaço depois das opções, mas tinha folga
entre pergunta e opções. O novo início das opções é
`(novo_inicio_rotulo - bytes_opcoes - 1) & ~3` e precisa ficar estritamente após
o NUL da pergunta e antes da posição antiga das opções. Se não couber, recusar.

Os bytes completos da pergunta e opções, inclusive controles, quebras, tabs e
terminadores, são comparados antes/depois. Não são abreviados, retraduzidos nem
reordenados. Cabeçalhos, tamanho/posição do registro, fronteiras SSD e extents ISO
não mudam. Somente strings e zeros dentro do mesmo registro são recompostos.
Não há expansão entre registros nem liberação geral de repack das escolhas nomeadas.

O scanner original em 0x1C6D2C..0x1C6D68 foi executado em memória sintética
para conferir a busca das opções após a pergunta, incluindo branch-likely e delay
slots. A busca do NUL da pergunta está ligada a 0x1C6CC0..0x1C6CD4 e ao helper
0x2262C8 escalar, já delimitado. Os percursos anteriores até o rótulo também são
executados antes/depois; o parse estrutural confere todos os offsets. Probes de
comprimento, pedido de alocação, cópia e getter continuam aplicados.

Isso não executa o handler completo das opções, SIMD alinhado, alocador, objetos,
retratos, GPU ou PCSX2. Não inferir validação visual ou identidade canônica de NPC.
Os nomes próprios, Hunter/Soldier e os códigos PT-BR continuam protegidos.

Os metadados/fingerprints de extração e `label.editable=false` ficam intactos.
O wrapper `compiled_dialogue_segment_offsets` registra as posições compiladas
dos segmentos destes 45 IDs; o wrapper anterior de rótulos também é acumulado.
A leitura final independente usa esses offsets. O compilador legado continua
recusando edição de rótulos. Uma falha recusa o lote inteiro; um patch por ID.
Não editar o mapa EXTRA desta política para mudar traduções históricas: revisões
editoriais futuras exigem perfil/versionamento que conserve a reprodução anterior.

## Verificação e continuidade

**64 testes distintos aprovados**: oito novos do perfil contextual, seis da v036
e 50 de auditoria, reinserção, cobertura, codec, controles, preflight, retenção e
alpha. Incluem todos os segmentos/metadados anteriores, bytes de opções movidas,
posições acumuladas, nomes proibidos, hashes/offsets/layout adulterados, duplicação,
preservações, preparação herdada e recusa pelo compilador legado. Repetições não
somadas; não houve nova fonte nem alteração de bitmap/métrica.

Comparação integral da ISO v036→v037: **633 bytes diferentes em 45 registros MAP**,
conforme `reports/interface-v037.json`.
Mudam somente os 45 registros enumerados, incluindo os deslocamentos internos
das quatro opções. Demais bytes, diretório, fontes, arte e interface idênticos.
Triagem em `reports/rotulos-falantes-v037.json` e `reports/dialogos-pendencias-v037.json`.
Preflight e iniciador em dry-run aprovados; cinco ISOs e alpha protegida mantidos.

O usuário pode conferir os quatro casos de opções em partida normal, além dos
nomes da catedral, do funcionário do Hunter Office e do fã de ônibus. Observar
se as respostas estão corretas, se avançam normalmente e se os rótulos cabem.
Não houve navegação PCSX2 nesta rodada, OneDrive ou desligamento automático.

Os 49 msgn restantes já não possuem separador adicional de opções para aproveitar.
A próxima frente precisa de revisão contextual ou nova estratégia de armazenamento
com prova própria. Não cortar falas/artigos, retirar acentos ou repetir tentativas
nos mesmos zeros inexistentes; não reinvestigar N$3 já decidido nem inventar contexto
para as oito ocorrências nativas. A ampliação do universo conhecido ainda é distinta
da porcentagem de tradução do jogo inteiro.
