# Interface v008 — linha de base do Satcom

O usuário aprovou preliminarmente o desenho recuperado dos botões, mas mostrou
desalinhamento entre letras em Procurados, Mensagens e outros rótulos. A imagem
enviada corresponde à proposta gráfica; não é tratada como execução validada no
PCSX2. A rodada anterior v007 foi interrompida antes da documentação final e do
commit; seu perfil e a ISO local permanecem como referência histórica.

Esta revisão corrige o posicionamento vertical. As traduções e os desenhos dos
demais recursos permanecem iguais: 573 campos textuais, 40 ocorrências gráficas
(26 Satcom e 14 de outras famílias), MAP v030 e layout v005. Não aumenta a
contagem de traduções nem libera novas estruturas.

## Causa comprovada

A v007 extraía as letras claras dos botões usando a altura de origem das palavras
escuras correspondentes. Os próprios desenhos originais têm variações de um
pixel entre essas posições. A extração precisa compensá-las por variante:

| Palavra usada na amostragem | Slot normal / claro | Topo normal / claro na célula | Correção da origem clara |
|---|---|---|---|
| Music | 19 / 7 | 5 / 6 | +1: subir o glifo recuperado |
| Config | 21 / 9 | 6 / 5 | −1: descer o glifo recuperado |
| Diary | 22 / 10 | 4 / 5 | +1: subir o glifo recuperado |

Isso colocava a/u/s/c/r/D um pixel abaixo, f/C um pixel acima, e g também acima
de seu descendente correto. Os glifos construídos herdavam as diferenças.
Remote não tinha esse desvio de origem e permanece byte por byte original.

## Correção sem mudança de escala

Política opt-in `satcom-native-baseline-v005`, em `tools/satcom_native_font.py`.
O ajuste ocorre na origem da extração, antes das construções L/P/J/j e acentos.
A política v004 continua reproduzindo o desenho antigo, com os mesmos hashes.
Receita corrigida: `translations/interface-graphics-v005.json`, vinculada por hash
na `translations/interface-v008.json`.

Referência métrica: tinta forte (cobertura a partir de 160) do R original de Remote.
Na célula de 18 pixels, o corpo termina em **15, exclusivo**: maiúsculas/ascendentes
ocupam linhas 3–14, minúsculas de altura-x ocupam 7–14. Acentos ficam acima do corpo;
g/j/ç podem alcançar linhas 15–17 abaixo da base. Não alinhar seus descendentes
pela borda inferior dos demais caracteres nem tornar todas as letras da mesma
altura. O importante é alinhar o corpo à linha comum, preservando a tipografia.

Nenhum resize ou compressão é aplicado. Os testes comparam larguras e a forma
recortada da tinta forte de todos os 21 glifos recuperados antes/depois: a forma
é idêntica, mudando somente sua posição. As construções derivadas passam a usar
os traços reposicionados; seus pontos de junção e acentos seguem a base corrigida.

O perfil normal já tinha a linha correta e foi preservado integralmente. O perfil
claro recebe a correção. Bordas, Remote, rótulos riscados, paleta/alpha, GANM,
dimensões e offsets continuam protegidos. Os outros 14 rótulos gráficos não mudam.

## Uso e validação

- `Preparar-Graficos.cmd`: compõe e confere previews corrigidos, sem ISO.
- `Preparar-Interface.cmd`: valida a receita v008.
- `Iniciar-Teste.cmd`/`Testar-Interface.cmd`: abrem a ISO consolidada v008.
- ISO: `work/interface-v008/MetalSaga-ptbr-interface-v008.iso`.
- Comparação ampliada: `work/satcom-baseline-v005/comparacao-alinhamento.png`.

```powershell
python tools/interface_graphics.py --recipe translations/interface-graphics-v005.json --output work/alinhamento-revisao-nova
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v008.json --output work/interface-v008 --build-iso
```

Diretórios de saída devem ser novos. Os previews foram inspecionados localmente;
a revisão visual do usuário e o teste em jogo continuam pendentes. Quando for
conveniente, comparar Procurados, Mensagens, Diário, Música e Confirmar com Remote,
observando a linha do corpo e os descendentes naturais separadamente.

Não houve cópia para OneDrive nesta rodada. Preservar a alpha, os originais e o
limite de dez ISOs de trabalho. Anexos privados do chat foram incluídos no gitignore.


## Verificações executadas

- 60 testes aprovados: interface/tipografia (39), índice da ajuda (4), ajuda/regressão MAP (6), retenção (4), layout v005 (4) e alpha (3). A regressão inclui reprodução da política v004 anterior e recusa de seus hashes quando usados no perfil de alinhamento novo.
- Preview e comparação ampliada foram gerados e inspecionados. `work/satcom-baseline-v005/linhas-de-base.png` mostra Remote, Procurados e Mensagens com guias; as guias são apenas da ilustração e não entram na ISO.
- ISO v008 construída contra o original: 1.704.427.520 bytes; SHA-256 `b620386274561ce9a69bbdfb9ff3db880eefb51db669d4f64278598fa743ca2b`. Compilação com 5.892 registros MAP alterados, 1.339 preservados, zero recusas e 613 ocorrências de interface.
- Mantidas dez ISOs sob work/ e alpha fora da retenção. Relatórios próprios: `reports/interface-v008-validation.json`, `reports/interface-v008-delta.json` e `reports/satcom-baseline-v005-evidence.json`. Não houve execução do PCSX2 nesta rodada.

- Comparação integral v007→v008 concluída: 986 bytes diferentes em um patch de pixels da textura 3 do Satcom. Todo o restante da ISO permaneceu idêntico, incluindo fontes, código, diálogos e tabelas.
