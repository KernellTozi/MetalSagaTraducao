# Interface v055 — comandos reais da batalha

O usuário abriu corretamente `Iniciar-Teste.cmd`, iniciou um jogo novo e
encontrou Skill/Weapon/Drive/Defend/Flee em inglês. O log do PCSX2 confirma
que foi aberta a v054. A conferência direta da ISO confirma que o atlas de
FBS_DATA já estava traduzido. Portanto, não era uma escolha errada do
iniciador nem um estado rápido restaurando os gráficos antigos.

## Causa comprovada e recursos encontrados

A batalha usa outros atlas, comprimidos em `DATA/MMBATTLE/MMBATTLE.BIN`.
O atlas FBS é um recurso separado. A hipótese de cobertura geral da batalha
somente pela edição de FBS não se sustenta frente à captura e aos novos
recursos encontrados.

A tabela inicial contém pares u32 little-endian `(tamanho, offset)`, por ID.
Foram encontrados 15 fluxos com TIM2 nas entradas 1586–1600; a extração dos
15 foi inspecionada visualmente. Somente os dois abaixo foram liberados.
Não interpretar ausência de strings ASCII no arquivo comprimido como
ausência de texto gráfico.

| Entrada | Offset de arquivo | Slot original | Consumo original | Novo consumo | Sobra |
|---|---:|---:|---:|---:|---:|
| 1589 | 321460224 / 0x13291800 | 35840 | 35152 | 35017 | 823 |
| 1594 | 321573888 / 0x132AD400 | 13312 | 12566 | 12257 | 1055 |

Os IDs 1589 e 1594 são materializados pelo carregador em ELF+0x109180 e
ELF+0x109248, respectivamente; as janelas incluem a montagem dos descritores.
Offsets de ELF são de arquivo. Evidência e hashes vinculados em
`translations/batalha-grafica-v001.json`; resultados em
`reports/batalha-grafica-v001.json`.

O fluxo usa a variante já comprovada de LZSS, dicionário zerado de 1024
bytes, cursor inicial 1006 e tamanho de saída u32. Cada saída tem 66624
bytes: TIM2 de uma imagem linear 256×256, 8 bits, cabeçalho total de 64,
65536 índices e 1024 bytes de paleta RGBA. A visualização da CLUT CSM1
troca grupos de oito entradas; não reorganiza os índices de pixels.

## Alterações

- Oito comandos: Habil., Equip., Munição, Fugir, Dirigir, Arma, Passar e Defesa.
- Cinco etiquetas: Fogo, Ácido, Veneno, Atord. e Caído.
- O pequeno ícone textual Skill também passa a Habil.
- MAIN/SUB/SE e Item preservam os pixels originais. Ícones, retratos, tanques,
  bordas, coordenadas, cabeçalhos, paletas e dimensões não foram alterados.

São 14 rótulos novos; a contagem heterogênea de interface passa de 3848
para 3862. Nenhuma nova tradução de armas foi aplicada. MAP v044, 6044
registros alterados, 991 referências de falantes e 541 nomes permanecem
iguais à v054, assim como o layout de acentuação v005.

As letras vêm dos glifos GFI já usados pelo projeto, com quatro níveis de
cobertura, escolhendo somente cores/alpha da paleta original. A primeira
tentativa com muitos níveis excedia o slot: 37736 bytes para 35840. Foi
descartada; a quantização adequada ao texto pequeno levou a 35017. Nenhum
extent, registro ou arquivo foi aumentado. Veneno usa máscara de 11 pixels
de altura na etiqueta de 16; demais etiquetas usam 12. A fonte do jogo não
foi modificada. A aparência ainda exige confirmação visual no PCSX2.

## Reprodução e validação

`tools/battle_menu_atlas.py` valida o pai v054 exato, os hashes de origem,
os slots, máscaras e interiores de letras. Reutiliza o recompressor próprio.
O retorno é conferido tanto pelo decoder Python quanto pela execução do
laço original do ELF em memória simulada. Isso não executa o carregador
completo, a GPU ou o jogo.

As três receitas novas têm preservação de bytes em `.gitattributes`, pois
seus vínculos usam SHA-256 bruto. Não renormalizar receitas históricas.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v055.json --compact-output --build-iso --output work/interface-v055-reproducao
python -m unittest discover -s tests -p test_battle_menu_atlas.py -v
python tools/start_test.py --dry-run
```

O iniciador principal continua sendo **Iniciar-Teste.cmd** e agora abre
`work/interface-v055/MetalSaga-ptbr-interface-v055.iso`.

SHA-256: `47509f21ccf240ae084fe67b0afe723c71d39688502445b116b09569123be49a`.
Tamanho: 1704427520 bytes. Preflight completo executado; PCSX2 não foi aberto.
Comparação integral com a v054 em `reports/interface-v055-delta.json`.

Para o teste do usuário: entrar em uma batalha a pé e verificar comandos,
etiquetas, legibilidade, seleção e ações. Verificar também o menu de tanque
na mesma passagem, mantendo MAIN/SUB/SE. Não precisa repetir a abertura
de um jogo novo se puder usar um memory card válido. O perfil isolado
histórico está com cartões desativados; nenhum cartão/save/configuração foi
modificado nesta rodada.

## Revisão de armas e próximos recursos

`docs/revisao-armas-v001.md` descreve a revisão completa das quatro classes
identificadas. As sugestões não são aplicadas por este compilador.

Os atlas comprimidos 1587/1588 também contêm textos de efeitos/atributos
de batalha. Foram localizados visualmente, mas não editados nesta entrega.
Isso é uma lacuna gráfica nova, fora do catálogo anterior de 20 candidatos;
não reabrir pôsteres Wanted ou títulos de minigames preservados pelo usuário.
