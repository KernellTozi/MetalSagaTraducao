# Interface v059 — efeitos e atributos de batalha

Sobre a v058 completa, mantendo MAP v044 e layout v005. São **34 rótulos
gráficos traduzidos** em dois atlas comprimidos de MMBATTLE.BIN. Não são
novos diálogos nem itens: os 627 nomes de itens, 6044 registros MAP alterados,
5991 corpos/opções e 991 referências de falantes permanecem iguais.
A contagem heterogênea de interface passa de 4155 para **4189**.

## Texto e contexto

| Grupo | Traduções |
|---|---|
| Estados e recuperação | Fogo, Ácido, Pane, Veneno, Atord., Recuperado, Recuperação 2x |
| Atributos e peças | Dirigir, Iniciativa, Ataque, Defesa, Durab., Taxa crítica, Todas as peças, Quebrado, Esquiva, Motor, Precisão, Mais rápido |
| Alcance, ações e proteção | Precisão, Ação dupla, Fora de alcance, Proteção corpo a corpo, No ar, Proteção a distância, Subsolo, Alta altitude, Submerso, Furtivo, Abrigo, Danificado, Quebrado, Protetor, Isca |

Precisão e Quebrado aparecem em ambos os atlas e contam por ocorrência.
Os componentes MAIN/SUB/SE, HP/SP, C Unit, Chassis e o rótulo Normal conservam
os pixels originais. Os ícones de seta também ficam intactos.

**Quatro rótulos continuam em inglês por contexto insuficiente:** Dummy,
UP, DOWN e Damage Override. Não presumir que UP/DOWN são sempre aumento/
redução de atributo, nem confundir Damage Override com dano fixo/ignorado
sem rastrear seu consumidor. O rótulo pequeno inicialmente lido como
Overpower era **Underground**, confirmado ao ampliar o original: agora
Subsolo. Não há uma quinta pendência Overpower nesse atlas.

## Estrutura comprovada e limites

| Entrada | Offset em MMBATTLE.BIN | Slot | Comprimido novo | Folga |
|---|---:|---:|---:|---:|
| 1587 | 321425408 | 18432 | 15669 | 2763 |
| 1588 | 321443840 | 16384 | 13099 | 3285 |

Os seletores do carregador original são conferidos em ELF+0x109108 e
0x109130, dentro da janela vinculada 0x109104–0x109154. Os índices 1587/1588
correspondem a 0x633/0x634. Mantém-se o TIM2 já comprovado: 66624 bytes,
uma imagem linear 256×256, índices de oito bits, cabeçalho de 64 bytes e
paleta de 1024 bytes com CLUT CSM1. O diretório e os extents não mudam.

Cada palavra é isolada em uma célula inspecionada. O importador identifica
a caixa dos pixels originalmente não transparentes e **só escreve dentro
dessa caixa**. Não utiliza a área branca aparente como espaço livre, não
altera UVs e não presume margem adicional. Uma célula que encosta em tinta
original é rejeitada, evitando aceitar um recorte truncado como evidência.
Cabeçalho, paleta, ícones e todos os pixels externos são comparados.

## Desenho reproduzível

As palavras completas são desenhadas localmente com **Impact**, instalada
em C:/Windows/Fonts/impact.ttf, com inclinação à direita, preenchimento
branco e contorno preto. É uma aproximação do estilo, não uma identificação
da fonte original. O manifesto vincula o hash do arquivo da fonte e das
34 máscaras; fontes do Windows não são copiadas ao Git nem ao jogo.
Os GFI e a correção de acentos v005 não são alterados.

O desenho usa somente índices já existentes: transparência original e
tons de cinza opacos da própria paleta. Quatro níveis reduzem ruído e
crescimento comprimido. A escala horizontal não pode ficar abaixo de 70%
da largura natural da palavra na altura escolhida. Fora de alcance e
Danificado reduzem a altura do preenchimento em **um pixel**; as demais
mantêm a altura máxima prevista dentro da caixa original, com contorno.
Durab. e Atord. são abreviações para preservar legibilidade. Todos os
acentos dos textos escolhidos são mantidos.

A reinserção reutiliza o compressor LZSS de dicionário de 1024 bytes. Cada
saída é conferida pelo decoder Python e pela execução do laço original do
ELF com RAM simulada. O restante de cada slot recebe zeros como no original.
Isso não executa a GPU, o carregador completo ou o PCSX2.

## Como reproduzir e testar

Ferramenta: tools/battle_effect_atlas.py. Política opt-in exata:
`battle-effect-original-ink-bounds-v001`. Manifesto:
translations/batalha-efeitos-v001.json. O filho v059 precisa ser idêntico ao
pai v058, exceto pelo vínculo, nome da ISO e descrição. Compila o pai pelo
seu mecanismo validado e acrescenta somente dois patches.

```powershell
python tools/battle_effect_atlas.py
python -m unittest discover -s tests -p test_battle_effect_atlas.py -v
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v044.json --interface-draft translations/interface-v059.json --compact-output --build-iso --output work/interface-v059-reproducao
python tools/start_test.py --dry-run
```

Preparar-Interface.cmd valida a receita sem gerar ISO. Iniciar-Teste.cmd
abre work/interface-v059/MetalSaga-ptbr-interface-v059.iso após o preflight.
As comparações lado a lado ficam em:

- work/batalha-atributos-v001/comparacao-1587.png
- work/batalha-atributos-v001/comparacao-1588.png

O usuário faz a conferência visual durante a partida, sem necessidade de
alcançar cada efeito imediatamente. Observar avisos flutuantes de combate,
acentos, contornos, cortes, setas e transições. O atlas é armazenamento:
a disposição das palavras na comparação não reproduz uma tela do jogo.
Não declarar todos os efeitos vistos no PCSX2 por terem passado pelo decoder.

Relatórios consolidados: reports/interface-v059.json e
reports/interface-v059-delta.json. Nenhuma cópia OneDrive, alteração de
cartões/saves/BIOS ou novo desligamento é solicitada nesta rodada.

A comparação integral v058→v059 confirmou **32772 bytes diferentes em
somente dois patches de MMBATTLE.BIN**. Diretório ISO, fontes/layout e todos
os patches anteriores permanecem idênticos. Tamanho da imagem: 1704427520
bytes. SHA-256:
`ab243c520f6e84169d52ee765cb71faeeeb605fb79b34aecd9adc126ea008094`.
O preflight completo e o iniciador em modo de conferência passaram sem abrir
o emulador. Mantidas cinco ISOs de trabalho e a alpha fora da retenção.

Passaram **54 testes distintos**: dez específicos do novo atlas e 44 de
regressão de armas aprovadas, atlas de comandos, Satcom, Mundo aberto,
preflight e retenção. Incluem reprodução das máscaras, preservação de pixels
externos/paleta/setas, identidade de todos os patches anteriores, retorno
pelo decoder original, recusa de overflow e de mudanças em vínculos,
fontes/retângulos e receitas. O auditor de capacidade reconhece o filho v059
e mantém zero das revisões de nomes anteriormente bloqueadas.
