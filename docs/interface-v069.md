# Interface v069 — terminologia brasileira dos jogos de cartas

O usuário pediu rever traduções pouco usadas no Brasil, principalmente no
poker. Esta versão revisa a v068 sem alterar as regras ou a lógica dos jogos.

## Decisões

| v068 | v069 |
|---|---|
| Sequência real | Royal Flush |
| Sequência de naipe | Straight Flush |
| Trinca e par | Full House |
| Mesmo naipe | Flush |
| Pôquer | Poker |
| Vinte e um, no nome do jogo | Blackjack |
| vinte e um natural, nas regras | blackjack |
| VINTE E UM PAGA 3:2, na mesa | BLACKJACK PAGA 3:2 |

Quadra, trinca, sequência, dois pares, par alto/baixo e sem par permanecem em
português. Quina é mantida para a combinação especial com coringa desta
variante. Não transformar essa regra em Texas Hold'em nem incluir ações
como fold, raise ou check onde a mecânica é manter/trocar cartas.

As instruções, explicações das mãos, coringa, apostas e comandos comuns
continuam em português. No blackjack, pedir carta, parar, dobrar, dividir
e seguro têm uso em português; não há motivo para devolver toda a interface
ao inglês. O distintivo 21 continua representando o objetivo numérico.

## Referências consultadas

- [PokerStars Brasil: classificação das mãos](https://www.pokerstars.com/pt-BR/poker/games/rules/hand-rankings/)
  combina Royal Flush, Straight Flush, Full House e Flush com quadra,
  sequência, trinca e pares.
- [PokerStars Brasil: vídeo poker](https://www.pokerstars.com/pt-BR/casino/how-to-play/videopoker/)
  confirma a mesma combinação de nomes em uma modalidade mais próxima do
  minigame, sem pressupor regras idênticas.
- [PokerStars Brasil: blackjack](https://www.pokerstars.com/pt-BR/casino/how-to-play/blackjack/premium/)
  e [glossário](https://www.pokerstars.com/pt-BR/casino/terms/)
  usam Blackjack junto de termos portugueses como dobrar, dividir e seguro.

As fontes sustentam a escolha terminológica. A adoção de Poker em vez da
grafia portuguesa Pôquer é uma padronização editorial para este projeto;
Pôquer também é uma forma correta.

## Implementação e reprodução

`tools/card_terms_review.py` revisa somente sete planos de textura NDATA e
dois literais ELF existentes, com os mesmos IDs, offsets, tamanhos e bytes
de origem. A receita v068 e seus recursos continuam reproduzíveis.

Os painéis e rótulos são redesenhados pelo mecanismo existente, com fontes
vinculadas por hash; não se pressupõe que tenham a família exata do original.
Cartas de exemplo, ícones, paletas, alpha, descritores e referências são
preservados. MAP v047 e o layout v005 permanecem iguais. Revisão não aumenta
o número de unidades traduzidas.

```powershell
python tools/card_terms_review.py
python -m unittest discover -s tests -p test_card_terms_review.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v047.json --interface-draft translations/interface-v069.json --compact-output --build-iso --output work/interface-v069
```

O construtor exige saída nova. Manifesto `translations/termos-cartas-v001.json`;
comparações em `work/cartas-v069/`. Nas comparações desta revisão, esquerda
é v068 e direita é v069, apesar do cabeçalho genérico do exportador.

O usuário confere em partida mãos premiadas, tabela de pagamentos, instruções,
nome do jogo e inscrição da mesa. A inspeção dos gráficos exportados e os
testes binários não equivalem à execução no PCSX2.

## Entrega e verificações

- ISO: `work/interface-v069/MetalSaga-ptbr-interface-v069.iso`,
  1.704.427.520 bytes.
- SHA-256: `d37aeed756e3dfacce3969d103930350cd8bc692a3cffeba6d8726a0ce93de72`.
- Oito testes específicos e 12 de regressão aprovados: 20 distintos.
  Reproduzem os patches, rejeitam alterações alheias e conferem preservação
  dos demais patches, células ELF, nomes usuais, ícones e cartas de exemplo.
- Preflight integral aprovado; nenhum journal ou arquivo parcial pendente.
- Comparação integral v068→v069 aprovada: 27.132 bytes nos nove patches
  previstos; diretório da ISO, fontes e layout idênticos. Evidência em
  `reports/interface-v069-delta.json`; resumo em `reports/interface-v069.json`.
- UI mantém 4.640 unidades e MAP 6.044 registros alterados, sem recusas.
- Backup v059 conferido por hash integral e atributo somente leitura.
  Retenção mantém cinco imagens de trabalho; v064 removida, receitas preservadas.
- `Iniciar-Teste.cmd` e `Abrir-Pasta-da-Ultima-Versao.cmd` foram simulados
  e apontam para a v069. Não houve execução no PCSX2 nesta rodada.
