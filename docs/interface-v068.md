# Interface v068 — localização dos minigames

O pedido de 05/11/2026 amplia o escopo para os gráficos e instruções de
todos os minigames, incluindo os títulos decorativos anteriormente dispensados
e os painéis japoneses. A receita v068 herda integralmente a v067, usa MAP
v047 e mantém o perfil `ptbr-layout-v005`.

## Conteúdo

Foram trabalhados 53 planos de textura em seis arquivos SDA, com 200 células
de rótulos, 17 painéis de instruções, três inscrições da mesa de vinte e um
e 27 literais ELF. São 247 unidades de autoria, incluindo revisões. As seis
telas de regras já traduzidas nas versões anteriores também fazem parte da
imagem consolidada. A contagem de unidades mistura palavras, legendas e
painéis completos.

| Conjunto | Conteúdo localizado |
|---|---|
| Caça-níqueis | Regras, controles, apostas, saldo, ganho e botões dos três estados de iluminação |
| Roleta | Quatro páginas, tabela japonesa, mesa, dúzias, pares/ímpares, proporções e histórico |
| Pôquer | Quatro páginas, combinações, resultados, dobro ou nada, manter/trocar, botões e coringas |
| Vinte e um | Três páginas, ações, saldo/aposta/ganho, estouro, seguro e inscrições curvas da mesa |
| Caça-números | Duas páginas, níveis, tentativas, dicas, resultados e botões |
| Corrida de sapos | Apostar/correr, acerto/erro, posições, comandos e letras da chegada |
| Dança e musculação | Preparação, início, bom/erro, comandos e placa do cenário |
| Rinha de cães | Regras japonesas, vitória/derrota e cinco rodadas |
| Fogo cruzado | Título, início/fim, pontos, vidas e instrução do botão START |
| Corrida até Arthur | Preparação, largada, tempo esgotado, chegada e derrota |
| Disputa de copos | Preparação, início, fim do tempo, conclusão, leite e vinagre |
| Máquina de venda e vitrola | Bônus e legendas do atlas de reprodução/download |

Os nomes dos sapos e das músicas seguem a política de nomes próprios do
projeto. Naipes, valores das cartas, J/Q/K/A, moeda G, ícones, nomes físicos
dos botões e identificadores de mecânica são preservados. Pôsteres Wanted
estão fora deste conjunto.

## Recursos e reprodução

- `tools/minigames_release.py` prepara e confere os gráficos localmente.
- `translations/minigames-conteudo-v001.json` guarda textos, recortes,
  posições, exemplos copiados e parâmetros de desenho.
- `translations/minigames-v001.json` vincula pai, conteúdo, fontes e saídas
  por SHA-256.
- `translations/interface-v068.json` integra o lote ao construtor existente.
- `reports/minigames-cobertura-v001.json` classifica os 107 registros gráficos
  examinados, com offsets e hashes.

A varredura abrange os 105 atlas reconhecidos de NDATA e dos cinco arquivos
RMG, mais duas texturas de cenário identificadas anteriormente. Destes, 53
recebem alterações nesta versão, cinco painéis portugueses são preservados
integralmente, dois atlas mantêm nomes de músicas, sete registros pertencem
a opções/itens/referências de interface e 40 contêm cenário, símbolos ou
nenhuma palavra localizável observada. O sexto painel português anterior é
o da corrida de sapos, que recebe a revisão do botão CORRER.

```powershell
python tools/minigames_release.py
python -m unittest discover -s tests -p test_minigames_release.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v047.json --interface-draft translations/interface-v068.json --compact-output --build-iso --output work/interface-v068
```

O construtor exige uma pasta de saída nova. O processo de preparo e compilação
usa somente recursos locais e dispensa IA/APIs. As fontes instaladas ficam
vinculadas por hash, sem distribuição dos arquivos TTF.

## Limites binários

Todos os patches de imagem ficam nos planos de pixels existentes. As dimensões,
profundidades de 4/8 bits, tabelas de paleta com seus valores alpha, cabeçalhos,
GANM, hotspots, sequências, contêineres e offsets continuam vinculados à origem.
O transporte de índices passa por reversão para recuperar integralmente a
imagem original em memória.

