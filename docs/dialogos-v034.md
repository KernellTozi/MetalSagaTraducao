# Diálogos v034 — funções dos falantes

Traduzidos **553 rótulos em 72 funções/estabelecimentos**, preservando todos os
corpos, opções, comandos e nomes próprios da v033. Exemplos: Guard → Guarda,
Mechanic → Mecânico, Old Woman → Idosa, Railroad Staff → Ferroviário,
Part Shop → Autopeças. Hunter, Soldier, Punk, personagens, facções e marcadores
não receberam substituições automáticas.

| Medida | Resultado |
|---|---:|
| Referências a rótulos no catálogo | 1.527 |
| Valores originais distintos | 134 |
| Rótulos traduzidos nesta rodada | **553** |
| Funções originais distintas traduzidas | **72** |
| Funções revistas adiadas por capacidade | **367 referências** |
| Referências fora da seleção editorial | **607** |
| Registros MAP com algum campo alterado | **5.999 / 7.231** |
| Registros com corpo/opções traduzidos | **5.983**, sem aumento |
| Novos registros alterados somente pelo rótulo | **16** |
| Adiamentos técnicos de corpos | **27**, sem mudança |

Os demais 537 rótulos pertencem a registros que já tinham falas traduzidas.
Não contar os 553 campos como 553 novas falas. Dos 27 adiamentos, 19 são nomes
N$3 deliberadamente preservados e oito são ocorrências nativas de contexto
desconhecido. As 607 referências excluídas incluem nomes, profissões preservadas,
marcadores e rótulos ainda não selecionados; não são 607 traduções obrigatórias.

## Uso e reprodução

Abra **Iniciar-Teste.cmd**. A imagem atual é:

`work/interface-v034/MetalSaga-ptbr-interface-v034.iso`

SHA-256: `13ecb3029d86b9d85b6dddb738816e646cb112715f5be99463cb5e5026daa2be`

Tamanho: 1.704.427.520 bytes. Interface: 3.526 campos preservados, com título
v014 e layout PT-BR v005. `Preparar-Interface.cmd` valida sem criar ISO;
`Auditar-Traducao.cmd` recompila a receita vinculada e substitui somente
`work/dialogos-pendencias-atual.json`, separando rótulos e corpos traduzidos.

