# Pendências atuais — base v054

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
  991 referências de falantes traduzidas e 541 nomes de itens aplicados.
  Essas métricas não permitem calcular uma porcentagem confiável do jogo.
