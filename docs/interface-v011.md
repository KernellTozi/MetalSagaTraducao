# Interface v011 — desenho do R e crédito de tradução

Atende ao retorno visual do usuário sobre a tela inicial v010. O R reconstruído
em RETOMAR tinha uma forma ambígua, parecida com A. A v011 altera **somente R**
no alfabeto experimental do título: mantém a altura, abre o espaço interno da
parte superior e separa a perna diagonal da haste. INSTALAR recebe a mesma
correção. Os demais glifos e as receitas históricas continuam reproduzíveis.

Acrescenta a linha solicitada **“Traduzido por: Kernell Tozi”**, preservando os
créditos oficiais existentes. Textos de interface v010, MAP v030 e layout v005
permanecem iguais. Total compilado: **621 campos/ocorrências**, sendo 44 gráficos.
O aumento de um campo corresponde à assinatura; correções não contam novamente
como traduções novas.

## Implementação e limites

Política opt-in `title-credit-and-raster-v007`, receita
`translations/interface-graphics-v007.json`, ferramenta `tools/title_credit.py`.
Herda por hash a receita gráfica v006, conserva todos os patches FBS_DATA e
substitui somente o transporte da textura e dos seis frames RTITLE.

Não injeta código no ELF, não acrescenta chamadas de desenho, não modifica
vídeos e não altera as funções dos botões. A textura 256×256 foi reorganizada
dentro dos mesmos 65.536 bytes de pixels. Os seis frames, contagem zero de
animações, paleta/alpha e offsets SDA permanecem. Frames de fundo e fade são
copiados com pixels idênticos, preservando suas dimensões/hotspots.

O frame de Retomar cresce de 180×24 para **256×128**, com hotspot horizontal
90→128 para manter o texto centralizado em x=320. O hotspot vertical continua
12 e a posição do objeto permanece y=330. A área entre o botão e a assinatura
é inteiramente transparente, permitindo que a imagem de fundo e os créditos
oficiais continuem visíveis. Não aumentar extents ou arquivos da ISO.

| Frame | Retângulo novo | Hotspot |
|---|---|---|
| Novo jogo | 0,0,180,24 | 90,12 |
| Retomar + assinatura | 0,128,256,256 | 128,12 |
| Instalar | 0,24,180,48 | 90,12 |
| Fade | 240,0,245,4 | 1,1 |
| Borda | 0,48,228,88 | 114,22 |
| Fundo | 0,88,228,128 | 114,22 |

O crédito ocupa x=247..392, y=430..443 no espaço virtual 640×448, centralizado
abaixo do menu. Usa a fonte GFI já existente **somente para a nova linha de
créditos**, com corpo de 12 pixels e contorno preto; os botões mantêm sua fonte
própria. Não houve compressão horizontal. A fonte do motor, os bancos ASCII
e os acentos não foram modificados.

**Limitação explícita:** a assinatura acompanha a cor, transparência e visibilidade
do elemento Retomar. Pode ficar acinzentada quando esse botão estiver desabilitado.
Uma linha independente desse estado exigiria outra solução de desenho. Isso
ainda precisa de conferência no jogo, assim como a distância das três linhas
de créditos originais; o preview geométrico não inclui a imagem de fundo real.

## Reprodução e teste visual

```powershell
python tools/title_credit.py --output work/credito-revisao-nova
python tools/interface_graphics.py --recipe translations/interface-graphics-v007.json --output work/graficos-credito-novo
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v011.json --output work/interface-v011 --build-iso
```

Diretórios devem ser novos. Previews em `work/title-credit-v007/`:
`atlas-ptbr.png` e `posicionamento-menu-credito.png`. O segundo é uma projeção
geométrica sobre fundo neutro, **não uma captura do PCSX2**.

`Iniciar-Teste.cmd` e `Testar-Interface.cmd` abrem a ISO v011:
`work/interface-v011/MetalSaga-ptbr-interface-v011.iso`.
Conferir numa inicialização limpa:

- Os dois R de RETOMAR devem ser legíveis como R, com perna diagonal.
- A assinatura deve estar completa, centralizada e sem cobrir créditos oficiais.
- Conferir a assinatura com Retomar acinzentado e, quando houver save disponível,
  selecionável. Comparar também as bordas e a seleção de Novo jogo/Retomar.
- O rótulo Instalar continua apenas traduzido; não se ativou sua função.

A execução visual desta versão permanece pendente. Não houve cópia OneDrive.
A alpha continua permanente e a retenção mantém dez ISOs de trabalho.

## Verificações executadas

- **60 testes de interface passaram**, incluindo seis novos para o R, separação
  dos frames, cópia exata de borda/fundo/fade, transparência intermediária,
  limites da assinatura, preservação dos patches FBS e recusa de deriva na receita.
- ISO de 1.704.427.520 bytes, SHA-256
  `de08838897a3ceda7b9066b10fc3b1344cfd6d1ca2fa5a8d6dc4e5c5771c7849`.
  Compilação com 5.892 registros MAP alterados, 1.339 preservados, zero recusas;
  621 campos/ocorrências de interface.
- Comparação integral v010→v011: **20.861 bytes diferentes em dois patches**,
  ambos RTITLE (pixels e tabela dos seis frames). Todo o restante da ISO,
  inclusive o ELF, vídeos, fontes e diálogos, permaneceu idêntico.
- Previews inspecionados localmente. A tentativa de abrir DEMO.STM diretamente
  no ffprobe não reconheceu o contêiner MSTM; não houve decodificação/edição do
  vídeo nem extração de quadro para conferir o fundo. Não afirmar que a posição
  da assinatura foi validada contra os créditos em execução.
- Mantidas dez ISOs de trabalho; alpha fora da retenção. Relatórios próprios:
  `reports/interface-v011-validation.json`, `reports/interface-v011-delta.json`
  e `reports/title-credit-v007-evidence.json`.