Quatro planos de pixels herdados são revisados sob o mesmo ID. Há 49 planos
novos e 27 literais ELF novos. O compilador rejeita sobreposição parcial com
patches anteriores e alterações alheias à receita. A comparação de versões
exige a v067 exata como pai.

Os literais ELF preservam os tokens originais dos botões, R1 e o separador
nativo. As células de menus têm 16 bytes nos nomes apresentados. Pôquer usa
uma célula de oito bytes. Três legendas de aposta usam células de 40 bytes
com caudas zeradas comprovadas e sem referências interiores. A legenda de
poses usa 32 bytes. Outros campos permanecem no intervalo original até NUL.
Não há redirecionamento de ponteiros ou expansão de registros.

## Desenho e tipografia

Os rótulos usam Impact, Arial Bold e Times New Roman Bold como aproximações
visuais. Os parágrafos reutilizam o desenho GFI existente. Um fallback TTF
permite caracteres gráficos como ordinais e maiúsculas acentuadas sem criar
novos códigos no motor de diálogos. A família original desses títulos não
foi identificada.

As máscaras são desenhadas diretamente no tamanho final. O tamanho de ponto
é ajustado para caber na célula original, com rótulos menores nas áreas mais
estreitas. As inscrições curvas da mesa são montadas por glifos rotacionados
e convertidas para a paleta existente. Os exemplos de cartas e os desenhos
de controles das instruções conservam os pixels de origem, exceto o texto
CORINGA explicitamente localizado dentro das cartas de exemplo.

Os quatro glifos de cenário G/O/A/L da chegada viram F/I/M/!, conservando
quatro células e o mapeamento geométrico. A placa MUSCLES DANCE recebe
DANÇA MUSCULAR. Os valores de recompensa, probabilidades, dificuldade,
tempo e comportamento dos comandos seguem os dados anteriores.

A inspeção das comparações corrigiu fundos confundidos com tinta em palavras
densas, um recorte japonês com altura diferente, botões em estados de luz
distintos e a posição dos dois rótulos verticais nas cartas de coringa.
As versões preliminares foram descartadas antes da entrega.

## Conferência visual

As comparações ficam em `work/minigames-v068/`, nas folhas `regras-00.png`
até `regras-05.png` e `rotulos-00.png` até `rotulos-16.png`. Elas comparam
a versão anterior à versão localizada e são previews dos recursos.

O usuário confere em partida a identificação dos comandos, recortes, estados
selecionado/desmarcado, legibilidade dos rótulos pequenos, cartas de coringa,
placas e resultados animados. Upload, composição, animação e todos os caminhos
de seleção no PCSX2 continuam sujeitos a esse teste. A inspeção cobre os
recursos catalogados e os usos identificados.

## Entrega e verificações

- ISO: `work/interface-v068/MetalSaga-ptbr-interface-v068.iso`, 1.704.427.520 bytes.
- SHA-256: `3fbcbb28e1f956d758b0114e826b56ff2d1ffd5a26d0ad56f55543e9b45712ba`.
- Construção concluída: 4.640 unidades UI; MAP mantém 6.044 registros
  alterados, sem recusas nesta compilação. Perfil de fontes/layout v005.
- Passaram 14 testes específicos e 22 de regressão, total de 36 testes
  distintos. Conferem limites, fontes vinculadas, reprodução dos patches,
  reversão 4/8bpp, ícones, exemplos de cartas, comandos, nomes e proteção
  das áreas externas aos recortes.
- Preflight da ISO aprovado, com tamanho e hash completos conferidos.
  Nenhuma transação pendente foi detectada pelo verificador.
- Comparação integral v067→v068 aprovada: 1.210.230 bytes diferentes nos
  80 patches previstos, diretório e fontes/layout idênticos. Evidência em
  `reports/interface-v068-delta.json`; resumo em `reports/interface-v068.json`.
- Backup v059 conferido por hash integral e atributo somente leitura.
  Retenção mantém cinco ISOs de trabalho; v063 removida, receitas preservadas.
- Os dois atalhos foram simulados e apontam para v068. Não houve execução
  no PCSX2 nem cópia para OneDrive nesta rodada.

Abra `Iniciar-Teste.cmd`. Confira cada minigame, alternando telas de regras,
estados de botões, vitória/derrota e páginas de resultados. Para comparar
recursos antes de jogar, use as folhas em `work/minigames-v068/`.
