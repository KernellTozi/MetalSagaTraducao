# Interface v006 — primeiro lote gráfico

Preserva os **573 campos de texto** da v005 e todos os diálogos MAP v030.
Acrescenta **40 ocorrências de rótulos gráficos**, com variantes selecionadas e
normais contadas separadamente: 26 no Satcom, dez comandos de batalha e quatro
cabeçalhos. São 613 campos/ocorrências de interface compilados; isso não equivale
a 613 palavras únicas nem a cobertura completa da interface do jogo.

## Rótulos desta rodada

Satcom: Lojas, Dados, Caça, Procurados, Mensagens, Alerta, Música, Jogos, Ajustes,
Diário, Ajuda, Cancelar e Confirmar, em duas variantes cada.

Batalha: **MAIN, SUB, SE**, Habil., Equip., Munição, Fugir, Arma, Passar e Defesa.
Item já é adequado em português; Drive fica preservado nesta rodada para manter
consistência com os dez tutoriais existentes e a ajuda. Remote também permanece
coerente com o índice e a ajuda atuais. Uma mudança futura desses termos exige
revisão conjunta das referências; não trocar somente o botão.

Cabeçalhos: De, Assunto, Título e Tempo de jogo. O antigo “Sub” é assunto da
mensagem, contexto distinto da categoria **SUB** dos tanques. A regra do usuário
continua preservada para o armamento. O corpo das mensagens não foi localizado
por este trabalho e não é declarado traduzido.

Não foram editados os dois rótulos riscados de Música/Jogos indisponíveis, o
pequeno PlayingTime junto aos algarismos nem Satcom/BS-Controller. O lote não
altera RTITLE, New Game/Load Game, opções gráficas ou a tela gráfica de nomeação.
Esses são conjuntos distintos, que continuam na investigação de interface.

## Uso

`Preparar-Interface.cmd` valida a receita consolidada. `Iniciar-Teste.cmd` e
`Testar-Interface.cmd` abrem a v006:
`work/interface-v006/MetalSaga-ptbr-interface-v006.iso`.

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v006.json --output work/interface-v006 --build-iso
```

O diretório de construção deve ser novo. Para conferir somente os desenhos, sem
gerar ISO, executar **Preparar-Graficos.cmd**. A ferramenta compõe os glifos
localmente e exporta seis previews RGB (três originais e três traduzidos) e um
relatório em uma pasta nova de work/graficos/:

```powershell
python tools/interface_graphics.py --output work/graficos-revisao-nova
```

Não usa IA, APIs, fontes do Windows ou fontes externas. Os desenhos são compostos
dos glifos GFI do próprio jogo, com os acentos do perfil de bitmap v002 já usado
pelo layout v005. Os arquivos GFI e as rotinas de texto não são modificados nesta
rodada. A fonte é apenas a matéria-prima dos pixels já rasterizados na textura.

## Segurança e reprodução

Manual técnico: `docs/graficos-interface-v003.md`. A receita
`translations/interface-graphics-v003.json` tem hash vinculado na v006. IDs,
traduções revisadas, recortes GANM e máscaras rasterizadas são conferidos antes de
produzir três patches de tamanho fixo somente nos dados de pixels do FBS_DATA.
Headers, paletas, alpha, GANM, offsets, tamanhos e outros recursos são preservados.
Desenhos que não couberem ou divergirem da máscara vinculada são recusados.

Os previews foram inspecionados localmente. A execução no PCSX2 ainda não foi
realizada nesta rodada. Quando for possível jogar, conferir o Satcom, o menu de
batalha e os cabeçalhos de diário/mensagens: legibilidade, acentos, estados de
seleção, recortes e consistência das cores. Não é necessário testar agora para
permitir o avanço de tarefas independentes.

Alpha preservada e no máximo dez ISOs de trabalho. Conforme o usuário reafirmou,
copiar para o OneDrive somente mediante novo pedido explícito.


## Verificações executadas nesta entrega

- 50 testes automatizados aprovados: interface e gráficos (29), índice da ajuda (4), ajuda/regressão de diálogos (6), retenção (4), layout v005 (4) e alpha (3).
- CLI gráfico executado: 40 ocorrências conferidas, três pares de previews inspecionados, nenhuma ISO alterada por esse comando. Previews locais em `work/interface-graphics-v003-final/`.
- Construção consolidada: 5.892 registros MAP alterados, 1.339 preservados, zero recusas; 573 campos textuais e 40 ocorrências gráficas. Comparação integral contra a ISO original concluída pelo construtor.
- Comparação integral com a v005: 18.058 bytes diferentes em três patches somente de pixels FBS. Diretório ISO, headers/tabelas SDA e GANM, paletas, fontes/layout, ELF, diálogos e demais recursos preservados.
- ISO de 1.704.427.520 bytes; SHA-256 `3a65621e67249c3b78e58cbe9a5104bb51f207379c2842b0c577ad51a43082ab`. Dez ISOs em work/, com a alpha permanente fora da retenção.
- Relatórios próprios: `reports/interface-v006-validation.json`, `reports/interface-v006-delta.json` e `reports/interface-graphics-v003-evidence.json`. PCSX2 não executado; teste visual consolidado continua pendente.
