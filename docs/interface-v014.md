# Interface v014 — arte completa aprovada aplicada

Aplica a proposta de `docs/arte-titulo-v001.md`, aprovada expressamente pelo
usuário: “Ótimo, pode aplicar essa versão”. Substitui NOVO JOGO, RETOMAR e
INSTALAR pelas palavras completas geradas e preparadas na rodada anterior.
Não há nova geração de imagem, colagem de glifos ou alteração da arte aprovada.

## Transporte e preservação

Ferramenta `tools/title_wordart.py`, política opt-in
`title-approved-complete-word-art-v010`, receita
`translations/interface-graphics-v010.json`. Herda por hash a receita gráfica
v009 e substitui somente o patch dos pixels RTITLE. Os três PNGs indexados de
`work/title-wordart-v001/preparado/` têm SHA-256 de arquivo e índices vinculados
individualmente, identidade e ordem explícitas. RGB e alpha bruto da paleta
original devem ser idênticos; formato P e tamanho 228×24 são obrigatórios.

As células aprovadas entram nos retângulos:

| Palavra | Posição no atlas | Célula |
|---|---|---|
| NOVO JOGO | 0,0 | 228×24 |
| RETOMAR | 14,128 | 228×24 |
| INSTALAR | 0,24 | 228×24 |

Retomar continua centralizado no frame 256×128 que também contém a assinatura.
Somente suas primeiras 24 linhas recebem a nova palavra. Os pixels da assinatura,
as imagens de borda/fundo/fade, os seis frames e seus hotspots/UV, a paleta, os
descritores e o código ELF ficam idênticos à v013. A assinatura ainda acompanha
a cor/visibilidade de Retomar; esta rodada não altera esse comportamento.

É proibido promover um PNG modificado apenas por ter o mesmo nome. A compilação
recusa hashes, índices, ordem, dimensão, modo ou paleta divergentes e verifica
que todas as diferenças estejam dentro dos três intervalos permitidos.
O round-trip recupera o atlas pai byte a byte.

Os assets locais aprovados e seu master permanecem em work/, com pacote
`work/title-wordart-v001/palavras-editaveis.zip`. Devem ser preservados para
reproduzir esta receita; scripts e hashes no Git não recriam o desenho sem esses
PNGs. A execução de preparação/aplicação já é integralmente local, sem IA/API.

## Versão e reprodução

- Receita atual `translations/interface-v014.json`, sobre MAP v030/layout v005.
- Mesmos 641 campos/ocorrências de interface (44 gráficos), 5.892 traduções MAP
  e 1.339 registros preservados. Esta revisão é gráfica e não aumenta contagens.
- `Iniciar-Teste.cmd` e `Testar-Interface.cmd` abrem
  `work/interface-v014/MetalSaga-ptbr-interface-v014.iso`.
- `Preparar-Interface.cmd` valida v014; `Preparar-Graficos.cmd` usa gráficos v010.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v014.json --output work/interface-reproducao-v014 --build-iso
python -m unittest discover -s tests -p "test_interface*.py" -v
```

A aprovação foi do desenho apresentado em preview. Não equivale à validação
visual desta ISO no PCSX2. O usuário realiza o teste: iniciar sem savestate e
conferir desenho, espaçamento, recorte e seleção de NOVO JOGO/RETOMAR. INSTALAR
recebe a mesma arte, sem ativar ou modificar sua função. Sem nova navegação
automática, cópia OneDrive ou desligamento nesta rodada. Originais/alpha e
retenção de dez ISOs de trabalho preservados.

## Verificações executadas

- Suíte de interface: 75 testes passaram em 239,091 s. Um teste adicional de
  transporte exato dos índices aprovados passou em 19,662 s: 76 testes distintos.
- Comparação integral v013→v014: 9.284 bytes diferentes em um único patch de
  pixels RTITLE; todo o restante da ISO e seu diretório permanecem idênticos.
- ISO: 1.704.427.520 bytes; SHA-256
  `fa516e211df45c868dc9958cfd8b9e62cfb6d737cd8662b3170f5b2fa757fbbf`.
- Relatórios: `reports/interface-v014-validation.json` e
  `reports/interface-v014-delta.json`. Nenhuma execução no PCSX2 nesta rodada.
