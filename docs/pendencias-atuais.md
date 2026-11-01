# Pendências atuais — v059, com auditoria histórica v054

A v059 é agora a cópia de segurança em dist/backup-v059/; as ISOs antigas
v055–v058 e a antiga alpha foram removidas por nova ordem do usuário, após
verificação integral. A imagem jogável do iniciador continua v059. O novo
protótipo dos 13 falantes está em docs/falantes-lookup-v001.md: resolve os
nomes completos em RAM simulada, mas ainda exige reserva comprovada de
armazenamento no ELF/heap. Nenhuma tradução de falante foi aplicada à ISO.

A v059 traduz 34 rótulos gráficos de efeitos/atributos nos atlas comprimidos
1587/1588. Só a área das letras originais é alterada; setas, paletas e termos
protegidos conservam os pixels. A aparência e o contexto de exibição aguardam
a partida do usuário. Comparações em work/batalha-atributos-v001/ e manual
docs/interface-v059.md. Permanecem quatro rótulos por contexto: Dummy, UP,
DOWN e Damage Override. O pequeno Underground foi confirmado por ampliação
e traduzido como Subsolo; não existe uma pendência Overpower nesse atlas.

A v058 aplica o lote humano de armas: 86 nomes, 91 referências de ação,
89 MANTER preservados, zero fallback/conflitos. As 15 munições especiais
ficaram intactas. Conferir visualmente equipamentos, lojas e batalha na próxima
partida. Detalhes em docs/interface-v058.md. A habilidade 946 é um alias fora
da autorização e permanece intacta; não traduzi-la automaticamente.

A v057 muda somente os avisos de saída e o fallback ELF para **Mundo aberto**,
conforme pedido do usuário. Demais traduções e pendências da v056 preservadas.

A v056 resolve as capturas de Lojas/meta financeira/aviso de saída: Qual loja?,
Atual, Meta e 113 prefixos Mapa do mundo; revê o desenho de Tempo de jogo.
Ver docs/interface-v056.md. Novos rótulos de navegação não aumentam a contagem
de diálogos. Confirmar apresentação e transição de saída no teste do usuário.

A v055 corrige 14 rótulos de batalha em dois atlas comprimidos que não eram
os de FBS_DATA. O log e a conferência da ISO confirmaram que o usuário usou
corretamente o iniciador v054; não era um save state. Ver docs/interface-v055.md.
Testes visuais da correção ficam pendentes do usuário.

Revisão histórica de 175 registros de armas e anexo de 15 munições em
work/revisao-armas-v001/ARMAS-PARA-REVISAR.md. As decisões humanas recebidas
foram aplicadas na v058; os 89 MANTER são preservações, não pendências.
Os atlas comprimidos 1587/1588 receberam o lote v059 descrito acima; os quatro
casos sem contexto não foram promovidos por suposição. A triagem anterior de
20 candidatos gráficos não representava cobertura completa desses recursos.

Auditoria reproduzida na interface v054, sem modificar a ISO.
Relatórios: reports/auditoria-dialogos-v054.json e
reports/pendencias-consolidadas-v054.json.

## Desenvolvimento ainda pendente

**13 rótulos genéricos sem espaço seguro**, em cinco grupos:

| Rótulo atual | Tradução completa prevista | Ocorrências |
|---|---|---:|
| Worker | Trabalhador | 9 |
| Man | Homem | 1 |
| Transporter | Transportador | 1 |
| Cat | Gato | 1 |
| Dog | Cão | 1 |

IDs para consulta:

```text
Worker: map.msgn.057d67dc, map.msgn.0db14094, map.msgn.0db140dc,
        map.msgn.0db147f8, map.msgn.0db14898, map.msgn.0db148e0,
        map.msgn.0e777edc, map.msgn.0e778354, map.msgn.14aad804
Man: map.msgn.0be1acd8
Transporter: map.msgn.0be25188
Cat: map.msgn.0be2d3a4
Dog: map.msgn.19f55614
```

O espaço compilado desses rótulos é, respectivamente, 7/3/11/3/3 bytes;
os alvos precisam de 10/5/13/4/4. As soluções atuais de slot, cauda e
revisão contextual não liberam esses casos. Não encurtar Trabalhador, remover
acentos, apagar falas ou tomar bytes externos. Uma solução futura precisa
de outra hipótese de armazenamento/lookup e de prova própria; não repetir
indefinidamente as buscas de padding já encerradas. Esses rótulos continuam
em inglês, sem impedir a versão jogável.

Essa nova hipótese já tem uma sonda funcional de 170 bytes e propostas
restritas aos 13 registros. O bloqueio atual é a reserva em memória:
classificar 12 referências ao fim da imagem 0x4B599C antes de testar um
segundo segmento. Os zeros do cabeçalho ELF não são uma code cave carregada,
e a limpeza de BSS escreve até 0x4B59A0. Não aplicar os marcadores sem o hook.

**Revisão contextual do inglês remanescente:** 523 referências de falantes
fora desses 13 incluem personagens, nomes, marcadores, Hunter/Soldier/Punk e
termos que ainda exigem contexto. Não são 523 traduções obrigatórias.
Os 124 registros de triagem editorial, 455 candidatos de nomes/expressões e
589 de pontuação/controles também não são contagens de frases faltantes.

**Cobertura fora do catálogo:** o scanner dirigido não encontrou novos
candidatos ASCII em registros SSD fora dos parsers conhecidos. Isso não
exclui texto curto, nativo, comprimido ou fora desse banco. Três raízes
especiais continuam sem semântica textual comprovada; reabrir somente com
indício novo ou tela observada no jogo. Não anunciar 100% de cobertura.

## Conferência visual e encerramento

Falta uma passagem contínua pela versão consolidada: menus de personagens,
inventário/equipamento, lojas e preços, ações de batalha, escolhas, Satcom,
mensagens e diário. Não exigir que o usuário alcance cada cena imediatamente.
Registrar versão, cena, texto e imagem quando aparecer um problema. Os nomes
de até 19 bytes da v054 têm conferência visual pendente, apesar dos testes
binários e de métricas já concluídos.

O pacote local foi preparado e reconstruído com hash idêntico à v054; ver
docs/patch-local-v001.md. Isso adianta a infraestrutura de entrega, mas a
publicação de uma versão final depende da revisão de jogo e das limitações
documentadas. Não houve publicação do pacote nesta rodada.

## O que está encerrado ou deve ser preservado

- As 16 revisões humanas de nomes bloqueadas foram tratadas nas v052–v054.
- Zero grupos nativos e zero outros controles pendentes no catálogo conhecido.
- Os 19 adiamentos técnicos restantes são nomes de tanques N$3 preservados.
- Os 20 candidatos gráficos têm disposição documentada: nove cobertos e
  onze preservados por decisão do usuário. Não reabrir pôsteres Wanted,
  títulos decorativos de minigames/cassino ou o painel japonês dos cães.
- Continuam 6.044 registros MAP alterados, 5.991 com corpo/opções modificados,
  991 referências de falantes traduzidas e 627 nomes de itens aplicados.
  Essas métricas não permitem calcular uma porcentagem confiável do jogo.
