# Interface v013 — título nativo e assinatura

Esta revisão atende à reprovação visual da v012. A fonte Arial Black usada naquela
tentativa descaracterizou o menu; **não é a fonte recomendada para os botões**.
As receitas anteriores ficam preservadas para reprodução e comparação.

## O que mudou

- NOVO JOGO, RETOMAR e INSTALAR voltam a usar o desenho raster original de RTITLE.
  As letras disponíveis permanecem idênticas ao atlas: N/O/E/T/A/M/G etc.
  V, J e R são reconstruções explícitas de componentes de W/U/O/E/T/N.
- Corrigido o recorte de V, removendo um traço vizinho do W; o R mantém um
  espaço superior e uma perna diagonal; J aproveita a haste/bacia de U.
- Um pixel entre células, sem compressão ou redimensionamento horizontal.
  NOVO JOGO ocupa 197 pixels; RETOMAR, 166; INSTALAR, 172. Para acomodar
  o primeiro sem apertar as letras, os frames 0/2 passam a 228×24 com
  hotspot 114,12, mantendo o centro. A largura útil da borda é respeitada.
- “Traduzido por: Kernell Tozi” abandona a GFI condensada do diálogo.
  Usa Arial Rounded MT Bold de 14 pixels, contorno de um pixel e composição
  local com supersampling 4×, sem compressão horizontal. É uma aproximação
  visual à família dos créditos oficiais, **não identificação da fonte original**.
  O arquivo instalado ARLRDBD.TTF é vinculado por SHA-256 na receita e não
  é copiado nem versionado. A máscara também é vinculada por hash.

Ferramenta: `tools/title_authentic.py`; política
`title-native-separated-labels-credit-v009`; receita gráfica v009.
Os mesmos seis frames, os offsets SDA e o tamanho do recurso são preservados;
paleta, imagens de borda/fundo/fade e cabeçalho GANM permanecem intactos.

## Crédito fora da tela: causa comprovada

A v011 calculou sua posição usando y=330 para Retomar. Contudo, a rotina original
ELF 0x393A0 usa **306 + 42×índice quando existem duas opções** e 296 + 34×índice
quando existem três. Com duas, Retomar estava em y=348 e a assinatura começava
em **y=448**, completamente fora da imagem virtual 640×448. A captura do usuário
e uma inicialização limpa da v011 confirmaram sua ausência.

A v012 normalizou duas opções para as mesmas posições 296/330 das três primeiras
opções. Somente duas constantes foram alteradas: instruções em 0x393BC
`2402002A→24020022` e 0x393C8 `24420132→24420128`. A v013 conserva essa correção.
O menu de três opções permanece nas posições originais. O ELF original completo
é vinculado por hash. O crédito v013 ocupa x=226..413, y=428..443.

**Limitação ainda existente:** a assinatura pertence ao sprite de Retomar e herda
sua cor/visibilidade. Quando ele está desabilitado/cinza, ela também pode ficar
acinzentada. A nova máscara tem corpo mais cheio e legível, mas não cria um
elemento de desenho independente. Não declarar esse comportamento resolvido.
Os créditos oficiais e o vídeo de fundo não foram modificados.

## Correções da batalha, herdadas da v012

O espaço após í/ê não vinha de um espaço ASCII na palavra: o renderizador
VA 0x18B0B8 (arquivo 0x8C0B8..0x8C2E0) avança uma célula inteira ao ler dois bytes,
enquanto ASCII avança meia célula. Esse caminho é distinto do diálogo já corrigido.

A política `battle-ptbr-half-cell-advance-v001` recompõe a função dentro dos
mesmos 552 bytes. Somente os 18 pares 8240..824E e 8259..825B passam ao avanço
ASCII existente. Preserva despacho de glifo, dois bytes consumidos e tamanho
da letra. Não libera outros códigos SJIS. Ferramentas: `battle_font_advance.py`
e `battle_advance_probe.py`. O segundo é uma execução limitada de instruções com
ABIs de desenho/lookup declaradas; não emula o PS2 nem prova renderização.

Três traduções “Soma” foram retiradas da receita para recuperar **Total**, que
já existe nos bytes originais: 0x323A00, 0x323A58 e 0x33D770. A lista explícita
`restored_originals` é cumulativa. O comparador exige autorização exata para
patches removidos e compara sua restauração com o original.

Incluídas 23 descrições/avisos de comandos de batalha, mantendo MAIN/SUB/SE,
prefixos, espaços finais e limites originais. Total: **641 campos/ocorrências
de interface**, 44 gráficos, com MAP v030 (5.892 alterados e 1.339 preservados)
e perfil de fonte/layout de diálogo v005. Não contar correções como textos novos.

## Executar e conferir

Abrir `Iniciar-Teste.cmd` ou `Testar-Interface.cmd`. A imagem atual é
`work/interface-v013/MetalSaga-ptbr-interface-v013.iso`. Fazer inicialização limpa.
O usuário pediu realizar a conferência visual; não reabrir automaticamente o
emulador para tentar alcançar telas.

Conferir desenho e separação das letras, seleção/borda, assinatura completa e
sem sobreposição, e o espaçamento interno de Nível/Prêmio e Total após batalha.
A captura enviada pelo usuário comprova que o crédito v012 apareceu, mas
reprova suas duas fontes. **A v013 ainda precisa de avaliação visual.**

Reprodução em pasta nova:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v013.json --output work/interface-reproducao-v013 --build-iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

Originais e alpha preservados; retenção de dez ISOs sob work/. Sem cópia
OneDrive nem desligamento solicitado nesta rodada. Próxima prioridade permanece
interface/menus; não retomar pequenos fragmentos MAP nesta correção.

## Verificações desta entrega

- 66 testes de interface passaram em 171,254 s; mais cinco testes específicos
  do retorno ao título nativo passaram em 11,189 s: 71 testes distintos.
- Testes de batalha cobrem os 256 classificadores de byte inicial, 3.328 casos
  de limites de bytes e os 18 códigos em três combinações de tamanho/escala/avanço.
  Despacho, quantidade de bytes consumidos e códigos vizinhos são comparados.
- Comparação integral v011→v013: 11.322 bytes diferentes em 31 patches previstos,
  diretório ISO inalterado, todos os demais bytes idênticos. A comparação verifica
  também as três restaurações de Total e a preservação dos diálogos/fontes GFI.
- ISO de 1.704.427.520 bytes, SHA-256
  `28c941ebea3c9a587495175f9fea1638cfacb0ed9e93427c5192666950e81d12`.
- Evidências próprias: `reports/interface-v013-validation.json` e
  `reports/interface-v013-delta.json`. Previews de composição em
  `work/title-authentic-proposal.png` e `work/title-credit-proposal.png`;
  não são capturas do emulador. A v013 não foi executada pelo agente.