Para construir em uma pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v034.json --interface-draft translations/interface-v034.json --output work/interface-v034-reproducao --compact-output --build-iso
```

A seleção pode ser reproduzida a partir da v033, com nomes de saída novos:

```powershell
python tools/prepare_speaker_labels.py --parent translations/regiao-inicial-v033.json --output translations/regiao-inicial-v034-reproducao.json --report reports/rotulos-falantes-v034-reproducao.json
```

Essa ferramenta aplica somente o mapa editorial explícito em
`tools/speaker_labels.py`. Não classifica/traduz nomes por heurística, não usa
IA/APIs e não deve ser usada para substituir silenciosamente receitas existentes.

## Evidência técnica e limites

Nova política opt-in **map-generic-speaker-label-fixed-slots-v001**, separada
da política v014 dos corpos. Todas as posições abaixo são offsets no arquivo
ELF original, com VA = offset + 0xFF000. Hash integral do ELF e sete janelas
de instruções são vinculados à receita.

- Calls de msgn em 0x1C6548 e smnn/2snm em 0x1C6DE0 encaminham o ponteiro
  do rótulo ao setter 0x1FD968. A terceira string já está identificada pelo parser.
- O setter retém a origem e chama strlen em 0x2266CC. O caminho escalar original
  em 0x2267F0 conta bytes até NUL, inclusive pares PT-BR, sem presumir UTF-8.
- Em 0x1FD9E0..0x1FDA18 foi executado o cálculo original do pedido ao alocador:
  **(comprimento_em_bytes + 4) & ~3**, com alinhamento 16. Há espaço para NUL.
  A arena foi fornecida em memória sintética; o alocador real foi substituído.
- Em 0x1FDA18..0x1FDA28 foi executado o encaminhamento da origem/destino e
  armazenamento do destino no campo objeto+0x34. A cópia original em 0x2265B4
  foi executada pelo ramo escalar de 0x2266AC, com ponteiros sintéticos desalinhados.
  Confirmados bytes PT-BR+NUL, origem intacta e sentinelas/padding intactos.
- O getter 0x1FDB00 devolve esse ponteiro quando o campo +0x34 não é zero.
  O ramo de fallback para nome de entidade não foi usado no probe. Não confundir
  esse getter com 0x1FEB00, lookup de objeto usado pelo chamador msgn.

Os probes não executam limpeza de alocação anterior, alocador, cópia SIMD
alinhada, criação das entidades, GPU, retratos ou PCSX2. Isso não comprova todas
as relações possíveis entre nomes e retratos. Os parâmetros das falas e seus
cabeçalhos foram mantidos, e nomes próprios ficaram fora da seleção.

Cada alvo está vinculado ao ID, hash do registro completo e hash do rótulo.
Somente msgn/smnn/2snm elegíveis, em slots fixos, sem controles desconhecidos,
com tradução exata do mapa editorial, passam. Fontes e codec PT-BR existentes
são reutilizados; delimitadores/controles injetados, overflow, nomes não revistos,
metadados incompatíveis e decisões de preservação são recusados.

O compilador de corpos é executado primeiro, mantendo `label.editable=false`
e suas proibições históricas. Depois, o overlay privado substitui somente o slot
do rótulo e combina a alteração com o patch do mesmo registro: um único patch
final por ID. Não há realocação nem repack. Todos os bytes fora daquele slot
são comparados com o registro já compilado; o registro é reparsed em uma sombra
estrutural neutra para os pares PT-BR, com os mesmos offsets. A leitura final
independente compara todos os segmentos. Uma falha interrompe a construção.

O campo `named_choice_evidence.label_and_tail_immutable` do relatório continua
descrevendo a prova do **compilador legado de corpos**, antes do overlay.
As exceções de rótulos são enumeradas em `speaker_labels.results`, pela nova
política; não representam liberação geral da terceira string ou da cauda.
Fingerprints de extração e receitas históricas não foram alterados.

## Verificação e pendências

**57 testes distintos aprovados**: oito novos de rótulos/regressão real,
cinco de controles v014 e 44 de reinserção, codec nativo, cobertura, auditoria,
preflight, retenção e alpha. Incluem tentativa de editar rótulo pelo compilador
legado, que continua recusada, adulteração de hashes/instruções/capacidade,
duplicação, preservações, comparação de todos os segmentos herdados e reversão
dos deltas dos rótulos. Não houve nova execução de PCSX2.

Comparação integral v033→v034: **4.340 bytes diferentes em 553 registros MAP**.
Todos os demais bytes da imagem, fontes, interface, arte e diretório ficaram
idênticos. Relatório em `reports/interface-v034.json`; triagem das capacidades
em `reports/rotulos-falantes-v034.json`; catálogo atualizado em
`reports/dialogos-pendencias-v034.json`. Hash/tamanho/journals e iniciador em
dry-run foram conferidos. Cinco ISOs de trabalho, alpha permanente preservada.

Na próxima partida normal, conferir títulos dos NPCs/lojas e os rótulos com
acentos: alinhamento, largura, corte, associação com a fala/retrato e passagem
de opções. Não exigir acesso imediato a cenas distantes. Validação visual pendente.

**367 adiamentos por espaço**: exemplos Man → Homem, Worker → Trabalhador,
Transporter → Transportador, Dog → Cão. São decisões por bytes, não por número
de caracteres Unicode. Não encurtar artificialmente ou remover acentos para
obter contagens. A cópia em memória suporta comprimento variável no caminho
analisado, mas isso não cria espaço no registro em disco. Próxima frente:
investigar remanejamento interno seguro de rótulos nos registros com folga,
sem crescimento de registros/SSD, e continuar revisão contextual dos poucos
corpos ainda não decididos. Não repetir N$3 nem promover candidatos por contagem.
