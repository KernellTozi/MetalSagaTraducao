# Interface v005 — índice da ajuda

Esta rodada traduz **53 rótulos do índice da ajuda** e padroniza mais um literal
de status do tanque como `MAIN %d SUB %d SE %d`. Acumulado: **573 campos alterados
de interface**, mantendo integralmente os 519 anteriores e os diálogos MAP v030.
Não há novos diálogos nem alteração das fontes/layout v005.

O índice possui 56 rótulos: 12 categorias e 44 tópicos vinculados às páginas da
rodada anterior. Satcom, Remote e Alpha Series permanecem iguais por contexto;
esses três rótulos preservados não são contados como traduções.

## Uso local

`Preparar-Interface.cmd` valida a receita v005 sem criar ISO.
`Iniciar-Teste.cmd` e `Testar-Interface.cmd` abrem
`work/interface-v005/MetalSaga-ptbr-interface-v005.iso`.
Não é necessário alcançar uma cena distante: o teste pendente pode ser feito
na ajuda do Satcom durante uma passagem normal pelo jogo, quando conveniente.

Construção reproduzível com diretório novo:

```powershell
python tools/build_translation_pilot.py --draft translations/regiao-inicial-v030.json --interface-draft translations/interface-v005.json --output work/interface-v005 --build-iso
```

Exportação independente, local e sem APIs:

```powershell
python tools/help_index.py --output work/indice-ajuda-novo.json
```

## Evidências e limites

Política opt-in `ndata-help-index-fixed-load-v005`, somente entrada 173 do NDATA:
offset **0x10E4800**, tamanho carregado **798 bytes**. A tradução também ocupa
798 bytes; nenhum tamanho, extent ou ponteiro estático é alterado.

O carregador não usa um par contíguo de dados para esse índice: o endereço e o
tamanho estão codificados nas instruções em 0xD35D4/0xD35E0/0xD35E4, passando
`0x010E4800` e `0x31E` ao leitor em 0xD35E8. Janelas do carregador
0xD35CC–0xD35F0 e do parser 0xD3600–0xD37D0 são vinculadas por SHA-256, além do
ELF integral e do recurso NDATA original.

Categorias usam quatro dígitos e vírgula; os tópicos usam TAB, três dígitos e
vírgula. Cada linha termina em LF. O parser original transforma os separadores
em NUL na cópia carregada, converte os números e guarda ponteiros para os textos.
Os códigos de categoria são condições/valores consumidos pelo jogo, não nomes
de cenas comprovados. São preservados exatamente, incluindo repetições de 2502.
Os 44 números de tópico correspondem precisamente aos slots da tabela de páginas
em 0x322368. Não renumerar nem deduplicar pelo valor da categoria.

Não permitir vírgulas, TAB/LF/CR, NUL, pipes ou marcações injetadas nos rótulos.
O orçamento é o total carregado; o parser reconstrói seus ponteiros a partir das
linhas, permitindo redistribuir os comprimentos dentro desses 798 bytes. Preservar
ordem, IDs, hashes, agrupamento e todas as referências. O compilador lê de volta
o índice e verifica a reversão do recurso inteiro.

Esta é uma comprovação estrutural com análise estática do leitor, não execução
do PCSX2. Conferir posteriormente nomes de categorias/tópicos, cortes de rótulo,
acentos e a abertura da página correta. Os testes da ajuda v004 continuam
acumulados no mesmo roteiro; nenhuma aprovação visual foi presumida.

## Avanço dos textos gráficos

A ferramenta `tools/interface_texture_pack.py` já permite exportar/importar seis
texturas inspecionadas sem perda, em cópias separadas. Manual em
`docs/texturas-interface-v002.md`. Exportação e reconstrução sem edição foram
executadas: os dois SDA resultantes são idênticos aos originais por bytes/hash.
Isso prepara a próxima etapa de rótulos rasterizados, mas **não representa
tradução desses desenhos** nem aplicação de texturas novas à ISO.

A alpha permanece preservada; no máximo dez ISOs sob work/. A cópia do OneDrive
da rodada anterior não é substituída automaticamente: uma nova entrega exige
solicitação explícita, conforme a regra permanente do usuário.


## Verificações executadas

- 45 testes automatizados aprovados: índice (4), interface e transporte gráfico (24), ajuda anterior/regressão MAP (6), retenção (4), layout v005 (4) e alpha (3).
- CLI de exportação do índice executada: 56 rótulos. CLI de texturas executada em exportação/importação: seis PNGs, dois SDA idênticos aos originais. Os testes de edição usaram somente cópias temporárias isoladas.
- Construção: 5.892 registros MAP alterados, 1.339 preservados, zero recusas e 573 campos de interface. Conferência integral contra a ISO original realizada pelo construtor.
- Comparação integral contra a v004: somente 762 bytes diferentes em dois patches. Todo o restante, incluindo MAP, fontes, layout e diretório ISO, permanece igual. O verificador reutiliza a compilação de diálogos quando as duas receitas resolvidas são idênticas, sem abreviar a comparação dos bytes das imagens.
- ISO: 1.704.427.520 bytes; SHA-256 `fa0dc5783fefe0fa9593ba670365f7f5dcdb05288a202bece422acd9b9343434`. Dez imagens de trabalho, mais a alpha preservada fora da retenção.
- Metadados em `reports/interface-v005-validation.json`, `reports/interface-v005-delta.json` e `reports/interface-v005-index-evidence.json`. PCSX2 não executado nesta rodada; aprovação visual permanece pendente.
